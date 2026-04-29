# GenAI Product Consistency Engine - API Reference & Quick Start

## API Quick Reference

### Authentication Endpoints

#### `POST /api/auth/register`
Register a new user with OAuth provider or email.

```json
{
  "email": "user@example.com",
  "password": "secure_password",
  "full_name": "John Doe",
  "organization_name": "Acme Corp"
}
```

Response:
```json
{
  "user_id": "usr_123",
  "auth_token": "eyJhbGc...",
  "organization_id": "org_456",
  "status": "created"
}
```

#### `POST /api/auth/login`
Authenticate user and receive JWT token.

```json
{
  "email": "user@example.com",
  "password": "secure_password"
}
```

Response:
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer",
  "expires_in": 86400,
  "user": {
    "id": "usr_123",
    "email": "user@example.com",
    "full_name": "John Doe",
    "organization_id": "org_456"
  }
}
```

#### `POST /api/auth/refresh-token`
Refresh expired JWT token.

```json
{
  "refresh_token": "eyJhbGc..."
}
```

---

### Analysis Endpoints

#### `POST /api/analysis/create`
Create a new analysis session.

```bash
curl -X POST http://localhost:8000/api/analysis/create \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "org_id": "org_456",
    "title": "Mobile App PRD Review",
    "description": "Consistency check for Q2 mobile product update"
  }'
```

Response:
```json
{
  "analysis_id": "ana_789",
  "status": "created",
  "org_id": "org_456",
  "title": "Mobile App PRD Review",
  "created_at": "2026-04-29T10:30:00Z",
  "upload_url": "https://api.example.com/api/analysis/ana_789/upload"
}
```

#### `POST /api/analysis/{id}/upload`
Upload documents for analysis.

```bash
curl -X POST http://localhost:8000/api/analysis/ana_789/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "files=@PRD.pdf" \
  -F "files=@Design.docx" \
  -F "files=@CodeSummary.txt"
```

Response:
```json
{
  "analysis_id": "ana_789",
  "status": "processing",
  "uploaded_documents": [
    {
      "id": "doc_1",
      "name": "PRD.pdf",
      "type": "prd",
      "size_bytes": 245680,
      "status": "processing"
    },
    {
      "id": "doc_2",
      "name": "Design.docx",
      "type": "design",
      "size_bytes": 156420,
      "status": "processing"
    },
    {
      "id": "doc_3",
      "name": "CodeSummary.txt",
      "type": "code",
      "size_bytes": 45230,
      "status": "processing"
    }
  ]
}
```

#### `GET /api/analysis/{id}`
Get analysis status and summary.

```bash
curl http://localhost:8000/api/analysis/ana_789 \
  -H "Authorization: Bearer $TOKEN"
```

Response:
```json
{
  "analysis_id": "ana_789",
  "status": "complete",
  "org_id": "org_456",
  "title": "Mobile App PRD Review",
  "consistency_score": 72,
  "total_conflicts": 8,
  "conflict_breakdown": {
    "HIGH": 2,
    "MEDIUM": 4,
    "LOW": 2
  },
  "processing_time_ms": 45230,
  "documents": [
    {
      "id": "doc_1",
      "name": "PRD.pdf",
      "type": "prd",
      "status": "processed"
    },
    {
      "id": "doc_2",
      "name": "Design.docx",
      "type": "design",
      "status": "processed"
    },
    {
      "id": "doc_3",
      "name": "CodeSummary.txt",
      "type": "code",
      "status": "processed"
    }
  ],
  "created_at": "2026-04-29T10:30:00Z",
  "started_at": "2026-04-29T10:31:00Z",
  "completed_at": "2026-04-29T10:32:15Z"
}
```

#### `GET /api/analysis/{id}/results`
Get detailed analysis results including conflicts.

```bash
curl http://localhost:8000/api/analysis/ana_789/results \
  -H "Authorization: Bearer $TOKEN"
