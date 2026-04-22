#!/bin/bash
#
# Verify that the bootstrap is complete and the cluster is healthy.
# Exits 0 if all checks pass, 1 otherwise.
#
# Usage:
#   ./verify.sh              # verify against current kubectl context
#   ./verify.sh --verbose    # show detailed output
#

set -uo pipefail

# ─── Config ───────────────────────────────────────────────────────────
HELLO_URL="${HELLO_URL:-https://hello.lyeh.dev}"
HELLO_NAMESPACE="${HELLO_NAMESPACE:-hello}"
CERT_MANAGER_NAMESPACE="${CERT_MANAGER_NAMESPACE:-cert-manager}"
CLUSTER_ISSUER_NAME="${CLUSTER_ISSUER_NAME:-letsencrypt-prod}"
TIMEOUT="${TIMEOUT:-10}"

VERBOSE=false
[[ "${1:-}" == "--verbose" || "${1:-}" == "-v" ]] && VERBOSE=true

# ─── Colors ───────────────────────────────────────────────────────────
RED=$'\033[0;31m'
GREEN=$'\033[0;32m'
YELLOW=$'\033[1;33m'
BLUE=$'\033[0;34m'
GRAY=$'\033[0;90m'
RESET=$'\033[0m'

# ─── State ────────────────────────────────────────────────────────────
PASS=0
FAIL=0
WARN=0
FAILED_CHECKS=()

# ─── Helpers ──────────────────────────────────────────────────────────
section() {
  echo ""
  echo "${BLUE}━━━ $1 ━━━${RESET}"
}

pass() {
  PASS=$((PASS + 1))
  echo "  ${GREEN}✓${RESET} $1"
  [[ "$VERBOSE" == true && -n "${2:-}" ]] && echo "    ${GRAY}$2${RESET}"
}

fail() {
  FAIL=$((FAIL + 1))
  FAILED_CHECKS+=("$1")
  echo "  ${RED}✗${RESET} $1"
  [[ -n "${2:-}" ]] && echo "    ${GRAY}$2${RESET}"
}

warn() {
  WARN=$((WARN + 1))
  echo "  ${YELLOW}!${RESET} $1"
  [[ -n "${2:-}" ]] && echo "    ${GRAY}$2${RESET}"
}

info() {
  [[ "$VERBOSE" == true ]] && echo "    ${GRAY}$1${RESET}"
}

require_tool() {
  if ! command -v "$1" &>/dev/null; then
    echo "${RED}ERROR:${RESET} required tool '$1' not found in PATH"
    exit 1
  fi
}

# ─── Pre-flight ───────────────────────────────────────────────────────
require_tool kubectl
require_tool curl

echo "${BLUE}Cluster verification — $(date '+%Y-%m-%d %H:%M:%S')${RESET}"
info "Context: $(kubectl config current-context 2>/dev/null || echo unknown)"
info "Target:  $HELLO_URL"

# ─── 1. kubectl connectivity ──────────────────────────────────────────
section "Layer 0: kubectl connectivity"

if kubectl version --request-timeout=5s &>/dev/null; then
  pass "kubectl can reach the API server"
else
  fail "kubectl cannot reach the API server" "check kubeconfig and network"
  echo ""
  echo "${RED}Aborting: nothing else can be checked without kubectl.${RESET}"
  exit 1
fi

# ─── 2. k3s node health ───────────────────────────────────────────────
section "Layer 1: k3s nodes"

NODE_STATUS=$(kubectl get nodes --no-headers 2>/dev/null)
NODE_COUNT=$(echo "$NODE_STATUS" | wc -l | tr -d ' ')
READY_COUNT=$(echo "$NODE_STATUS" | grep -c " Ready " || true)

if [[ "$NODE_COUNT" -gt 0 && "$READY_COUNT" -eq "$NODE_COUNT" ]]; then
  pass "All nodes Ready ($READY_COUNT/$NODE_COUNT)"
else
  fail "Some nodes not Ready ($READY_COUNT/$NODE_COUNT)" \
       "$(echo "$NODE_STATUS" | grep -v ' Ready ')"
fi

# ─── 3. Core system pods ──────────────────────────────────────────────
section "Layer 1: k3s system pods"

