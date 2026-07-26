+++
name = "Lea (Mei Ling) Yeh"
label = "Senior Software Engineer | AI/LLM Applied"
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

Senior Software Engineer in applied AI: sole technical decision-maker for a company's AI integration, currently architecting an agentic RAG system over internal documentation and business data. Came by the engineering path — PB-scale pipelines, then the analysis and model monitoring on them — and writes the internals: neural-net framework, autograd and tuner from scratch.

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

- Driving the company's AI integration as sole technical decision-maker — evaluating LLM tooling and defining the end-to-end agentic architecture strategy <!-- src: csense-h1 @bc64 -->
- Currently architecting an agentic RAG system (LangChain/LangGraph, Chroma, LLM cloud APIs) giving leadership cross-domain visibility over internal documentation and business data <!-- src: csense-h2 @7679 -->
- Architected a modular, layered software framework for SPM instrument control, separating hardware-vendor, orchestration, and application layers for long-term extensibility and reuse <!-- src: csense-h3 @d85d -->
- Defined cross-layer interface contracts and async command-routing patterns, isolating failure domains and enabling parallel hardware/software development <!-- src: csense-h4 @d8ac -->
- Delivered automated measurement workflows (spatial sampling, real-time safety management) that let researchers focus on experimental outcomes rather than instrument operation <!-- src: csense-h6 @a9d2 -->
- Built the GitOps delivery platform that ships the company's internal ML/AI services — ArgoCD-driven continuous delivery across environments, with architecture recorded as ADRs <!-- src: csense-h8 @ce2f -->

## MediaTek — Data Scientist
<!--meta
id = "mediatek-ds"
start = "2022-09-01"
end = "2023-09-01"
location = "Taipei, Taiwan"
url = "https://www.linkedin.com/company/17763"
-->

Devoted to data-related initiatives spanning cost control and chip development in the AI & Big Data department of a leading global semiconductor company.

- Implemented model-monitoring solutions using MLflow and Streamlit, ensuring high availability and performance consistency for production ML models <!-- src: mediatek-ds-h1 @72ec -->
- Developed ML models to enhance mobile temperature control mechanisms, achieving temperature errors below 1°C <!-- src: mediatek-ds-h2 @11c6 -->
- Collaborated with chip developers to reduce power consumption by 20%, resulting in a 14K Antutu score improvement in mobile performance <!-- src: mediatek-ds-h3 @4319 -->

## MediaTek — Data Engineer
<!--meta
id = "mediatek-de"
start = "2019-07-01"
end = "2022-09-01"
location = "Taipei, Taiwan"
url = "https://www.linkedin.com/company/17763"
-->

Built data infrastructure and analytics platforms for one of the world's largest IC design companies.

- Built ML model-monitoring infrastructure using MLflow and Grafana dashboards to track model performance and data drift in production <!-- src: mediatek-de-h4 @777d -->
- Implemented real-time data-quality monitoring and alerting, reducing data missing rates from 50% to <1% and lowering monthly labor costs by 7.5 man-days <!-- src: mediatek-de-h3 @ef9e -->
- Established automated data pipelines for structured and unstructured data; designed PB-level ETL processes using Airflow, NiFi, Dataflow, and BigQuery on GCP <!-- src: mediatek-de-h1 @2a03 -->
- Managed EDA License and Computing Farm costs via interactive BI Dashboard (Splunk + Grafana), aiding procurement decisions and reducing costs by 25% <!-- src: mediatek-de-h5 @345a -->

## MediaTek — Software Engineer
<!--meta
id = "mediatek-se"
start = "2016-09-01"
end = "2019-06-01"
location = "Taipei, Taiwan"
url = "https://www.linkedin.com/company/17763"
summary = ""
-->

- Developed an automated ICD DMS using Python and Jenkins to enforce documentation standards <!-- src: mediatek-se-h2 @0f13 -->
- Developed debugging and analysis tools for Modem Logs <!-- src: mediatek-se-h1 @c6c7 -->

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

