# Quick Start: 5 Minutos para Usar Qdrant com VS Code

Um guia rápido para ativar a indexação vetorial do seu projeto no VS Code.

## O Que Você Vai Fazer

1. ✅ Inicializar Qdrant (Docker)
2. ✅ Instalar dependências Python
3. ✅ Configurar client MCP (Continue/Cline)
4. ✅ Indexar projeto
5. ✅ Conversar com seu agent sobre o código

**Tempo: ~5 minutos** (primeira vez; depois é só chat)

---

## 1️⃣ Ensure Qdrant is Running

```bash
docker run -d -p 6333:6333 -p 6334:6334 \
  -v qdrant_storage:/qdrant/storage \
  --name qdrant_local \
  qdrant/qdrant:latest

# Verify
curl http://localhost:6333/health
# Expected: {"status":"ok"}
```

---

## 2️⃣ Set Up Python Environment

```bash
# Create venv (one-time)
python3 -m venv .venv

# Activate
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate  # Windows

# Install MCP server + FastEmbed (lightweight, CPU-friendly)
pip install -r mcp/qdrant_rag_server/requirements.txt
pip install -r mcp/qdrant_rag_server/requirements-fastembed.txt
```

**Alternatively, use the installer script:**
```bash
scripts/mcp_install_deps_report.sh fastembed
# Generates report in reports/mcp_install_deps_*.md
```

---

## 3️⃣ Create Qdrant Collection

```bash
QDRANT_URL=http://localhost:6333 \
QDRANT_COLLECTION=project_docs \
VECTOR_SIZE=384 \
python3 mcp/qdrant_rag_server/qdrant_create_db.py

# Expected output:
# [ok] Coleção 'project_docs' criada.
```

---

## 4️⃣ Configure Your VS Code Client

### Option A: Continue Extension (Recommended)

1. Install [Continue](https://marketplace.visualstudio.com/items?itemName=Continue.continue)
2. Open `~/.continue/config.json` and add:

```json
{
  "mcpServers": {
    "qdrant_rag": {
      "command": "python",
      "args": [
        "mcp/qdrant_rag_server/server.py"
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

3. Restart VS Code

### Option B: Cline Extension

1. Install [Cline](https://marketplace.visualstudio.com/items?itemName=saoudrizwan.claude-dev)
2. Go to Cline settings → MCP Servers → Add:
   - **Name:** `qdrant_rag`
   - **Command:** `python`
   - **Args:** `["mcp/qdrant_rag_server/server.py"]`
   - **Env:** (same as above)

---

## 5️⃣ Test It!

In VS Code, open **Continue** or **Cline** chat and ask:

```
Use the ingest tool to index my project. Include .py, .md, .yaml files.
```

Agent will ingest files → index them in Qdrant → done ✨

Now ask:

```
What are the main classes and functions in this project?
```

Agent searches Qdrant → returns relevant code → answers your question 🎉

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError: No module named 'fastembed'` | Run: `pip install -r mcp/qdrant_rag_server/requirements-fastembed.txt` |
| `ConnectionError: Failed to connect to Qdrant` | Check: `curl http://localhost:6333/health` |
| Client can't find MCP server | Verify command path is correct; use absolute path if needed |
| Ingest is slow (first time) | Normal: FastEmbed downloads model (~50MB) on first use |

---

## Next Steps

- **More control?** Read `INTEGRATION.md` for detailed setup and configurations
- **Diagnose issues?** Run: `scripts/mcp_qdrant_report.sh`
- **Test workflow?** Run: `scripts/mcp_test_ingest_report.sh --dry-run`

---

## What's Happening Behind the Scenes

```
You (VS Code)
  ↓ (chat message: "ingest project")
Continue/Cline Agent
  ↓ (calls MCP tool: ingest)
MCP Server (server.py)
  ├─ Reads project files
  ├─ Splits into chunks
  ├─ Generates embeddings (FastEmbed)
  └─ Uploads vectors to Qdrant
  ↓
Qdrant (localhost:6333)
  └─ Stores searchable index
  
Later: You ask "What is class X?"
  ↓
Agent calls query tool
  ↓
MCP searches Qdrant
  ↓
Returns relevant code + context
  ↓
Agent answers your question
```

---

**Ready?** Start with Step 1 above! 🚀
