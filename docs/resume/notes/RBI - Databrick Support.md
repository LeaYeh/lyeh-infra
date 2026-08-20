# RBI - Databricks Platform Support Engineer 面經

> created at: 2026-08-19
> updated at: 2026-08-19

## Job Description

### What you can expect
- Handle incidents, service requests, and user questions in a structured and timely way. 
- Directly analyze and debug Databricks issues, including jobs, clusters, permissions, Unity Catalog, data access, performance, and error messages. 
- Work closely with platform engineering, cloud, security, governance, and vendor teams to resolve more complex issues. 
- Support onboarding, user guidance, and adoption of platform capabilities such as Data Products, Unity Catalog, Genie/AI features, and cost transparency.  
- Identify recurring issues, improvement areas, and automation opportunities. 

### What you bring to the table
- Senior-level experience in platform support, data platform operations, application support, cloud operations, service management, or a similar role. 
- Hands-on experience with Databricks or similar platforms is required; strong AWS experience is also highly relevant. 
- Basic practical skills in SQL, Python, Spark, Github, or data engineering concepts. 
- Ability to debug technical issues directly, not only coordinate them. 
- Good understanding of modern data platform concepts such as Data Products, Unity Catalog, access management, platform governance, and cost monitoring. 
- Knowledge of agile working methods such as Scrum or Kanban. 

### Nice to have: 
- Experience supporting enterprise-scale Databricks or AWS-based data platforms. 
- Experience with monitoring, logging, root cause analysis, and operational reporting. 
- Experience in banking, financial services, or another regulated environment is a plus. 
- Interest in AI, Generative AI, and Large Language Models. 

## Before Interview

面試流程為 2 輪，

1. 第一輪為 cv review (45min)
   a. 公司方介紹 - 15min
   b. 自我介紹 - 15min
   c. 問答時間 - 15min
2. 第二輪為 technical interview (90min)
   a. 技術問題 - 60min
   b. 問答時間 - 30min

### 面試題目

#### Data Engineering

1. 你有使用過哪些資料庫 (PostgreSQL, MySQL, MongoDB, Redis, ...)
    BigQuery, PostgreSQL, MySQL, Redis, Elasticsearch, Splunk
2. 你有使用過哪些資料倉儲
    Built Datawarehouse on BigQuery (ODS, DWD, DWS, DM)
3. 你知道 Databricks 是什麼嗎
    我知道 Databricks 是 .... 但我沒有實務經驗

4. 你有使用過哪些資料處理框架 
5. 說明 Data pipeline 的設計流程
6. 解釋 Data Lake, Lakehouse and Data Warehouse 說明
    我們透過 GCP 的 GCS -> Airflow -> BigQuery 建立 Data Warehouse
    1. Data Lake: GCS, 存放原始資料，沒有 schema，資料格式不固定
    2. 透過 Airflow ETL 將資料轉成 BigQuery 的 DWD / DWS / ADS，建立 Data Warehouse
        - DWD: Data Warehouse Detail, de-normalized, normalized field, de-duplicated, cleaned, structured, transformed
        - DWS: Data Warehouse Summary, aggregated data, for reporting and analysis
        - ADS: Data Warehouse Application, for specific business use case
        - 對應到 Lakehouse 的概念，
            - bronze: GCS/ODS, raw data
            - silver: BigQuery DWD, cleaned data
            - gold: BigQuery DWS/ADS, aggregated data
7. 怎麼做 Data Quality Check (DQC) and how to handle DQC failure
    難點在於 Completeness + Validity 很難做到每個欄位定義 validation rule，實務上我們只對關鍵指標設定 rules，其他欄位只做 schema check，並且在 ETL pipeline 裡面加上 DQC 檢查，當 DQC 失敗時，會發送 alert 給 on-call engineer，並且暫停 pipeline，直到問題被解決。
    Business rule check 則是透過 dashboard 監控關鍵指標。

    ```flow
    GCS (raw)
    │
    ├─► DQC-1: Schema check（欄位是否存在、型別是否符合）
    │
    ▼
    Airflow (bronze → silver)
    │
    ├─► DQC-2: Completeness + Validity（清洗後檢查）
    │
    ▼
    BigQuery silver table
    │
    ├─► DQC-3: Consistency（跨表 join 完整性、row count 比對）
    │
    ▼
    BigQuery gold table
    │
    ├─► DQC-4: Business rule check（業務邏輯是否合理，e.g. 營收不可為負）
    │
    ▼
    Dashboard / ML training
    ```

