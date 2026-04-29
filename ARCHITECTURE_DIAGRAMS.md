# GenAI Product Consistency Engine - Visual Architecture Diagrams

## System Component Diagram

```mermaid
graph TB
    subgraph Frontend["Frontend Layer (Next.js + Tailwind)"]
        Upload["Document Upload<br/>Component"]
        Dashboard["Analysis<br/>Dashboard"]
        ResultsView["Results &<br/>Conflicts View"]
        RecommendationUI["Recommendations<br/>UI"]
    end

    subgraph Gateway["API Gateway (FastAPI)"]
        Auth["Authentication<br/>Middleware"]
        Router["Request<br/>Router"]
        RateLimit["Rate<br/>Limiting"]
    end

    subgraph Processing["Processing Layer"]
        DocProcessor["Document<br/>Processor"]
        Embedding["Embedding<br/>Service"]
        
        subgraph Orchestrator["Master Orchestrator"]
            OrchestratorCore["Orchestration<br/>Engine"]
        end
        
        subgraph AgentLayer["Agent Layer"]
            PRDAgent["PRD<br/>Agent"]
            DevAgent["Dev<br/>Agent"]
            DesignAgent["Design<br/>Agent"]
        end
        
        Analyzer["Consistency<br/>Analyzer"]
        ConflictDetector["Conflict<br/>Detector"]
        Recommender["Recommendation<br/>Engine"]
    end

    subgraph DataLayer["Data Layer (Supabase)"]
        DB["PostgreSQL<br/>Database"]
        VectorDB["pgvector<br/>Embeddings"]
        Storage["File<br/>Storage"]
        Auth_SB["Authentication"]
    end

    Frontend -->|REST/WebSocket| Gateway
    Gateway -->|Auth Check| Auth
    Gateway -->|Route| Router
    Router -->|Apply Limits| RateLimit
    
    RateLimit -->|Process| DocProcessor
    DocProcessor -->|Create Vectors| Embedding
    
    Embedding -->|Provide Context| OrchestratorCore
    OrchestratorCore -->|Dispatch| PRDAgent
    OrchestratorCore -->|Dispatch| DevAgent
    OrchestratorCore -->|Dispatch| DesignAgent
    
    PRDAgent -->|Analyze| Analyzer
    DevAgent -->|Analyze| Analyzer
    DesignAgent -->|Analyze| Analyzer
    
    Analyzer -->|Detect| ConflictDetector
    ConflictDetector -->|Generate| Recommender
    
    Gateway -->|Read/Write| DB
    DocProcessor -->|Store Chunks| VectorDB
    Embedding -->|Index| VectorDB
    Upload -->|Save Files| Storage
    Auth -->|Verify| Auth_SB
```

## Data Flow Diagram

```mermaid
sequenceDiagram
    actor User
    participant Frontend as Next.js<br/>Frontend
    participant API as FastAPI<br/>Backend
    participant DB as Supabase<br/>Database
    participant Agent as Agent<br/>Pool
    participant Analyzer as Analyzer

    User->>Frontend: Upload PRD, Design, Code
    Frontend->>API: POST /api/analysis/upload
    API->>DB: Store documents
    API->>DB: Create analysis record
    API->>Frontend: Return analysis_id + WebSocket

    API->>API: Extract & chunk text
    API->>API: Create embeddings
    API->>DB: Store vectors

    API->>Agent: Initialize agents
    par Parallel Agent Execution
        Agent->>Agent: PRD Agent analyzes
        Agent->>Agent: Dev Agent analyzes
        Agent->>Agent: Design Agent analyzes
    end

    Agent->>API: Return structured JSON
    note over API: features, flows, requirements

    API->>Analyzer: Compare outputs
    Analyzer->>Analyzer: Detect gaps & conflicts
    Analyzer->>Analyzer: Generate scores

    API->>DB: Store conflicts & recommendations
    API->>Frontend: WebSocket: analysis_complete
    Frontend->>Frontend: Display results

    User->>Frontend: View conflicts
    User->>Frontend: Resolve conflict manually
    Frontend->>API: PATCH /conflict/{id}
    API->>DB: Update conflict status
    API->>Frontend: WebSocket: conflict_resolved
```

## Agent Communication Flow

