+++
name = "Lea (Mei Ling) Yeh"
label = "Senior Software Engineer | Systems Architecture"
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

Senior Software Engineer with solution architecture responsibilities at c-sense GmbH — the sole engineer responsible for the full software stack: layered SPM instrument-control framework (hardware abstraction, async command routing, interface contracts). Background spans 9+ years in Software Engineering. Continuously advancing expertise in Linux kernel internals and DevOps at 42 Vienna.

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

- Architected a modular, layered SPM instrument-control framework, deliberately separating hardware-vendor, orchestration, and application layers for long-term extensibility and reuse across future instrument variants <!-- src: csense-h3 @d85d -->
- Defined cross-layer interface contracts and async command-routing patterns so hardware and software teams could develop in parallel, reducing integration risk during concurrent R&D cycles <!-- src: csense-h4 @d8ac -->
- Designed a hardware-abstraction layer over a proprietary LabVIEW-based API, keeping the software stack agnostic to vendor-specific instrument changes <!-- src: csense-h5 @bcb5 -->
- Delivered automated measurement capabilities (spatial sampling, real-time safety management) demanding careful concurrency and failure handling, letting researchers focus on experimental outcomes rather than instrument operation <!-- src: csense-h6 @a9d2 -->
- Built the internal delivery platform for the company's service pipeline — ArgoCD-driven continuous delivery across environments, with every architectural decision recorded as an ADR <!-- src: csense-h8 @ce2f -->
- Translated physics measurement protocols from hardware engineers and research scientists into reliable, automated software workflows <!-- src: csense-h7 @8516 -->

## MediaTek — Data Scientist
<!--meta
id = "mediatek-ds"
start = "2022-09-01"
end = "2023-09-01"
location = "Taipei, Taiwan"
url = "https://www.linkedin.com/company/17763"
-->

Devoted to data-related initiatives spanning cost control and chip development in the AI & Big Data department of a leading global semiconductor company.

- Implemented ML models driving mobile temperature-control mechanisms, achieving temperature errors below 1°C <!-- src: mediatek-ds-h2 @11c6 -->
- Worked with chip developers to cut power consumption by 20%, yielding a 14K Antutu score improvement in mobile performance <!-- src: mediatek-ds-h3 @4319 -->

## MediaTek — Data Engineer
<!--meta
id = "mediatek-de"
start = "2019-07-01"
end = "2022-09-01"
location = "Taipei, Taiwan"
url = "https://www.linkedin.com/company/17763"
-->

Built data infrastructure and analytics platforms for one of the world's largest IC design companies.

- Designed and built PB-level ETL processes on GCP (Airflow, NiFi, Dataflow, BigQuery), automating ingestion of structured and unstructured data <!-- src: mediatek-de-h1 @2a03 -->
- Introduced dimensional modeling and a data-warehouse architecture, raising table reuse during the company's early digital transformation <!-- src: mediatek-de-h2 @c2f3 -->

## MediaTek — Software Engineer
<!--meta
id = "mediatek-se"
start = "2016-09-01"
end = "2019-06-01"
location = "Taipei, Taiwan"
url = "https://www.linkedin.com/company/17763"
summary = ""
-->

- Developed debugging and analysis tooling for Modem Logs, giving firmware engineers a workable view of high-volume trace data <!-- src: mediatek-se-h1 @c6c7 -->
- Automated an ICD document-management system with Python and Jenkins, enforcing documentation standards as part of the build pipeline <!-- src: mediatek-se-h2 @0f13 -->
- Built an internal StackOverflow-style Q&A platform with AngularJS <!-- src: mediatek-se-h4 @b983 -->
- Created a World Wide Field Trial Upload Tool using Vue.js with Electron <!-- src: mediatek-se-h3 @bc02 -->

# Volunteer

## 42 Vienna — Peer Tutor & Workshop Host
<!--meta
id = "42-vienna-tutor"
start = "2024-07-01"
end = "2024-10-01"
url = "https://www.42vienna.com/"
-->

Volunteered as a peer tutor at 42 Vienna, supporting fellow students in system programming and software engineering fundamentals. Designed and hosted a Git workshop for the student community.