8. 怎麼做 Data Lineage
    我針對 DAG 中 table 之間的調用、依賴關係，建立一個 metadata graph，並且在 DAG 執行時，將每個 task 的 input/output table 記錄下來，形成完整的 lineage。這樣可以追蹤資料的來源、流向，以及在 pipeline 中的轉換過程。
    但這跳套法當時的缺點是只知道 table level lineage，無法追蹤到 row level lineage。
    Data Lineage 主要的應用是，當上游的 table 發生變化時，可以追蹤到下游受影響的 table，透過 lineage graph 可以快速定位問題，並且通知相關的 owner 決定是否需要重新跑 pipeline 或是修正資料。


#### Databricks

1. 說明對 Databricks 的理解
2. 說明 儲存與事務層 - Delta Lake
    Overview of Delta Lake:
    ```example
                                Delta Table
                                │
                ┌──────────────┴──────────────┐
                │                             │
                ▼                             ▼
            _delta_log/                    Data Files
                │                             │
                │                             │
            ┌──────┴──────┐              ┌───────┴────────┐
            ▼             ▼              ▼                ▼
        JSON       Checkpoint      part-00000       part-00001
            │             │           .parquet          .parquet
            │             │
            ▼             ▼
        Actions       Snapshot
            │
    ┌────┴────┐
    ▼         ▼
    AddFile   RemoveFile
    │
    │ references
    ▼
    part-00001.snappy.parquet
    ```
    Delta Lake 是一個開源的儲存層，提供 ACID 事務、版本控制、Schema Enforcement、Time Travel 等功能，讓資料湖可以像資料倉儲一樣可靠地管理資料。
    > Data Files + Transaction Log

    我的了解是 Delta Lake 是建立在 Parquet 之上，並且使用 transaction log 來管理資料的版本，當有資料寫入時，
    1. 先寫資料檔案(Parquet)到 storage: 這時候檔案已經存在,但對 reader 來說還不可見(因為還沒被 log 記錄)
    2. 再寫一筆 commit 到 _delta_log: 一個 JSON 檔案,記錄「這次 transaction 新增了哪些檔案、刪除了哪些檔案
    3. 這個 log commit 才是真正的「原子開關」，當 reader 看到這個 commit 時，才會把這次 transaction 的檔案視為可見，否則 reader 只會看到舊的檔案。
2. 說明 Delta Log
    Delta Log 的單位是「Table」,不是「資料檔案」。 一張 Delta Table(也就是一個 LOCATION 路徑)只有一個 _delta_log/ 資料夾,裡面按順序記錄這張 table從建立以來所有的 transaction。不管這張 table 底下累積了 10 個 Parquet 檔案還是 10 萬個,log 資料夾都只有一份,不會每個 Parquet 檔案各自配一個 log。
    ```example
    s3://bucket/sensor_readings/
    ├── _delta_log/
    │   ├── 00000000000000000000.json   ← version 0: CREATE TABLE
    │   ├── 00000000000000000001.json   ← version 1: 第一次 INSERT
    │   ├── 00000000000000000002.json   ← version 2: 第二次 INSERT
    │   └── 00000000000000000003.json   ← version 3: UPDATE
    ├── part-00001-aaaa.snappy.parquet   ← version 1 產生
    ├── part-00002-bbbb.snappy.parquet   ← version 2 產生
    ├── part-00003-cccc.snappy.parquet   ← version 3 remove 的舊檔(邏輯刪除,物理還在)
    └── part-00004-dddd.snappy.parquet   ← version 3 產生的新檔
    ```
