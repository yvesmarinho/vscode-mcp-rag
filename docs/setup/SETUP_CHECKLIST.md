# Setup Checklist

Siga esta lista para ter seu projeto 100% configurado com Qdrant + VS Code.

## Pre-Setup
- [ ] Docker instalado e rodando
- [ ] Python 3.10+ instalado
- [ ] Git clonado/repo setup

## 1. Python Environment
- [ ] `python3 -m venv .venv`
- [ ] `source .venv/bin/activate` (macOS/Linux) ou `.venv\Scripts\activate` (Windows)
- [ ] Verificar que `python` aponta para venv: `which python` deve mostrar `.venv`

## 2. Install MCP Server Dependencies
Escolha UM:
- [ ] **FastEmbed (Recommended):** `make install-fastembed`
- [ ] SentenceTransformers: `make install-sentencetransformers`
- [ ] OpenAI: `make install-openai`

Ou manualmente:
```bash
pip install -r mcp/qdrant_rag_server/requirements.txt
pip install -r mcp/qdrant_rag_server/requirements-fastembed.txt  # ou outro
```

Verify: `python3 -c "from fastembed import TextEmbedding; print('✓')"` (ou equivalente)

## 3. Configure .env
- [ ] Copiar: `cp mcp/qdrant_rag_server/.env.example mcp/qdrant_rag_server/.env`
- [ ] Editar: `mcp/qdrant_rag_server/.env`
  - [ ] `QDRANT_URL=http://localhost:6333`
  - [ ] `EMBEDDINGS_PROVIDER=fastembed` (ou sua escolha)
  - [ ] `MODEL_NAME=BAAI/bge-small-en-v1.5` (se fastembed)

## 4. Start Qdrant
- [ ] Docker running: `docker ps | grep qdrant` ou `docker run ...`
- [ ] Health check: `curl http://localhost:6333/health` → `{"status":"ok"}`

## 5. Create Collection
- [ ] `make create-collection` ou manual script
- [ ] Verify: `curl http://localhost:6333/collections`

## 6. Install VS Code Extensions
- [ ] Python extension: `ms-python.python`
- [ ] Pylance: `ms-python.vscode-pylance`
- [ ] Continue: `Continue.continue`
- [ ] (Optional) Cline: `saoudrizwan.claude-dev`

## 7. Configure MCP Client
Choose ONE:

### Continue
- [ ] Create/edit `~/.continue/config.json`
- [ ] Add MCP server config (see [CONFIGURATION.md](CONFIGURATION.md#continue-extension))
- [ ] Restart VS Code

### Cline
- [ ] Go to Cline settings
- [ ] Add MCP server with same params
- [ ] Test that it detects tools

## 8. Test Integration
- [ ] Open Continue/Cline chat in VS Code
- [ ] Type: `Use the ingest tool to index my project. Include .py and .md files.`
- [ ] Wait for indexing to complete
- [ ] Ask: `What are the main files in this project?`
- [ ] Verify it returns relevant code

## 9. Verify Everything Works
- [ ] `make diagnose` — Full health check
- [ ] `scripts/mcp_test_ingest_report.sh` — Test ingest
- [ ] Check `reports/` for diagnostic outputs

## Troubleshooting

If anything fails:

1. **Read:** [CONFIGURATION.md](CONFIGURATION.md#troubleshooting-configuration)
2. **Run:** `scripts/mcp_qdrant_report.sh` → check `reports/`
3. **Check:** `INTEGRATION.md` → Troubleshooting section

## Quick Commands

```bash
make help                    # Show all commands
make install-fastembed       # Install deps (FastEmbed)
make qdrant-start           # Start Qdrant Docker
make create-collection      # Create Qdrant collection
make diagnose               # Full diagnostics
scripts/mcp_quickstart_report.sh    # Setup plan
```

## Success Indicators

✅ When working correctly:
- Qdrant responds to `curl http://localhost:6333/health`
- Continue/Cline shows "qdrant_rag" tool available
- Ingest completes and shows files indexed
- Queries return relevant code snippets
