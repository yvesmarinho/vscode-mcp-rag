# VS Code + Qdrant + MCP Integration Guide

Complete setup guide to use Qdrant for storing and querying project data via VS Code with GitHub Copilot or Continue/Cline extensions.

## Architecture Overview

```
VS Code (with Continue/Cline/Copilot)
    ↓ (calls MCP tools via stdio)
MCP Server (mcp/qdrant_rag_server/server.py)
    ├─ ingest: convert files → chunks → embeddings → Qdrant
    └─ query: convert text → embedding → semantic search in Qdrant
    ↓
Qdrant (Docker container + vector database)
    └─ stores vectors + metadata (file path, chunk content, etc.)
```

## Prerequisites

### 1. Qdrant Container (Docker)

Ensure a Qdrant instance is running locally:

```bash
docker run -p 6333:6333 -p 6334:6334 \
  -v qdrant_storage:/qdrant/storage \
  qdrant/qdrant:latest
```

- **URL:** http://localhost:6333 (default)
- **API Key:** None required for local; generate one for production

Verify health:
```bash
curl http://localhost:6333/health
# Expected: {"status":"ok"}
```

### 2. Python 3.10+ Environment

```bash
# Create venv
python3 -m venv .venv

# Activate
source .venv/bin/activate  # macOS/Linux
# or
.venv\Scripts\activate  # Windows
```

### 3. MCP Server Dependencies

Choose **one** embeddings provider (CPU-only, no GPU required):

#### Option A: FastEmbed (lightweight, recommended)
```bash
pip install -r mcp/qdrant_rag_server/requirements.txt
pip install -r mcp/qdrant_rag_server/requirements-fastembed.txt
```
Set in `.env`: `EMBEDDINGS_PROVIDER=fastembed`

#### Option B: SentenceTransformers (offline, good quality)
```bash
pip install -r mcp/qdrant_rag_server/requirements.txt
pip install -r mcp/qdrant_rag_server/requirements-sentencetransformers.txt
```
Set in `.env`: `EMBEDDINGS_PROVIDER=sentence-transformers`

#### Option C: OpenAI (cloud, requires API key)
```bash
pip install -r mcp/qdrant_rag_server/requirements.txt
pip install -r mcp/qdrant_rag_server/requirements-openai.txt
```
Set in `.env`: `EMBEDDINGS_PROVIDER=openai` + `OPENAI_API_KEY=sk-...`

---

## Configuration

### Step 1: Create Qdrant Collection

Run the collection creation script to initialize Qdrant:

```bash
# Check plan first (no changes)
QDRANT_URL=http://localhost:6333 \
QDRANT_COLLECTION=project_docs \
VECTOR_SIZE=384 \
python3 mcp/qdrant_rag_server/qdrant_create_db.py
```

Expected output:
```
[ok] Coleção 'project_docs' criada.
[info] Status da coleção:
  name: project_docs
  vectors_count: 0
  config: ...
```

### Step 2: Configure MCP Server

Copy and edit `.env` in `mcp/qdrant_rag_server/`:

```bash
cp mcp/qdrant_rag_server/.env.example mcp/qdrant_rag_server/.env
```

Edit `.env`:
```properties
# Qdrant
QDRANT_URL=http://localhost:6333
QDRANT_COLLECTION=project_docs

# Choose provider (FastEmbed recommended for CPU)
EMBEDDINGS_PROVIDER=fastembed
MODEL_NAME=BAAI/bge-small-en-v1.5

# Only if using OpenAI:
# OPENAI_API_KEY=sk-...
```

### Step 3: Configure VS Code Client

#### Option A: Continue Extension

