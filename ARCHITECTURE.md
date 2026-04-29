# GenAI Product Consistency Engine - System Architecture

## 1. System Overview

The GenAI Product Consistency Engine is a multi-agent AI system that analyzes uploaded product documents (PRD, Design Docs, Code Summaries) and detects inconsistencies across different product perspectives.

### Key Objectives
- Validate product consistency across documentation layers
- Detect conflicts between PRD, design, and implementation
- Suggest corrections and updates
- Provide structured insights for product teams

---

## 2. High-Level System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          CLIENT LAYER (Next.js)                         │
│                                                                         │
│  ┌──────────────────┐  ┌──────────────────┐  ┌────────────────────┐  │
│  │  Document Upload │  │  Analysis Board  │  │  Results Dashboard │  │
│  │  (Drag & Drop)   │  │  (Real-time)     │  │  (Conflicts View)  │  │
│  └──────────┬───────┘  └──────┬───────────┘  └────────┬───────────┘  │
│             │                 │                        │               │
│             └─────────────────┴────────────────────────┘               │
│                    WebSocket / REST API                                │
└──────────────────────────────┬──────────────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────────────┐
│                      API GATEWAY (FastAPI)                              │
│                                                                         │
│  • Authentication (Supabase Auth)                                      │
│  • Request Routing                                                     │
│  • Rate Limiting & Monitoring                                         │
│  • WebSocket Server                                                   │
└──────────────────────────────┬──────────────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────────────┐
│                    PROCESSING LAYER (FastAPI)                          │
│                                                                         │
│  ┌────────────────────────────────────────────────────────────────┐   │
│  │        Document Processing Pipeline                            │   │
│  │  • File Extraction (PDF/DOCX/TXT)                              │   │
│  │  • Text Chunking & Preprocessing                               │   │
│  │  • Vector Embedding                                            │   │
│  └────────────────────────────────────────────────────────────────┘   │
│                               │                                        │
│  ┌────────────────────────────▼────────────────────────────────────┐  │
│  │        MASTER ORCHESTRATOR                                      │  │
│  │  ◇ Coordinates multi-agent workflow                           │  │
│  │  ◇ Manages state & results aggregation                        │  │
│  │  ◇ Triggers consistency analysis                              │  │
│  └────────────────────────────┬─────────────────────────────────────┘ │
│                               │                                        │
│  ┌────────────────────────────┴─────────────────────────────────────┐ │
│  │                    AGENT LAYER                                   │ │
│  │                                                                 │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │ │
│  │  │  PRD Agent   │  │  Dev Agent   │  │ Design Agent │          │ │
│  │  │              │  │              │  │              │          │ │
│  │  │ • Extracts   │  │ • Analyzes   │  │ • Parses     │          │ │
│  │  │   features   │  │   code       │  │   design     │          │ │
│  │  │ • Maps users │  │   patterns   │  │   systems    │          │ │
│  │  │ • Defines    │  │ • Identifies │  │ • Validates  │          │ │
│  │  │   flows      │  │   tech stack │  │   specs      │          │ │
│  │  └──────────────┘  └──────────────┘  └──────────────┘          │ │
│  │                                                                 │ │
│  └─────────────────────────────────────────────────────────────────┘ │
│                                                                     │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │        CONSISTENCY ANALYZER                                    │  │
│  │  • Compares agent outputs                                      │  │
│  │  • Identifies gaps & conflicts                                 │  │
│  │  • Generates recommendations                                   │  │
│  │  • Scores consistency level                                    │  │
│  └────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────┬────────────────────────────────────────┘
                              │
┌─────────────────────────────▼────────────────────────────────────────────┐
│                      DATA LAYER (Supabase)                               │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐  │
│  │              PostgreSQL Database                                │  │
│  │                                                                 │  │
│  │  • Users & Organizations                                       │  │
│  │  • Documents & Analysis Results                                │  │
│  │  • Agent Outputs & Embeddings                                  │  │
│  │  • Conflict Records & Recommendations                          │  │
│  └─────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐  │
│  │              Vector Storage (pgvector)                          │  │
│  │  • Document embeddings                                         │  │
│  │  • Semantic search                                             │  │
│  └─────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐  │
│  │              Auth & Storage                                    │  │
│  │  • Supabase Auth (JWT)                                         │  │
│  │  • File Storage (Documents)                                    │  │
│  └─────────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## 3. System Data Flow

### 3.1 Request → Processing → Output

