---
title: "lyeh-infra"
date: 2026-04-01
summary: "Personal brand infrastructure on Hetzner CX23. k3s cluster with ArgoCD GitOps, Traefik ingress, cert-manager TLS, and multi-app deployment via ApplicationSet."
tags: ["Kubernetes", "k3s", "ArgoCD", "Traefik", "cert-manager", "Hetzner"]
---

## Overview

Personal cloud infrastructure for running self-hosted services and demonstrating platform engineering skills.

## Stack

- **Compute:** Hetzner CX23 (3 vCPU / 4 GB RAM)
- **Orchestration:** k3s (lightweight Kubernetes)
- **GitOps:** ArgoCD with ApplicationSet (Git directory generator)
- **Ingress:** Traefik (built-in k3s)
- **TLS:** cert-manager + Let's Encrypt production

## Architecture

Apps are auto-discovered by ArgoCD — adding a new service is as simple as creating a directory under `apps/` and pushing to Git. ArgoCD handles deployment, health checks, and self-healing automatically.

## Links

- [GitHub](https://github.com/LeaYeh/lyeh-infra)