## litetorch + litetune + sklite — AI Framework Toolkit
<!--meta
id = "litetorch-suite"
start = "2025-03-01"
end = "2025-06-01"
url = "https://github.com/42-CC-RNCP"
roles = ["Author"]
-->

A trio of educational ML infrastructure projects: litetorch (neural network framework built from scratch inspired by PyTorch), litetune (hyperparameter tuner inspired by Ray Tune), and sklite (ML preprocessing toolkit inspired by scikit-learn). Demonstrates understanding of ML internals beyond API usage.

- Implemented forward/backpropagation, autograd, and layer abstractions from scratch in litetorch <!-- src: litetorch-suite-h1 @70e1 -->
- Built a hyperparameter search and experiment tracking system in litetune, mirroring Ray Tune's trial management model <!-- src: litetorch-suite-h2 @379e -->
- Designed preprocessing pipelines and utility functions in sklite for educational clarity and extensibility <!-- src: litetorch-suite-h3 @f737 -->

## lyeh-infra — Self-Hosted Kubernetes Infrastructure (GitOps)
<!--meta
id = "lyeh-infra"
start = "2026-04-01"
end = ""
url = "https://github.com/LeaYeh/lyeh-infra"
roles = ["Author"]
-->

Personal cloud infrastructure on a single Hetzner CX23 VM running k3s, deployed via ArgoCD GitOps. Everything is declared in Git — adding a new service means creating a directory and pushing; ArgoCD handles the rest. This portfolio site is hosted on it.

- Designed a GitOps deployment model using an ArgoCD ApplicationSet with a Git directory generator — every subdirectory under apps/ is auto-discovered and deployed to its own namespace, with prune and self-heal enabled <!-- src: lyeh-infra-h1 @e59c -->
- Configured Traefik ingress (hostname-based routing) and cert-manager for automatic Let's Encrypt TLS certificate provisioning and renewal <!-- src: lyeh-infra-h2 @fed6 -->
- Built a fully automated CI/CD pipeline (GitHub Actions): Hugo build → Docker image to GHCR pinned by content SHA → image tag written back into deployment.yaml → ArgoCD rolling update <!-- src: lyeh-infra-h3 @6eb8 -->
- Pinned deployments by immutable image SHA rather than mutable tags so Git remains an exact source of truth and ArgoCD reliably detects changes <!-- src: lyeh-infra-h4 @2b98 -->
- Scripted the full zero-to-running bootstrap (provision → k3s → cert-manager → ArgoCD) so a fresh VM becomes self-managing in four steps <!-- src: lyeh-infra-h5 @bad4 -->

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
- Prometheus
- Grafana
- ELK stack (Elasticsearch, Logstash, Kibana)
- Splunk
- CI/CD
- Docker
- GitHub Actions

## Machine Learning & ML Internals
<!--meta
id = "skill-ml-internals"
level = "Advanced"
-->

- PyTorch
- Deep Learning
- Model Evaluation
- Autograd / backpropagation (from scratch)
- Hyperparameter tuning
- Explainable AI
- Streamlit

## Platform & Orchestration
<!--meta
id = "skill-platform-ops"
level = "Advanced"
-->

- Kubernetes (K3s)
- Docker
- GitOps / ArgoCD
- Vagrant / VM provisioning
- Kustomize
- CI/CD
- Git Flow

## Programming
<!--meta
id = "skill-programming"
level = "Master"
-->

- Python
- OOP
- Pandas
- SQL
- C/C++

## LLM / Applied AI (in-progress)
<!--meta
id = "skill-llm-ai-progress"
level = "Foundation"
-->

- LLM application development (in-progress)
- RAG (in-progress)
- Agentic RAG (in-progress)
- LangGraph (in-progress)
- LLM observability (in-progress)

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
