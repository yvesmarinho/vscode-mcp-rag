# Configuration Guide

Documentação completa para configurar seu ambiente Qdrant + MCP + VS Code.

## Environment Variables

Crie `.env` em `mcp/qdrant_rag_server/` (copie de `.env.example`):

```properties
# Qdrant Server
QDRANT_URL=http://localhost:6333          # URL do Qdrant
QDRANT_API_KEY=                           # Deixe vazio para local; preencha para cloud
QDRANT_COLLECTION=project_docs            # Nome da coleção

# Embeddings Provider (escolha um)
EMBEDDINGS_PROVIDER=fastembed             # fastembed | sentence-transformers | openai
MODEL_NAME=BAAI/bge-small-en-v1.5         # Depend do provider

# OpenAI (se EMBEDDINGS_PROVIDER=openai)
# OPENAI_API_KEY=sk-...
# OPENAI_EMBEDDING_MODEL=text-embedding-3-small
```

### Embedding Models by Provider

#### FastEmbed (Recommended for CPU)
```
MODEL_NAME=BAAI/bge-small-en-v1.5    # Fast, good quality (384 dims)
MODEL_NAME=BAAI/bge-base-en-v1.5     # Larger model (768 dims)
MODEL_NAME=BAAI/bge-large-en-v1.5    # Largest (1024 dims)
```

#### SentenceTransformers
```
MODEL_NAME=all-MiniLM-L6-v2           # Small, fast (384 dims)
MODEL_NAME=all-mpnet-base-v2          # Medium, good (768 dims)
MODEL_NAME=paraphrase-multilingual-mpnet-base-v2  # Multilingual (768 dims)
```

#### OpenAI
```
OPENAI_EMBEDDING_MODEL=text-embedding-3-small    # Cheap, fast (1536 dims)
OPENAI_EMBEDDING_MODEL=text-embedding-3-large    # Better quality (3072 dims)
```

---

## VS Code Client Configuration

### Continue Extension

