+++
name = "Lea (Mei Ling) Yeh"
label = "Senior Software Engineer | DevOps & MLOps"
image = "https://gravatar.com/avatar/4b1c334c82a3cc63710620b6daa88880?size=256&cache=1713618229156"
email = "lea.yeh.ml@gmail.com"
phone = ""

[location]
countryCode = "AT"
address = "Austria, Vienna"
postalCode = "1190"
city = "Vienna"

[[profiles]]
network = "LinkedIn"
username = "Lea Yeh"
url = "https://www.linkedin.com/in/lea-yeh-60296b74/"

[[profiles]]
network = "GitHub"
username = "LeaYeh"
url = "https://github.com/LeaYeh"
+++

# Summary

Senior Software Engineer with solution architecture responsibilities at c-sense GmbH — the sole engineer responsible for the full software stack. Background spans 9+ years in Data Engineering and Software Engineering — including PB-scale ETL pipelines and ML model monitoring at MediaTek. Continuously advancing expertise in DevOps at 42 Vienna.

# Work

## c-sense GmbH — Senior Software Engineer
<!--meta
id = "csense"
start = "2024-08-01"
end = ""
location = "Vienna, Austria"
url = "https://www.c-sense.at/"
-->

c-sense develops nanoscale sensor technology and AFM/SPM instruments for scientific and industrial applications.

- Built the GitOps delivery platform for the company's internal service pipeline — ArgoCD-driven continuous delivery across environments, with every architectural decision recorded as an ADR <!-- src: csense-h8 @ce2f -->
- Defined cross-layer interface contracts and async command-routing patterns, isolating failure domains and enabling parallel HW/SW development while reducing integration risk during concurrent R&D cycles <!-- src: csense-h4 @d8ac -->
- Architected a modular, layered SPM instrument-control framework, deliberately separating hardware-vendor, orchestration, and application layers for long-term extensibility and reuse across future instrument variants <!-- src: csense-h3 @d85d -->
- Designed a hardware-abstraction layer over a proprietary LabVIEW-based API, keeping the software stack vendor-agnostic and resilient to instrument changes <!-- src: csense-h5 @bcb5 -->
- Delivered automated measurement workflows (spatial sampling, real-time safety management) demanding concurrency and reliability, letting researchers focus on experimental outcomes rather than instrument operation <!-- src: csense-h6 @a9d2 -->

## MediaTek — Data Scientist
<!--meta
id = "mediatek-ds"
start = "2022-09-01"
end = "2023-09-01"
location = "Taipei, Taiwan"
url = "https://www.linkedin.com/company/17763"
-->

Devoted to data-related initiatives spanning cost control and chip development in the AI & Big Data department of a leading global semiconductor company.

- Built model-monitoring infrastructure (MLflow + Streamlit) for production ML systems, ensuring high availability and performance consistency <!-- src: mediatek-ds-h1 @72ec -->
- Implemented ML models for mobile thermal control achieving temperature errors below 1°C, integrated into automated workflows <!-- src: mediatek-ds-h2 @11c6 -->
- Collaborated with chip developers to reduce power consumption by 20%, yielding a 14K Antutu performance improvement <!-- src: mediatek-ds-h3 @4319 -->

## MediaTek — Data Engineer
<!--meta
id = "mediatek-de"
start = "2019-07-01"
end = "2022-09-01"
location = "Taipei, Taiwan"
url = "https://www.linkedin.com/company/17763"
-->

Built data infrastructure and analytics platforms for one of the world's largest IC design companies.

- Built model-monitoring infrastructure (MLflow + Grafana dashboards) tracking ML model performance and data drift in production <!-- src: mediatek-de-h4 @777d -->
- Built a real-time data-quality monitoring and alerting stack, driving missing-data rates from 50% to <1% and lowering monthly operational labor by 7.5 man-days <!-- src: mediatek-de-h3 @ef9e -->
- Operated PB-scale ETL infrastructure on GCP (Airflow, NiFi, Dataflow, BigQuery), establishing automated pipelines for structured and unstructured data <!-- src: mediatek-de-h1 @2a03 -->
- Managed EDA license and computing-farm cost via interactive BI dashboards (Splunk + Grafana), informing procurement decisions and reducing costs by 25% <!-- src: mediatek-de-h5 @345a -->

## MediaTek — Software Engineer
<!--meta
id = "mediatek-se"
start = "2016-09-01"
end = "2019-06-01"
location = "Taipei, Taiwan"
url = "https://www.linkedin.com/company/17763"
summary = ""
-->