3. 說明 Delta Table 中的 version and commit 關係
    成功對 Delta Table 寫入資料後,會產生一個 commit, `SELECT` and `VACUUM` 則不會產生 commit。每個 commit 都會對應一個 version, version 只會增加,不會減少,也不會跳號。
    ```example
    對 Delta Table 的成功**寫入**
            ↓
    產生 commit
            ↓
    version + 1

    Delta Table
    │
    └── Transaction Log
           │
           ├── Version 0
           │     └── Commit
           │           ├── Action
           │           ├── Action
           │           └── Action
           │
           ├── Version 1
           │     └── Commit
           │           ├── Action
           │           └── Action
           │
           └── Version 2
                 └── Commit
                       ├── Action
                       ├── Action
                       └── Action
    ```
    一次成功地寫入可能需要多個 action 才能完成,例如一個 MERGE INTO 可能會產生多個 action in a commit,因為它可能需要先刪除舊檔案再新增新檔案,每個刪除或新增都會產生一個 action,但 commit and version 只會增加一次。
    ```sql
    MERGE INTO sales AS target
    USING updates AS source
    ON target.id = source.id
    WHEN MATCHED THEN
    UPDATE SET *
    WHEN NOT MATCHED THEN
    INSERT *;
    ```

    對於 reader 來說,他只會看到 version 的變化,不會看到 commit 的細節,因為 commit 是內部實作細節,對使用者透明。
    ```example
    v5
    │
    └── commit
        ├── RemoveFile A
        ├── AddFile B
        ├── AddFile C
        └── ...
        
    → v6
    ```
4. 說明 Checkpoint 機制
    如果一張 table 累積了幾萬次 transaction,每次查詢都要從 version 0 開始一路重播幾萬個 JSON 檔案才能知道「現在到底哪些檔案是有效的」,這樣太慢。所以 Delta Lake 有一個優化:
    ```example
    _delta_log/
    ├── 00000000000000000000.json
    ├── ...
    ├── 00000000000000000010.json
    ├── 00000000000000000010.checkpoint.parquet   ← 每 10 個 commit 產生一次的快照
    ├── _last_checkpoint                           ← 一個小檔案,記錄最新 checkpoint 在哪
    ├── 00000000000000000011.json
    └── ...
    ```
    Checkpoint 是什麼: 每累積 10 個 commit(預設值,可調整),Delta Lake 會把「當下所有仍然有效的檔案清單」壓縮成一個 Parquet 格式的快照存下來。之後 reader 要讀這張 table,不用從 version 0 開始重播,直接讀最近的 checkpoint,再把 checkpoint 之後少數幾筆 JSON commit 疊加上去就好 —— 這是典型的「full snapshot + incremental delta」設計,你在 event sourcing 或任何 log-based 系統應該都遇過同樣的模式。
