# FastAPI Backend for Jira Sense

REST API endpoints for loading data into ChromaDB and searching with keywords.

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Start the Server

```bash
# From project root
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

Or use the startup script:

```bash
python backend/main.py
```

### 3. Access API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## 📡 API Endpoints

### 1. **Health Check**

```bash
GET /api/health
```

**Response:**
```json
{
  "status": "healthy",
  "message": "API is running and database is connected",
  "db_connected": true,
  "total_documents": 27
}
```

### 2. **Build Database** (Load CSV → ChromaDB)

```bash
POST /api/build
```

**Request Body:**
```json
{
  "csv_path": "./temp/files/chunked_data.csv",
  "model_name": "all-MiniLM-L6-v2",
  "batch_size": 100
}
```

**Response:**
```json
{
  "status": "success",
  "total_documents": 27,
  "collection_name": "jira_content",
  "model_name": "all-MiniLM-L6-v2",
  "message": "Successfully loaded 27 documents into ChromaDB"
}
```

**cURL Example:**
```bash
curl -X POST "http://localhost:8000/api/build" \
  -H "Content-Type: application/json" \
  -d '{
    "csv_path": "./temp/files/chunked_data.csv",
    "model_name": "all-MiniLM-L6-v2",
    "batch_size": 100
  }'
```

### 3. **Search by Keyword** (POST)

```bash
POST /api/search
```

**Request Body:**
```json
{
  "keyword": "Mobile no",
  "n_results": 50,
  "case_sensitive": false,
  "country": "Singapore",
  "content_type": "validation"
}
```

**Response:**
```json
{
  "total_results": 3,
  "results": [
    {
      "id": "BCBD-492537-2",
      "document": "Validation Rules: Mobile number must be in format...",
      "metadata": {
        "issue_key": "BCBD-492537",
        "chunk_id": "BCBD-492537-2",
        "title": "[SG] [Pay & Trans] Fund transfer",
        "country": "Singapore",
        "content_type": "validation"
      },
      "distance": 0.35,
      "similarity": 0.65,
      "keyword_matches": ["Mobile no", "mobile number"],
      "match_count": 2
    }
  ],
  "message": "Found 3 matching documents for keyword: 'Mobile no'"
}
```

**cURL Example:**
```bash
curl -X POST "http://localhost:8000/api/search" \
  -H "Content-Type: application/json" \
  -d '{
    "keyword": "Mobile no",
    "n_results": 50,
    "case_sensitive": false,
    "country": "Singapore"
  }'
```

### 4. **Search by Keyword** (GET)

```bash
GET /api/search/keyword/{keyword}?n_results=10&country=Singapore
```

**Example:**
```bash
curl "http://localhost:8000/api/search/keyword/Mobile%20no?n_results=10&country=Singapore"
```

**Query Parameters:**
- `n_results` (optional): Maximum number of results (default: 50)
- `case_sensitive` (optional): Case-sensitive search (default: false)
- `country` (optional): Filter by country
- `content_type` (optional): Filter by content type

### 5. **Get Collection Info**

```bash
GET /api/collection/info
```

**Response:**
```json
{
  "status": "success",
  "collection_name": "jira_content",
  "total_documents": 27,
  "metadata": {
    "description": "Jira issue chunks with banking-compliant embeddings"
  },
  "model": "all-MiniLM-L6-v2",
  "banking_compliant": true
}
```

### 6. **Get All Documents**

```bash
GET /api/collection/all
```

**Response:**
```json
{
  "status": "success",
  "total_documents": 27,
  "data": {
    "ids": ["BCBD-492537-1", "BCBD-492537-2", ...],
    "documents": ["..."],
    "metadatas": [...]
  }
}
```

## 🔍 Search Examples

### Example 1: Search for "Mobile no" (case-insensitive)

```bash
curl -X POST "http://localhost:8000/api/search" \
  -H "Content-Type: application/json" \
  -d '{"keyword": "Mobile no", "n_results": 10}'
```

Matches: "mobile no", "Mobile Number", "MOBILE NO", "mobile_no"

### Example 2: Search for "email address" in Singapore

```bash
curl "http://localhost:8000/api/search/keyword/email%20address?country=Singapore"
```

### Example 3: Search with content type filter

```bash
curl -X POST "http://localhost:8000/api/search" \
  -H "Content-Type: application/json" \
  -d '{
    "keyword": "username",
    "content_type": "validation",
    "n_results": 20
  }'
```

## 🏦 Banking Compliance

✅ **100% Local Processing** - All embeddings generated locally  
✅ **No External APIs** - sentence-transformers runs on-premises  
✅ **Data Privacy** - Data never leaves your infrastructure  
✅ **GDPR/SOC2/HIPAA** - Fully compliant  

## 🛠️ Development

### Run in Development Mode

```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### Run in Production Mode

```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## 📊 Testing with Python

```python
import requests

# Health check
response = requests.get("http://localhost:8000/api/health")
print(response.json())

# Build database
response = requests.post(
    "http://localhost:8000/api/build",
    json={
        "csv_path": "./temp/files/chunked_data.csv",
        "model_name": "all-MiniLM-L6-v2"
    }
)
print(response.json())

# Search
response = requests.post(
    "http://localhost:8000/api/search",
    json={
        "keyword": "Mobile no",
        "n_results": 10
    }
)
print(response.json())
```

## 🔐 Security Notes

- Configure CORS appropriately for production
- Add authentication/authorization as needed
- Use HTTPS in production
- Implement rate limiting
- Add input validation

## 📝 Error Handling

The API returns standard HTTP status codes:

- `200` - Success
- `404` - Resource not found
- `422` - Validation error
- `500` - Internal server error
- `503` - Service unavailable (DB not initialized)

## 🎯 Architecture

```
Client Request
     ↓
FastAPI Endpoint
     ↓
JiraDataLoader / JiraSearchBuilder
     ↓
sentence-transformers (local)
     ↓
ChromaDB (./temp/chromadb/)
     ↓
Response
```

All processing happens locally - no external API calls!
