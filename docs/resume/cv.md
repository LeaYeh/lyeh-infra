+++
name = "Lea (Mei Ling) Yeh"
label = "Senior Software Engineer | Systems Architecture | DevOps & MLOps | Applied AI"
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

Senior Software Engineer and de facto systems architect at c-sense GmbH — the sole engineer responsible for the full software stack: layered SPM instrument-control framework (hardware abstraction, async command routing, interface contracts) and currently architecting an agentic RAG system (LangChain/LangGraph, Chroma, LLM cloud APIs) to give the CEO cross-domain visibility into internal technical documentation, sales/CRM data, competitor products, and prospective customers.

Background spans 8+ years in Data Engineering, Data Science, and Software Engineering — including PB-scale ETL pipelines and ML model monitoring at MediaTek. Deepening systems foundations at 42 Vienna: Linux kernel internals, DevOps (K3s/ArgoCD/GitOps), and architecture design patterns.

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

- Driving the company's AI integration initiative as sole technical decision-maker — evaluating LLM tooling and defining the end-to-end agentic architecture strategy {#csense-h1}
- Currently architecting an agentic RAG system (LangChain/LangGraph, Chroma, LLM cloud APIs) to give the CEO cross-domain visibility into internal technical documentation, sales/CRM data, competitor product analysis, and prospective customer profiling {#csense-h2}
- Architected a modular, layered software framework for SPM instrument control — deliberately separating hardware vendor, orchestration, and application layers for long-term extensibility and reuse across future instrument variants {#csense-h3}
- Defined cross-layer interface contracts and async command routing patterns to enable parallel development by hardware and software teams, reducing integration risk during concurrent R&D cycles {#csense-h4}
- Led the design of a hardware abstraction strategy over a LabVIEW-based proprietary API, keeping the software stack agnostic to vendor-specific instrument changes {#csense-h5}
- Delivered automated measurement capabilities (spatial sampling, real-time safety management) that allow researchers to focus on experimental outcomes rather than instrument operation {#csense-h6}

## MediaTek — Data Scientist
<!--meta
id = "mediatek-ds"
start = "2022-09-01"
end = "2023-09-01"
location = "Taipei, Taiwan"
url = "https://www.linkedin.com/company/17763"
-->

Devoted to data-related initiatives spanning cost control and chip development in the AI & Big Data department of a leading global semiconductor company.

- Implemented model monitoring solutions using AWS and Streamlit, ensuring high availability and performance consistency for production ML models {#mediatek-ds-h1}
- Implemented ML models to enhance mobile temperature control mechanisms, achieving temperature errors below 1°C {#mediatek-ds-h2}
- Collaborated with chip developers to reduce power consumption by 20%, resulting in a 14K Antutu score improvement in mobile performance {#mediatek-ds-h3}

## MediaTek — Data Engineer
<!--meta
id = "mediatek-de"
start = "2019-07-01"
end = "2022-09-01"
location = "Taipei, Taiwan"
url = "https://www.linkedin.com/company/17763"
-->

Built data infrastructure and analytics platforms for one of the world's largest IC design companies.

- Established automated data pipelines for structured and unstructured data; designed PB-level ETL processes using Airflow, NiFi, Dataflow, and BigQuery on GCP {#mediatek-de-h1}
- Introduced dimensional-modeling and data-warehouse architecture, improving data table reuse rates during the company's early digital transformation {#mediatek-de-h2}
- Implemented real-time data quality monitoring and alerting, reducing data missing rates from 50% to <1% and lowering monthly labor costs by 7.5 man-days {#mediatek-de-h3}
- Built model monitoring infrastructure using MLflow and Grafana dashboards to track ML model performance and data drift in production {#mediatek-de-h4}
- Managed EDA License and Computing Farm costs via interactive BI Dashboard (Splunk + Grafana), aiding EO procurement decisions and reducing costs by 25% {#mediatek-de-h5}

## MediaTek — Software Engineer
<!--meta
id = "mediatek-se"
start = "2016-09-01"
end = "2019-06-01"
location = "Taipei, Taiwan"
url = "https://www.linkedin.com/company/17763"
summary = ""
-->

- Developed debugging and analysis tools for Modem Logs {#mediatek-se-h1}
- Developed an automated ICD DMS using Python and Jenkins to enforce documentation standards {#mediatek-se-h2}
- Created a World Wide Field Trial Upload Tool using Vue.js with Electron {#mediatek-se-h3}
- Developed a StackOverflow-like QA platform using AngularJS {#mediatek-se-h4}

# Volunteer

## 42 Vienna — Peer Tutor & Workshop Host
<!--meta
id = "42-vienna-tutor"
start = "2024-07-01"
end = "2024-10-01"
url = "https://www.42vienna.com/"
-->

Volunteered as a peer tutor at 42 Vienna, supporting fellow students in system programming and software engineering fundamentals. Designed and hosted a Git workshop for the student community.

- Hosted a Git Essentials workshop — 'Something You Should Know Before Git Branch' — covering branching strategy, rebase, conflict resolution, and collaborative workflows {#42-vienna-tutor-h1}
- Provided peer tutoring in C/C++ system programming, shell scripting, and software architecture concepts {#42-vienna-tutor-h2}

## Taiwan in Data Science (TWiDS) — Event Ambassador & Volunteer Organizer
<!--meta
id = "twids"
start = "2023-10-01"
end = "2024-05-01"
url = "https://www.facebook.com/TWiDataScience/"
-->

Served as one of the organizers at Taiwan in Data Science (TWiDS), a volunteer organization dedicated to promoting data-related fields in Taiwan.

- Served as event ambassador: conducted interviews with data domain experts for the TWiDS podcast series {#twids-h1}
- Co-organized the annual TWiDS conference, coordinating speakers, logistics, and community outreach {#twids-h2}

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

## lyeh-infra — Self-Hosted Kubernetes Infrastructure (GitOps)
<!--meta
id = "lyeh-infra"
start = "2026-04-01"
end = ""
url = "https://github.com/LeaYeh/lyeh-infra"
roles = ["Author"]
-->

Personal cloud infrastructure on a single Hetzner CX23 VM running k3s, deployed via ArgoCD GitOps. Everything is declared in Git — adding a new service means creating a directory and pushing; ArgoCD handles the rest. This portfolio site is hosted on it.

- Designed a GitOps deployment model using an ArgoCD ApplicationSet with a Git directory generator — every subdirectory under apps/ is auto-discovered and deployed to its own namespace, with prune and self-heal enabled {#lyeh-infra-h1}
- Configured Traefik ingress (hostname-based routing) and cert-manager for automatic Let's Encrypt TLS certificate provisioning and renewal {#lyeh-infra-h2}
- Built a fully automated CI/CD pipeline (GitHub Actions): Hugo build → Docker image to GHCR pinned by content SHA → image tag written back into deployment.yaml → ArgoCD rolling update {#lyeh-infra-h3}
- Pinned deployments by immutable image SHA rather than mutable tags so Git remains an exact source of truth and ArgoCD reliably detects changes {#lyeh-infra-h4}
- Scripted the full zero-to-running bootstrap (provision → k3s → cert-manager → ArgoCD) so a fresh VM becomes self-managing in four steps {#lyeh-infra-h5}

## ft_transcendence — Full-Stack Platform with Observability Stack
<!--meta
id = "ft-transcendence"
start = "2025-10-01"
end = "2026-03-01"
url = "https://github.com/anastasiiap42/ft_transcendence/tree/main/devops"
roles = ["DevOps Engineer"]
-->

Contributed the DevOps module for a full-stack multiplayer web platform (42 Vienna capstone project). Responsible for designing and deploying the complete observability infrastructure covering metrics, logging, and alerting.

- Deployed Prometheus for metrics collection and configured alerting rules for service health and performance thresholds {#ft-transcendence-h1}
- Built Grafana dashboards for real-time visibility into application and infrastructure metrics across the platform {#ft-transcendence-h2}
- Set up ELK stack (Elasticsearch, Logstash, Kibana) for centralized log aggregation and search across distributed services {#ft-transcendence-h3}
- Containerized the full observability stack with Docker Compose, enabling reproducible deployment and local development parity {#ft-transcendence-h4}

## ft_linux — Linux From Scratch
<!--meta
id = "ft-linux"
start = "2025-09-01"
end = "2026-01-01"
url = "https://github.com/42-CC-RNCP/ft_linux"
roles = ["Author"]
-->

Built a fully bootable Linux system from scratch, covering every layer from cross-compilation toolchain to kernel configuration, filesystem hierarchy, init system, and bootloader. Follows LFS/BLFS/ALFS methodology with a custom automation layer.

- Compiled a custom Linux kernel (4.x) with hand-selected driver and filesystem configuration {#ft-linux-h1}
- Built a two-phase cross-compilation toolchain (temporary + final) to produce a host-independent, self-contained Linux system {#ft-linux-h2}
- Automated the full build pipeline (14 stages) via an ALFS-style bootstrap script with environment isolation and error recovery {#ft-linux-h3}
- Designed partition layout, configured GRUB bootloader, SysV init, and udev for dynamic device management {#ft-linux-h4}

## Inception-of-Things — K3s Kubernetes Cluster
<!--meta
id = "inception-of-things"
start = "2025-06-01"
end = "2025-10-01"
url = "https://github.com/42-CC-RNCP/Inception-of-Things"
roles = ["Developer"]
-->

Provisioned and configured a multi-node K3s (lightweight Kubernetes) cluster using Vagrant and VirtualBox, covering cluster networking, ingress, and GitOps-style deployment workflows.

- Deployed a multi-node K3s cluster with Vagrant-provisioned VMs, including nested virtualization setup {#inception-of-things-h1}
- Configured Kubernetes ingress, service routing, and workload deployment across cluster nodes {#inception-of-things-h2}
- Applied GitOps principles with ArgoCD for continuous deployment in the bonus track {#inception-of-things-h3}

## libftpp — C++ Architecture Library
<!--meta
id = "libftpp"
start = "2025-10-01"
end = "2026-01-01"
url = "https://github.com/42-CC-RNCP/libftpp"
roles = ["Author"]
-->

A modern C++20 library built through structured exercises practicing SOLID principles, hexagonal architecture, and design patterns. Includes Architectural Decision Records (ADRs) documenting trade-off reasoning.

- Implemented core data structures and utilities applying SOLID principles and hexagonal (ports & adapters) architecture {#libftpp-h1}
- Documented architectural decisions via ADRs, treating design trade-offs as first-class engineering artifacts {#libftpp-h2}
- Maintained CI pipeline with CMake, clang-format, and automated test suite {#libftpp-h3}

## litetorch + litetune + sklite — AI Framework Toolkit
<!--meta
id = "litetorch-suite"
start = "2025-03-01"
end = "2025-06-01"
url = "https://github.com/42-CC-RNCP"
roles = ["Author"]
-->

A trio of ML infrastructure projects — litetorch (neural network framework built from scratch, inspired by PyTorch), litetune (hyperparameter tuner inspired by Ray Tune), and sklite (ML preprocessing toolkit inspired by scikit-learn) — demonstrating ML internals depth beyond API usage.

- Implemented forward/backpropagation, autograd, and layer abstractions from scratch in litetorch {#litetorch-suite-h1}
- Built a hyperparameter search and experiment tracking system in litetune, mirroring Ray Tune's trial management model {#litetorch-suite-h2}
- Designed preprocessing pipelines and utility functions in sklite for educational clarity and extensibility {#litetorch-suite-h3}

## webserver — HTTP/1.1 Server in C++
<!--meta
id = "webserver"
start = "2024-06-01"
end = "2024-09-01"
url = "https://github.com/LeaYeh/webserver"
roles = ["Developer"]
-->

Implemented a standards-compliant HTTP/1.1 web server in C++ from scratch, handling concurrent connections, request parsing, and static/dynamic content serving.

- Built non-blocking I/O event loop handling concurrent HTTP connections using poll/select {#webserver-h1}
- Implemented HTTP/1.1 request parsing, routing, and response generation {#webserver-h2}
- Supported CGI execution, static file serving, and configurable virtual hosts {#webserver-h3}

## minishell — Bash-compatible Shell
<!--meta
id = "minishell"
start = "2023-12-01"
end = "2024-03-01"
url = "https://github.com/LeaYeh/minishell"
roles = ["Developer"]
-->

Reimplemented core GNU Bash shell features including command parsing, process management, and built-in execution.

- Developed a syntax analyzer using the shift-reduce algorithm for Bash-like grammar interpretation {#minishell-h1}
- Optimized subprocess management and pipeline execution across multi-stage pipelines {#minishell-h2}
- Employed Docker to ensure consistent development environments across the team {#minishell-h3}

## CDNJS — Content Delivery Network for JavaScript
<!--meta
id = "cdnjs"
start = "2015-09-01"
end = "2016-09-01"
url = "https://cdnjs.com/"
roles = ["Contributor"]
-->

Open-source CDN for JavaScript libraries used by over 3.5 million websites, serving 30+ billion requests per month.

- Contributed to a platform serving over 30 billion requests per month across 3.5 million websites {#cdnjs-h1}
- Assisted with library maintenance and automation tooling for the open-source CDN {#cdnjs-h2}

# Skills

## Systems Architecture
<!--meta
id = "skill-systems-architecture"
level = "Advanced"
-->

- Hexagonal Architecture (Ports & Adapters)
- Microservices & layered system design
- Event-driven / async architecture
- Interface-first / contract-driven design
- Hardware Abstraction Layer (HAL)
- SDD (Specification-Driven Development)
- Cross-functional stakeholder communication

## Platform & Container Orchestration
<!--meta
id = "skill-platform-orchestration"
level = "Advanced"
-->

- DevOps & MLOps
- Kubernetes (K8s / K3s)
- Docker
- Kustomize
- Vagrant / VM provisioning
- ArgoCD
- Traefik ingress
- cert-manager
- Self-hosted infrastructure

## CI/CD & GitOps
<!--meta
id = "skill-cicd-gitops"
level = "Advanced"
-->

- ArgoCD / GitOps
- CI/CD pipelines

## Observability & MLOps
<!--meta
id = "skill-observability-mlops"
level = "Advanced"
-->

- Prometheus
- Grafana
- ELK stack (Elasticsearch, Logstash, Kibana)
- Splunk
- MLflow
- Model monitoring
- Model deployment
- Apache Airflow

## Data Engineering
<!--meta
id = "skill-data-engineering"
level = "Master"
-->

- Databricks
- Big data pipeline
- Data Warehouse
- ETL
- Data Quality Monitoring
- Google Cloud Platform (GCP)
- Apache Airflow
- Data Governance
- NiFi
- BigQuery
- Dataflow

## Data Science
<!--meta
id = "skill-data-science"
level = "Advanced"
-->

- Supervised learning (Random Forest, XGBoost)
- Time series analysis & forecasting
- Neural network design & deep learning
- Explainable AI (SHAP)
- Dimensionality reduction & feature engineering
- Root Cause Analysis (RCA)
- Model evaluation & validation
- ML internals (autograd, backpropagation from scratch)

## Python
<!--meta
id = "skill-python"
level = "Master"
-->

- OOP
- PyTorch
- Streamlit
- Pandas
- Pythonic

## SQL
<!--meta
id = "skill-sql"
level = "Advanced"
-->

- MySQL
- BigQuery

## C/C++
<!--meta
id = "skill-cpp"
level = "Intermediate"
-->

- Performance Optimization
- Multiprocessing
- Parallel Computing
- Linux kernel

## Software Quality & Testing
<!--meta
id = "skill-quality-testing"
level = "Foundation"
-->

- ISTQB CTFL v4.0
- Test design techniques
- Test planning

## Data Analysis
<!--meta
id = "skill-data-analysis"
level = "Advanced"
-->

- BI Dashboard
- Splunk
- Plotly
- Data Visualization

## LLM & AI Application Development
<!--meta
id = "skill-llm-ai"
level = "Intermediate"
-->

- LLM Application Development
- Agentic RAG (in-progress)
- LangChain / LangGraph (in-progress)
- Chroma (vector DB)

## Systems & Low-Level Programming
<!--meta
id = "skill-systems-lowlevel"
level = "Intermediate"
-->

- Linux Kernel Internals
- Socket Programming
- High-performance Web Server
- Non-blocking I/O event loops

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
publisher = "National Chiao Tung University"
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