```

Response:
```json
{
  "analysis_id": "ana_789",
  "status": "complete",
  "consistency_score": 72,
  "agent_summaries": {
    "prd_agent": {
      "status": "success",
      "features_extracted": 24,
      "users_identified": 5,
      "flows_mapped": 12,
      "confidence": 0.92
    },
    "dev_agent": {
      "status": "success",
      "components_identified": 18,
      "apis_found": 8,
      "dependencies": 14,
      "confidence": 0.88
    },
    "design_agent": {
      "status": "success",
      "screens_identified": 16,
      "interactions_mapped": 32,
      "component_states": 24,
      "confidence": 0.85
    }
  },
  "conflicts": [
    {
      "id": "conf_1",
      "type": "MISSING_FEATURE",
      "severity": "HIGH",
      "title": "Offline Mode Not Implemented",
      "description": "PRD specifies offline capability but not found in design or code",
      "affected_agents": ["prd_agent", "design_agent", "dev_agent"],
      "prd_reference": "Section 3.2 - Offline Sync",
      "design_reference": null,
      "dev_reference": null,
      "suggested_resolution": "Add offline mode to design system and implement sync mechanisms",
      "status": "open"
    },
    {
      "id": "conf_2",
      "type": "CONTRADICTING",
      "severity": "MEDIUM",
      "title": "Authentication Method Mismatch",
      "description": "PRD mentions OAuth2, Design specifies JWT tokens, Dev uses session cookies",
      "affected_agents": ["prd_agent", "design_agent", "dev_agent"],
      "prd_reference": "Section 2.1 - Auth System",
      "design_reference": "Authentication Flow Diagram",
      "dev_reference": "auth/handler.ts",
      "suggested_resolution": "Consolidate on OAuth2 as per PRD, update design and implementation",
      "status": "open"
    }
  ],
  "recommendations": [
    {
      "id": "rec_1",
      "priority": "HIGH",
      "title": "Implement Offline Functionality",
      "description": "Add offline caching and sync capabilities as specified in PRD",
      "action_items": [
        "Design offline sync architecture",
        "Implement local storage strategy",
        "Add conflict resolution logic",
        "Test offline transitions"
      ],
      "estimated_effort": "HIGH",
      "applied": false
    }
  ]
}
```

#### `GET /api/analysis/{id}/conflicts`
Get paginated list of conflicts.

```bash
curl "http://localhost:8000/api/analysis/ana_789/conflicts?page=1&limit=10&severity=HIGH" \
  -H "Authorization: Bearer $TOKEN"
```

Response:
```json
{
  "page": 1,
  "limit": 10,
  "total": 8,
  "conflicts": [
    {
      "id": "conf_1",
      "type": "MISSING_FEATURE",
      "severity": "HIGH",
      "title": "Offline Mode Not Implemented",
      "status": "open",
      "created_at": "2026-04-29T10:32:15Z"
    }
  ]
}
```

#### `PATCH /api/analysis/{id}/conflict/{conflict_id}`
Update conflict status or add resolution comment.

```bash
curl -X PATCH http://localhost:8000/api/analysis/ana_789/conflict/conf_1 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "resolved",
    "resolution_notes": "Added offline mode to Q3 roadmap",
    "resolution_type": "DEFERRED"
  }'
```

Response:
```json
{
  "id": "conf_1",
  "status": "resolved",
  "resolved_by": "usr_123",
  "resolved_at": "2026-04-29T14:00:00Z",
  "resolution_notes": "Added offline mode to Q3 roadmap",
  "resolution_type": "DEFERRED"
}
```

#### `GET /api/analysis/{id}/agent/{agent_name}`
Get individual agent output (prd, dev, design).

```bash
curl http://localhost:8000/api/analysis/ana_789/agent/prd \
  -H "Authorization: Bearer $TOKEN"
```

Response:
```json
{
  "agent_name": "prd_agent",
  "analysis_id": "ana_789",
  "status": "success",
  "timestamp": "2026-04-29T10:31:45Z",
  "processing_time_ms": 12500,
  "confidence": 0.92,
  "extracted_data": {
    "features": [
      {
        "id": "feat_1",
        "name": "User Authentication",
        "description": "OAuth2 with Google & GitHub support",
        "priority": "HIGH",
        "acceptance_criteria": [
          "Must support OAuth2",
          "Must support Google provider",
          "Must support GitHub provider",
          "Session timeout after 30 minutes"
        ]
      }
    ],
    "user_personas": [
      {
        "name": "Developer",
        "goals": ["Quick setup", "Customizer ability"],
        "pain_points": ["Complexity", "Setup time"]
      }
    ]
  },
  "quality_score": {
    "clarity": 0.85,
    "completeness": 0.78,
    "consistency": 0.88,
    "overall": 0.84
  }
}
```

#### `GET /api/analysis/{id}/export`
Export analysis results.

```bash
# Export as PDF
curl http://localhost:8000/api/analysis/ana_789/export?format=pdf \
  -H "Authorization: Bearer $TOKEN" \
  --output analysis_report.pdf