5. 說明 Delta Table and Delta Live Table
    Delta Live Table (DLT) 是 Databricks 提供的一個 declarative 的資料 pipeline framework,讓使用者可以用 SQL 或 Python 來定義資料 pipeline,並且自動處理 schema enforcement, data validation, data cleaning, lineage tracking 等工作。
    不同於傳統 DQC 作法需要在不同層做 schema check, data validation, data cleaning, Delta Live Table (DLT) 提供了一個 declarative 的方式來定義資料 pipeline,讓使用者只需要描述「我想要的資料長什麼樣子」,DLT 會自動幫你做 schema enforcement, data validation, data cleaning, 並且自動產生 lineage graph。
    ```example
    ┌────────────────────────────────────────────────────────┐
    │             Delta Live Tables (DLT) Framework          │
    │  ( Pipeline Orchestration, Quality Checks, Lineage )   │
    └───────────────────────────┬────────────────────────────┘
                                │ 建立與維護
                                ▼
    ┌────────────────────────────────────────────────────────┐
    │                   Delta Table (Storage)                │
    │             ( Parquet + _delta_log / ACID )            │
    └────────────────────────────────────────────────────────┘
    ```
    | 特性 | Delta Table | Delta Live Tables (DLT) |
    | :--- | :--- | :--- |
    | **本質** | 儲存層格式（Storage Format） | 框架與管線工具（Pipeline Framework） |
    | **主要語法** | SQL / PySpark (`format("delta")`) | DLT 特有裝飾器 `@dlt.table` 或 SQL 語法 |
    | **資料品質驗證** | 僅支援基本 Constraint / Schema Enforcement | 支援進階 Expectations（警告、刪除、中斷） |
    | **依賴管理** | 需手動搭配 Airflow 或 Databricks Workflows 排程 | 自動根據 SQL/Python 宣告建構 DAG 依賴 |
    | **表格維護** | 需要手動或寫排程執行 `OPTIMIZE` / `VACUUM` | 系統自動背景維護與優化 |
    | **底層儲存** | 產出的資料就是 Delta Table | DLT 運算出的最終結果也是以 Delta Table 格式儲存 |

    Expectations 可以直接在 DLT pipeline 裡面定義，發現異常資料時可選擇警告、丟棄或中斷管線: 
    | 處置方式 | SQL 關鍵字 | Python 裝飾器 | 適用情境與行為 |
    | :--- | :--- | :--- | :--- |
    | **警告 (Warn)** | `EXPECT` | `@dlt.expect` | **預設機制**。不合規資料仍會寫入表格，但系統會發出警示並記錄指標。 |
    | **丟棄 (Drop)** | `EXPECT ... ON VIOLATION DROP ROW` | `@dlt.expect_or_drop` | **自動過濾**。直接丟棄不合規資料，合規資料正常寫入表格。 |
    | **中斷 (Fail)** | `EXPECT ... ON VIOLATION FAIL TASK` | `@dlt.expect_or_fail` | **嚴格止血**。一旦發現任何不合規資料，整個 DLT Pipeline 立即停止運作。 |

    ```sql
    -- 1. 警告 (Warn)：記錄不合規筆數，資料照常寫入
    CREATE OR REFRESH LIVE TABLE sales_cleaned
    (
    CONSTRAINT valid_amount EXPECT (amount > 0),
    CONSTRAINT valid_user_id EXPECT (user_id IS NOT NULL)
    )
    AS SELECT * FROM STREAM(LIVE.sales_raw);

    -- 2. 丟棄 (Drop)：自動剔除無效資料
    CREATE OR REFRESH LIVE TABLE filtered_customers
    (
    CONSTRAINT valid_email EXPECT (email LIKE '%@%.%') ON VIOLATION DROP ROW
    )
    AS SELECT * FROM LIVE.customers_raw;

    -- 3. 中斷 (Fail)：發現無效資料時立刻中斷 Task
    CREATE OR REFRESH LIVE TABLE financial_records
    (
    CONSTRAINT non_negative_balance EXPECT (balance >= 0) ON VIOLATION FAIL TASK
    )
    AS SELECT * FROM LIVE.accounts_raw;
    ```
