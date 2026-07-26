+++
name = "Lea (Mei Ling) Yeh"
label = "Data Engineer | Data Platform | ETL at Scale"
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

Data Engineer with PB-scale ETL and data-quality depth: built MediaTek's first data-warehouse layer with Airflow/NiFi/Dataflow/BigQuery on GCP, cutting missing-data rates from 50% to under 1%. Azure Databricks certified.

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

- Architected a modular, layered software framework for SPM instrument control, applying interface contracts and SOLID principles for long-term extensibility <!-- src: csense-h3 @d85d -->
- Built automated measurement workflows that turn high-volume sensor measurement protocols into reliable, reproducible data-acquisition processes <!-- src: csense-h6 @a9d2 -->
- Built the GitOps delivery platform carrying the company's internal data pipeline to its environments, with ArgoCD-driven continuous delivery and ADR-recorded architecture <!-- src: csense-h8 @ce2f -->

## MediaTek — Data Scientist
<!--meta
id = "mediatek-ds"
start = "2022-09-01"
end = "2023-09-01"
location = "Taipei, Taiwan"
url = "https://www.linkedin.com/company/17763"
-->

Devoted to data-related initiatives spanning cost control and chip development in the AI & Big Data department of a leading global semiconductor company.

- Deployed model-monitoring infrastructure (MLflow + Streamlit) to track production model performance and consistency, extending data-quality practices from pipelines to ML systems <!-- src: mediatek-ds-h1 @72ec -->

## MediaTek — Data Engineer
<!--meta
id = "mediatek-de"
start = "2019-07-01"
end = "2022-09-01"
location = "Taipei, Taiwan"
url = "https://www.linkedin.com/company/17763"
-->

Built data infrastructure and analytics platforms for one of the world's largest IC design companies.

- Designed PB-scale ETL pipelines on GCP (Airflow, NiFi, Dataflow, BigQuery) for structured and unstructured data, processing distributed datasets across the company's data platform <!-- src: mediatek-de-h1 @2a03 -->
- Architected the company's first data-warehouse layer, introducing dimensional-modeling theory that improved data-table reuse during the company's early digital transformation <!-- src: mediatek-de-h2 @c2f3 -->
- Built real-time data-quality monitoring and alerting that cut missing-data rates from 50% to under 1% and saved 7.5 man-days per month <!-- src: mediatek-de-h3 @ef9e -->
- Tracked ML model performance and data drift in production via MLflow and Grafana dashboards, bridging data engineering and DataOps/MLOps <!-- src: mediatek-de-h4 @777d -->
- Managed EDA license and computing-farm costs via interactive BI dashboards (Splunk + Grafana), informing procurement decisions and reducing costs by 25% <!-- src: mediatek-de-h5 @345a -->

## MediaTek — Software Engineer
<!--meta
id = "mediatek-se"
start = "2016-09-01"
end = "2019-06-01"
location = "Taipei, Taiwan"
url = "https://www.linkedin.com/company/17763"
summary = ""
-->

- Developed an automated ICD documentation-management system using Python and Jenkins to enforce data-documentation standards <!-- src: mediatek-se-h2 @0f13 -->
- Built debugging and analysis tooling for large-volume Modem Logs <!-- src: mediatek-se-h1 @c6c7 -->

# Volunteer

## Taiwan in Data Science (TWiDS) — Volunteer Organizer
<!--meta
id = "twids"
start = "2023-10-01"
end = "2024-05-01"
url = "https://www.facebook.com/TWiDataScience/"
-->

Served as one of the organizers at Taiwan in Data Science (TWiDS), a volunteer organization dedicated to promoting data-related fields in Taiwan.

- Promoted awareness and understanding of data science across Taiwan <!-- src: twids-h3 @8475 -->
- Led preparations for workshops, podcasts, and conferences in 2024 <!-- src: twids-h4 @6678 -->

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

## Inception-of-Things — K3s Kubernetes Cluster
<!--meta
id = "inception-of-things"
start = "2025-06-01"
end = "2025-10-01"
url = "https://github.com/42-CC-RNCP/Inception-of-Things"
roles = ["Developer"]
-->

Provisioned and configured a multi-node K3s (lightweight Kubernetes) cluster using Vagrant and VirtualBox, covering cluster networking, ingress, and GitOps-style deployment workflows — foundational infrastructure for running containerized data pipelines and CI/CD.

- Deployed a multi-node K3s cluster with Vagrant-provisioned VMs, including nested virtualization setup <!-- src: inception-of-things-h1 @2eed -->
- Configured Kubernetes ingress, service routing, and workload deployment across cluster nodes <!-- src: inception-of-things-h2 @b8a4 -->
- Applied GitOps principles with ArgoCD for continuous deployment in the bonus track <!-- src: inception-of-things-h3 @2291 -->

# Skills

## Data Engineering & ETL
<!--meta
id = "skill-data-engineering-etl"
level = "Master"
-->

- Apache Airflow
- NiFi
- Dataflow
- BigQuery
- ETL / ELT
- Data Warehouse
- Dimensional Modeling
- Big data pipelines
- Batch & streaming ingestion

## SQL & Python
<!--meta
id = "skill-sql-python"
level = "Master"
-->

- SQL
- BigQuery SQL
- MySQL
- Python
- Pandas
- Pythonic / OOP

## Data Quality & Monitoring
<!--meta
id = "skill-data-quality-monitoring"
level = "Advanced"
-->

- Data-quality frameworks
- Real-time monitoring & alerting
- Data drift detection
- MLflow
- Grafana
- Splunk
- BI dashboards

## Cloud & Platforms
<!--meta
id = "skill-cloud-platforms"
level = "Advanced"
-->

- Google Cloud Platform (GCP)
- Object storage (AWS S3, MinIO)
- Beam / Dataflow (distributed data)
- Azure Databricks (certified)
- Delta Lake (learning)

## CI/CD & DevOps
<!--meta
id = "skill-cicd-devops"
level = "Advanced"
-->

- Git / Git Flow
- GitHub Actions
- Jenkins
- Docker
- CI/CD pipelines
- Kubernetes (K3s)
- GitOps via ArgoCD

## Software Quality & Testing
<!--meta
id = "skill-quality-testing"
level = "Foundation"
-->

- ISTQB CTFL v4.0
- Test design techniques
- Defect management
- SDLC quality assurance

# Awards

## IT Annual Award
<!--meta
id = "mediatek-it-award"
date = "2020-12-01"
awarder = "MediaTek"
-->

Recognized for impact on data infrastructure and cost reduction initiatives.

# Certificates

## Microsoft Azure Databricks for Data Engineering
<!--meta
id = "azure-databricks"
date = "2024-04-01"
issuer = "Microsoft"
url = "https://www.coursera.org/account/accomplishments/verify/QCEEXZ8HWETC"
-->

## ISTQB Certified Tester Foundation Level (CTFL) v4.0
<!--meta
id = "istqb-ctfl"
date = "2026-04-04"
issuer = "ISTQB / GASQ"
url = "https://app.skillsclub.com/credential/293353-28e36a6435ba059718f6ef53a2b8cf79f593a6d16221c0bd0d9483b06a51c5c3"
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
