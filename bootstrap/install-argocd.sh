#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
SSH_KEY="${HOME}/.ssh/argocd_lyeh_infra"
REPO_URL="git@github.com:LeaYeh/lyeh-infra.git"

# Step 1: Verify SSH key exists
if [[ ! -f "${SSH_KEY}" ]]; then
  echo "❌ SSH key not found: ${SSH_KEY}"
  echo "   Ensure the key exists and its public key is added to:"
  echo "   GitHub → LeaYeh/lyeh-infra → Settings → Deploy Keys"
  exit 1
fi
echo "✅ SSH key found: ${SSH_KEY}"

# Step 2: Create argocd namespace
kubectl create namespace argocd --dry-run=client -o yaml | kubectl apply -f -

# Step 3: Install ArgoCD
echo "⏳ Installing ArgoCD..."
kubectl apply -k "${REPO_ROOT}/argocd/install/"

# Step 4: Wait for ArgoCD server to be ready
echo "⏳ Waiting for ArgoCD server..."
kubectl rollout status deployment/argocd-server -n argocd --timeout=300s

# Step 5: Create repository secret with existing SSH private key
echo "🔑 Configuring repo access..."
kubectl apply -f - <<EOF
apiVersion: v1
kind: Secret
metadata:
  name: argocd-repo-lyeh-infra
  namespace: argocd
  labels:
    argocd.argoproj.io/secret-type: repository
stringData:
  type: git
  url: ${REPO_URL}
  sshPrivateKey: |
$(sed 's/^/    /' "${SSH_KEY}")
EOF

# Step 6: Apply AppProject
kubectl apply -f "${REPO_ROOT}/argocd/projects/lyeh-dev.yaml"

# Step 7: Apply ApplicationSets — ArgoCD takes over from here
kubectl apply -f "${REPO_ROOT}/argocd/applicationsets/apps.yaml"
kubectl apply -f "${REPO_ROOT}/argocd/applicationsets/platform.yaml"

echo ""
echo "✅ ArgoCD is running. GitOps mode active."
echo "   argocd.lyeh.dev will be reachable once the platform ApplicationSet syncs (~3 min)"
echo ""
echo "   Initial admin password:"
kubectl -n argocd get secret argocd-initial-admin-secret \
  -o jsonpath="{.data.password}" | base64 -d
echo ""