- Built CI/CD automation (Python + Jenkins) enforcing documentation standards across an automated ICD DMS <!-- src: mediatek-se-h2 @0f13 -->

# Volunteer

## 42 Vienna — Peer Tutor & Workshop Host
<!--meta
id = "42-vienna-tutor"
start = "2024-07-01"
end = "2024-10-01"
url = "https://www.42vienna.com/"
-->

Volunteered as a peer tutor at 42 Vienna, supporting fellow students in system programming and software engineering fundamentals. Designed and hosted a Git workshop for the student community.

- Hosted a Git Essentials workshop — 'Something You Should Know Before Git Branch' — covering branching strategy, rebase, conflict resolution, and collaborative workflows (slides: https://docs.google.com/presentation/d/13InmNDRSfkeUnGWHNXWFiTr3QCAz4ecFL_wFz-NFdoI/edit?usp=sharing) <!-- src: 42-vienna-tutor-h1 @69e6 -->
- Provided peer review and guidance in C/C++ system programming, shell scripting, and software architecture concepts <!-- src: 42-vienna-tutor-h2 @d02a -->

# Education

## 42 Vienna — Computer Science — Software Architecture, Linux Kernel & DevOps
<!--meta
id = "42-vienna"
studyType = "Ongoing Professional Development"
start = "2023-09-01"
end = ""
url = "https://www.42vienna.com/about/"
score = ""
-->

- Software Architecture — SOLID principles, hexagonal architecture, ADR-driven design (libftpp)
- Linux Kernel Internals — built Linux from scratch: toolchain, kernel compilation, bootloader, init (ft_linux)
- DevOps & Container Orchestration — K3s, Kubernetes, Vagrant, GitOps/ArgoCD (Inception-of-Things)
- System Programming — HTTP server, shell interpreter in C/C++ (webserver, minishell)
- AI Framework Internals — neural net framework, hyperparameter tuner, ML toolkit from scratch (litetorch, litetune, sklite)

## National Chiao Tung University — Computer Science — Data Mining
<!--meta
id = "nctu"
studyType = "Master of Science"
start = "2014-09-01"
end = "2016-06-01"
url = "https://www.nycu.edu.tw/nycu/en/"
score = ""
-->

- Data Mining
- High-dimensional Clustering

## Tatung University — Computer Science — Computer Vision & Algorithms
<!--meta
id = "tatung"
studyType = "Bachelor"
start = "2010-09-01"
end = "2014-06-01"
url = "https://ao.ttu.edu.tw/"
score = ""
-->

- Computer Vision
- Algorithm

# Projects

## Personal Hetzner Infrastructure — Live GitOps Cluster
<!--meta
id = "lyeh-infra"
start = "2026-04-01"
end = ""
url = "https://github.com/LeaYeh"
roles = ["Author"]
-->

A personal production infrastructure running live on a Hetzner cloud server: a k3s Kubernetes cluster with ArgoCD-driven GitOps, deploying multiple self-hosted applications.

- Runs a k3s cluster on a Hetzner CX23 instance with ArgoCD continuously reconciling application state from Git <!-- src: lyeh-infra-h1 @e59c -->
- Operates the full deployment lifecycle (build, containerize, deploy, observe) for live self-hosted services <!-- src: lyeh-infra-h3 @6eb8 -->
- Configured Traefik ingress (hostname-based routing) and cert-manager for automatic Let's Encrypt TLS certificate provisioning and renewal <!-- src: lyeh-infra-h2 @fed6 -->
- Pinned deployments by immutable image SHA rather than mutable tags so Git remains an exact source of truth and ArgoCD reliably detects changes <!-- src: lyeh-infra-h4 @2b98 -->

## Inception-of-Things — K3s Kubernetes Cluster
<!--meta
id = "inception-of-things"
start = "2025-06-01"
end = "2025-10-01"
url = "https://github.com/42-CC-RNCP/Inception-of-Things"
roles = ["Developer"]
-->

Provisioned and configured a multi-node K3s (lightweight Kubernetes) cluster using Vagrant and VirtualBox, covering cluster networking, ingress, and GitOps-style deployment workflows.

- Deployed a multi-node K3s cluster with Vagrant-provisioned VMs, including nested virtualization setup <!-- src: inception-of-things-h1 @2eed -->
- Configured Kubernetes ingress, service routing, and workload deployment across cluster nodes <!-- src: inception-of-things-h2 @b8a4 -->
- Applied GitOps principles with ArgoCD for continuous deployment in the bonus track <!-- src: inception-of-things-h3 @2291 -->

## ft_transcendence — Full-Stack Platform with Observability Stack
<!--meta
id = "ft-transcendence"
start = "2025-10-01"
end = "2026-03-01"
url = "https://github.com/anastasiiap42/ft_transcendence/tree/main/devops"
roles = ["DevOps Engineer"]
-->

Contributed the DevOps module for a full-stack multiplayer web platform (42 Vienna capstone project). Responsible for designing and deploying the complete observability infrastructure covering metrics, logging, and alerting.

- Deployed Prometheus for metrics collection and configured alerting rules for service health and performance thresholds <!-- src: ft-transcendence-h1 @d4fc -->
- Built Grafana dashboards for real-time visibility into application and infrastructure metrics across the platform <!-- src: ft-transcendence-h2 @7adb -->
- Set up ELK stack (Elasticsearch, Logstash, Kibana) for centralized log aggregation and search across distributed services <!-- src: ft-transcendence-h3 @0e32 -->
- Containerized the full observability stack with Docker Compose, enabling reproducible deployment and local development parity <!-- src: ft-transcendence-h4 @ef5c -->

# Skills

## MLOps & Model Operations
<!--meta
id = "skill-mlops-model-ops"
level = "Advanced"
-->

- MLflow
- Model monitoring
- Model deployment
- Data drift tracking
- Data Quality Monitoring
- Streamlit

## GitOps, CI/CD & Delivery
<!--meta
id = "skill-gitops-delivery"
level = "Advanced"
-->

- ArgoCD / GitOps
- Kustomize
- GitHub Actions
- Jenkins
- CI/CD pipelines
- Docker
- Git / Git Flow

## Kubernetes & Platform
<!--meta
id = "skill-kubernetes-platform"
level = "Advanced"
-->

- Kubernetes (K3s)
- Traefik ingress
- cert-manager
- Sealed Secrets
- Vagrant / VM provisioning
- Self-hosted infrastructure

## Observability & Alerting
<!--meta
id = "skill-observability-alerting"
level = "Advanced"
-->

- Prometheus
- Grafana
- ELK stack (Elasticsearch, Logstash, Kibana)
- Splunk
- Alerting
- BI dashboards

## Systems Architecture
<!--meta
id = "skill-systems-architecture"
level = "Advanced"
-->

- Event-driven / async architecture
- Layered system design
- SOLID principles
- Hardware abstraction
- Interface-first design
- ADR-driven design

## Python, Bash & Linux
<!--meta
id = "skill-python-bash-linux"
level = "Master"
-->

- Python / OOP / Pythonic
- Pandas
- Automation tooling
- Shell scripting
- Linux internals

## Data Platform
<!--meta
id = "skill-data-platform"
level = "Master"
-->

- Apache Airflow
- NiFi
- Dataflow
- BigQuery
- ETL
- Data Warehouse
- Google Cloud Platform (GCP)
- Object storage (AWS S3, MinIO)
- SQL

# Awards

## IT Annual Award
<!--meta
id = "mediatek-it-award"
date = "2020-12-01"
awarder = "MediaTek"
-->

Recognized for impact on data infrastructure and cost reduction initiatives.

# Certificates

## ISTQB Certified Tester Foundation Level (CTFL) v4.0
<!--meta
id = "istqb-ctfl"
date = "2026-04-04"
issuer = "ISTQB / GASQ"
url = "https://app.skillsclub.com/credential/293353-28e36a6435ba059718f6ef53a2b8cf79f593a6d16221c0bd0d9483b06a51c5c3"
-->

## Microsoft Azure Databricks for Data Engineering
<!--meta
id = "azure-databricks"
date = "2024-04-01"
issuer = "Microsoft"
url = "https://www.coursera.org/account/accomplishments/verify/QCEEXZ8HWETC"
-->

# Publications

## Clustering using Radius-Weighted Means and Analytical Radius-Preserved Formula
<!--meta
id = "clustering-radius"
publisher = "NCTU"
releaseDate = "2016-06-01"
-->

# Languages

## Chinese
<!--meta
id = "chinese"
fluency = "Native Speaker"
-->

## Taiwanese
<!--meta
id = "taiwanese"
fluency = "Native Speaker"
-->

## English
<!--meta
id = "english"
fluency = "Professional Working Proficiency"
-->

## German
<!--meta
id = "german"
fluency = "Beginner"
-->
