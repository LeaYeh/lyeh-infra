# RBI - AI Engineer 面經

> created at: 2026-08-05
> updated at: 2026-08-05

## Job Description

Join a team where start-up pace meets the scale of an international banking group.

In this role, you will deliver AI and machine-learning solutions end-to-end—from agentic AI systems (LLMs, RAG, MCP, agent frameworks) to traditional ML models—and bring them into production across our network banks.

This role demands a polyvalent engineer who moves fluidly between deep technical work and direct engagement with business stakeholders across risk, fraud, operations, and customer analytics. You will be the bridge between complex technology and concrete business value.

**Your mission at RBI:**
- Own use cases end-to-end: problem framing, build, deploy, monitor, iterate.
- Design and deliver both agentic AI solutions (LLM orchestration, RAG, tool integrations) and traditional ML models.
- Establish MLOps/LLMOps practices: experiment tracking, CI/CD, monitoring, cost management.
- Run rigorous evaluations: backtesting, A/B testing, drift detection, red teaming.
- Work with business partners across the bank to define requirements, explain trade-offs, and support adoption.

**Your core competencies:**
- Experience shipping ML/AI systems to production (typically gained over ~5+ years). Financial services experience is a plus.
- Proficiency in Python and SQL; experience using Spark for data processing.
- Hands-on experience with both GenAI/agentic AI (LangChain, LlamaIndex, or similar; RAG; prompt engineering) and classical ML.
- MLOps fundamentals: MLflow, Docker, CI/CD, monitoring.
- The ability and willingness to engage a wide range of non-technical stakeholders: translating business problems into technical approaches, aligning on requirements, and communicating decisions and trade-offs. Fluent English required; German is an advantage.

**Nice to Have:**
- Responsible AI and regulatory awareness (EU AI Act, model risk).
- Software engineering foundations: APIs, microservices, containers, testing.
- Experience with Databricks.
- Banking domain knowledge.

## Before Interview

### 面試流程 聽說

面試流程為 2 輪，

1. 第一輪為 cv review (30min)
   a. 公司方介紹 - 10min
   b. 自我介紹 - 10min
   c. 問答時間 - 10min
2. 第二輪為 technical interview (90min)
   a. 技術問題 - 60min
   b. 問答時間 - 30min

### 面試題目

#### 第一輪 - CV Review

1. 請介紹你過去的專案經驗
2. 在專案中使用了哪些工具或框架？
3. 針對 JD 中提到的技能，請舉例說明你過去的經驗

##### RAG

目前我正為公司設計內部知識系統，目標是能回答多意圖的問題，答案需要參考，

1. cloud drive 上的文件 (pdf, ppt, docx, xlsx)
2. email 內容
3. postgres 資料庫中的資料 (CRM, ERP)
4. web 上的資料 (搜尋競品)

並且能夠在回答中引用文件來源。

1. 意圖識別是怎麼做的

   分層設計，考慮到成本、延遲、準確率，意圖識別分為三層：

   1. Rule layer: 使用正則表達式或關鍵字匹配，快速識別明確的意圖
      - 例如，當用戶輸入包含 "查詢" 或 "查找" 的句子時，可以將其分類為查詢意圖。
      - if 單意圖 and keyword match, then return intent
      - elif 多意圖 -> fallback to contextual layer
      - if confidence < threshold -> fallback to contextual layer
   2. Contextual layer: 使用 SLM + session context management，
      - SLM (Small Language Model) 用於理解用戶的輸入，並生成初步的意圖分類。
        - 但我現在的專案中目前是先走 prompt-based classification
      - Session context management 用於追蹤用戶的歷史對話，提供上下文信息，以提高意圖識別的準確性。
   3. Tool layer: LLM + tool integration
      - LLM (Large Language Model) 用於處理更複雜的意圖識別，特別是當用戶的輸入涉及多個意圖或模糊的表達時。
      - Tool integration 用於調用外部工具或服務，以獲取更多信息，從而輔助意圖識別。

