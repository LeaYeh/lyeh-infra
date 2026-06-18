# agent — Remote AI Agent Environment

Runbook for the out-of-band setup that is intentionally NOT in git.

## 1. Cloudflare Tunnel (Zero Trust dashboard)

1. Zero Trust → Networks → Tunnels → Create a tunnel (type: Cloudflared).
2. Name it `agent`. Copy the **tunnel token** (used for the `cloudflared-token` Secret).
3. Add a **Public Hostname**:
   - Subdomain/Domain: `agent.lyeh.dev`
   - Service: `HTTP` → `claudecodeui.agent.svc.cluster.local:80`
   - (DNS for `agent.lyeh.dev` must be on Cloudflare; the tunnel creates the CNAME.)

## 2. Cloudflare Access (SSO + allowlist)

1. Zero Trust → Access → Applications → Add → Self-hosted.
2. Application domain: `agent.lyeh.dev`.
3. Identity: add a login method (GitHub or Google) under Settings → Authentication.
4. Policy: Action **Allow**, Include → **Emails** → your email only.
5. (Optional) Require MFA; set short session duration.

## 3. Create cluster Secrets (not in git)

```bash
# Tunnel token from step 1.2
kubectl create secret generic cloudflared-token \
  -n agent --from-literal=token='<TUNNEL_TOKEN>'

# Reused full-access GitHub SSH private key already on the VM.
# (Accepted risk per spec; recommended follow-up: scope to a fine-grained PAT/deploy key.)
kubectl create secret generic agent-git-ssh \
  -n agent --from-file=id_ed25519=$HOME/.ssh/id_ed25519
```

## 4. First-run Claude login (persists on the PVC)

```bash
kubectl exec -it deploy/claudecodeui -n agent -- claude /login
# Complete the OAuth flow; creds land in /data/.claude and survive pod restarts.
```

## 5. Git identity (one-time, inside the workspace)

```bash
kubectl exec -it deploy/claudecodeui -n agent -- sh -lc \
  'git config --global user.name "Lea Yeh" && git config --global user.email "<you@example.com>"'
```
