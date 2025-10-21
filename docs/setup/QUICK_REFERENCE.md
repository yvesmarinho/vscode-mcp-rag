# 🚀 QUICK REFERENCE - Qdrant + MCP

## 📋 Comandos Essenciais

```bash
# ========== INICIAR TUDO ==========
make qdrant-start      # Docker: Qdrant
make mcp-start         # Systemd: MCP Server

# ========== VERIFICAR STATUS ==========
make qdrant-health     # Health check
make mcp-status        # MCP status
docker ps              # Ver containers

# ========== PARAR TUDO ==========
make mcp-stop          # Parar MCP
make qdrant-stop       # Parar Qdrant

# ========== LOGS ==========
make mcp-logs          # MCP logs (follow)
docker logs qdrant     # Qdrant logs
```

---

## 🔌 Endpoints

| Serviço | URL | Type |
|---------|-----|------|
| Qdrant API | `http://localhost:6333` | REST |
| Qdrant gRPC | `localhost:6334` | gRPC |
| MCP Server | stdin/stdout | JSON-RPC |

---

## 🔐 Credenciais

```
Qdrant API Key: J7fR-pO*rA4w1SEcaq*BOTheCUthuCuP94qIklxobicHuwU#u=9TlRes5t3TUFAz
Collection: project_docs
Vector Size: 384 (FastEmbed)
Distance: Cosine
```

---

## 🧪 Testar Rápido

### Python Test
```python
from qdrant_client import QdrantClient
from fastembed import TextEmbedding

client = QdrantClient(
    url="http://localhost:6333",
    api_key="J7fR-pO*rA4w1SEcaq*BOTheCUthuCuP94qIklxobicHuwU#u=9TlRes5t3TUFAz"
)
model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")

# Test embedding
emb = list(model.query_embed(["test"]))[0]

# Test search
results = client.query_points(
    collection_name="project_docs",
    query=emb,
    limit=3
)
for r in results.points:
    print(f"Score: {r.score:.1%}")
```

### cURL Test
```bash
# Health
curl http://localhost:6333/health

# Collections
curl http://localhost:6333/collections

# Collection info
curl http://localhost:6333/collections/project_docs
```

---

## 📁 Diretórios Importantes

```
/home/yves_marinho/Documentos/DevOps/Projetos/mcp_vector_project/
├── docker/
│   └── docker-compose.yaml          # Docker config
├── mcp/
│   └── qdrant_rag_server/
│       ├── server.py                # MCP Server
│       ├── .env                     # Configurações
│       ├── start-daemon.sh          # Daemon wrapper
│       └── requirements*.txt        # Dependencies
├── Makefile                         # Automation
└── [DOCUMENTAÇÃO]
    ├── CONCLUSAO_FINAL.md
    ├── MCP_COMPLETE.md
    └── STATUS_FINAL.txt
```

---

## 🔄 Arquitetura

```
┌─────────────────────────────────────────┐
│         VS Code (Continue)              │
│         or Other MCP Client             │
└────────────────┬────────────────────────┘
                 │
                 │ JSON-RPC 2.0
                 │ stdin/stdout
                 ▼
┌─────────────────────────────────────────┐
│     MCP Server (Python)                 │
│  ├─ ingest tool                         │
│  ├─ query tool                          │
│  └─ Systemd: qdrant-mcp-server.service  │
└────────────────┬────────────────────────┘
                 │
                 │ HTTP/REST
                 │ localhost:6333
                 ▼
┌─────────────────────────────────────────┐
│  Qdrant Container (Docker)              │
│  ├─ Collection: project_docs            │
│  ├─ Points: 35 indexed                  │
│  ├─ Volume: qdrant_storage (persist)    │
│  └─ Status: 🟢 GREEN                    │
└─────────────────────────────────────────┘
                 │
                 │ FastEmbed (CPU)
                 │ BAAI/bge-small-en-v1.5
                 ▼
┌─────────────────────────────────────────┐
│    Your Documents & Code                │
│    (35 chunks indexed)                  │
└─────────────────────────────────────────┘
```

---

## 📊 Status Check Script

```bash
#!/bin/bash
echo "=== Qdrant Status ==="
curl -s http://localhost:6333/health | jq . || echo "❌ Offline"

echo -e "\n=== MCP Status ==="
systemctl --user status qdrant-mcp-server.service --no-pager

echo -e "\n=== Docker Containers ==="
docker ps | grep qdrant

echo -e "\n=== Memory Usage ==="
docker stats --no-stream qdrant 2>/dev/null || echo "Qdrant not running"
```

---

## 🆘 Quick Fixes

| Problema | Solução |
|----------|---------|
| MCP não responde | `make mcp-stop && make mcp-start` |
| Qdrant offline | `docker-compose -f docker/docker-compose.yaml restart` |
| Busca vazia | Reindexar com `python3 mcp/qdrant_rag_server/qdrant_create_db.py` |
| Erro de conexão | Verificar `.env` - QDRANT_URL e QDRANT_API_KEY |
| Alto consumo CPU | Reduzir `chunk_size` ou limitar `top_k` em buscas |

---

## 📞 Informações Úteis

- **Python:** 3.12.3 (.venv)
- **Qdrant:** latest (Docker)
- **FastEmbed:** BAAI/bge-small-en-v1.5 (384 dims)
- **MCP Protocol:** JSON-RPC 2.0
- **Systemd User Service:** Gerenciar sem sudo

---

**Última atualização:** 17 de outubro de 2025

Para documentação completa, veja `CONCLUSAO_FINAL.md` ou `MCP_COMPLETE.md`