```
┌─────────────────────────────────────────────────────────────────────┐
│ STEP 1: DOCUMENT UPLOAD & VALIDATION                                │
├─────────────────────────────────────────────────────────────────────┤
│ • User uploads PRD, Design Doc, Code Summary                        │
│ • Frontend validates file types (PDF, DOCX, TXT)                    │
│ • Files sent to backend with analysis_id                           │
│ • Files stored in Supabase Storage                                 │
└────────────────────┬────────────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────────────┐
│ STEP 2: DOCUMENT PROCESSING                                         │
├────────────────────────────────────────────────────────────────────┤
│ • Extract text from files                                          │
│ • Chunk text (sliding window: 512 tokens, 256 overlap)            │
│ • Create embeddings (OpenAI/local model)                          │
│ • Store in pgvector for semantic search                           │
│ • Save raw text to database                                       │
└────────────────────┬────────────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────────────┐
│ STEP 3: MASTER ORCHESTRATOR INITIALIZATION                         │
├────────────────────────────────────────────────────────────────────┤
│ • Create analysis session                                          │
│ • Prepare context for each agent                                  │
│ • Initialize agent queues                                         │
│ • Broadcast "analysis_started" to client                          │
└────────────────────┬────────────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────────────┐
│ STEP 4: PARALLEL AGENT EXECUTION                                   │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐ │
│  │  PRD AGENT       │  │  DEV AGENT       │  │ DESIGN AGENT     │ │
│  ├──────────────────┤  ├──────────────────┤  ├──────────────────┤ │
│  │ Analyzes:        │  │ Analyzes:        │  │ Analyzes:        │ │
│  │ • User stories   │  │ • Architecture   │  │ • Components     │ │
│  │ • Requirements   │  │ • Dependencies   │  │ • Interactions   │ │
│  │ • Flows          │  │ • Patterns       │  │ • Flows          │ │
│  │ • Acceptance     │  │ • Data models    │  │ • Accessibility  │ │
│  │   criteria       │  │ • APIs           │  │ • States         │ │
│  │                  │  │ • Error handling │  │                  │ │
│  │ Returns JSON     │  │ Returns JSON     │  │ Returns JSON     │ │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘ │
│                                                                    │
└────────────────────┬───────────────────────────────────────────────┘
                     │
┌────────────────────▼───────────────────────────────────────────────┐
│ STEP 5: CONSISTENCY ANALYSIS                                       │
├───────────────────────────────────────────────────────────────────┤
│ Master Orchestrator receives all agent outputs:                   │
│ • Compare extracted features across agents                        │
│ • Identify missing requirements                                   │
│ • Find contradictions in specifications                           │
│ • Map coverage between layers (PRD → Design → Dev)              │
│ • Validate tech stack alignment                                  │
│ • Generate confidence scores (0-100%)                            │
└────────────────────┬───────────────────────────────────────────────┘
                     │
┌────────────────────▼───────────────────────────────────────────────┐
│ STEP 6: CONFLICT DETECTION & RECOMMENDATIONS                      │
├───────────────────────────────────────────────────────────────────┤
│ Conflict Types:                                                   │
│ • MISSING_FEATURE: Feature in PRD not in Design/Dev              │
│ • CONTRADICTING: Different implementations across layers         │
│ • INCOMPLETE_SPEC: Unclear requirements                          │
│ • TECH_MISMATCH: Design/Dev doesn't match PRD tech choices       │
│                                                                  │
│ Each conflict includes:                                          │
│ • Type & severity (HIGH/MEDIUM/LOW)                             │
│ • Location in documents                                         │
│ • Suggested resolution                                          │
│ • References from all documents                                 │
└────────────────────┬───────────────────────────────────────────────┘
                     │
┌────────────────────▼───────────────────────────────────────────────┐
│ STEP 7: RESULT AGGREGATION & STORAGE                              │
├───────────────────────────────────────────────────────────────────┤
│ Store in database:                                               │
│ • Analysis record with metadata                                  │
│ • Individual agent outputs                                       │
│ • Conflict list with resolutions                                │
│ • Consistency score                                             │
│ • Execution timestamps & performance metrics                    │
└────────────────────┬───────────────────────────────────────────────┘
                     │
┌────────────────────▼───────────────────────────────────────────────┐
│ STEP 8: CLIENT NOTIFICATION & DISPLAY                             │
├───────────────────────────────────────────────────────────────────┤
│ • WebSocket: Push final results to client                        │
│ • Display consistency score (0-100%)                            │
│ • Show conflict list with severity                             │
│ • Highlight problem areas in documents                         │
│ • Display recommendations                                       │
│ • Allow manual conflict resolution                             │
└───────────────────────────────────────────────────────────────────┘
```

---

## 4. API Architecture

### 4.1 RESTful Endpoints

