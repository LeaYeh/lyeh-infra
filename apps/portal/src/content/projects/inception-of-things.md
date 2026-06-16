---
title: "Inception-of-Things — K3s Kubernetes Cluster"
date: 2025-06-01
summary: "Provisioned a multi-node K3s cluster using Vagrant and VirtualBox, with ingress routing, GitOps-style deployment via ArgoCD, and full cluster networking."
tags: ["Kubernetes", "k3s", "ArgoCD", "GitOps", "Vagrant", "DevOps"]
---

## Overview

Provisioned and configured a multi-node K3s (lightweight Kubernetes) cluster using Vagrant and VirtualBox, covering cluster networking, ingress, and GitOps-style deployment workflows.

## What I built

- Deployed a multi-node K3s cluster with Vagrant-provisioned VMs, including nested virtualization setup
- Configured Kubernetes ingress, service routing, and workload deployment across cluster nodes
- Applied GitOps principles with ArgoCD for continuous deployment in the bonus track

## Connection to lyeh-infra

This project was the hands-on foundation for [lyeh-infra](/projects/lyeh-infra/) — the real-world single-node k3s cluster now serving this site. The difference: Inception-of-Things was a controlled learning environment; lyeh-infra is production.

## Links

- [GitHub](https://github.com/42-CC-RNCP/Inception-of-Things)
