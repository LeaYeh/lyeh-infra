#!/bin/bash
set -euo pipefail

kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.15.0/cert-manager.yaml
kubectl wait --for=condition=Available deployment -l app=cert-manager -n cert-manager --timeout=300s

# Apply ClusterIssuer from platform/
kubectl apply -f ../platform/cert-manager/cluster-issuer.yaml

echo "✅ cert-manager ready"