```
Authentication
├── POST   /api/auth/register
├── POST   /api/auth/login
├── POST   /api/auth/logout
└── POST   /api/auth/refresh-token

Organizations
├── GET    /api/orgs
├── POST   /api/orgs
├── GET    /api/orgs/{org_id}
└── PATCH  /api/orgs/{org_id}

Documents & Analysis
├── POST   /api/analysis/create              (Create new analysis session)
├── POST   /api/analysis/{id}/upload         (Upload documents)
├── GET    /api/analysis/{id}                (Get analysis status & results)
├── GET    /api/analysis/{id}/results        (Get detailed results)
├── GET    /api/analysis/{id}/conflicts      (Paginated conflicts list)
├── PATCH  /api/analysis/{id}/conflict/{cid} (Resolve/update conflict)
├── GET    /api/analysis/history             (List past analyses)
└── DELETE /api/analysis/{id}                (Archive analysis)

Agent Outputs
├── GET    /api/analysis/{id}/agent/{name}   (PRD/Dev/Design agent output)
└── GET    /api/analysis/{id}/master-report  (Master orchestrator summary)

Recommendations
├── GET    /api/analysis/{id}/recommendations
└── POST   /api/analysis/{id}/apply-recommendation

Export & Reports
├── GET    /api/analysis/{id}/export?format=pdf|json
└── POST   /api/analysis/{id}/generate-report
```

### 4.2 WebSocket Events

```
Client → Server
├── "start_analysis"         → Begin multi-agent processing
├── "cancel_analysis"        → Stop running analysis
├── "resolve_conflict"       → User conflict resolution
└── "request_update"         → Regenerate specific agent output

Server → Client
├── "analysis_started"       → Processing initiated
├── "agent_started"          → Agent begins work
├── "agent_progress"         → {agent: "prd", completion: 45}
├── "agent_complete"         → {agent: "prd", output: {...}}
├── "analysis_complete"      → Full results ready
├── "conflicts_detected"     → {conflicts: [...], severity: "HIGH"}
├── "error"                  → Error notification
└── "analysis_cancelled"     → Processing stopped
```

### 4.3 Request/Response Examples

**Create Analysis Session:**
```json
POST /api/analysis/create

Request:
{
  "org_id": "org_123",
  "title": "Q2 Mobile App Review",
  "description": "Consistency check for mobile app PRD, design, and code"
}

Response:
{
  "analysis_id": "ana_789",
  "status": "created",
  "org_id": "org_123",
  "created_at": "2026-04-29T10:30:00Z",
  "upload_url": "https://supabase.../upload/ana_789"
}
```

**Upload Documents:**
```json
POST /api/analysis/{analysis_id}/upload

Request:
{
  "files": [
    {"name": "PRD.pdf", "type": "pdf", "doc_type": "prd"},
    {"name": "Design.docx", "type": "docx", "doc_type": "design"},
    {"name": "code_summary.txt", "type": "txt", "doc_type": "code"}
  ]
}

Response:
{
  "analysis_id": "ana_789",
  "uploaded_documents": [
    {"id": "doc_1", "name": "PRD.pdf", "status": "processed"},
    {"id": "doc_2", "name": "Design.docx", "status": "processed"},
    {"id": "doc_3", "name": "code_summary.txt", "status": "processed"}
  ],
  "ready_for_analysis": true
}
```

**Get Analysis Results:**
```json
GET /api/analysis/{analysis_id}/results

Response:
{
  "analysis_id": "ana_789",
  "status": "complete",
  "consistency_score": 72,
  "total_conflicts": 8,
  "conflict_summary": {
    "HIGH": 2,
    "MEDIUM": 4,
    "LOW": 2
  },
  "agent_summaries": {
    "prd_agent": {"features": 24, "users": 5, "flows": 12},
    "dev_agent": {"components": 18, "apis": 8, "dependencies": 14},
    "design_agent": {"screens": 16, "interactions": 32, "states": 24}
  },
  "key_conflicts": [
    {
      "id": "conf_1",
      "type": "MISSING_FEATURE",
      "severity": "HIGH",
      "title": "Offline Mode not implemented",
      "description": "PRD specifies offline capability but not in design or code",
      "prd_ref": "Section 3.2",
      "design_ref": "Not mentioned",
      "dev_ref": "Not implemented",
      "resolution": "Add offline support to design and implementation"
    }
  ],
  "processed_at": "2026-04-29T10:45:30Z",
  "processing_time_ms": 45000
}
```

---

## 5. Agent Communication Flow

### 5.1 Multi-Agent Orchestration Pattern

```
┌──────────────────────────────────────────────────────────────────┐
│                    MASTER ORCHESTRATOR                            │
│                                                                  │
│  Responsibilities:                                              │
│  • Initialize agent pool                                        │
│  • Distribute document context                                  │
│  • Collect outputs                                              │
│  • Trigger consistency checks                                   │
│  • Generate final report                                        │
└────────┬─────────────────┬──────────────────┬────────────────────┘
         │                 │                  │
    ┌────▼────┐       ┌────▼────┐       ┌────▼────┐
    │ PRD     │       │ DEV     │       │ DESIGN  │
    │ AGENT   │       │ AGENT   │       │ AGENT   │
    └─────────┘       └─────────┘       └─────────┘
         │                 │                  │
         └────────┬────────┴────────┬─────────┘
                  │                 │
           ┌──────▼────────────────▼──────┐
           │  CONSISTENCY ANALYZER        │
           │  • Cross-reference outputs   │
           │  • Detect gaps & conflicts   │
           │  • Generate recommendations  │
           └──────┬──────────────────────┘
                  │
           ┌──────▼──────────────────────┐
           │  RESULTS STORE              │
           │  • Save to database         │
           │  • Send to client via WS    │
           └─────────────────────────────┘
```