```mermaid
graph LR
    subgraph Input["Input Documents"]
        PRD_Doc["PRD Document"]
        Design_Doc["Design Document"]
        Code_Doc["Code Summary"]
    end

    subgraph Processing["Processing"]
        Preprocessing["Text Extraction<br/>& Chunking"]
        Embedding_Gen["Embedding<br/>Generation"]
        Context["Context<br/>Creation"]
    end

    subgraph Agents["Agent Execution"]
        subgraph PRD["PRD Agent"]
            PRD_Extract["Extract<br/>Requirements"]
            PRD_Features["Map<br/>Features"]
            PRD_Output["Output:<br/>JSON"]
        end
        
        subgraph Dev["Dev Agent"]
            Dev_Parse["Parse<br/>Architecture"]
            Dev_Extract["Extract<br/>Patterns"]
            Dev_Output["Output:<br/>JSON"]
        end
        
        subgraph Design["Design Agent"]
            Design_Parse["Parse<br/>Systems"]
            Design_Extract["Extract<br/>Specs"]
            Design_Output["Output:<br/>JSON"]
        end
    end

    subgraph Analysis["Analysis & Detection"]
        Compare["Cross-Reference<br/>Outputs"]
        Conflicts["Detect<br/>Conflicts"]
        Score["Calculate<br/>Score"]
    end

    subgraph Results["Results"]
        Recommendations["Generate<br/>Recommendations"]
        Report["Create<br/>Report"]
        Store["Store in<br/>Database"]
    end

    PRD_Doc --> Preprocessing
    Design_Doc --> Preprocessing
    Code_Doc --> Preprocessing
    
    Preprocessing --> Embedding_Gen
    Embedding_Gen --> Context
    
    Context -->|Feed| PRD_Extract
    Context -->|Feed| Dev_Parse
    Context -->|Feed| Design_Parse
    
    PRD_Extract --> PRD_Features --> PRD_Output
    Dev_Parse --> Dev_Extract --> Dev_Output
    Design_Parse --> Design_Extract --> Design_Output
    
    PRD_Output --> Compare
    Dev_Output --> Compare
    Design_Output --> Compare
    
    Compare --> Conflicts
    Compare --> Score
    
    Conflicts --> Recommendations
    Score --> Recommendations
    Recommendations --> Report
    Report --> Store
```

## Database Schema Relationship Diagram

```mermaid
erDiagram
    ORGANIZATIONS ||--o{ ORGANIZATION_MEMBERS : has
    ORGANIZATIONS ||--o{ ANALYSES : owns
    AUTH_USERS ||--o{ ORGANIZATION_MEMBERS : joins
    AUTH_USERS ||--o{ ANALYSES : creates
    
    ANALYSES ||--o{ DOCUMENTS : contains
    ANALYSES ||--o{ AGENT_OUTPUTS : has
    ANALYSES ||--o{ CONFLICTS : has
    ANALYSES ||--o{ RECOMMENDATIONS : has
    
    DOCUMENTS ||--o{ DOCUMENT_CHUNKS : splits
    DOCUMENT_CHUNKS ||--o{ EMBEDDING_CACHE : stores
    
    CONFLICTS ||--o{ RECOMMENDATIONS : triggers
    
    AUTH_USERS ||--o{ CONFLICTS : resolves
    AUTH_USERS ||--o{ AUDIT_LOGS : creates
    ORGANIZATIONS ||--o{ AUDIT_LOGS : logs

    ORGANIZATIONS {
        uuid id PK
        string name
        string plan
        datetime created_at
    }

    AUTH_USERS {
        uuid id PK
        string email UK
        string name
    }

    ORGANIZATION_MEMBERS {
        uuid id PK
        uuid org_id FK
        uuid user_id FK
        string role
    }

    ANALYSES {
        uuid id PK
        uuid org_id FK
        string title
        string status
        int consistency_score
        datetime created_at
    }

    DOCUMENTS {
        uuid id PK
        uuid analysis_id FK
        string name
        string doc_type
        string file_path
        text raw_text
    }

    DOCUMENT_CHUNKS {
        uuid id PK
        uuid document_id FK
        int chunk_index
        text content
        vector embedding
    }

    EMBEDDING_CACHE {
        uuid id PK
        uuid document_chunk_id FK
        vector embedding
    }

    AGENT_OUTPUTS {
        uuid id PK
        uuid analysis_id FK
        string agent_name
        jsonb output_json
        float confidence_score
    }

    CONFLICTS {
        uuid id PK
        uuid analysis_id FK
        string conflict_type
        string severity
        string title
        text description
        string status
    }

    RECOMMENDATIONS {
        uuid id PK
        uuid analysis_id FK
        uuid conflict_id FK
        string priority
        string title
        boolean applied
    }

    AUDIT_LOGS {
        uuid id PK
        uuid org_id FK
        uuid user_id FK
        string action
        jsonb old_values
        jsonb new_values
    }
```

## API Endpoint Hierarchy