# Export as JSON
curl http://localhost:8000/api/analysis/ana_789/export?format=json \
  -H "Authorization: Bearer $TOKEN" \
  --output analysis_report.json
```

#### `GET /api/analysis/history`
Get list of past analyses.

```bash
curl "http://localhost:8000/api/analysis/history?page=1&limit=20" \
  -H "Authorization: Bearer $TOKEN"
```

Response:
```json
{
  "page": 1,
  "limit": 20,
  "total": 45,
  "analyses": [
    {
      "id": "ana_789",
      "title": "Mobile App PRD Review",
      "org_id": "org_456",
      "status": "complete",
      "consistency_score": 72,
      "total_conflicts": 8,
      "created_at": "2026-04-29T10:30:00Z",
      "completed_at": "2026-04-29T10:32:15Z"
    }
  ]
}
```

---

## WebSocket Events

### Connection
```javascript
const ws = new WebSocket('ws://localhost:8000/ws?token=YOUR_JWT_TOKEN');
```

### Client → Server Events

#### `start_analysis`
```json
{
  "event": "start_analysis",
  "analysis_id": "ana_789"
}
```

#### `cancel_analysis`
```json
{
  "event": "cancel_analysis",
  "analysis_id": "ana_789"
}
```

#### `resolve_conflict`
```json
{
  "event": "resolve_conflict",
  "analysis_id": "ana_789",
  "conflict_id": "conf_1",
  "status": "resolved",
  "notes": "Deferred to Q3"
}
```

### Server → Client Events

#### `analysis_started`
```json
{
  "event": "analysis_started",
  "analysis_id": "ana_789",
  "timestamp": "2026-04-29T10:31:00Z"
}
```

#### `agent_started`
```json
{
  "event": "agent_started",
  "agent": "prd_agent",
  "timestamp": "2026-04-29T10:31:05Z"
}
```

#### `agent_progress`
```json
{
  "event": "agent_progress",
  "agent": "prd_agent",
  "completion": 45,
  "step": "extracting_features"
}
```

#### `agent_complete`
```json
{
  "event": "agent_complete",
  "agent": "prd_agent",
  "output": {
    "features": [...],
    "confidence": 0.92
  }
}
```

#### `conflicts_detected`
```json
{
  "event": "conflicts_detected",
  "conflicts": [
    {
      "id": "conf_1",
      "type": "MISSING_FEATURE",
      "severity": "HIGH",
      "title": "Offline Mode"
    }
  ],
  "severity_breakdown": {
    "HIGH": 2,
    "MEDIUM": 4,
    "LOW": 2
  }
}
```

#### `analysis_complete`
```json
{
  "event": "analysis_complete",
  "analysis_id": "ana_789",
  "consistency_score": 72,
  "total_conflicts": 8,
  "processing_time_ms": 45230
}
```

#### `error`
```json
{
  "event": "error",
  "error_code": "AGENT_TIMEOUT",
  "message": "PRD Agent exceeded timeout"
}
```

---

## JavaScript Client Example

```javascript
// Initialize analysis
async function analyzeDocuments() {
  const formData = new FormData();
  formData.append('file', prdFile);
  formData.append('file', designFile);
  formData.append('file', codeFile);
  formData.append('title', 'Q2 Product Review');

  // Create analysis
  const createRes = await fetch('/api/analysis/create', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      org_id: orgId,
      title: 'Q2 Product Review'
    })
  });

  const { analysis_id } = await createRes.json();

  // Upload documents
  const uploadRes = await fetch(`/api/analysis/${analysis_id}/upload`, {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${token}` },
    body: formData
  });

  // Connect WebSocket
  const ws = new WebSocket(
    `ws://localhost:8000/ws?analysis_id=${analysis_id}&token=${token}`
  );

  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    
    if (data.event === 'agent_progress') {
      updateProgressBar(data.agent, data.completion);
    } else if (data.event === 'conflicts_detected') {
      displayConflicts(data.conflicts);
    } else if (data.event === 'analysis_complete') {
      showFinalResults(data.consistency_score, data.total_conflicts);
    }
  };

  // Start analysis
  ws.send(JSON.stringify({
    event: 'start_analysis',
    analysis_id
  }));
}
```

---

## Python Client Example

```python
import asyncio
import aiohttp
import websockets
import json