2. routing 是怎麼做的

   根據問題種類我分成

   - Authoritative question: 有準確答案的問題，直接從資料庫
   - Knowledge question: 需要從文件中找答案的問題
   - email question: 需要從 email 中找答案的問題
   - External question: 需要從網路上找答案的問題

   1. Logical routing
      - LLM classification + function calling -> structured output -> routing

      ```prompt
      You are a router.

      Available tools:
      1. sql_database
      2. document_search
      3. email_search
      4. web_search


      Classify the query.

      Return intent in JSON format:
      {
          "data_source": "sql_database | document_search | email_search | web_search",
          "query": "the original query"
          "confidence": 0.0-1.0
      }
      ```

    2. Semantic routing
        1. 使用 embedding model 將 query 與各個資料來源的向量化表示進行相似度計算
        2. 根據相似度分數選擇最相關的資料來源進行檢索

    目前還在開發中，我判斷可解釋性 and debugable 比較重要，因此選用 logical routing
    不用 semantic routing 因為，
    1. 決策過程是黑盒
    2. Debug 成本不對稱
        - 改 embedding model 比改 prompt 還要麻煩，開發初期 iteration 會比較慢


3. 為什麼用 langgraph 而不是 langchain

    LangChain 跟 LangGraph 不是兩個互斥的選擇，而是抽象層級不同
    - LangChain 提供的是 chain（線性/固定順序的呼叫序列）跟 agent executor（ReAct 風格的迴圈，但控制流是隱式的、包在 executor 內部）
    - LangGraph 是建立在 LangChain 元件之上的 graph-based orchestration 層，把控制流變成顯式的 state machine（node + edge + conditional edge）

    考慮到我的 question routing 是一個 state machine，且需要可解釋性，我選擇 LangGraph
    1. 控制流顯式 vs 隱式
        - LangChain 的 AgentExecutor 是一個黑盒迴圈：LLM 決定下一步、執行、再讓 LLM 決定，整個過程你看不到、也難以插入自訂邏輯
    2. State 管理
        - Multi-hop 情境下（例如先查 SQL 拿到帳號資訊，再用這個資訊去查文件），你需要在多個步驟之間傳遞、累積、修改狀態
    3. Cycle / 回退能力
        - Multi-intent query 有時候需要「先試一條路徑，發現資訊不夠，回頭再查另一條路徑」
    

4. 怎麼選擇 RAG 架構 (SAG, CRAG, agentic RAG, Naive RAG, ...)

    判斷原則：用「問題型別」跟「準確率要求」反推架構，避免過度設計
    1. 排除 Naive RAG
        - Naive RAG 是單次 retrieve-then-generate，沒有 routing、沒有修正機制。我的系統需要處理多意圖問題（同一個 query 可能需要跨 SQL/文件/email/web 多個資料源），Naive RAG 連「這題該去哪裡查」都無法判斷，直接被排除。
    2. 借鑑 Self-RAG 的 re-query 機制
        - 雖然沒有完整採用 Self-RAG 架構，但它的核心概念——模型自我評估檢索結果品質，決定是否需要重新檢索——我借鑑到系統的 re-query 邏輯裡。當 retrieval 出來的 chunk 跟 query 相關性不足（例如 reranker 分數低於 threshold），系統會觸發重新檢索，而不是硬生生把不相關的內容塞給生成模型
    3. 選擇 Agentic RAG 支援 routing
        - 因為多意圖 + 需要跨資料源決策，我需要一個有「決策能力」的架構，而不是固定流程——這正是前幾題講的 LangGraph StateGraph + logical routing 的實作基礎。Agentic RAG 讓系統可以在檢索前先判斷「這題該用哪個工具」，而不是無腦對所有資料源做檢索再合併
    4. 排除 Graph RAG
        - Graph RAG 需要維護 entity/relation 抽取的正確性，這是一個持續性的維運負擔。作為 sole architect，我沒有團隊分攤這個維護成本，POC 階段引入 Graph RAG 的維運風險大於它帶來的準確率提升——這是基於團隊規模跟系統成熟度的現實判斷，不是能力上做不到

5. 怎麼選擇 embedding model
6. 文件的向量化是怎麼做的
7. 如何做 retrieval
8. 如何做 answer generation
9. How to do evaluation (accuracy, latency, cost)

##### Agentic AI

1. 你對 agentic AI 的理解是什麼
2. 你有使用過 agentic AI 的經驗嗎

