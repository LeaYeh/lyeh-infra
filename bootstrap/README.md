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

## Remote AI agent (claudecodeui) — optional

The `agent` app (claudecodeui behind a Cloudflare Tunnel) is deployed by ArgoCD
from `apps/agent/`. Its two secrets and the Cloudflare side are out-of-band, so
finish the setup with the helper:

```bash
./setup-agent.sh            # interactive: creates secrets, waits, runs `claude /login`
./setup-agent.sh --help     # options (--key, --skip-login)
```

It creates the `agent-git-ssh` and `cloudflared-token` secrets, prints the exact
Cloudflare Tunnel + Access values to enter (`agent.lyeh.dev` →
`claudecodeui.agent.svc.cluster.local:80`, SSO + email allowlist), and logs in to
your Claude subscription. Full reference: `../apps/agent/README.md`.