### 5.2 Agent Interaction Sequence

```
Sequence: Analysis Request → Agent Processing → Results

Time  │ Orchestrator    │ PRD Agent  │ Dev Agent  │ Design Agent
──────┼─────────────────┼────────────┼────────────┼────────────────
0ms   │ INIT
      │ ├─ Load docs   
      │ ├─ Create CTX
      │ └─ Send queues
      │
10ms  │                │ START      │            │
      │                │ Processing │            │
      │                │            │ START      │
      │                │            │ Processing │
      │                │            │            │ START
      │                │            │            │ Processing
      │
100ms │ ◄── Progress   
      │    45%
      │
200ms │                │ ◄── All    │
      │                │    Features│
      │                │    Extracted
      │                │            │ ◄── Code   │
      │                │            │    Parsed
      │                │            │            │ ◄── Design
      │                │            │            │    Specs
      │
250ms │ Check → All outputs received
      │ 
      │ Begin: Consistency analysis
      │ • Cross-reference features
      │ • Identify gaps
      │ • Find conflicts
      │
300ms │ Generate: Conflicts list
      │ Store: Results in DB
      │ Notify: Client
      │
[Results ready for display]
```

### 5.3 Agent Output Contract

Each agent returns a standardized JSON structure:

```json
{
  "agent_name": "prd_agent",
  "analysis_id": "ana_789",
  "status": "success",
  "timestamp": "2026-04-29T10:45:15Z",
  "processing_time_ms": 12500,
  
  "metadata": {
    "document_id": "doc_1",
    "document_name": "PRD.pdf",
    "model": "gpt-4",
    "confidence": 0.92
  },
  
  "extracted_data": {
    "features": [
      {
        "id": "feat_1",
        "name": "User Authentication",
        "description": "OAuth2 with Google & GitHub",
        "priority": "HIGH",
        "acceptance_criteria": ["Must support OAuth2", "..."],
        "related_features": ["feat_2", "feat_3"]
      }
    ],
    
    "user_personas": [
      {
        "id": "user_1",
        "name": "Developer",
        "goals": ["Quick setup", "Customization"],
        "pain_points": ["Complexity", "Setup time"]
      }
    ],
    
    "user_flows": [
      {
        "flow_id": "flow_1",
        "name": "Signup Flow",
        "steps": ["Visit site", "Click signup", "..."],
        "variations": ["Social OAuth", "Email signup"]
      }
    ],
    
    "requirements": {
      "functional": ["Feature list"],
      "non_functional": ["Performance", "Security"]
    }
  },
  
  "embeddings": {
    "feature_embeddings": [...],
    "summary_embedding": [...]
  },
  
  "quality_score": {
    "clarity": 0.85,
    "completeness": 0.78,
    "consistency": 0.88,
    "overall": 0.84
  },
  
  "warnings": [
    {
      "type": "AMBIGUOUS_REQUIREMENT",
      "location": "Section 3.2",
      "message": "Performance requirements not quantified"
    }
  ]
}
```

---

## 6. Database Schema Overview

### 6.1 Core Tables

