---
title: "Building lyeh-infra: Self-hosting on k3s with ArgoCD GitOps"
date: 2026-04-27
tags: ["Kubernetes", "k3s", "ArgoCD", "GitOps", "Hetzner"]
summary: "How I built a personal cloud infrastructure on a €5/month Hetzner VM — k3s, ArgoCD, Traefik, cert-manager, and full GitOps from day one."
---

## Why self-host?

Running your own infrastructure is a good way to understand the tools you work with every day — and for a backend/platform engineer, that includes Kubernetes.

I wanted a playground that felt real: real TLS, real GitOps, real ingress routing — not just a local Minikube cluster.

## The stack

- **Hetzner CX23** — 3 vCPU, 4 GB RAM, €5/month. Enough for multiple small services.
- **k3s** — Lightweight Kubernetes. Comes with Traefik and a local storage provisioner. Perfect for single-node setups.
- **ArgoCD** — GitOps controller. Watches a GitHub repo and keeps the cluster in sync with what's declared in Git.
- **cert-manager** — Automatic Let's Encrypt certificates. Set it up once, forget about it.
- **Traefik** — Ingress controller (built into k3s). Routes traffic to the right service based on hostname.

## The GitOps pattern

The key decision was using ArgoCD's **ApplicationSet** with a **Git directory generator**. This means:

1. Any directory I create under `apps/` gets automatically detected and deployed
2. No manual ArgoCD setup per app — just push to Git
3. The cluster self-heals if someone manually changes something

New app in 3 steps:
```bash
mkdir apps/my-new-service
# add kustomization.yaml, deployment.yaml, service.yaml, ingress.yaml
git push
# ArgoCD picks it up within ~3 minutes
```

## What I learned

- k3s is remarkably stable for personal projects
- ArgoCD's sync wave feature is useful for ordering resource creation
- cert-manager's ACME HTTP-01 challenge works seamlessly behind Traefik

## Source

Full source at [github.com/LeaYeh/lyeh-infra](https://github.com/LeaYeh/lyeh-infra).