SYSTEM_ISSUES=$(kubectl get pods -n kube-system --no-headers 2>/dev/null | \
  awk '$3 != "Running" && $3 != "Completed" {print "    " $0}')

if [[ -z "$SYSTEM_ISSUES" ]]; then
  pass "All kube-system pods are Running/Completed"
else
  fail "Some kube-system pods are unhealthy" "$SYSTEM_ISSUES"
fi

# Check Traefik (k3s default ingress)
if kubectl get pods -n kube-system -l app.kubernetes.io/name=traefik --no-headers 2>/dev/null | grep -q Running; then
  pass "Traefik ingress controller is Running"
elif kubectl get pods -n ingress-nginx --no-headers 2>/dev/null | grep -q Running; then
  pass "ingress-nginx is Running"
else
  warn "No known ingress controller found (Traefik or ingress-nginx)" \
       "expected for k3s default setup"
fi

# ─── 4. cert-manager ──────────────────────────────────────────────────
section "Layer 2: cert-manager"

if kubectl get namespace "$CERT_MANAGER_NAMESPACE" &>/dev/null; then
  pass "Namespace '$CERT_MANAGER_NAMESPACE' exists"
else
  fail "Namespace '$CERT_MANAGER_NAMESPACE' missing" \
       "run bootstrap/install-cert-manager.sh"
fi

CM_DEPLOYMENTS=(cert-manager cert-manager-webhook cert-manager-cainjector)
for dep in "${CM_DEPLOYMENTS[@]}"; do
  STATUS=$(kubectl get deployment "$dep" -n "$CERT_MANAGER_NAMESPACE" \
    -o jsonpath='{.status.readyReplicas}/{.status.replicas}' 2>/dev/null)
  if [[ "$STATUS" == "1/1" ]]; then
    pass "Deployment '$dep' is ready"
  else
    fail "Deployment '$dep' is not ready" "got '$STATUS', expected '1/1'"
  fi
done

if kubectl get clusterissuer "$CLUSTER_ISSUER_NAME" &>/dev/null; then
  CI_READY=$(kubectl get clusterissuer "$CLUSTER_ISSUER_NAME" \
    -o jsonpath='{.status.conditions[?(@.type=="Ready")].status}' 2>/dev/null)
  if [[ "$CI_READY" == "True" ]]; then
    pass "ClusterIssuer '$CLUSTER_ISSUER_NAME' is Ready"
  else
    fail "ClusterIssuer '$CLUSTER_ISSUER_NAME' not Ready" \
         "$(kubectl describe clusterissuer "$CLUSTER_ISSUER_NAME" | tail -5)"
  fi
else
  fail "ClusterIssuer '$CLUSTER_ISSUER_NAME' not found" \
       "apply platform/cert-manager/cluster-issuer.yaml"
fi

# ─── 5. hello app ─────────────────────────────────────────────────────
section "Layer 3: hello smoke-test app"

if kubectl get namespace "$HELLO_NAMESPACE" &>/dev/null; then
  pass "Namespace '$HELLO_NAMESPACE' exists"
else
  fail "Namespace '$HELLO_NAMESPACE' missing" \
       "run: kubectl apply -k apps/hello/"
  # Skip remaining hello checks
  SKIP_HELLO=true
fi