```sql
-- Users & Organizations
CREATE TABLE organizations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(255) NOT NULL,
  description TEXT,
  created_by UUID NOT NULL REFERENCES auth.users(id),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  plan VARCHAR(50) NOT NULL, -- free, pro, enterprise
  status VARCHAR(50) DEFAULT 'active' -- active, paused, archived
);

CREATE TABLE organization_members (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES auth.users(id),
  role VARCHAR(50) NOT NULL, -- admin, editor, viewer
  created_at TIMESTAMP DEFAULT NOW()
);

-- Analysis Sessions
CREATE TABLE analyses (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  title VARCHAR(500) NOT NULL,
  description TEXT,
  status VARCHAR(50) DEFAULT 'created', -- created, processing, complete, error
  consistency_score INT, -- 0-100
  created_by UUID NOT NULL REFERENCES auth.users(id),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  started_at TIMESTAMP,
  completed_at TIMESTAMP,
  error_message TEXT
);

-- Documents
CREATE TABLE documents (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  analysis_id UUID NOT NULL REFERENCES analyses(id) ON DELETE CASCADE,
  name VARCHAR(500) NOT NULL,
  doc_type VARCHAR(50) NOT NULL, -- prd, design, code, other
  file_path VARCHAR(1000) NOT NULL,
  file_size INT,
  mime_type VARCHAR(100),
  raw_text TEXT,
  processing_status VARCHAR(50) DEFAULT 'pending', -- pending, processing, complete, error
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Document Chunks (for semantic search)
CREATE TABLE document_chunks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
  chunk_index INT NOT NULL,
  content TEXT NOT NULL,
  embedding vector(1536),
  start_char INT,
  end_char INT,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_chunks_embedding ON document_chunks USING ivfflat (embedding vector_cosine_ops);

-- Agent Outputs
CREATE TABLE agent_outputs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  analysis_id UUID NOT NULL REFERENCES analyses(id) ON DELETE CASCADE,
  agent_name VARCHAR(50) NOT NULL, -- prd_agent, dev_agent, design_agent
  output_json JSONB NOT NULL,
  processing_time_ms INT,
  model_used VARCHAR(100),
  confidence_score FLOAT,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Conflicts & Issues
CREATE TABLE conflicts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  analysis_id UUID NOT NULL REFERENCES analyses(id) ON DELETE CASCADE,
  conflict_type VARCHAR(100) NOT NULL, -- MISSING_FEATURE, CONTRADICTING, INCOMPLETE_SPEC, TECH_MISMATCH
  severity VARCHAR(50) NOT NULL, -- HIGH, MEDIUM, LOW
  title VARCHAR(500) NOT NULL,
  description TEXT NOT NULL,
  affected_agents TEXT[] NOT NULL, -- {prd_agent, dev_agent, design_agent}
  prd_reference TEXT,
  design_reference TEXT,
  dev_reference TEXT,
  suggested_resolution TEXT,
  status VARCHAR(50) DEFAULT 'open', -- open, resolved, ignored
  resolved_by UUID REFERENCES auth.users(id),
  resolved_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Recommendations
CREATE TABLE recommendations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  analysis_id UUID NOT NULL REFERENCES analyses(id) ON DELETE CASCADE,
  conflict_id UUID REFERENCES conflicts(id),
  priority VARCHAR(50) NOT NULL, -- HIGH, MEDIUM, LOW
  title VARCHAR(500) NOT NULL,
  description TEXT NOT NULL,
  action_items TEXT[],
  estimated_effort VARCHAR(50), -- LOW, MEDIUM, HIGH
  applied BOOLEAN DEFAULT FALSE,
  applied_by UUID REFERENCES auth.users(id),
  applied_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Audit Trail
CREATE TABLE audit_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  user_id UUID REFERENCES auth.users(id),
  action VARCHAR(100) NOT NULL,
  resource_type VARCHAR(50) NOT NULL,
  resource_id UUID,
  old_values JSONB,
  new_values JSONB,
  ip_address INET,
  user_agent TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);
```

### 6.2 Vector Search Tables

```sql
-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Stored embeddings for quick semantic search
CREATE TABLE embedding_cache (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  document_chunk_id UUID NOT NULL REFERENCES document_chunks(id),
  embedding vector(1536) NOT NULL,
  embedding_model VARCHAR(100) NOT NULL, -- text-embedding-3-large, etc.
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_embeddings ON embedding_cache USING hnsw (embedding vector_cosine_ops);
```

### 6.3 Performance Indices

```sql
-- Frequently Queried
CREATE INDEX idx_analyses_org_id ON analyses(org_id);
CREATE INDEX idx_analyses_status ON analyses(status);
CREATE INDEX idx_analyses_created_at ON analyses(created_at DESC);

CREATE INDEX idx_documents_analysis_id ON documents(analysis_id);
CREATE INDEX idx_documents_doc_type ON documents(doc_type);

CREATE INDEX idx_conflicts_analysis_id ON conflicts(analysis_id);
CREATE INDEX idx_conflicts_severity ON conflicts(severity);
CREATE INDEX idx_conflicts_status ON conflicts(status);

CREATE INDEX idx_agent_outputs_analysis_id ON agent_outputs(analysis_id);
CREATE INDEX idx_agent_outputs_agent_name ON agent_outputs(agent_name);

CREATE INDEX idx_audit_logs_org_id ON audit_logs(org_id);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at DESC);
```

### 6.4 Sample Query: Find Conflicts for an Analysis

