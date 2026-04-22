#!/bin/bash
# Install k3s on a fresh Ubuntu VM
set -euo pipefail

curl -sfL https://get.k3s.io | sh -

# Wait for k3s to be ready
until kubectl get nodes &>/dev/null; do sleep 2; done

echo "✅ k3s installed"
echo "📋 Next: run ./install-cert-manager.sh"