6. 說明 高效能運算引擎 - Photon & Spark
7. 說明 資料治理與安全 - Unity Catalog (Workspace / Catalog / Schema / Table)
    Databricks: catalog.schema.table <-> GCP: project.dataset.table

    | 階層 / 結構 | 說明 | 存取與權限範圍 |
    | :--- | :--- | :--- |
    | **Account / Workspace** | Workspace 是開發作業環境，可有多個。Unity Catalog 隸屬於 Account 級別，能綁定多個 Workspaces 共享相同 Catalog。 | **跨環境隔離**：決定使用者可以在哪個作業環境下讀寫資料。 |
    | **1st Level: Catalog** | 命名空間的最頂層，通常用來劃分環境（如 `dev`, `prod`）或業務部門（如 `finance`, `marketing`）。 | **頂層隔離**：可直接在 Catalog 層級授權（例如：`GRANT USE CATALOG ON dev TO developers;`）。 |
    | **2nd Level: Schema (Database)** | 包含在 Catalog 之下，用於將資料依據主題或資料階段進行邏輯分組（如 `bronze`, `silver`, `gold` 或 `sales_raw`）。 | **主題邏輯區分**：便於管理特定業務主題下的物件權限與存取。 |
    | **3rd Level: Table / Asset** | 最底層的實際資產，可為結構化表格（Table/View）、儲存非結構化檔案的 **Volume** 或 MLflow **Model**。 | **實體資料**：定義欄位 Schema 與實際檔案路徑，套用最終欄位遮蔽與資料讀寫權限。 |

    跟 GCP BigQuery 的對照表：
    | 階層概念 | Databricks (Unity Catalog) | GCP BigQuery | 對照說明 |
    | :--- | :--- | :--- | :--- |
    | **最高管理層** | Account | GCP Organization | 企業的最頂層容器，管理全公司的帳號、計費與整體政策。 |
    | **工作/資源環境** | Workspace | GCP Project | 劃分開發環境或專案資源（如 `dev-project` vs `prod-project`）。 |
    | **1st Level (頂層目錄)** | Catalog | BigQuery Project | 資料的頂層隔離。在 SQL 語法中對應最前方的名稱。 |
    | **2nd Level (邏輯分組)** | Schema (或 Database) | BigQuery Dataset | 將相關表格依業務或階段（`bronze`/`raw`）分組的容器。 |
    | **3rd Level (實體資產)** | Table / View / Volume | Table / View / External Table | 最終存放資料的實體物件。 |
8. 說明 三層架構 - Bronze / Silver / Gold

    | 比較維度 | 你的實際經驗 (MTK + GCP 演進架構) | Databricks Lakehouse 體系 |
    | :--- | :--- | :--- |
    | **架構範式** | **混合型 ETL + Cloud DW** (地端/混合雲 Extract ➔ GCP 載入與數據集市) | **Unified Data Lakehouse** (批次、串流、AI/ML 全部收攏於同一平台) |
    | **Extract & Load (E & L)**<br>*(寫入 Raw / Bronze)* | **Apache NiFi + Parser Scripts + Airflow**<br>• 用 NiFi 解析複雜格式/地端資料<br>• Airflow 排程搬運至 GCS / BigQuery ODS | **Auto Loader (`cloudFiles`) / Lakeflow Connect**<br>• 自動監控 Cloud Storage 檔案寫入<br>• 自動推斷 Schema，增量串流寫入 Delta Table |
    | **Transform (T)**<br>*(Bronze ➔ Silver ➔ Gold)* | **GCP Airflow (Cloud Composer) + SQL**<br>• 用 Airflow 排程觸發 BigQuery SQL<br>• 進行 ODS ➔ DWD ➔ DWS 運算 | **Delta Live Tables (DLT) / Spark SQL**<br>• 宣告式 pipeline，自動建構 DAG<br>• 內建 Expectations 做資料品質檢核與攔截 |
    | **Orchestration (排程調度)** | **Apache Airflow**<br>（跨地端與 GCP 的全域流程控制與依存關聯） | **Databricks Workflows** 或 **外部 Airflow**<br>（Databricks Workflows 為內建 DAG 工具；亦可由 Airflow 觸發） |
    | **底層運算引擎 (Compute)** | **BigQuery Engine** (Serverless SQL)<br>+ 外部 Parser 腳本 (Python/Java) | **Photon Engine** (C++ 向量化 SQL 引擎)<br>+ **Apache Spark** (JVM 分散式運算) |
    | **儲存與格式 (Storage)** | **GCS** (Raw files) + **BigQuery Native Storage** | **Cloud Object Storage (GCS/S3)** + **Delta Lake** (開源 ACID 格式) |
    | **資料治理 (Governance)** | **GCP Cloud IAM + Data Catalog**<br>（搭配 GCP Project / Dataset 權限） | **Unity Catalog**<br>（3-Level Namespace: `catalog.schema.table` 跨雲治理） |