```mermaid
graph TD
    ROOT["/api"]
    
    ROOT --> AUTH["<b>/auth</b>"]
    AUTH --> AUTH_REG["POST /register"]
    AUTH --> AUTH_LOGIN["POST /login"]
    AUTH --> AUTH_LOGOUT["POST /logout"]
    AUTH --> AUTH_REFRESH["POST /refresh-token"]
    
    ROOT --> ORGS["<b>/orgs</b>"]
    ORGS --> ORGS_GET["GET / — List orgs"]
    ORGS --> ORGS_CREATE["POST / — Create org"]
    ORGS --> ORGS_BY_ID["GET /{id} — Get org"]
    ORGS --> ORGS_UPDATE["PATCH /{id} — Update org"]
    
    ROOT --> ANALYSIS["<b>/analysis</b>"]
    ANALYSIS --> ANALYSIS_CREATE["POST /create"]
    ANALYSIS --> ANALYSIS_ID["<b>/{id}</b>"]
    
    ANALYSIS_ID --> ANALYSIS_UPLOAD["POST /upload"]
    ANALYSIS_ID --> ANALYSIS_GET["GET / — Get status"]
    ANALYSIS_ID --> ANALYSIS_RESULTS["GET /results"]
    ANALYSIS_ID --> ANALYSIS_CONFLICTS["GET /conflicts"]
    ANALYSIS_ID --> ANALYSIS_CONFLICT_ID["<b>/conflict/{cid}</b>"]
    
    ANALYSIS_CONFLICT_ID --> CONFLICT_PATCH["PATCH / — Resolve"]
    ANALYSIS_ID --> AGENT["<b>/agent</b>"]
    AGENT --> AGENT_PRD["GET /prd — PRD output"]
    AGENT --> AGENT_DEV["GET /dev — Dev output"]
    AGENT --> AGENT_DESIGN["GET /design — Design output"]
    AGENT --> AGENT_MASTER["GET /master — Master report"]
    
    ANALYSIS_ID --> REC["GET /recommendations"]
    ANALYSIS_ID --> EXPORT["GET /export?format=pdf|json"]
    
    ANALYSIS --> HISTORY["GET /history"]
```

## Deployment Architecture

```mermaid
graph TB
    Client["👥 Client Browser"]
    
    subgraph CDN["CDN / Edge"]
        EdgeCache["Edge Cache"]
    end
    
    subgraph FrontendInfra["Vercel Deployment"]
        Frontend["Next.js App<br/>Auto-scaled"]
        FrontendImageOpt["Image<br/>Optimization"]
    end
    
    subgraph BackendInfra["Render / Railway"]
        LoadBalancer["Load Balancer"]
        API1["FastAPI Pod 1"]
        API2["FastAPI Pod 2"]
        API3["FastAPI Pod 3"]
        Cache["Redis Cache"]
        Queue["Job Queue"]
    end
    
    subgraph Database["Supabase Cloud"]
        DBPrimary["PostgreSQL<br/>Primary"]
        DBReplica["Read<br/>Replica"]
        Auth["Auth Service"]
        Storage["Object Storage<br/>S3"]
        VectorDB["pgvector<br/>Index"]
    end
    
    subgraph Monitoring["Observability"]
        Metrics["Prometheus<br/>Metrics"]
        Logs["CloudWatch<br/>Logs"]
        Traces["Jaeger<br/>Tracing"]
        Alerts["AlertManager"]
    end
    
    Client -->|HTTPS| CDN
    Client -->|WebSocket| LoadBalancer
    CDN -->|Cache Hit| EdgeCache
    EdgeCache -->|Fallback| FrontendInfra
    
    FrontendInfra -->|API Calls| LoadBalancer
    LoadBalancer -->|Round Robin| API1
    LoadBalancer -->|Round Robin| API2
    LoadBalancer -->|Round Robin| API3
    
    API1 -->|Query| Cache
    API2 -->|Query| Cache
    API3 -->|Query| Cache
    Cache -->|Miss| DBPrimary
    
    API1 -->|Enqueue| Queue
    API2 -->|Enqueue| Queue
    API3 -->|Enqueue| Queue
    
    API1 -->|Read| DBReplica
    API2 -->|Read| DBReplica
    API3 -->|Read| DBReplica
    
    API1 -->|Write| DBPrimary
    API2 -->|Write| DBPrimary
    API3 -->|Write| DBPrimary
    
    DBPrimary -->|Vector Search| VectorDB
    
    API1 -->|Upload/Download| Storage
    API2 -->|Upload/Download| Storage
    API3 -->|Upload/Download| Storage
    
    Auth -->|Validate JWT| API1
    Auth -->|Validate JWT| API2
    Auth -->|Validate JWT| API3
    
    API1 -->|Metrics| Metrics
    API2 -->|Metrics| Metrics
    API3 -->|Metrics| Metrics
    
    API1 -->|Logs| Logs
    API2 -->|Logs| Logs
    API3 -->|Logs| Logs
    
    Metrics -->|Alert| Alerts
    Logs -->|Alert| Alerts
```

