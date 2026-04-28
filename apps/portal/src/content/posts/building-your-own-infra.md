---
title: "Building Your Own Infrastructure for the Portfolio: Self-hosting on k3s with ArgoCD GitOps"
date: 2026-04-27
tags: ["Kubernetes", "k3s", "ArgoCD", "GitOps", "Hetzner", "Traefik", "cert-manager"]
summary: "Why I built my own Kubernetes infrastructure instead of using GitHub Pages or Vercel — and how the infra itself became part of the portfolio."
---

## Why not GitHub Pages or Vercel?

I needed three things a static hosting service can't give me:

1. **A version-controlled resume** that I can update with a `git push` and track over time
2. **A place to demo side projects** — not just link to code, but actually run them with a real URL
3. **An architecture showcase** — somewhere I can embed live demos and document design decisions in context

GitHub is too scattered for this. WordPress isn't flexible enough. Vercel and Netlify only serve static files or serverless functions — they can't run a real service with its own subdomain.

The key insight: **if I self-host on Kubernetes, the infrastructure itself becomes part of the portfolio**. Any side project gets its own subdomain and a real deployment pipeline. The infra I built to host the portfolio demonstrates the same skills I'm trying to show.

| | GitHub Pages | Vercel / Netlify | Self-host k3s |
|---|---|---|---|
| Version-controlled resume | ✅ | ✅ | ✅ |
| Run real services | ❌ | ❌ | ✅ |
| Live demo per subdomain | ❌ | ❌ | ✅ |
| Architecture as a portfolio piece | ❌ | ❌ | ✅ |
| Long-term side project hosting | ❌ | ❌ | ✅ |
| Cost | Free | Free–$20 | €6/mo |

## Why k3s on a single VM

Full Kubernetes is designed for multi-node clusters. The control plane alone consumes significant resources — on a single €6/month VM, that overhead doesn't make sense. k3s ships as a single ~70 MB binary with Traefik and a storage provisioner included. On one VM, it's the obvious choice.

Minikube and kind are local-only tools for development — they can't serve real traffic.

## The stack

- **Hetzner CX23** — 3 vCPU, 4 GB RAM, €6/month
- **k3s** — lightweight Kubernetes, single binary, ships with Traefik
- **Traefik** — ingress controller, routes traffic by hostname to the right service
- **cert-manager** — requests and renews Let's Encrypt certificates automatically
- **ArgoCD** — watches the Git repo and keeps the cluster in sync
- **Cloudflare** — DNS + CDN in front of the VM (orange cloud, Full SSL mode)

## The GitOps design: ApplicationSet

The core architectural decision was using ArgoCD's **ApplicationSet** with a **Git directory generator** instead of managing Applications manually.

Every subdirectory under `apps/` is automatically discovered and deployed:

```
apps/
├── portal/      → auto-deployed as "portal" app to namespace "portal"
├── monitoring/  → auto-deployed as "monitoring" app
└── argocd/      → self-managed
```

Adding a new service:
```bash
mkdir apps/my-service
# add kustomization.yaml, deployment.yaml, service.yaml, ingress.yaml
git push
# ArgoCD picks it up within ~3 minutes, namespace created automatically
```

The cluster self-heals: if anything is changed manually, ArgoCD reverts it to match Git. Git is the only source of truth.

## How traffic flows

```
Browser → Cloudflare (CDN, Full SSL) → Hetzner VM :443
  → Traefik (routes by hostname)
  → Service (ClusterIP)
  → Pod
```

Traefik reads `Ingress` resources to know which hostname maps to which service. cert-manager watches those same resources and requests TLS certificates from Let's Encrypt when it sees the `letsencrypt-prod` annotation.

## Bootstrap: from blank VM to running cluster

The entire setup is scripted and runs in four steps:

```
1. Provision VM + open firewall ports (80, 443, 6443)
   Configure DNS A records: lyeh.dev and *.lyeh.dev → VM IP

2. Install k3s
   curl -sfL https://get.k3s.io | sh -

3. Install cert-manager + ClusterIssuer

4. Run bootstrap/install-argocd.sh (once)
   → installs ArgoCD, loads SSH deploy key, applies ApplicationSet
   → GitOps mode active, cluster is now self-managing
```

After step 4, I never need to run `kubectl apply` for a new service again.

## The hardest debugging session

After getting everything running — k3s healthy, ArgoCD synced, nginx responding — the site still showed the old page. I checked the VM, the pods, the ingress. Everything looked correct.

The problem was Cloudflare. With orange cloud enabled, Cloudflare caches responses and serves them directly without hitting the origin. The cluster was fine; the traffic never reached it.

Fix: **Purge Cache** from the Cloudflare dashboard. The correct content appeared immediately.

Lesson: when Cloudflare is in proxy mode, always purge cache before debugging the origin. After this, cache stays on — that's the whole point of running through Cloudflare.

## Source

[github.com/LeaYeh/lyeh-infra](https://github.com/LeaYeh/lyeh-infra)
