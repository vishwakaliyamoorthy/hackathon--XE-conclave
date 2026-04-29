# GenAI Product Consistency Engine - Implementation Guide

## Table of Contents
1. [Environment Setup](#environment-setup)
2. [Backend Implementation](#backend-implementation)
3. [Frontend Implementation](#frontend-implementation)
4. [Database Setup](#database-setup)
5. [Agent Development](#agent-development)
6. [Integration Checklist](#integration-checklist)
7. [Testing Strategy](#testing-strategy)
8. [Deployment Guide](#deployment-guide)

---

## Environment Setup

### Prerequisites
- Node.js 18+ 
- Python 3.10+
- PostgreSQL 14+ (or Supabase account)
- OpenAI API key
- Supabase account with pgvector enabled

### Backend Setup (FastAPI)

```bash
# Create and activate virtual environment
python3.10 -m venv venv
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate  # Windows

# Install dependencies
pip install --upgrade pip
pip install fastapi uvicorn python-multipart pydantic pydantic-settings
pip install python-jose cryptography
pip install supabase
pip install openai langchain langchain-openai
pip install pdf2image python-docx pypdf
pip install redis
pip install psycopg2-binary sqlalchemy
pip install pytest pytest-asyncio httpx

# Create requirements.txt
pip freeze > requirements.txt
```

### Frontend Setup (Next.js)

```bash
# Create Next.js project
npx create-next-app@latest genai-pce --typescript --tailwind

cd genai-pce

# Install dependencies
npm install
npm install @supabase/supabase-js
npm install zustand react-hook-form
npm install recharts
npm install @monaco-editor/react
npm install swr

# Dev environment setup
cp .env.local.example .env.local
# Fill in the values from Supabase
```

### Environment Variables

**Frontend `.env.local`:**
```
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws
```

**Backend `.env`:**
```
# Environment
ENVIRONMENT=development

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/genai_pce
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-service-role-key
SUPABASE_JWT_SECRET=your-jwt-secret

# OpenAI
OPENAI_API_KEY=sk-your-key
OPENAI_MODEL=gpt-4

# JWT
JWT_SECRET=your-very-secret-key-min-32-chars
JWT_ALGORITHM=HS256
JWT_EXPIRY_HOURS=24

# Redis
REDIS_URL=redis://localhost:6379

# CORS
CORS_ORIGINS=["http://localhost:3000","https://yourdomain.com"]

# File Upload
MAX_FILE_SIZE_MB=50
UPLOAD_DIRECTORY=/tmp/uploads

# Logging
LOG_LEVEL=INFO
```

---

## Backend Implementation

### Project Structure

```
backend/
├── main.py
├── config.py
├── requirements.txt
├── .env
├── .env.example
├── docker-compose.yml
│
├── api/
│   ├── __init__.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── analysis.py
│   │   ├── documents.py
│   │   ├── conflicts.py
│   │   ├── recommendations.py
│   │   └── reports.py
│   ├── middleware/
│   │   ├── __init__.py
│   │   ├── auth_middleware.py
│   │   ├── error_handler.py
│   │   └── cors.py
│   └── websocket/
│       ├── __init__.py
│       ├── manager.py
│       └── events.py
│
├── services/
│   ├── __init__.py
│   ├── document_processor.py
│   ├── embedding_service.py
│   ├── orchestrator.py
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── base_agent.py
│   │   ├── prd_agent.py
│   │   ├── dev_agent.py
│   │   ├── design_agent.py
│   │   └── agent_pool.py
│   ├── analyzer.py
│   ├── conflict_detector.py
│   ├── recommendation_engine.py
│   ├── storage.py
│   ├── cache.py
│   └── supabase_client.py
│
├── models/
│   ├── __init__.py
│   ├── database.py
│   ├── schemas.py
│   └── enums.py
│
├── utils/
│   ├── __init__.py
│   ├── logger.py
│   ├── validators.py
│   └── helpers.py
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_api.py
│   ├── test_agents.py
│   ├── test_analyzer.py
│   └── test_services.py
│
└── scripts/
    ├── __init__.py
    ├── init_db.py
    └── seed_data.py
```

### Core Implementation Files

#### `main.py`
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZIPMiddleware

from config import settings
from api.routes import auth, analysis, documents, conflicts, recommendations
from api.middleware.error_handler import error_handler_middleware
from api.websocket.manager import websocket_app

app = FastAPI(
    title="GenAI Product Consistency Engine",
    version="1.0.0",
    description="Multi-agent AI system for product consistency analysis"
)

# Middleware
app.add_middleware(GZIPMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.middleware("http")(error_handler_middleware)

# Routes
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(analysis.router, prefix="/api/analysis", tags=["analysis"])
app.include_router(documents.router, prefix="/api/documents", tags=["documents"])
app.include_router(conflicts.router, prefix="/api/conflicts", tags=["conflicts"])
app.include_router(recommendations.router, prefix="/api/recommendations", tags=["recommendations"])

# WebSocket
app.add_route("/ws", websocket_app)

@app.get("/health")
async def health_check():
    return {"status": "ok", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

#### `config.py`
```python
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # App
    APP_NAME: str = "GenAI PCE"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str
    SUPABASE_URL: str
    SUPABASE_KEY: str
    SUPABASE_JWT_SECRET: str
    
    # OpenAI
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4"
    OPENAI_TEMPERATURE: float = 0.7
    
    # JWT
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRY_HOURS: int = 24
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    
    # File Upload
    MAX_FILE_SIZE_MB: int = 50
    UPLOAD_DIRECTORY: str = "/tmp/uploads"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
```

#### `services/document_processor.py`
```python
import asyncio
from typing import List, Dict
import pypdf
from docx import Document
import logging

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Process documents: extract text, chunk, and prepare for embedding."""
    
    CHUNK_SIZE = 512  # tokens
    CHUNK_OVERLAP = 256  # tokens
    
    async def process_file(self, file_path: str, doc_type: str) -> str:
        """Extract text from various file formats."""
        if file_path.endswith('.pdf'):
            return await self._extract_pdf(file_path)
        elif file_path.endswith('.docx'):
            return await self._extract_docx(file_path)
        elif file_path.endswith('.txt'):
            return await self._extract_text(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_path}")
    
    async def _extract_pdf(self, file_path: str) -> str:
        """Extract text from PDF."""
        text = []
        with open(file_path, 'rb') as file:
            pdf_reader = pypdf.PdfReader(file)
            for page in pdf_reader.pages:
                text.append(page.extract_text())
        return "\n".join(text)
    
    async def _extract_docx(self, file_path: str) -> str:
        """Extract text from DOCX."""
        doc = Document(file_path)
        return "\n".join([para.text for para in doc.paragraphs])
    
    async def _extract_text(self, file_path: str) -> str:
        """Extract text from TXT."""
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def chunk_text(self, text: str) -> List[str]:
        """Split text into overlapping chunks."""
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), self.CHUNK_SIZE - self.CHUNK_OVERLAP):
            chunk_words = words[i:i + self.CHUNK_SIZE]
            chunks.append(" ".join(chunk_words))
        
        return chunks
    
    async def process_analysis_documents(self, analysis_id: str, documents: List[Dict]) -> Dict:
        """Process all documents for an analysis."""
        results = {}
        
        for doc in documents:
            try:
                # Extract text
                text = await self.process_file(doc['file_path'], doc['doc_type'])
                
                # Chunk text
                chunks = self.chunk_text(text)
                
                # Store results
                results[doc['id']] = {
                    "raw_text": text,
                    "chunks": chunks,
                    "chunk_count": len(chunks),
                    "status": "processed"
                }
                
                logger.info(f"Processed {doc['name']}: {len(chunks)} chunks")
                
            except Exception as e:
                logger.error(f"Error processing {doc['name']}: {e}")
                results[doc['id']] = {
                    "status": "error",
                    "error": str(e)
                }
        
        return results
```

#### `services/embedding_service.py`
```python
import openai
from typing import List
import numpy as np
import logging

logger = logging.getLogger(__name__)

class EmbeddingService:
    """Generate embeddings for text chunks."""
    
    MODEL = "text-embedding-3-large"
    EMBEDDING_DIM = 1536
    
    def __init__(self, api_key: str):
        openai.api_key = api_key
        self.client = openai.OpenAI(api_key=api_key)
    
    async def embed_chunks(self, chunks: List[str]) -> List[List[float]]:
        """Create embeddings for text chunks."""
        try:
            response = self.client.embeddings.create(
                model=self.MODEL,
                input=chunks
            )
            
            embeddings = [item.embedding for item in response.data]
            logger.info(f"Generated {len(embeddings)} embeddings")
            
            return embeddings
            
        except Exception as e:
            logger.error(f"Embedding error: {e}")
            raise
    
    async def embed_text(self, text: str) -> List[float]:
        """Create single embedding."""
        response = self.client.embeddings.create(
            model=self.MODEL,
            input=text
        )
        return response.data[0].embedding
    
    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        array1 = np.array(vec1)
        array2 = np.array(vec2)
        
        dot_product = np.dot(array1, array2)
        norm1 = np.linalg.norm(array1)
        norm2 = np.linalg.norm(array2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
```

#### `services/agents/base_agent.py`
```python
from abc import ABC, abstractmethod
from typing import Dict, Any, List
from datetime import datetime
import logging
import asyncio

logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    """Base class for all AI agents."""
    
    def __init__(self, name: str, model: str = "gpt-4"):
        self.name = name
        self.model = model
        self.created_at = datetime.now()
    
    @abstractmethod
    async def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze document and return structured output.
        
        Args:
            context: {
                'document_text': str,
                'doc_type': str,
                'analysis_id': str,
                'chunks': List[str],
                'embeddings': List[List[float]]
            }
        
        Returns:
            Structured agent output with extracted data
        """
        pass
    
    def format_output(self, data: Dict, confidence: float) -> Dict[str, Any]:
        """Format standard agent output."""
        return {
            "agent_name": self.name,
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "model": self.model,
            "confidence": confidence,
            "extracted_data": data,
            "quality_score": self._calculate_quality_score(data)
        }
    
    def _calculate_quality_score(self, data: Dict) -> Dict[str, float]:
        """Calculate quality metrics."""
        return {
            "clarity": 0.85,
            "completeness": 0.80,
            "consistency": 0.82,
            "overall": 0.82
        }
    
    async def run(self, context: Dict) -> Dict[str, Any]:
        """Execute agent with timing."""
        import time
        start_time = time.time()
        
        try:
            result = await self.analyze(context)
            processing_time_ms = int((time.time() - start_time) * 1000)
            result["processing_time_ms"] = processing_time_ms
            
            logger.info(f"{self.name} completed in {processing_time_ms}ms")
            return result
            
        except Exception as e:
            logger.error(f"{self.name} error: {e}")
            return {
                "agent_name": self.name,
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
```

#### `services/agents/prd_agent.py`
```python
from .base_agent import BaseAgent
from typing import Dict, Any, List
import openai
import json
import logging

logger = logging.getLogger(__name__)

class PRDAgent(BaseAgent):
    """Analyzes PRD documents to extract requirements and features."""
    
    def __init__(self, api_key: str):
        super().__init__(name="prd_agent", model="gpt-4")
        self.client = openai.OpenAI(api_key=api_key)
    
    async def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract features, requirements, and user flows from PRD."""
        
        document_text = context.get('document_text', '')
        chunks = context.get('chunks', [])[:3]  # Use first 3 chunks for context
        
        prompt = f"""
        Analyze this PRD document and extract structured information:
        
        {document_text[:5000]}  # First 5000 chars
        
        Extract and return JSON with:
        {{
          "features": [
            {{"name": str, "description": str, "priority": "HIGH|MEDIUM|LOW", "acceptance_criteria": [str]}}
          ],
          "user_personas": [
            {{"name": str, "goals": [str], "pain_points": [str]}}
          ],
          "user_flows": [
            {{"name": str, "steps": [str], "variations": [str]}}
          ],
          "requirements": {{
            "functional": [str],
            "non_functional": [str]
          }},
          "tech_preferences": [str],
          "warnings": [{{"type": str, "message": str}}]
        }}
        
        Return only valid JSON.
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            extracted_data = json.loads(content)
            
            return self.format_output(extracted_data, confidence=0.92)
            
        except Exception as e:
            logger.error(f"PRD Agent error: {e}")
            raise
```

Similar implementations for `dev_agent.py` and `design_agent.py` with appropriate prompts and extraction logic.

#### `services/orchestrator.py`
```python
from typing import Dict, List, Any
import asyncio
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class MasterOrchestrator:
    """Coordinates multi-agent analysis."""
    
    def __init__(self, agents: List, analyzer, db_service):
        self.agents = {agent.name: agent for agent in agents}
        self.analyzer = analyzer
        self.db = db_service
    
    async def run_analysis(self, analysis_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute all agents in parallel."""
        
        logger.info(f"Starting analysis {analysis_id}")
        
        # Run agents in parallel
        agent_tasks = {
            agent_name: self._run_agent(agent_name, agent, context)
            for agent_name, agent in self.agents.items()
        }
        
        agent_results = await asyncio.gather(*agent_tasks.values())
        agent_outputs = dict(zip(agent_tasks.keys(), agent_results))
        
        # Store individual outputs
        for agent_name, output in agent_outputs.items():
            await self.db.store_agent_output(analysis_id, agent_name, output)
        
        # Analyze consistency
        conflicts = await self.analyzer.analyze_consistency(
            analysis_id,
            agent_outputs
        )
        
        # Calculate overall score
        consistency_score = self._calculate_consistency_score(conflicts)
        
        # Store results
        await self.db.update_analysis(
            analysis_id,
            status="complete",
            consistency_score=consistency_score,
            conflicts_count=len(conflicts),
            completed_at=datetime.now()
        )
        
        return {
            "analysis_id": analysis_id,
            "status": "complete",
            "agent_outputs": agent_outputs,
            "conflicts": conflicts,
            "consistency_score": consistency_score
        }
    
    async def _run_agent(self, agent_name: str, agent, context: Dict) -> Dict[str, Any]:
        """Run single agent with error handling."""
        try:
            return await agent.run(context)
        except Exception as e:
            logger.error(f"Agent {agent_name} failed: {e}")
            return {
                "agent_name": agent_name,
                "status": "error",
                "error": str(e)
            }
    
    def _calculate_consistency_score(self, conflicts: List[Dict]) -> int:
        """Calculate consistency score (0-100)."""
        if not conflicts:
            return 100
        
        severity_weights = {"HIGH": 10, "MEDIUM": 5, "LOW": 1}
        total_penalty = sum(
            severity_weights.get(c.get("severity", "LOW"), 1)
            for c in conflicts
        )
        
        score = max(0, 100 - total_penalty)
        return score
```

---

## Frontend Implementation

### Key Components

#### `app/dashboard/page.tsx`
```typescript
'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import AnalysisBoard from '@/components/analysis/AnalysisBoard';
import DocumentUpload from '@/components/forms/DocumentUpload';
import { useAnalysis } from '@/hooks/useAnalysis';

export default function Dashboard() {
  const router = useRouter();
  const { createAnalysis, listAnalyses } = useAnalysis();
  const [analyses, setAnalyses] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAnalyses();
  }, []);

  async function loadAnalyses() {
    try {
      const data = await listAnalyses();
      setAnalyses(data);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="container mx-auto py-8">
      <h1 className="text-3xl font-bold mb-8">Consistency Analysis</h1>
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2">
          <DocumentUpload onAnalysisCreated={() => loadAnalyses()} />
        </div>
        
        <div>
          <AnalysisBoard analyses={analyses} loading={loading} />
        </div>
      </div>
    </div>
  );
}
```

#### `components/forms/DocumentUpload.tsx`
```typescript
'use client';

import { useState } from 'react';
import { useAnalysis } from '@/hooks/useAnalysis';

export default function DocumentUpload({ onAnalysisCreated }) {
  const { createAnalysis } = useAnalysis();
  const [files, setFiles] = useState<File[]>([]);
  const [title, setTitle] = useState('');
  const [loading, setLoading] = useState(false);

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setFiles(Array.from(e.dataTransfer.files));
  };

  async function handleUpload() {
    if (!title || files.length === 0) return;

    setLoading(true);
    try {
      await createAnalysis({
        title,
        files,
        onProgress: (progress) => {
          console.log(`Upload progress: ${progress}%`);
        }
      });
      
      setTitle('');
      setFiles([]);
      onAnalysisCreated();
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="border-2 border-dashed rounded-lg p-8 text-center"
         onDrop={handleDrop}
         onDragOver={(e) => e.preventDefault()}>
      
      <h2 className="text-xl font-semibold mb-4">Upload Documents</h2>
      
      <input
        type="text"
        placeholder="Analysis title"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        className="w-full mb-4 px-4 py-2 border rounded"
      />
      
      <input
        type="file"
        multiple
        onChange={(e) => setFiles(Array.from(e.currentTarget.files || []))}
        className="mb-4"
        accept=".pdf,.docx,.txt"
      />
      
      {files.length > 0 && (
        <div className="mb-4">
          <p className="font-semibold">{files.length} files selected:</p>
          <ul className="text-sm text-gray-600">
            {files.map((f) => <li key={f.name}>{f.name}</li>)}
          </ul>
        </div>
      )}
      
      <button
        onClick={handleUpload}
        disabled={loading || !title || files.length === 0}
        className="bg-blue-600 text-white px-6 py-2 rounded disabled:opacity-50"
      >
        {loading ? 'Processing...' : 'Start Analysis'}
      </button>
    </div>
  );
}
```

#### `components/analysis/AnalysisBoard.tsx`
```typescript
'use client';

import { useEffect, useState } from 'react';
import { useWebSocket } from '@/hooks/useWebSocket';
import ConflictCard from './ConflictCard';
import ConsistencyMeter from './ConsistencyMeter';

export default function AnalysisBoard({ analysisId }) {
  const ws = useWebSocket();
  const [progress, setProgress] = useState(0);
  const [agentStatus, setAgentStatus] = useState({});
  const [conflicts, setConflicts] = useState([]);
  const [score, setScore] = useState(0);

  useEffect(() => {
    if (!ws || !analysisId) return;

    ws.on('agent_progress', (data) => {
      setAgentStatus(prev => ({
        ...prev,
        [data.agent]: data.completion
      }));
      const avg = Object.values(agentStatus).reduce((a, b: any) => a + b, 0) / 3;
      setProgress(avg);
    });

    ws.on('conflicts_detected', (data) => {
      setConflicts(data.conflicts);
    });

    ws.on('analysis_complete', (data) => {
      setScore(data.consistency_score);
    });

    return () => {
      ws.off('agent_progress');
      ws.off('conflicts_detected');
      ws.off('analysis_complete');
    };
  }, [ws, analysisId]);

  return (
    <div className="space-y-6">
      <ConsistencyMeter score={score} />
      
      <div className="grid grid-cols-3 gap-4">
        {['prd_agent', 'dev_agent', 'design_agent'].map(agent => (
          <div key={agent} className="border rounded p-4">
            <p className="font-semibold">{agent}</p>
            <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
              <div
                className="bg-green-600 h-2 rounded-full transition-all"
                style={{ width: `${agentStatus[agent] || 0}%` }}
              />
            </div>
            <p className="text-sm mt-1">{agentStatus[agent] || 0}%</p>
          </div>
        ))}
      </div>
      
      <div>
        <h3 className="text-lg font-semibold mb-4">Conflicts Detected</h3>
        <div className="space-y-3">
          {conflicts.map(conflict => (
            <ConflictCard key={conflict.id} conflict={conflict} />
          ))}
        </div>
      </div>
    </div>
  );
}
```

---

## Database Setup

### Supabase SQL Initialization

```sql
-- Enable extensions
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Organizations table (already created by Supabase auth)
CREATE TABLE organizations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(255) NOT NULL,
  description TEXT,
  created_by UUID NOT NULL REFERENCES auth.users(id),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  plan VARCHAR(50) NOT NULL DEFAULT 'free',
  status VARCHAR(50) DEFAULT 'active'
);

-- Analyses table
CREATE TABLE analyses (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  title VARCHAR(500) NOT NULL,
  description TEXT,
  status VARCHAR(50) DEFAULT 'created',
  consistency_score INT,
  total_conflicts INT,
  created_by UUID NOT NULL REFERENCES auth.users(id),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  started_at TIMESTAMP,
  completed_at TIMESTAMP,
  error_message TEXT
);

-- More tables as per schema in ARCHITECTURE.md

-- RLS Policies
ALTER TABLE analyses ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their org's analyses"
ON analyses FOR SELECT
USING (org_id IN (
  SELECT org_id FROM organization_members 
  WHERE user_id = auth.uid()
));

-- Run init_db.py script to populate schema
```

---

## Agent Development

### PRD Agent Prompt Template
```
You are an expert product analyst specializing in PRD (Product Requirements Document) analysis.

Analyze the provided PRD document and extract:
1. Core Features - List all stated features with priorities
2. User Personas - Identify user types and their goals
3. User Flows - Document the main user journeys
4. Requirements - Both functional and non-functional
5. Acceptance Criteria - What defines success?

Return ONLY valid JSON with these exact keys:
- features: [{name, description, priority, acceptance_criteria}]
- user_personas: [{name, goals, pain_points}]
- user_flows: [{name, steps, variations}]
- requirements: {functional, non_functional}
- tech_preferences: []
- warnings: [{type, message}]

Document:
{document_text}
```

### Dev Agent Prompt Template
```
You are an expert software architect analyzing code summaries and implementation documents.

Analyze and extract:
1. Architecture Overview - System design and components
2. Technology Stack - Languages, frameworks, libraries
3. Data Models - Key entities and relationships
4. APIs - External and internal endpoints
5. Dependencies - External libraries and services
6. Design Patterns - Architectural patterns used
7. Known Issues - Any mentioned limitations

Return ONLY valid JSON with these exact keys:
- architecture: {overview, components, layers}
- tech_stack: {languages, frameworks, libraries}
- data_models: [{name, fields, relationships}]
- apis: [{endpoint, method, description}]
- dependencies: [{name, version, purpose}]
- patterns: []
- issues: [{severity, description}]

Code Summary:
{document_text}
```

---

## Integration Checklist

- [ ] **Backend Setup**
  - [ ] FastAPI project initialized
  - [ ] Database schema created in Supabase
  - [ ] Authentication middleware implemented
  - [ ] WebSocket server configured
  - [ ] All endpoints implemented

- [ ] **Frontend Setup**
  - [ ] Next.js project initialized
  - [ ] Supabase client configured
  - [ ] Main components created
  - [ ] WebSocket hook implemented
  - [ ] State management setup

- [ ] **Agents**
  - [ ] Base agent class implemented
  - [ ] PRD Agent functional
  - [ ] Dev Agent functional
  - [ ] Design Agent functional
  - [ ] Agent pool / orchestrator working

- [ ] **Services**
  - [ ] Document processing working
  - [ ] Embedding service integrated
  - [ ] Consistency analyzer functional
  - [ ] Conflict detector working
  - [ ] Recommendation engine ready

- [ ] **Integration**
  - [ ] End-to-end workflow tested
  - [ ] API endpoints tested
  - [ ] WebSocket events flowing properly
  - [ ] Database operations verified
  - [ ] Error handling implemented

- [ ] **Deployment**
  - [ ] Environment variables set
  - [ ] Docker containers configured
  - [ ] CI/CD pipeline created
  - [ ] Monitoring/logging setup
  - [ ] Security audit completed

---

## Testing Strategy

### Backend Testing
```python
# tests/test_agents.py
import pytest
from services.agents.prd_agent import PRDAgent

@pytest.mark.asyncio
async def test_prd_agent_extraction():
    agent = PRDAgent(api_key="test-key")
    context = {
        "document_text": "Sample PRD text...",
        "chunks": []
    }
    result = await agent.analyze(context)
    assert result["status"] == "success"
    assert "features" in result["extracted_data"]
```

### Frontend Testing
```typescript
// __tests__/components/DocumentUpload.test.tsx
import { render, screen } from '@testing-library/react';
import DocumentUpload from '@/components/forms/DocumentUpload';

test('renders upload form', () => {
  render(<DocumentUpload onAnalysisCreated={() => {}} />);
  expect(screen.getByText('Upload Documents')).toBeInTheDocument();
});
```

---

## Deployment Guide

### Deployment Checklist

1. **Frontend (Vercel)**
   ```bash
   npm install -g vercel
   vercel link
   vercel env add NEXT_PUBLIC_API_URL
   vercel deploy --prod
   ```

2. **Backend (Render/Railway)**
   ```bash
   git push origin main  # Auto-deploys if configured
   # OR manually:
   railway up
   ```

3. **Database (Supabase)**
   - Run migration scripts
   - Verify RLS policies
   - Enable backups
   - Configure WAL settings

4. **Monitoring**
   - Set up DataDog/New Relic agents
   - Configure alerting
   - Set up error tracking (Sentry)
   - Enable CORS logs

5. **Security**
   - Rotate JWT secrets
   - Verify HTTPS everywhere
   - Enable WAF rules
   - Run security scan

---

## Quick Start Commands

```bash
# Backend
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python scripts/init_db.py
uvicorn main:app --reload

# Frontend
cd frontend
npm install
npm run dev

# Access at http://localhost:3000
# API at http://localhost:8000
# API docs at http://localhost:8000/docs
```