1. **Install:** [Continue.continue](https://marketplace.visualstudio.com/items?itemName=Continue.continue)

2. **Configure:** Edit `~/.continue/config.json`:

```json
{
  "models": [
    {
      "title": "GPT-4",
      "provider": "openai",
      "model": "gpt-4"
    }
  ],
  "mcpServers": {
    "qdrant_rag": {
      "command": "python",
      "args": [
        "/absolute/path/to/mcp/qdrant_rag_server/server.py"
      ],
      "env": {
        "QDRANT_URL": "http://localhost:6333",
        "QDRANT_COLLECTION": "project_docs",
        "EMBEDDINGS_PROVIDER": "fastembed",
        "MODEL_NAME": "BAAI/bge-small-en-v1.5"
      }
    }
  }
}
```

**Note:** Use absolute path to `server.py` or ensure it's in PATH.

### Cline Extension

1. **Install:** [Cline](https://marketplace.visualstudio.com/items?itemName=saoudrizwan.claude-dev)

2. **Configure:** In Cline settings → MCP Servers → Add New:
   - **Name:** `qdrant_rag`
   - **Command:** `python`
   - **Arguments:** `["mcp/qdrant_rag_server/server.py"]` or `["/absolute/path/..."]`
   - **Environment:** (same vars as Continue above)

---

## Docker Qdrant Setup

### Option 1: Docker Run (Quick Start)

```bash
docker run -d -p 6333:6333 -p 6334:6334 \
  -v qdrant_storage:/qdrant/storage \
  --name qdrant_local \
  qdrant/qdrant:latest
```

### Option 2: Docker Compose (Recommended)

**File:** `docker/docker-compose.yaml` (already configured in workspace)

**Start:**
```bash
cd docker/
docker-compose up -d
```

**Features in the provided `docker-compose.yaml`:**
- ✅ Health check (auto-detects service availability)
- ✅ Named volume (portable across machines)
- ✅ Optional API key support (`QDRANT_API_KEY` env var)
- ✅ Logging configuration (max 100MB per file, 10 files)
- ✅ Bridge network (self-contained, no external network required)
- ✅ Resource limits (commented; uncomment to enforce CPU/memory caps)

**Environment Variables:**
```bash
# Optional: Enable API key authentication
export QDRANT_API_KEY=your-secure-key-here
docker-compose up -d
```

Or add to `.env` file in `docker/` directory:
```properties
QDRANT_API_KEY=your-secure-key-here
```

**Verify Running:**
```bash
docker-compose ps
# Expected: qdrant | Up X seconds | ...
```

**View Logs:**
```bash
docker-compose logs -f qdrant
```

**Stop:**
```bash
docker-compose down
```

**Stop + Remove Data:**
```bash
docker-compose down -v
```

### Health Check

**Direct HTTP:**
```bash
curl http://localhost:6333/health
# Expected: {"status":"ok"}
```

**Via Docker:**
```bash
docker-compose ps
# Shows "healthy" in STATUS column if health check passes
```

**Monitor Health:**
```bash
while true; do curl -s http://localhost:6333/health | jq .; sleep 5; done
```

### API Access

- **REST API:** http://localhost:6333
- **gRPC:** localhost:6334
- **Web Console (if enabled):** http://localhost:6333/dashboard

### Configuration Details

**Port Mapping:**
| Port | Protocol | Purpose |
|------|----------|---------|
| 6333 | HTTP REST | Main API, admin console |
| 6334 | gRPC | High-performance protocol |
| 6335 | Internal | Cluster communication (not exposed) |

**Storage:**
- Mounted volume: `qdrant_storage` (Docker managed)
- Host location: Docker's default volume storage location
- Persist across restarts: ✅ Yes (automatic)

**Logging:**
- Format: JSON file driver
- Max size: 100MB per file
- Retention: 10 files (1GB total)
- Location: Docker's log storage

---

## Python Setup

### Virtual Environment

```bash
# Create
python3 -m venv .venv

# Activate
source .venv/bin/activate        # macOS/Linux
.venv\Scripts\activate           # Windows

# Deactivate
deactivate
```

### Install MCP Server + Provider

**Option 1: FastEmbed (Recommended)**
```bash
pip install -r mcp/qdrant_rag_server/requirements.txt
pip install -r mcp/qdrant_rag_server/requirements-fastembed.txt
```

**Option 2: SentenceTransformers**
```bash
pip install -r mcp/qdrant_rag_server/requirements.txt
pip install -r mcp/qdrant_rag_server/requirements-sentencetransformers.txt
```

**Option 3: OpenAI**
```bash
pip install -r mcp/qdrant_rag_server/requirements.txt
pip install -r mcp/qdrant_rag_server/requirements-openai.txt
```

### Verify Installation

```bash
python3 -c "from qdrant_client import QdrantClient; print('✓ qdrant-client OK')"
python3 -c "from fastembed import TextEmbedding; print('✓ fastembed OK')"
# or
python3 -c "from sentence_transformers import SentenceTransformer; print('✓ sentence-transformers OK')"
# or
python3 -c "from openai import OpenAI; print('✓ openai OK')"
```

---

## Collection Creation

### Manual Script

```bash
QDRANT_URL=http://localhost:6333 \
QDRANT_COLLECTION=project_docs \
VECTOR_SIZE=384 \
python3 mcp/qdrant_rag_server/qdrant_create_db.py
```

### Via Make

```bash
make create-collection
```

### Vector Sizes by Provider

| Provider | Model | Vector Size |
|----------|-------|-------------|
| FastEmbed | BAAI/bge-small-en-v1.5 | 384 |
| FastEmbed | BAAI/bge-base-en-v1.5 | 768 |
| SentenceTransformers | all-MiniLM-L6-v2 | 384 |
| SentenceTransformers | all-mpnet-base-v2 | 768 |
| OpenAI | text-embedding-3-small | 1536 |
| OpenAI | text-embedding-3-large | 3072 |

---

## Testing MCP Server

### List Available Tools

```bash
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | python3 mcp/qdrant_rag_server/server.py
```

Expected output:
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": [
    {
      "name": "ingest",
      "description": "Indexa arquivos de um diretório no Qdrant com embeddings",
      ...
    },
    {
      "name": "query",
      "description": "Busca semântica de trechos no Qdrant",
      ...
    }
  ]
}
```

### Test Ingest

```bash
scripts/mcp_test_ingest_report.sh --dry-run    # Plan only
scripts/mcp_test_ingest_report.sh              # Real ingest
```

---

## Troubleshooting Configuration

| Issue | Solution |
|-------|----------|
| `QDRANT_URL` not found | Export: `export QDRANT_URL=http://localhost:6333` |
| Wrong embeddings size | Check `VECTOR_SIZE` matches model output; recreate collection |
| MCP server not starting | Check `.env` syntax; ensure deps installed |
| Continue can't find server | Use absolute path in config; check Python is in PATH |
| Ingest is slow | First run downloads model; subsequent runs use cache |

---

## Recommendations

- **For CPU-only:** Use FastEmbed with `BAAI/bge-small-en-v1.5`
- **For quality:** Use SentenceTransformers `all-mpnet-base-v2` or OpenAI
- **For multilingual:** Use `paraphrase-multilingual-mpnet-base-v2`
- **For speed:** Use smaller models (all-MiniLM-L6-v2)