3. MCP and function calling 的理解與使用經驗
    對於 LLM 來說 MCP and function calling 並無不同，都是透過 input prompt 讓 LLM 產生 structured output，然後再由外部程式去解析這個 output 並呼叫對應的 function。MCP 實作是在 agent 外部，function calling 實作是在 agent 內部。
        - MCP
            - 由 agent 外部 MCP server 建立 connection，agent 透過 MCP server 來呼叫 function
            - 以 github 為例，github operation logic 會實作在 MCP server，agent 只需要知道 function name + input parameters 就可以呼叫
            - 對後續維護比較方便，可插拔
        - function calling
            - 由 agent 內部直接呼叫 function，agent 內部實作 github operation logic
            - user 需要基於 interface 去實作 function，後續維護比較麻煩，因為 agent 內部的 function 可能會隨著 agent 的更新而改變

4. 你有使用過 agentic AI 的框架嗎 (LangChain, LlamaIndex, AutoGen, LangGraph, ...)

##### Classical ML

1. 你有使用過哪些 ML 模型
    - random forest, xgboost, lightgbm, linear regression, logistic regression, naive bayes, neural network
2. 你有使用過哪些 ML 框架 (sklearn, pytorch, tensorflow, ...)
    - I use sklearn for classical ML, pytorch for deep learning and for better understanding I tried to implement framework from scratch 
    
3. 怎麼做 feature selection / Dimensionality reduction
    EDA log，一筆資料 10k 個 feature（電性參數、時序參數、良率相關指標等），目標是找出哪些 feature 跟良率/失效模式有因果或高度相關關係，回饋給 RD 優化製程參數
    1. Correlation Matrix → Family Grouping
        - Pearson correlation 抓線性關係
        - Spearman correlation 抓非線性關係 exponential
        - distance correlation 與 mutual information（任意非線性依賴關係）
        - 用相關係數矩陣（1 - |corr| 當作距離）做 hierarchical clustering，把 10k 個 feature 分成數十到數百個 family group——同一個 family 裡的 feature 高度相關，代表它們可能反映同一個底層物理/電路機制
    2. Family 內挑代表 feature
        - 統計面：挑 family 內跟目標變數（良率/失效標籤）相關性最高、或 variance 最大（訊噪比最好）的 feature 當代表
        - 跟 RD 合作的關鍵環節：純統計挑出來的代表 feature 不一定有物理意義，需要跟 RD domain expert 對照
    3. 降維後的模型驗證
        - 把從 10k 降到可控數量（幾十到幾百）的 feature 丟進 xgboost/lightgbm，用 SHAP 做 attribution，確認模型判斷的重要 feature 跟 family grouping 挑出來的代表一致——這是一個交叉驗證統計方法有效性的手段
        - 用 bootstrap 重抽樣檢查 feature 被選中的穩定性，避免單次結果是偶然
    4. 怎麼做 RCA
        找出高影響力 family 之後，RCA 是把統計相關性收斂成工程上的因果假設
        1. 鎖定影響最大的幾個 family
        2. 跟 RD 一起把 family 代表 feature 對應回實際製程參數/測試站點
        3. 提出假設（例如某個製程步驟的參數漂移導致這組 feature 異常）

    "為什麼不直接用 PCA 降維，而是用 correlation-based family grouping？"
        - PCA 降維後的主成分失去物理可解釋性，RD 沒辦法直接對應到製程參數；family grouping 保留了原始 feature 的意義，犧牲一點統計最優性換取可解釋性跟跨部門溝通效率

5. 怎麼做 model evaluation (accuracy, precision, recall, f1, auc, ...)
6. 怎麼做 hyperparameter tuning
    - Optuna and Ray Tune to do hyperparameter tuning xgboost and neural network model
    - 我用過 grid search, random search, bayesian optimization, genetic algorithm, and hyperband for hyperparameter tuning

7. Forward propagation 與 Backward propagation 說明
8. 說明 xgboost / lightgbm 的原理
9. 說明 CNN / RNN / Transformer 的原理

##### LLM

1. transformer architecture 說明

##### MLOps

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

##### GitOps

1. 你有使用過哪些 GitOps 工具
    ArgoCD, Jenkins, GitHub Actions
2. 怎麼做 GitOps 的 CI/CD
3. 使用過 k8s 的經驗 (deployment, service, ingress, configmap, secret, ...)

##### Data Engineering

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