9. 解釋 Data Lake, Lakehouse and Data Warehouse 說明
    我們透過 GCP 的 GCS -> Airflow -> BigQuery 建立 Data Warehouse
    1. Data Lake: GCS, 存放原始資料，沒有 schema，資料格式不固定
    2. 透過 Airflow ETL 將資料轉成 BigQuery 的 DWD / DWS / ADS，建立 Data Warehouse
        - DWD: Data Warehouse Detail, de-normalized, normalized field, de-duplicated, cleaned, structured, transformed
        - DWS: Data Warehouse Summary, aggregated data, for reporting and analysis
        - ADS: Data Warehouse Application, for specific business use case
        - 對應到 Lakehouse 的概念，
            - bronze: GCS/ODS, raw data
            - silver: BigQuery DWD, cleaned data
            - gold: BigQuery DWS/ADS, aggregated data

#### MLOps

MLOps = CI/CD + Data + Model 的 DevOps
- Experiment Tracking
- Model Registry
- Staging / Production / Archived
- 做 version control, rollback, A/B testing
- Reproducibility
- Code / parameters / environment
- Deployment
- Monitoring


1. 你有使用過哪些 MLOps 工具
    MLflow 紀錄實驗參數 and eval metrics, MLflow 管 training side
2. 你有使用過哪些 CI/CD 工具
    很久以前使用過 Jenkins，現在在我每個專案都會用 Github action 跑 CI/CD (unit test, lint, build docker image, push to registry, deploy to k8s)
    對於公司內部專案我用 Github action + ArgoCD 做 GitOps
3. 怎麼做 model monitoring (drift detection, performance monitoring, alerting, ...)
    我們用 Prometheus + Grafana 做 model monitoring，Prometheus 負責收集 metrics，Grafana 負責可視化和 alerting
    1. define metrics
        - PSI: 某個 feature 的「比例結構」變了多少
        - KS: 兩個 distribution（分佈）是不是長得一樣
        
        ```example
        Null hypothesis: no drift
        Alternative hypothesis: drift

        KS = 0.03, PSI = 0.72
        => 如果沒有 drift, 看到這個結果的機率 72% -> no drift

        KS = 0.25, PSI = 0.001
        => 如果沒有 drift, 看到這個結果的機率 0.1% -> drift
        ```
    2. log metrics into Prometheus
    3. Grafana alerting
    4. HITL Root cause analysis

4. 怎麼做 model deployment (docker, kubernetes, serverless, ...)
    我們用 MLflow + Docker + Kubernetes 做 model deployment
    1. MLflow model registry
        - model versioning, stage management (staging, production, archived)
    2. Docker image build
    3. Kubernetes deployment
        - Deployment, Service, Ingress, ConfigMap, Secret
5. 怎麼做 model versioning (MLflow, DVC, git, ...)
    1. code versioning: git
    2. data versioning
        1. 訓練前，先把資料凍結成 snapshot - BigQuery snapshot table
        2. 用 mlflow.data 做更正式的 dataset lineage
        3. Model Registry 階段，把 snapshot 資訊帶到 model version 的 tag

6. 怎麼做 model rollback
    1. Grafana alert 觸發（drift score / error rate 超標）
    2. On-call 確認：查看 MLflow run 對應的 data_snapshot、訓練時的 metrics baseline
    3. 決策：alias 切換（軟）或 ArgoCD revert（硬）
    4. 執行 rollback
    5. 驗證：Grafana dashboard 確認指標回穩
    6. 事後：在 v(current) model version tag 記錄 rollback 原因，寫 incident note
8. Data Drifting 怎麼 detect and handle
9. Model Drifting 怎麼 detect and handle
    Feature 分布可能沒變，但是 X → Y relationship changed
    1. monitor model performance metrics (accuracy, precision, recall, f1, auc, ...)
    2. model output distribution
    3. re-train or re-design model 