```sql
-- Get all conflicts with severity breakdown
SELECT 
  a.title,
  COUNT(*) as total_conflicts,
  COUNT(CASE WHEN c.severity = 'HIGH' THEN 1 END) as high,
  COUNT(CASE WHEN c.severity = 'MEDIUM' THEN 1 END) as medium,
  COUNT(CASE WHEN c.severity = 'LOW' THEN 1 END) as low
FROM analyses a
LEFT JOIN conflicts c ON a.id = c.analysis_id
WHERE a.id = $1
GROUP BY a.id, a.title;

-- Get specific conflict with full context
SELECT 
  c.id,
  c.title,
  c.conflict_type,
  c.severity,
  c.description,
  c.suggested_resolution,
  d_prd.name as prd_doc,
  d_design.name as design_doc,
  d_code.name as code_doc
FROM conflicts c
LEFT JOIN documents d_prd ON c.prd_reference LIKE CONCAT('%', d_prd.id, '%')
LEFT JOIN documents d_design ON c.design_reference LIKE CONCAT('%', d_design.id, '%')
LEFT JOIN documents d_code ON c.dev_reference LIKE CONCAT('%', d_code.id, '%')
WHERE c.analysis_id = $1 AND c.id = $2;
```

---

## 7. Component Architecture

### 7.1 Frontend Components (Next.js + Tailwind)

```
src/
├── app/
│   ├── page.tsx                     (Landing page)
│   ├── dashboard/                   
│   │   ├── layout.tsx               
│   │   ├── page.tsx                 (Main dashboard)
│   │   ├── analysis/
│   │   │   ├── [id]/
│   │   │   │   ├── page.tsx         (Analysis detail)
│   │   │   │   ├── results.tsx      (Results view)
│   │   │   │   ├── conflicts.tsx    (Conflicts manager)
│   │   │   │   └── recommendations.tsx
│   │   │   └── new/page.tsx         (New analysis form)
│   │   ├── history.tsx              (Past analyses)
│   │   └── settings/
│   │       ├── org.tsx              (Org settings)
│   │       └── team.tsx             (Team management)
│   └── auth/
│       ├── login/page.tsx
│       ├── signup/page.tsx
│       └── callback/page.tsx        (OAuth callback)
│
├── components/
│   ├── layout/
│   │   ├── Header.tsx
│   │   ├── Sidebar.tsx
│   │   └── Footer.tsx
│   ├── forms/
│   │   ├── DocumentUpload.tsx       (Drag & drop upload)
│   │   └── AnalysisForm.tsx
│   ├── analysis/
│   │   ├── AnalysisBoard.tsx        (Real-time progress)
│   │   ├── ConflictCard.tsx         (Conflict display)
│   │   ├── AgentOutputPanel.tsx     (Agent output viewer)
│   │   └── ConsistencyMeter.tsx     (Score visualization)
│   ├── shared/
│   │   ├── Button.tsx
│   │   ├── Modal.tsx
│   │   ├── Badge.tsx
│   │   └── Spinner.tsx
│   └── charts/
│       ├── ConsistencyChart.tsx     (Score breakdown)
│       └── ConflictTimeline.tsx
│
├── hooks/
│   ├── useAnalysis.ts               (Analysis data fetching)
│   ├── useWebSocket.ts              (WS connection)
│   └── useAuth.ts                   (Authentication)
│
├── services/
│   ├── api.ts                       (API client)
│   ├── websocket.ts                 (WebSocket client)
│   ├── supabase.ts                  (Supabase client)
│   └── storage.ts                   (Document upload)
│
├── store/
│   ├── analysisSlice.ts             (Redux slice)
│   ├── authSlice.ts
│   └── store.ts
│
├── types/
│   ├── index.ts                     (TypeScript types)
│   ├── api.ts
│   └── analysis.ts
│
└── utils/
    ├── formatting.ts
    ├── constants.ts
    └── helpers.ts
```

### 7.2 Backend Structure (FastAPI)

```
backend/
├── main.py                          (App entry)
├── config.py                        (Settings & env)
├── requirements.txt
│
├── api/
│   ├── __init__.py
│   ├── routes/
│   │   ├── auth.py                 (Auth endpoints)
│   │   ├── analysis.py             (Analysis endpoints)
│   │   ├── documents.py            (Document upload/storage)
│   │   ├── conflicts.py            (Conflict management)
│   │   ├── recommendations.py      (Recommendations endpoints)
│   │   └── reports.py              (Export/report generation)
│   ├── middleware/
│   │   ├── auth.py                 (JWT middleware)
│   │   ├── cors.py
│   │   └── error_handler.py
│   └── websocket/
│       ├── manager.py              (WebSocket connection manager)
│       └── events.py               (WS event handlers)
│
├── services/
│   ├── __init__.py
│   ├── document_processor.py       (Text extraction, chunking)
│   ├── embedding_service.py        (Vector embeddings)
│   ├── orchestrator.py             (Master orchestrator)
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── base_agent.py           (Base agent class)
│   │   ├── prd_agent.py            (PRD analysis)
│   │   ├── dev_agent.py            (Dev analysis)
│   │   ├── design_agent.py         (Design analysis)
│   │   └── agent_pool.py           (Agent management)
│   ├── analyzer.py                 (Consistency analyzer)
│   ├── conflict_detector.py        (Conflict detection logic)
│   ├── recommendation_engine.py    (Recommendation generation)
│   ├── storage.py                  (File storage ops)
│   ├── cache.py                    (Redis caching)
│   └── supabase_client.py          (DB operations)
│
├── models/
│   ├── __init__.py
│   ├── database.py                 (SQLAlchemy models)
│   ├── schemas.py                  (Pydantic request/response)
│   └── enums.py                    (Enumerations)
│
├── utils/
│   ├── __init__.py
│   ├── logger.py
│   ├── validators.py
│   ├── json_utils.py
│   └── helpers.py
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py                 (Test fixtures)
│   ├── test_api.py
│   ├── test_agents.py
│   ├── test_analyzer.py
│   └── test_services.py
│
└── scripts/
    ├── init_db.py                  (DB initialization)
    └── seed_data.py                (Test data)
```

