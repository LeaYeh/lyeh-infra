#!/bin/bash
#
# Task 10 helper — finish setting up the remote AI agent (claudecodeui) on the VM.
#
# The manifests (apps/agent/) are deployed by ArgoCD automatically. This script
# only handles the out-of-band steps that cannot live in git:
#   1. agent-git-ssh   secret  (reused GitHub SSH private key)
#   2. cloudflared-token secret (Cloudflare Tunnel token)
#   3. wait for pods, then run `claude /login` (subscription OAuth)
#
# Cloudflare Tunnel + Access themselves are configured in the Cloudflare
# Zero Trust dashboard — this script prints the exact values to enter and then
# takes the tunnel token from you.
#
# Usage:
#   ./setup-agent.sh                       # interactive, key at ~/.ssh/id_ed25519
#   ./setup-agent.sh --key ~/.ssh/id_xyz   # use a different SSH private key
#   ./setup-agent.sh --skip-login          # don't run `claude /login` at the end
#   ./setup-agent.sh -h
#
set -euo pipefail

# ─── Config ───────────────────────────────────────────────────────────
NS="agent"
DEPLOY="claudecodeui"
SVC_TARGET="claudecodeui.agent.svc.cluster.local:80"
HOSTNAME_FQDN="agent.lyeh.dev"
SSH_KEY="${HOME}/.ssh/id_ed25519"
RUN_LOGIN=true

# ─── Colors ───────────────────────────────────────────────────────────
GREEN=$'\033[0;32m'; YELLOW=$'\033[1;33m'; RED=$'\033[0;31m'
BLUE=$'\033[0;34m'; GRAY=$'\033[0;90m'; RESET=$'\033[0m'

# ─── Args ─────────────────────────────────────────────────────────────
while [[ $# -gt 0 ]]; do
  case "$1" in
    --key)        SSH_KEY="$2"; shift 2 ;;
    --skip-login) RUN_LOGIN=false; shift ;;
    -h|--help)
      awk 'NR==1{next} /^#/{l=$0; sub(/^# ?/,"",l); print l; next} {exit}' "$0"
      exit 0 ;;
    *) echo "${RED}Unknown arg: $1${RESET}"; exit 1 ;;
  esac
done

step()  { echo ""; echo "${BLUE}━━━ $1 ━━━${RESET}"; }
ok()    { echo "  ${GREEN}✓${RESET} $1"; }
warn()  { echo "  ${YELLOW}!${RESET} $1"; }
die()   { echo "  ${RED}✗ $1${RESET}"; exit 1; }

# Idempotent secret create (create-or-update without printing the value).
apply_secret() { kubectl create secret generic "$@" --dry-run=client -o yaml | kubectl apply -f - ; }

# ─── Pre-flight ───────────────────────────────────────────────────────
step "Pre-flight"
command -v kubectl >/dev/null || die "kubectl not found in PATH"
kubectl version --request-timeout=5s >/dev/null 2>&1 || die "kubectl cannot reach the cluster (check kubeconfig/context)"
ok "kubectl reachable — context: $(kubectl config current-context 2>/dev/null || echo unknown)"

if kubectl get namespace "$NS" >/dev/null 2>&1; then
  ok "namespace '$NS' exists (ArgoCD synced the agent app)"
else
  die "namespace '$NS' not found — ensure the 'agent' ArgoCD app has synced first"
fi

# ─── 1. SSH key secret ────────────────────────────────────────────────
step "1/4  agent-git-ssh secret (GitHub SSH key)"
if [[ ! -f "$SSH_KEY" ]]; then
  die "SSH private key not found: $SSH_KEY   (pass --key <path>)"
fi
warn "Reusing the full-access key '$SSH_KEY' (accepted risk per design)."
warn "Follow-up: scope to a fine-grained PAT / deploy key later."
apply_secret agent-git-ssh -n "$NS" --from-file=id_ed25519="$SSH_KEY"
ok "agent-git-ssh secret applied"