1. Install [Continue extension](https://marketplace.visualstudio.com/items?itemName=Continue.continue)
2. Edit `~/.continue/config.json`:

```json
{
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

#### Option B: Cline Extension

1. Install [Cline extension](https://marketplace.visualstudio.com/items?itemName=saoudrizwan.claude-dev)
2. Configure MCP server in Cline settings (UI or `cline_config.json`):
   - **Command:** `python`
   - **Args:** `["mcp/qdrant_rag_server/server.py"]` (relative or absolute path)
   - **Env:** same as above

#### Option C: Copilot with MCP Support

If using Copilot with MCP support (future versions), register the server in VS Code MCP extension settings.

---

## Usage Workflows

### Workflow 1: Ingest Project Files

1. Open Continue/Cline chat in VS Code
2. Ask the agent to ingest your project:
   ```
   Use the ingest tool to index my project directory starting from the repo root.
   Include Python, Markdown, YAML files. Chunk size: 800 characters.
   ```
3. Agent calls MCP tool `ingest` with parameters:
   ```json
   {
     "directory": "/path/to/project",
     "include_globs": ["**/*.py", "**/*.md", "**/*.yaml"],
     "chunk_size": 800,
     "overlap": 100
   }
   ```
4. Server reads files, generates embeddings (via FastEmbed/OpenAI), upserts to Qdrant
5. Response: `{"files_indexed": 25, "chunks": 150}`

### Workflow 2: Query Project Knowledge

1. In chat, ask a semantic question:
   ```
   What are the main classes and their responsibilities in this project?
   ```
2. Agent calls MCP tool `query`:
   ```json
   {
     "text": "main classes and responsibilities",
     "top_k": 5
   }
   ```
3. Server embeds query, searches Qdrant, returns relevant chunks:
   ```json
   {
     "hits": [
       {
         "score": 0.92,
         "path": "src/models.py",
         "text": "class ProjectManager: ..."
       },
       ...
     ]
   }
   ```
4. Agent uses results to answer your question

### Workflow 3: Reindex on Changes

1. After editing code, ask agent:
   ```
   Reindex the project files to capture my recent changes.
   ```
2. Agent re-calls `ingest` (idempotent; overwrites old embeddings)
3. New code is now searchable

---

## Helper Scripts

### Diagnostic Report
```bash
scripts/mcp_qdrant_report.sh
```
Generates a report with Qdrant health, collections, Python version, and suggested fixes. Output saved to `reports/mcp_qdrant_report_*.md`.

### Dependency Installer with Report
```bash
# Check plan without installing
scripts/mcp_install_deps_report.sh fastembed --check

# Install base + FastEmbed
scripts/mcp_install_deps_report.sh fastembed

# Or with SentenceTransformers
scripts/mcp_install_deps_report.sh sentence-transformers

# Or with OpenAI
scripts/mcp_install_deps_report.sh openai
```
Output: plan + installation results, saved to `reports/mcp_install_deps_*.md`.

---

## Troubleshooting

### Import Errors in MCP Server

**Error:** `ModuleNotFoundError: No module named 'sentence_transformers'`

**Solution:** Install the chosen embeddings provider:
```bash
pip install -r mcp/qdrant_rag_server/requirements-fastembed.txt
# OR
pip install -r mcp/qdrant_rag_server/requirements-sentencetransformers.txt
# OR
pip install -r mcp/qdrant_rag_server/requirements-openai.txt
```

### Qdrant Connection Refused

**Error:** `ConnectionError: Failed to connect to Qdrant at http://localhost:6333`

**Solution:**
1. Verify Docker container is running: `docker ps | grep qdrant`
2. Check health: `curl http://localhost:6333/health`
3. If not running: `docker run -p 6333:6333 qdrant/qdrant:latest`

### Agent Can't Call MCP Tools

**Symptoms:** Chat says "tool not available" or "MCP server not responding"

**Fixes:**
1. Verify MCP command in client config points to correct Python + file path
2. Test server manually: `python mcp/qdrant_rag_server/server.py` (should accept stdin)
3. Check Python venv is activated in client config (may need full `/path/to/.venv/bin/python`)
4. Run diagnostic: `scripts/mcp_qdrant_report.sh` and review output

### Slow Embeddings

**Symptom:** Ingest takes a long time on first run

**Expected:** FastEmbed downloads model on first use (~50MB); subsequent calls are cached. SentenceTransformers similar.

**Optimize:** Use smaller models or increase batch size in `server.py` (line `batch_size=32`).

---

## Key Files Reference

| File | Purpose |
|------|---------|
| `mcp/qdrant_rag_server/server.py` | MCP server (ingest/query tools) |
| `mcp/qdrant_rag_server/qdrant_create_db.py` | Collection creation script |
| `mcp/qdrant_rag_server/.env` | Configuration (QDRANT_URL, provider, etc.) |
| `mcp/qdrant_rag_server/requirements.txt` | Base dependencies (qdrant-client) |
| `mcp/qdrant_rag_server/requirements-fastembed.txt` | FastEmbed provider |
| `mcp/qdrant_rag_server/requirements-sentencetransformers.txt` | SentenceTransformers provider |
| `mcp/qdrant_rag_server/requirements-openai.txt` | OpenAI provider |
| `scripts/mcp_qdrant_report.sh` | Diagnostic/health check |
| `scripts/mcp_install_deps_report.sh` | Dependency installer |

---

## Imperative Directives

Per project policy:
- **No auto-execution:** Scripts are generated; you choose when and how to run them (via shell).
- **Report-based:** All scripts produce detailed reports saved to `reports/` for audit trail.
- **No secrets in output:** API keys/sensitive values never printed; only "set" / "not set" status.
- **Idempotent:** Rerunning scripts is safe (no duplicate inserts, etc.).

---

## Next Steps

1. **Quick Start:**
   - Ensure Qdrant container is running
   - Run: `scripts/mcp_install_deps_report.sh fastembed --check`
   - Run: `QDRANT_URL=http://localhost:6333 python3 mcp/qdrant_rag_server/qdrant_create_db.py`
   - Configure client (Continue/Cline)
   - Test: ask agent to ingest a small directory

2. **Production:**
   - Use QDRANT_API_KEY for remote/shared Qdrant
   - Consider larger embedding models if quality matters
   - Monitor collection size and prune old embeddings if needed

3. **Feedback:**
   - Check `reports/` for diagnostic outputs
   - Adjust `VECTOR_SIZE`, `MODEL_NAME`, chunk settings based on results