---

## 8. Technology Decisions & Trade-offs

### 8.1 Frontend: Next.js + Tailwind

**Why:**
- Full-stack capabilities (API routes, middleware)
- Excellent TypeScript support
- Built-in optimization (code splitting, image optimization)
- Server components for better performance
- Integrated testing & deployment tools

**Key Libraries:**
- `zustand` or `redux-toolkit`: State management
- `react-hook-form`: Form handling
- `shadcn/ui`: Pre-built components
- `monaco-editor`: Code/JSON display
- `recharts`: Data visualization

### 8.2 Backend: FastAPI

**Why:**
- High performance (async/await)
- Built-in OpenAPI documentation
- Excellent for ML/AI workloads
- Type hints for auto-validation
- Easy async support for concurrent agent processing

**Key Libraries:**
- `python-multipart`: File uploads
- `py-supabase`: Supabase SDK
- `openai`: LLM API calls
- `langchain`: Agent orchestration
- `pydantic`: Data validation
- `pydantic-settings`: Configuration management
- `python-jose`: JWT handling
- `pdf2image`, `python-docx`, `pypdf`: Document processing

### 8.3 Database: Supabase (PostgreSQL + Auth)

**Why:**
- Managed PostgreSQL (no ops burden)
- Built-in JWT authentication
- Realtime subscriptions (WebSocket)
- pgvector extension (vector search)
- File storage integration
- Row-level security (RLS)

**Key Features Used:**
- PostgreSQL for relational data
- pgvector for semantic search
- Supabase Auth for user management
- Supabase Storage for document uploads
- Realtime for live updates

### 8.4 AI/LLM Integration

**Agent Framework:**
- `langchain` for agent orchestration
- `llama-index` for document indexing
- `openai-api` for GPT-4/3.5

**Why Multi-Agent Approach:**
- Specialized agents focus on specific document types
- Parallel processing (faster results)
- Easier to debug and tune individual agents
- Better separation of concerns
- Easier to swap models per agent

---

## 9. Deployment Architecture

### 9.1 Deployment Stack

```
┌─────────────────────────────────────────┐
│     Vercel (Frontend Hosting)           │
│     • Next.js auto-deployment           │
│     • CDN distribution                  │
│     • Environment-based builds          │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│  Render / Railway (Backend Hosting)     │
│  • FastAPI on managed containers        │
│  • Auto-scaling based on load           │
│  • Environment variable management      │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│    Supabase Cloud (Database & Auth)    │
│    • PostgreSQL instance                │
│    • pgvector enabled                   │
│    • Automatic backups                  │
│    • S3 files storage                   │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│    Pinecone / Milvus (Vector DB Alt)   │
│    • Dedicated vector storage           │
│    • Semantic search optimization       │
│    • Hybrid search capability           │
└─────────────────────────────────────────┘
```

### 9.2 Environment Configuration

```yaml
# .env.local (Frontend)
NEXT_PUBLIC_API_URL=https://api.genai-pce.com
NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=xxx
NEXT_PUBLIC_WS_URL=wss://api.genai-pce.com/ws

# .env (Backend)
ENVIRONMENT=production
DATABASE_URL=postgresql://...
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=xxx
SUPABASE_JWT_SECRET=xxx
OPENAI_API_KEY=sk-xxx
PINECONE_API_KEY=xxx
REDIS_URL=redis://xxx
CORS_ORIGINS=["https://genai-pce.com"]
JWT_ALGORITHM=HS256
JWT_EXPIRY_HOURS=24
```

---

## 10. Security Considerations

### 10.1 Authentication & Authorization

```
Step 1: User Login via OAuth2 (Google/GitHub)
  ↓
Step 2: Supabase Auth token generated
  ↓
Step 3: JWT included in all API requests
  ↓
Step 4: FastAPI middleware validates JWT
  ↓
Step 5: Row-level security (RLS) enforces org-level access
  ↓
Step 6: User can only access org's data
```

### 10.2 Data Protection