- Provided peer review and guidance in C/C++ system programming, shell scripting, and software architecture concepts <!-- src: 42-vienna-tutor-h2 @d02a -->
- Hosted a Git Essentials workshop — 'Something You Should Know Before Git Branch' — covering branching strategy, rebase, conflict resolution, and collaborative workflows (slides: https://docs.google.com/presentation/d/13InmNDRSfkeUnGWHNXWFiTr3QCAz4ecFL_wFz-NFdoI/edit?usp=sharing) <!-- src: 42-vienna-tutor-h1 @69e6 -->

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

## libftpp — C++ Architecture Library
<!--meta
id = "libftpp"
start = "2025-10-01"
end = "2026-01-01"
url = "https://github.com/42-CC-RNCP/libftpp"
roles = ["Author"]
-->

A modern C++20 library practicing SOLID principles, hexagonal architecture, and design patterns, with Architectural Decision Records documenting the trade-off reasoning behind each design.

- Implemented core data structures and utilities applying SOLID principles and hexagonal (ports & adapters) architecture <!-- src: libftpp-h1 @43bb -->
- Documented architectural decisions via ADRs, treating design trade-offs as first-class engineering artifacts <!-- src: libftpp-h2 @1335 -->
- Maintained CI pipeline with CMake, clang-format, and automated test suite <!-- src: libftpp-h3 @96ca -->

## webserver — HTTP/1.1 Server in C++
<!--meta
id = "webserver"
start = "2024-06-01"
end = "2024-09-01"
url = "https://github.com/LeaYeh/webserver"
roles = ["Developer"]
-->

A standards-compliant HTTP/1.1 web server written in C++ from scratch, handling concurrent connections, request parsing, and static/dynamic content serving.

- Built a non-blocking I/O event loop handling concurrent HTTP connections using poll/select <!-- src: webserver-h1 @49df -->
- Implemented HTTP/1.1 request parsing, routing, and response generation <!-- src: webserver-h2 @dc19 -->
- Supported CGI execution, static file serving, and configurable virtual hosts <!-- src: webserver-h3 @d6e6 -->

## ft_linux — Linux From Scratch
<!--meta
id = "ft-linux"
start = "2025-09-01"
end = "2026-01-01"
url = "https://github.com/42-CC-RNCP/ft_linux"
roles = ["Author"]
-->

A fully bootable Linux system built from scratch, covering every layer from cross-compilation toolchain to kernel configuration, filesystem hierarchy, init system, and bootloader.

- Built a two-phase cross-compilation toolchain (temporary + final) to produce a host-independent, self-contained Linux system <!-- src: ft-linux-h2 @efd1 -->
- Compiled a custom Linux kernel (4.x) with hand-selected driver and filesystem configuration <!-- src: ft-linux-h1 @28e0 -->
- Automated the full build pipeline (14 stages) via an ALFS-style bootstrap script with environment isolation and error recovery <!-- src: ft-linux-h3 @5370 -->

## minishell — Bash-compatible Shell
<!--meta
id = "minishell"
start = "2023-12-01"
end = "2024-03-01"
url = "https://github.com/LeaYeh/minishell"
roles = ["Developer"]
-->

A reimplementation of core GNU Bash features — command parsing, process management, and built-in execution — in C.

- Developed a syntax analyzer using the shift-reduce algorithm for Bash-like grammar interpretation <!-- src: minishell-h1 @abe2 -->
- Optimized subprocess management and pipeline execution across multi-stage pipelines <!-- src: minishell-h2 @9541 -->
- Employed Docker to ensure consistent development environments across the team <!-- src: minishell-h3 @f177 -->

# Skills

## Systems Architecture
<!--meta
id = "skill-systems-architecture"
level = "Advanced"
-->

- Hexagonal Architecture (Ports & Adapters)
- Layered system design
- Event-driven / async architecture
- Interface-first / contract-driven design
- Hardware Abstraction Layer (HAL)
- SOLID principles
- ADR-driven design
- Design Patterns

## Languages & Core Programming
<!--meta
id = "skill-languages-core"
level = "Master"
-->

- Python
- OOP / Pythonic
- C / C++ (C++20)
- SQL
- Pandas

## Systems & Low-Level Programming
<!--meta
id = "skill-systems-lowlevel"
level = "Intermediate"
-->

- Linux Kernel Internals
- Socket Programming
- Non-blocking I/O event loops
- High-performance Web Server
- Multiprocessing & parallel computing
- Performance Optimization

## Application & Web Development
<!--meta
id = "skill-app-web"
level = "Intermediate"
-->

- Vue.js / Electron
- AngularJS
- Streamlit
- HTTP / CGI
- Desktop & internal tooling

## Build, CI/CD & Delivery
<!--meta
id = "skill-build-delivery"
level = "Advanced"
-->

- Git / Git Flow
- GitHub Actions
- Jenkins
- CMake / clang-format
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
- Test planning
- Automated test suites

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