class PCEClient:
    def __init__(self, api_url, ws_url, token):
        self.api_url = api_url
        self.ws_url = ws_url
        self.token = token
        self.headers = {"Authorization": f"Bearer {token}"}
    
    async def create_analysis(self, org_id, title):
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.api_url}/api/analysis/create",
                headers=self.headers,
                json={"org_id": org_id, "title": title}
            ) as resp:
                return await resp.json()
    
    async def upload_documents(self, analysis_id, files):
        async with aiohttp.ClientSession() as session:
            with aiohttp.MultipartWriter() as mpwriter:
                for file_path in files:
                    with open(file_path, 'rb') as f:
                        mpwriter.append(f.read())
            
            async with session.post(
                f"{self.api_url}/api/analysis/{analysis_id}/upload",
                headers=self.headers,
                data=mpwriter
            ) as resp:
                return await resp.json()
    
    async def listen_to_analysis(self, analysis_id):
        uri = f"{self.ws_url}/ws?analysis_id={analysis_id}&token={self.token}"
        
        async with websockets.connect(uri) as websocket:
            # Start analysis
            await websocket.send(json.dumps({
                "event": "start_analysis",
                "analysis_id": analysis_id
            }))
            
            # Listen for events
            async for message in websocket:
                data = json.loads(message)
                print(f"Event: {data['event']}")
                
                if data['event'] == 'analysis_complete':
                    return data
    
    async def get_results(self, analysis_id):
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.api_url}/api/analysis/{analysis_id}/results",
                headers=self.headers
            ) as resp:
                return await resp.json()

# Usage
async def main():
    client = PCEClient(
        api_url="http://localhost:8000",
        ws_url="ws://localhost:8000",
        token="your-jwt-token"
    )
    
    # Create analysis
    analysis = await client.create_analysis(
        org_id="org_456",
        title="Q2 Product Review"
    )
    analysis_id = analysis["analysis_id"]
    
    # Upload documents
    await client.upload_documents(analysis_id, [
        "PRD.pdf",
        "Design.docx",
        "CodeSummary.txt"
    ])
    
    # Listen to analysis
    final_results = await client.listen_to_analysis(analysis_id)
    print(f"Consistency Score: {final_results['consistency_score']}")
    
    # Get detailed results
    results = await client.get_results(analysis_id)
    print(json.dumps(results, indent=2))

asyncio.run(main())
```

---

## Error Handling

All error responses follow this format:

```json
{
  "error": {
    "code": "INVALID_REQUEST",
    "message": "Invalid file format",
    "details": {
      "field": "file_type",
      "expected": "pdf, docx, or txt",
      "received": "xlsx"
    }
  }
}
```

### Common Error Codes

| Code | Status | Description |
|------|--------|-------------|
| `INVALID_REQUEST` | 400 | Request validation failed |
| `UNAUTHORIZED` | 401 | Missing or invalid token |
| `FORBIDDEN` | 403 | Access denied to resource |
| `NOT_FOUND` | 404 | Resource not found |
| `FILE_TOO_LARGE` | 413 | Upload exceeds size limit |
| `UNSUPPORTED_FORMAT` | 415 | File format not supported |
| `RATE_LIMITED` | 429 | Too many requests |
| `AGENT_TIMEOUT` | 504 | Agent processing timeout |
| `INTERNAL_ERROR` | 500 | Server error |

---

## Rate Limiting

All API endpoints are rate limited:

```
Free Tier:
- API calls: 1000/hour
- File uploads: 20/day (50MB total)
- Analysis runs: 10/day
- Max file size: 50MB
- Concurrent analyses: 1

Pro Tier:
- API calls: 10,000/hour
- File uploads: 100/day (500MB total)
- Analysis runs: 100/day
- Max file size: 500MB
- Concurrent analyses: 5

Enterprise:
- Unlimited with custom SLA
```

Rate limit headers:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1704067200
```

---

## Authentication

### JWT Token Structure

Tokens are valid for 24 hours by default and include:
```json
{
  "sub": "usr_123",
  "org_id": "org_456",
  "email": "user@example.com",
  "iat": 1704010800,
  "exp": 1704097200
}
```

### Bearer Token Usage

All authenticated endpoints require:
```
Authorization: Bearer eyJhbGc...
```

### Refresh Token Flow

```javascript
// Check if token expired
if (isTokenExpired()) {
  const newToken = await refreshToken(refreshToken);
  localStorage.setItem('access_token', newToken);
}
```

---

## Helpful Resources

- **OpenAPI/Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **GitHub Repository**: [link-to-repo]
- **Documentation**: [ARCHITECTURE.md](./ARCHITECTURE.md)
- **Implementation Guide**: [IMPLEMENTATION_GUIDE.md](./IMPLEMENTATION_GUIDE.md)

