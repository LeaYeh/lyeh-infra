# Bootstrap

Rebuild the entire cluster from a fresh VM.

## Prerequisites
- Hetzner CX23/CX33 VM with Ubuntu 24.04
- DNS wildcard *.lyeh.dev pointing to VM IP
- SSH access

## Steps
1. SSH to VM
2. `git clone https://github.com/LeaYeh/lyeh-infra && cd lyeh-infra/bootstrap`
3. `./install-k3s.sh`
4. `./install-cert-manager.sh`
5. `kubectl apply -k ../apps/hello/`
6. `./verify.sh`