- **In Transit**: All APIs use HTTPS/WSS (TLS 1.3)
- **At Rest**: Database encryption enabled in Supabase
- **Storage**: S3 encryption for uploaded files
- **Secrets**: Environment variables managed via Supabase Vault / CI/CD secrets

### 10.3 Rate Limiting & Throttling

```python
# Per-user rate limiting
- API requests: 1000 req/hour
- File uploads: 50MB/day
- Analysis runs: 20 per day (free tier)
- WebSocket connections: 5 concurrent

# Per-IP rate limiting
- Authentication attempts: 10 per 15 minutes
- Public endpoints: 100 req/minute
```

### 10.4 Audit & Logging

```
All actions logged:
- User authentication events
- Document uploads
- Analysis runs
- Conflict resolutions
- Export/download actions
- Admin operations

Stored in: audit_logs table
Retention: 90 days (can be extended)
```

---

## 11. Performance Optimization

### 11.1 Frontend Optimization

```
• Code splitting: Route-based
• Image optimization: Next.js Image component
• State management: Zustand (lightweight)
• Caching: SWR or React Query
• Lazy loading: Intersection Observer API
• WebSocket compression: Enabled
```

### 11.2 Backend Optimization

```
• Async/await: All I/O operations
• Connection pooling: Database & Redis
• Caching: Query results (Redis)
• Batch processing: Document chunks
• Parallel agent execution: Concurrent futures
• Vector search: Indexed with HNSW
• Pagination: All list endpoints
```

### 11.3 Database Optimization

```
• Indexes on frequently queried columns
• Partitioning (future): By analysis date
• Query optimization: EXPLAIN ANALYZE
• Connection pooling: pgBouncer
• Archive old data: Move to cold storage after 1 year
```

### 11.4 Monitoring & Metrics

```
Track:
- API response times (p50, p95, p99)
- Agent processing times per document size
- Database query performance
- WebSocket connection stability
- Error rates and types
- Vector search latency
- Cost per analysis (LLM calls)

Tools: DataDog / New Relic / Custom Prometheus
```

---

## 12. Scalability Roadmap

### Phase 1 (MVP)
- Single FastAPI instance
- Supabase managed DB
- Sequential agent processing (if needed for cost)
- Basic rate limiting

### Phase 2 (Scale to 1000+ users)
- Deploy FastAPI with load balancer
- Redis caching layer
- Parallel agent execution with worker pool
- Separate vector DB (Pinecone)
- Implement advanced rate limiting

### Phase 3 (Enterprise)
- Kubernetes deployment
- Message queue (Celery + RabbitMQ)
- Multi-region database replicas
- Advanced monitoring & alerting
- Custom LLM fine-tuning
- Advanced security & compliance

---

## 13. Development Timeline & Milestones

```
Week 1-2:   Project setup, DB schema, basic API scaffolding
Week 3-4:   Document processing pipeline
Week 5-7:   Agent implementation (one agent at a time)
Week 8-9:   Master orchestrator & consistency analyzer
Week 10-11: Frontend development (dashboard, upload, results display)
Week 12:    Integration testing & bug fixes
Week 13:    Security audit & performance optimization
Week 14:    Deployment & monitoring setup
Week 15+:   Product launch & user feedback iteration
```

---

## 14. Success Metrics

### Key Performance Indicators

1. **System Effectiveness**
   - Conflict detection accuracy: > 90%
   - False positive rate: < 5%
   - Consistency score correlation with actual issues: > 0.85

2. **Performance**
   - Average analysis time: < 60 seconds (3 documents)
   - API response time: < 200ms (p95)
   - Vector search latency: < 100ms

3. **User Adoption**
   - Monthly active users
   - Average analyses per user
   - User retention rate
   - Net promoter score (NPS)

4. **Business**
   - Cost per analysis
   - Revenue per user
   - Customer acquisition cost (CAC)
   - Churn rate

---

## Appendix: Component Responsibilities

| Component | Responsibility |
|-----------|-----------------|
| **Master Orchestrator** | Coordinates agents, aggregates results, triggers analysis |
| **PRD Agent** | Extracts features, user personas, flows, requirements |
| **Dev Agent** | Analyzes code architecture, dependencies, patterns |
| **Design Agent** | Parses design systems, components, interactions |
| **Consistency Analyzer** | Compares outputs, detects conflicts, generates recommendations |
| **Document Processor** | Extracts text, chunks, creates embeddings |
| **WebSocket Manager** | Handles live client connections, broadcasts events |
| **Storage Service** | Manages file uploads/downloads from Supabase |
| **Cache Layer** | Redis caching for DB queries and embeddings |

---

## Conclusion

This architecture provides a scalable, maintainable foundation for the GenAI Product Consistency Engine. The multi-agent approach ensures specialized analysis of each document type, while the master orchestrator creates a unified view of consistency issues. The system is designed for incremental scaling from MVP to enterprise deployment.