## Agent Processing Timeline

```mermaid
timeline
    title Analysis Processing Timeline
    
    section Initialization
        0ms : Upload triggered
        10ms : Files extracted and stored
        20ms : Text chunked and embedded
        30ms : Orchestrator initialized
    
    section Parallel Agent Execution
        50ms : Agents start parallel execution
        60ms : PRD Agent processing
        60ms : Dev Agent processing
        60ms : Design Agent processing
        150ms : PRD Agent complete (features extracted)
        200ms : Dev Agent complete (architecture parsed)
        180ms : Design Agent complete (specs extracted)
    
    section Analysis Phase
        220ms : All agents finished
        230ms : Consistency analyzer starts
        280ms : Conflict detection complete
        300ms : Recommendations generated
        310ms : Results stored in database
    
    section Delivery
        320ms : WebSocket notification sent
        330ms : Frontend receives results
        340ms : Dashboard updated and displayed
```

## Multi-Tenancy & Security Model

```mermaid
graph TB
    subgraph Organization["Organization A"]
        User1["User 1<br/>(Admin)"]
        User2["User 2<br/>(Editor)"]
        User3["User 3<br/>(Viewer)"]
        Project1["Project 1"]
        Project2["Project 2"]
    end
    
    subgraph Organization2["Organization B"]
        User4["User 4<br/>(Admin)"]
        Project3["Project 3"]
    end
    
    subgraph Auth["Authentication Layer"]
        OAuth["OAuth2<br/>Provider"]
        JWTGen["JWT<br/>Generator"]
        TokenVerify["Token<br/>Verification"]
    end
    
    subgraph DB["Database Layer"]
        RLS["Row-Level<br/>Security<br/>Policies"]
        OrgTable["Organizations<br/>Table"]
        AnalysisTable["Analyses<br/>Table"]
        ConflictTable["Conflicts<br/>Table"]
    end
    
    User1 -->|Login| OAuth
    User2 -->|Login| OAuth
    User4 -->|Login| OAuth
    
    OAuth -->|Issue Token| JWTGen
    JWTGen -->|JWT| User1
    
    User1 -->|API Request| TokenVerify
    TokenVerify -->|Validate| RLS
    
    RLS -->|Enforce Access| OrgTable
    RLS -->|Filter Results| AnalysisTable
    RLS -->|Filter Results| ConflictTable
    
    Project1 -->|Belongs to| Organization
    Project2 -->|Belongs to| Organization
    Project3 -->|Belongs to| Organization2
    
    Organization -->|Grant| User1
    Organization -->|Grant| User2
    Organization -->|Grant| User3
    Organization2 -->|Grant| User4
    
    User1 -->|Can CRUD| Project1
    User1 -->|Can CRUD| Project2
    User2 -->|Can Edit| Project1
    User3 -->|Can View| Project1
    User4 -->|Cannot Access| Project1
```

## Conflict Detection Logic

```mermaid
graph LR
    PRDOutput["PRD Output<br/>Features:<br/>- Auth<br/>- Dashboard<br/>- Export"]
    
    DevOutput["Dev Output<br/>Components:<br/>- Auth UI<br/>- Dashboard<br/>- Settings"]
    
    DesignOutput["Design Output<br/>Screens:<br/>- Login<br/>- Dashboard<br/>- Profile"]
    
    Comparator["Comparator<br/>Checks for:<br/>1. Coverage<br/>2. Overlap<br/>3. Contradictions"]
    
    subgraph Conflicts["Detected Conflicts"]
        Missing["MISSING_FEATURE: Export<br/>not in Dev/Design"]
        Contradict["CONTRADICTING:<br/>Auth implementation<br/>differs across specs"]
        Incomplete["INCOMPLETE_SPEC:<br/>No tech stack detail<br/>for Dashboard"]
    end
    
    Recommendations["Recommendations<br/>- Add Export feature<br/>- Clarify Auth<br/>- Define Dashboard stack"]
    
    PRDOutput --> Comparator
    DevOutput --> Comparator
    DesignOutput --> Comparator
    
    Comparator -->|Analyze| Missing
    Comparator -->|Analyze| Contradict
    Comparator -->|Analyze| Incomplete
    
    Missing --> Recommendations
    Contradict --> Recommendations
    Incomplete --> Recommendations
```

