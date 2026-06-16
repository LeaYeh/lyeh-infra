---
title: "ft_transcendence — Observability Stack"
date: 2025-10-01
summary: "Designed and deployed a complete observability infrastructure (metrics, logging, alerting) for a full-stack multiplayer web platform — Prometheus, Grafana, ELK stack, containerized with Docker Compose."
tags: ["Prometheus", "Grafana", "ELK", "Docker", "DevOps", "Observability"]
---

## Overview

Contributed the DevOps module for a full-stack multiplayer web platform (42 Vienna capstone project). Responsible for designing and deploying the complete observability infrastructure covering metrics, logging, and alerting.

## What I built

- Deployed Prometheus for metrics collection and configured alerting rules for service health and performance thresholds
- Built Grafana dashboards for real-time visibility into application and infrastructure metrics across the platform
- Set up ELK stack (Elasticsearch, Logstash, Kibana) for centralized log aggregation and search across distributed services
- Containerized the full observability stack with Docker Compose, enabling reproducible deployment and local development parity

## Design decisions

The key architectural choice was keeping the observability stack decoupled from the application services — each service exposes a `/metrics` endpoint, and the observability layer scrapes independently. This means the monitoring infrastructure can be updated, replaced, or scaled without touching application code.

## Links

- [GitHub](https://github.com/anastasiiap42/ft_transcendence/tree/main/devops)