if [[ "${SKIP_HELLO:-false}" != "true" ]]; then
  # Deployment
  HELLO_READY=$(kubectl get deployment -n "$HELLO_NAMESPACE" \
    -o jsonpath='{.items[0].status.readyReplicas}/{.items[0].status.replicas}' 2>/dev/null)
  if [[ -n "$HELLO_READY" && "$HELLO_READY" != "/" ]]; then
    EXPECTED=$(echo "$HELLO_READY" | awk -F/ '{print $2}')
    ACTUAL=$(echo "$HELLO_READY" | awk -F/ '{print $1}')
    if [[ "$ACTUAL" == "$EXPECTED" && "$ACTUAL" != "0" ]]; then
      pass "Deployment has $HELLO_READY replicas ready"
    else
      fail "Deployment replicas not ready" "got $HELLO_READY"
    fi
  else
    fail "No deployment found in namespace '$HELLO_NAMESPACE'"
  fi

  # Service
  SVC_COUNT=$(kubectl get svc -n "$HELLO_NAMESPACE" --no-headers 2>/dev/null | wc -l | tr -d ' ')
  if [[ "$SVC_COUNT" -gt 0 ]]; then
    pass "Service exists ($SVC_COUNT found)"
  else
    fail "No Service found in namespace '$HELLO_NAMESPACE'"
  fi

  # Ingress
  ING_COUNT=$(kubectl get ingress -n "$HELLO_NAMESPACE" --no-headers 2>/dev/null | wc -l | tr -d ' ')
  if [[ "$ING_COUNT" -gt 0 ]]; then
    pass "Ingress exists ($ING_COUNT found)"
  else
    fail "No Ingress found in namespace '$HELLO_NAMESPACE'"
  fi

  # Certificate
  CERT_READY=$(kubectl get certificate -n "$HELLO_NAMESPACE" \
    -o jsonpath='{.items[0].status.conditions[?(@.type=="Ready")].status}' 2>/dev/null)
  if [[ "$CERT_READY" == "True" ]]; then
    pass "TLS Certificate is Ready"
    CERT_EXPIRY=$(kubectl get certificate -n "$HELLO_NAMESPACE" \
      -o jsonpath='{.items[0].status.notAfter}' 2>/dev/null)
    info "Expires: $CERT_EXPIRY"
  elif [[ -z "$CERT_READY" ]]; then
    warn "No Certificate resource found" "may still be provisioning"
  else
    fail "Certificate not Ready" \
         "$(kubectl describe certificate -n "$HELLO_NAMESPACE" | tail -10)"
  fi
fi

# ─── 6. End-to-end: external HTTPS ────────────────────────────────────
section "Layer 4: end-to-end external reachability"

HTTP_CODE=$(curl --silent --output /dev/null --write-out '%{http_code}' \
  --max-time "$TIMEOUT" "$HELLO_URL" 2>/dev/null || echo "000")

case "$HTTP_CODE" in
  200|301|302|308)
    pass "HTTPS $HELLO_URL returned $HTTP_CODE"
    ;;
  000)
    fail "HTTPS $HELLO_URL unreachable (timeout or DNS fail)" \
         "check VM firewall, DNS, Cloudflare proxy"
    ;;
  4*|5*)
    fail "HTTPS $HELLO_URL returned $HTTP_CODE" "check ingress routing"
    ;;
  *)
    warn "HTTPS $HELLO_URL returned unexpected $HTTP_CODE"
    ;;
esac

# Verify TLS cert is from Let's Encrypt (not self-signed / staging)
CERT_ISSUER=$(curl --silent --max-time "$TIMEOUT" -v "$HELLO_URL" 2>&1 | \
  grep -i "issuer:" | head -1 | sed 's/.*issuer: //I')

if [[ -n "$CERT_ISSUER" ]]; then
  if echo "$CERT_ISSUER" | grep -qi "Let's Encrypt"; then
    pass "TLS cert issued by Let's Encrypt"
    info "$CERT_ISSUER"
  elif echo "$CERT_ISSUER" | grep -qi "staging"; then
    warn "TLS cert is from Let's Encrypt STAGING" \
         "production traffic will see browser warnings"
  else
    warn "TLS cert issued by unexpected CA" "$CERT_ISSUER"
  fi
fi

# ─── Summary ──────────────────────────────────────────────────────────
echo ""
echo "${BLUE}━━━ Summary ━━━${RESET}"
echo "  ${GREEN}Passed:${RESET}  $PASS"
echo "  ${YELLOW}Warned:${RESET}  $WARN"
echo "  ${RED}Failed:${RESET}  $FAIL"

if [[ "$FAIL" -eq 0 ]]; then
  echo ""
  echo "${GREEN}✅ All checks passed. Bootstrap is healthy.${RESET}"
  exit 0
else
  echo ""
  echo "${RED}❌ $FAIL check(s) failed:${RESET}"
  for check in "${FAILED_CHECKS[@]}"; do
    echo "  ${RED}•${RESET} $check"
  done
  exit 1
fi
