---
title: "lyeh-infra"
date: 2026-04-01
summary: "Personal cloud infrastructure on a single Hetzner VM — k3s, ArgoCD GitOps, Traefik ingress, cert-manager TLS, Prometheus + Grafana monitoring. New services deploy by git push."
tags: ["Kubernetes", "k3s", "ArgoCD", "Traefik", "cert-manager", "Hetzner", "GitOps", "Prometheus", "Grafana"]
---

## Overview

Personal cloud infrastructure for running self-hosted services. Everything is declared in Git — adding a new service means creating a directory and pushing; ArgoCD handles the rest automatically.

**Live services:**
- `lyeh.dev` — this portfolio site (Hugo + nginx)
- `argocd.lyeh.dev` — ArgoCD UI
- `jd.lyeh.dev` — JD Explorer
- `monitoring.lyeh.dev` — Grafana dashboards (Prometheus stack)

## Architecture

### Traffic flow

```
Browser
  │  HTTPS
  ▼
Cloudflare  (orange cloud — CDN + DDoS protection, Full SSL mode)
  │  HTTPS → origin
  ▼
Hetzner CX23  :443
  │
Traefik  (Ingress Controller — routes by hostname)
  │  lyeh.dev → portal Service
  │  argocd.lyeh.dev → argocd Service
  │  ...
  ▼
Service (ClusterIP)
  │
Pod
```

Traefik runs as part of k3s and binds directly to host ports 80/443. It reads `Ingress` resources to know which hostname maps to which service — no manual routing config needed when adding new apps.

**TLS:** cert-manager watches Ingress resources for the `letsencrypt-prod` annotation, requests certificates from Let's Encrypt automatically, and stores them as Kubernetes Secrets. Traefik reads those Secrets to terminate TLS.

### GitOps with ArgoCD ApplicationSet

The core design is an ArgoCD **ApplicationSet** using a Git directory generator:

```
apps/
├── portal/        ← ArgoCD discovers this → deploys as "portal" app
├── monitoring/    ← ArgoCD discovers this → deploys as "monitoring" app
├── argocd/        ← self-managed
└── _template/     ← excluded
```

Every subdirectory under `apps/` becomes an ArgoCD Application automatically. The template:

```yaml
name: '{{path.basename}}'       # app name = directory name
path: '{{path}}'                # reads kustomization.yaml from that dir
namespace: '{{path.basename}}'  # deploys into same-named namespace
syncPolicy:
  automated:
    prune: true      # resources deleted from Git get deleted from cluster
    selfHeal: true   # manual cluster changes get reverted to match Git
  syncOptions:
    - CreateNamespace=true
```

**AppProject** defines the trust boundary — ArgoCD only accepts sources from `git@github.com:LeaYeh/lyeh-infra.git` and only deploys to the local cluster.

### Bootstrap sequence

A fresh VM goes from zero to fully running in four scripted steps:

```
1. Provision VM
   ├── Hetzner CX23 (3 vCPU / 4 GB RAM / €6 per month)
   ├── Firewall: open 80 (HTTP), 443 (HTTPS), 6443 (k8s API)
   └── DNS: A records for lyeh.dev and *.lyeh.dev → VM IP

2. Install k3s
   └── curl -sfL https://get.k3s.io | sh -
       → ships with Traefik + local-path provisioner, ready immediately

3. Install cert-manager
   └── kubectl apply -f cert-manager.yaml
       → apply ClusterIssuer pointing to Let's Encrypt production

4. Bootstrap ArgoCD (run once)
   ├── Install ArgoCD
   ├── Load SSH deploy key → ArgoCD can read the private repo
   ├── Apply AppProject + ApplicationSet
   └── ArgoCD takes over — GitOps mode active
```

After step 4, the cluster is self-managing. Every subsequent change goes through Git.

## CI/CD: how a content change reaches the site

The portal site (this site) has a fully automated pipeline. Every push to `apps/portal/src/` triggers GitHub Actions:

```
git push (content change in apps/portal/src/)
  │
  ▼
GitHub Actions
  ├── checkout repo (with --recurse-submodules for Blowfish theme)
  ├── install Hugo 0.160.1 extended
  ├── hugo --minify  → builds static HTML into public/
  ├── docker build   → nginx:alpine + public/
  ├── docker push    → ghcr.io/leayeh/portal:sha-{GITHUB_SHA}
  ├── sed -i         → update image tag in apps/portal/deployment.yaml
  └── git commit + push  → "chore(portal): bump image to sha-abc1234"
            │
            ▼
      ArgoCD detects deployment.yaml changed
            │
            ▼
      k8s rolling update → new pod up, old pod down
            │
            ▼
      lyeh.dev serves new content
```

The key step is the `sed` + `git commit` — GitHub Actions writes the new image SHA directly back into the repo. ArgoCD then picks it up like any other Git change.

### Why SHA, not a tag

Docker image tags — including `latest` and versioned tags like `v1.0.0` — are **mutable**. Any tag can be overwritten by pushing a new image with the same name. There is nothing in the Docker protocol that prevents this.

```
# Both of these can silently change over time:
ghcr.io/leayeh/portal:latest   →  image A  (Monday)
ghcr.io/leayeh/portal:latest   →  image B  (Tuesday, same tag, different content)

ghcr.io/leayeh/portal:v1.0.0   →  image A  (original release)
ghcr.io/leayeh/portal:v1.0.0   →  image C  (re-tagged after a hotfix, same version string)

# SHA is the only identifier that cannot be overwritten:
ghcr.io/leayeh/portal:sha-abc123  →  always image A, forever
ghcr.io/leayeh/portal:sha-def456  →  always image B, forever
```

A SHA is a cryptographic hash of the image content. It is computed from what's inside the image — two different images will always have different SHAs, and the same image will always produce the same SHA. It cannot be reassigned.

In a GitOps setup this matters for two reasons:

**1. Git is the source of truth.** The SHA pinned in `deployment.yaml` tells you exactly what is running — not approximately, not "probably v1.0.0", exactly. If you read the file six months from now you can pull that exact image and reproduce what was running.

**2. ArgoCD detects changes by diffing Git vs cluster state.** If `deployment.yaml` says `latest` and the cluster is already running `latest`, ArgoCD sees no diff — even if the image content changed. With SHA, every new build produces a new hash, the `sed` step writes it into `deployment.yaml`, ArgoCD sees a real diff and deploys.

The `latest` tag is still pushed alongside SHA as a convenience for local debugging — but it is never referenced in `deployment.yaml`.

## Why k3s

Single VM, no need for multi-node cluster management. Full Kubernetes control plane alone would consume a significant portion of the available RAM on a CX23. k3s ships as a ~70 MB binary with Traefik and storage provisioner included — everything needed for a single-node setup, nothing that isn't.

## Debugging: the Cloudflare cache trap

The trickiest issue during setup: after everything was working — VM running, ArgoCD synced, nginx responding — the site still showed the old page. The cluster was fine. The problem was Cloudflare had cached the previous response and was serving it directly without reaching the origin.

Fix: **Purge Cache** from the Cloudflare dashboard. Once the real content loaded correctly, cache was left enabled — that's the whole point of running through Cloudflare.

Lesson: when Cloudflare orange-cloud is active and changes aren't visible, always purge cache before debugging the origin.

## Links

- [GitHub](https://github.com/LeaYeh/lyeh-infra)
