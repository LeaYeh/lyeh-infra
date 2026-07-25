+++
name = "Lea (Mei Ling) Yeh"
label = "MLOps Engineer | AI Platform & Observability | ML Infrastructure"
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

MLOps engineer bridging the platform layer (model monitoring, data-drift, Prometheus/Grafana/MLflow, K3s/ArgoCD) and ML internals — built a neural-net framework, autograd, and hyperparameter tuner from scratch. Currently extending into LLM workloads: RAG/GraphRAG and LLM observability in progress.

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

- Architected a modular, layered software framework for SPM instrument control, separating hardware-vendor, orchestration, and application layers for long-term extensibility and reuse
- Defined cross-layer interface contracts and async command-routing patterns, isolating failure domains and enabling parallel hardware/software development
- Delivered automated measurement workflows (spatial sampling, real-time safety management) that let researchers focus on experimental outcomes rather than instrument operation

## MediaTek — Data Scientist
<!--meta
id = "mediatek-ds"
start = "2022-09-01"
end = "2023-09-01"
location = "Taipei, Taiwan"
url = "https://www.linkedin.com/company/17763"
-->

Devoted to data-related initiatives spanning cost control and chip development in the AI & Big Data department of a leading global semiconductor company.

- Implemented model-monitoring solutions using AWS and Streamlit, ensuring high availability and performance consistency for production ML models
- Developed ML models to enhance mobile temperature control mechanisms, achieving temperature errors below 1°C
- Collaborated with chip developers to reduce power consumption by 20%, resulting in a 14K Antutu score improvement in mobile performance

## MediaTek — Data Engineer
<!--meta
id = "mediatek-de"
start = "2019-07-01"
end = "2022-09-01"
location = "Taipei, Taiwan"
url = "https://www.linkedin.com/company/17763"
-->

Built data infrastructure and analytics platforms for one of the world's largest IC design companies.

- Built ML model-monitoring infrastructure using MLflow and Grafana dashboards to track model performance and data drift in production
- Implemented real-time data-quality monitoring and alerting, reducing data missing rates from 50% to <1% and lowering monthly labor costs by 7.5 man-days
- Established automated data pipelines for structured and unstructured data; designed PB-level ETL processes using Airflow, NiFi, Dataflow, and BigQuery on GCP
- Managed EDA License and Computing Farm costs via interactive BI Dashboard (Splunk + Grafana), aiding procurement decisions and reducing costs by 25%

## MediaTek — Software Engineer
<!--meta
id = "mediatek-se"
start = "2016-09-01"
end = "2019-06-01"
location = "Taipei, Taiwan"
url = "https://www.linkedin.com/company/17763"
summary = ""
-->

- Developed an automated ICD DMS using Python and Jenkins to enforce documentation standards
- Developed debugging and analysis tools for Modem Logs

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

- Implemented forward/backpropagation, autograd, and layer abstractions from scratch in litetorch
- Built a hyperparameter search and experiment tracking system in litetune, mirroring Ray Tune's trial management model
- Designed preprocessing pipelines and utility functions in sklite for educational clarity and extensibility

## ft_transcendence — Full-Stack Platform with Observability Stack
<!--meta
id = "ft-transcendence"
start = "2025-10-01"
end = "2026-03-01"
url = "https://github.com/anastasiiap42/ft_transcendence/tree/main/devops"
roles = ["DevOps Engineer"]
-->

Contributed the DevOps module for a full-stack multiplayer web platform (42 Vienna capstone project). Responsible for designing and deploying the complete observability infrastructure covering metrics, logging, and alerting.

- Deployed Prometheus for metrics collection and configured alerting rules for service health and performance thresholds
- Built Grafana dashboards for real-time visibility into application and infrastructure metrics across the platform
- Set up ELK stack (Elasticsearch, Logstash, Kibana) for centralized log aggregation and search across distributed services
- Containerized the full observability stack with Docker Compose, enabling reproducible deployment and local development parity

## Inception-of-Things — K3s Kubernetes Cluster
<!--meta
id = "inception-of-things"
start = "2025-06-01"
end = "2025-10-01"
url = "https://github.com/42-CC-RNCP/Inception-of-Things"
roles = ["Developer"]
-->

Provisioned and configured a multi-node K3s (lightweight Kubernetes) cluster using Vagrant and VirtualBox, covering cluster networking, ingress, and GitOps-style deployment workflows — the deployment substrate for running model/inference workloads.

- Deployed a multi-node K3s cluster with Vagrant-provisioned VMs, including nested virtualization setup
- Configured Kubernetes ingress, service routing, and workload deployment across cluster nodes
- Applied GitOps principles with ArgoCD for continuous deployment in the bonus track

## GraphRAG Proof-of-Concept (POC3) — in-progress
<!--meta
id = "graphrag-poc3"
start = "2026-01-01"
end = ""
url = "https://github.com/LeaYeh"
roles = ["Author"]
-->

In-progress proof-of-concept exploring GraphRAG and retrieval-augmented LLM workflows on observable infrastructure. Work is ongoing; RAG/GraphRAG/LangGraph components and LLM observability are not yet completed.

- Prototyping a GraphRAG retrieval pipeline and LLM evaluation approach (in-progress)
- Designing LLM observability and data-governance/access-control considerations into the system (in-progress)

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
- Helm
- CI/CD
- Git Flow

## Data Engineering
<!--meta
id = "skill-data-engineering"
level = "Master"
-->

- Big data pipeline
- ETL
- Data Warehouse
- Data Quality Monitoring
- Google Cloud Platform (GCP)
- Apache Airflow
- NiFi
- BigQuery
- Dataflow
- Databricks

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
- GraphRAG (in-progress)
- LangGraph (in-progress)
- LLM observability (in-progress)

## Systems Architecture
<!--meta
id = "skill-systems-architecture"
level = "Advanced"
-->

- Event-driven architecture
- Layered system design
- SOLID principles
- Hardware abstraction
- Interface design
- Design Patterns

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