# ─── 2. Cloudflare Tunnel + token ─────────────────────────────────────
step "2/4  cloudflared-token secret (Cloudflare Tunnel)"
cat <<EOF
${GRAY}In the Cloudflare Zero Trust dashboard, first create the tunnel:
  • Networks → Tunnels → Create a tunnel (Cloudflared), name it 'agent'
  • Add a Public Hostname:
        Hostname:  ${HOSTNAME_FQDN}
        Service:   HTTP  →  ${SVC_TARGET}
    (the ${HOSTNAME_FQDN%%.*}.lyeh.dev DNS / CNAME is created by the tunnel;
     the lyeh.dev zone must be on Cloudflare)
  • Then create the Access application (so the URL is protected):
        Access → Applications → Add → Self-hosted
        Domain: ${HOSTNAME_FQDN}
        Policy: Allow → Include → Emails → your email only${RESET}
EOF
echo ""
if kubectl get secret cloudflared-token -n "$NS" >/dev/null 2>&1; then
  read -rp "  cloudflared-token already exists — replace it? [y/N] " yn
  [[ "$yn" =~ ^[Yy]$ ]] || { warn "keeping existing cloudflared-token"; SKIP_TOKEN=true; }
fi
if [[ "${SKIP_TOKEN:-false}" != "true" ]]; then
  read -rsp "  Paste the Cloudflare Tunnel token (hidden): " CF_TOKEN; echo
  [[ -n "$CF_TOKEN" ]] || die "empty token"
  apply_secret cloudflared-token -n "$NS" --from-literal=token="$CF_TOKEN"
  unset CF_TOKEN
  ok "cloudflared-token secret applied"
fi

# ─── 3. Roll out & wait ───────────────────────────────────────────────
step "3/4  Restart & wait for pods"
kubectl rollout restart deploy/"$DEPLOY" deploy/cloudflared -n "$NS"
kubectl rollout status  deploy/"$DEPLOY" -n "$NS" --timeout=180s || warn "$DEPLOY not ready yet — check: kubectl describe pod -n $NS -l app=$DEPLOY"
kubectl rollout status  deploy/cloudflared -n "$NS" --timeout=120s || warn "cloudflared not ready yet — check: kubectl logs -n $NS deploy/cloudflared"

# ─── 4. Claude subscription login ─────────────────────────────────────
step "4/4  Claude login (subscription OAuth, persists on the PVC)"
if [[ "$RUN_LOGIN" == true ]]; then
  echo "  Launching 'claude /login' inside the pod — complete the browser OAuth flow."
  read -rp "  Continue? [Y/n] " yn
  if [[ ! "$yn" =~ ^[Nn]$ ]]; then
    kubectl exec -it deploy/"$DEPLOY" -n "$NS" -- claude /login || warn "login command exited non-zero"
  else
    warn "skipped — run later: kubectl exec -it deploy/$DEPLOY -n $NS -- claude /login"
  fi
else
  warn "skipped (--skip-login) — run later: kubectl exec -it deploy/$DEPLOY -n $NS -- claude /login"
fi

# ─── Done ─────────────────────────────────────────────────────────────
echo ""
echo "${GREEN}✅ Agent setup steps applied.${RESET}"
echo ""
echo "Next:"
echo "  • Confirm the Cloudflare Access policy is active (SSO + your email only)."
echo "  • Open https://${HOSTNAME_FQDN} on your phone → SSO → claudecodeui."
echo "  • (Optional) set git identity in the workspace:"
echo "      kubectl exec -it deploy/$DEPLOY -n $NS -- sh -lc 'git config --global user.name \"Lea Yeh\" && git config --global user.email \"<you@example.com>\"'"
echo "  • Verify blast-radius containment (cross-namespace must be blocked):"
echo "      kubectl exec -n $NS deploy/$DEPLOY -- sh -lc 'curl -m 5 -s -o /dev/null -w \"%{http_code}\\n\" http://jd-explorer.jd-explorer.svc.cluster.local:80 || echo BLOCKED'"
echo ""
echo "${GRAY}Pod status:${RESET}"
kubectl get pods -n "$NS"
