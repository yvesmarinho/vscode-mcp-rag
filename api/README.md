# 🚀 FastAPI Qdrant RAG Server

Centralized API for vector search across multiple projects. **No more individual `server.py` files needed!**

## 🎯 Overview

This FastAPI service provides a **unified RAG (Retrieval-Augmented Generation)** endpoint that:

- ✅ **Serves multiple projects** from one API
- ✅ **Eliminates individual MCP servers** per project  
- ✅ **Centralized document indexing** and search
- ✅ **RESTful API** with automatic OpenAPI docs
- ✅ **Docker-ready** for easy deployment

## 🏗️ Architecture

```
Multiple VS Code Projects
         ↓
    MCP Client (lightweight)
         ↓ HTTP
   FastAPI Server (centralized)
         ↓
   Qdrant Vector Database
```

## 🚀 Quick Start

### 1. Start with Docker Compose (Recommended)

```bash
# Clone and start everything
cd api/
docker-compose up -d

# Check status
docker-compose ps
```

### 2. Manual Setup

```bash
# Navigate to API directory
cd api/

# Start the server (creates venv, installs deps, starts API)
./start.sh
```

### 3. Verify Installation

```bash
# Check API health
curl http://localhost:8000/health

# View interactive docs
open http://localhost:8000/docs
```

## 📚 API Endpoints

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check and status |
| `POST` | `/query` | Search documents semantically |
| `POST` | `/ingest` | Index documents (async) |
| `POST` | `/ingest/sync` | Index documents (wait for completion) |
| `GET` | `/collections` | List all collections |
| `GET` | `/collections/{name}/stats` | Collection statistics |
| `DELETE` | `/collections/{name}` | Delete collection |

### Interactive Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 💻 Usage Examples

### Python Client

```python
from api.client import QdrantRAGClient

# Initialize client
client = QdrantRAGClient("http://localhost:8000")

# Search documents
results = client.query(
    text="how to configure docker",
    collection="project_docs",
    top_k=5
)

# Index new project
client.ingest(
    directory="./my-project",
    collection="my_project_docs",
    project_id="frontend"
)
```

### CLI Usage

```bash
# Search documents
python client.py query "docker configuration" --collection project_docs

# Index directory
python client.py ingest ./docs --collection my_docs --sync

# List collections
python client.py collections
```

### cURL Examples

```bash
# Search documents
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "how to setup authentication",
    "collection": "project_docs",
    "top_k": 3
  }'

# Index documents
curl -X POST "http://localhost:8000/ingest/sync" \
  -H "Content-Type: application/json" \
  -d '{
    "directory": "/path/to/docs",
    "collection": "my_docs",
    "project_id": "backend"
  }'
```

## 🔧 VS Code Integration

### Option 1: Use MCP Client (Recommended)

Create `.vscode/settings.json` in your project:

```json
{
  "continue.configPath": "./continue.config.json"
}
```

Create `continue.config.json`:

```json
{
  "mcpServers": {
    "rag_api": {
      "command": "python",
      "args": ["/path/to/api/mcp_client.py"],
      "env": {
        "FASTAPI_RAG_URL": "http://localhost:8000",
        "QDRANT_COLLECTION": "project_docs"
      }
    }
  }
}
```

### Option 2: Direct HTTP Integration

Configure your VS Code extension to make HTTP requests to the API endpoints.

## ⚙️ Configuration

### Environment Variables

Create `.env` file:

```env
# Qdrant Configuration
QDRANT_URL=http://localhost:6333
# QDRANT_API_KEY=your-api-key

# Embeddings Provider
EMBEDDINGS_PROVIDER=fastembed
MODEL_NAME=BAAI/bge-small-en-v1.5

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# For MCP Client
FASTAPI_RAG_URL=http://localhost:8000
QDRANT_COLLECTION=project_docs
```

### Embedding Providers

#### FastEmbed (Default)
```env
EMBEDDINGS_PROVIDER=fastembed
MODEL_NAME=BAAI/bge-small-en-v1.5
```

#### Sentence Transformers
```env
EMBEDDINGS_PROVIDER=sentence-transformers
MODEL_NAME=all-mpnet-base-v2
```

#### OpenAI
```env
EMBEDDINGS_PROVIDER=openai
OPENAI_API_KEY=sk-your-key
OPENAI_EMBEDDING_MODEL=text-embedding-3-large
```

## 🐳 Docker Deployment

### Development

```bash
docker-compose up -d
```

### Production

```bash
# Build and deploy
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Scale API instances
docker-compose up -d --scale rag-api=3
```

## 📊 Monitoring & Health

### Health Checks

```bash
# API health
curl http://localhost:8000/health

# Qdrant health  
curl http://localhost:6333/collections

# Collection stats
curl http://localhost:8000/collections/project_docs/stats
```

### Logs

```bash
# API logs
docker-compose logs -f rag-api

# Qdrant logs
docker-compose logs -f qdrant
```

## 🔧 Maintenance

### Backup Collections

```bash
# List collections
curl http://localhost:8000/collections

# Export collection (via Qdrant)
curl http://localhost:6333/collections/project_docs/snapshots -X POST
```

### Update Dependencies

```bash
# Update Python packages
pip install -r requirements.txt --upgrade

# Rebuild Docker image
docker-compose build rag-api
```

## 🚀 Migration from Individual MCP Servers

### Before (Per Project)
```
project1/
  ├── mcp/qdrant_rag_server/server.py
  └── .vscode/continue.config.json

project2/
  ├── mcp/qdrant_rag_server/server.py  
  └── .vscode/continue.config.json
```

### After (Centralized)
```
central-api/
  ├── main.py (FastAPI server)
  └── docker-compose.yml

project1/
  └── .vscode/continue.config.json (points to API)

project2/
  └── .vscode/continue.config.json (points to API)
```

### Migration Steps

1. **Start centralized API**:
   ```bash
   cd api/ && docker-compose up -d
   ```

2. **Index existing projects**:
   ```bash
   python client.py ingest /path/to/project1 --collection project1_docs
   python client.py ingest /path/to/project2 --collection project2_docs
   ```

3. **Update VS Code configs** to point to API

4. **Remove individual `server.py` files** 🎉

## 🔍 Troubleshooting

### Common Issues

**API won't start**:
```bash
# Check port conflicts
lsof -i :8000

# Check Qdrant connection
curl http://localhost:6333/collections
```

**No search results**:
```bash
# Check if documents are indexed
curl http://localhost:8000/collections/project_docs/stats

# Re-index if needed
python client.py ingest ./docs --sync
```

**VS Code integration not working**:
```bash
# Test MCP client directly
echo '{"jsonrpc":"2.0","method":"tools/list","id":"1"}' | python mcp_client.py
```

### Getting Help

1. **Check logs**: `docker-compose logs -f`
2. **API docs**: http://localhost:8000/docs
3. **Health check**: http://localhost:8000/health

---

**🎉 Result**: One centralized RAG service for all your projects!