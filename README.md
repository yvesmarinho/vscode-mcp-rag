# MCP Vector Project

Projeto MCP (Model Context Protocol) com integração Qdrant para busca semântica e RAG (Retrieval-Augmented Generation) no VS Code.

## 🚀 Quick Start

**Quer começar em 5 minutos?** Leia [`docs/setup/QUICKSTART.md`](docs/setup/QUICKSTART.md)

## Estrutura do Projeto

```
├── docs/                    # Documentação
│   ├── setup/              # Guias de instalação
│   ├── docker/             # Documentação Docker
│   ├── summaries/          # Resumos e conclusões
│   └── project/            # Documentação do projeto
├── config/                 # Arquivos de configuração
├── mcp/                    # Servidor MCP
├── docker/                 # Docker Compose
├── scripts/                # Scripts utilitários
└── export/                 # Arquivos de exportação
```

## Componentes Principais
- `mcp/qdrant_rag_server/`: Servidor MCP para Qdrant
- `docker/`: Infraestrutura Docker com Qdrant
- `scripts/`: Scripts de diagnóstico e setup
- `config/`: Configurações e templates

## 📖 Documentação

### Para Começar
- **[Quick Start](docs/setup/QUICKSTART.md)** ← **COMECE AQUI** (5 min)
- **[Setup Checklist](docs/setup/SETUP_CHECKLIST.md)** ← Lista de verificação
- **[Início Rápido](docs/setup/INICIO_RAPIDO.md)** ← Versão em português

### Configuração
- **[Configuration](docs/project/CONFIGURATION.md)** ← Configuração detalhada
- **[Integration](docs/project/INTEGRATION.md)** ← Integração completa

### Docker & Infraestrutura
- **[Docker Index](docs/docker/DOCKER_INDEX.md)** ← Índice Docker
- **[Quick Reference](docs/docker/DOCKER_QUICK_REF.md)** ← Comandos rápidos
- **[Architecture](docs/docker/DOCKER_ARCHITECTURE.md)** ← Diagramas visuais
- **[Checklist](docs/docker/DOCKER_CHECKLIST.md)** ← Checklist de setup
- **[Complete Guide](docs/docker/DOCKER.md)** ← Referência completa

## 🛠️ Comandos Rápidos
```bash
make help                   # Ver todos os comandos
make install-fastembed      # Setup + FastEmbed
make qdrant-start          # Iniciar Qdrant (Docker)
make create-collection     # Criar collection
make diagnose              # Verificar setup

# Docker direto
cd docker/
docker-compose up -d       # Iniciar Qdrant
docker-compose ps          # Verificar status
curl http://localhost:6333/health  # Testar saúde
```

## 📜 Scripts Utilitários
1. `scripts/mcp_quickstart_report.sh [--setup]` — Plano de setup
2. `scripts/mcp_qdrant_report.sh` — Diagnóstico completo
3. `scripts/mcp_install_deps_report.sh [fastembed|sentence-transformers|openai]` — Instalar deps
4. `scripts/mcp_test_ingest_report.sh [--dry-run]` — Testar ingestão

## Diretrizes do Projeto
- ✅ Nenhum comando executado automaticamente
- ✅ Scripts geram relatórios para auditoria
- ✅ Nenhum segredo exposto em logs
- ✅ Tudo é idempotente (seguro reexecutar)

| Arquivo | Propósito |
|---------|-----------|
| `QUICKSTART.md` | Guia de 5 min para começar |
| `INTEGRATION.md` | Referência completa com exemplos |
| `Makefile` | Atalhos para setup e testes |
| `.vscode/extensions.json` | Extensões recomendadas (Continue, Cline, etc.) |
| `pyproject.toml` | Dependências opcionais por provedor |
| `mcp/qdrant_rag_server/server.py` | Servidor MCP (ingest/query tools) |
| `mcp/qdrant_rag_server/.env.example` | Template de configuração |
| `mcp/qdrant_rag_server/requirements*.txt` | Deps base + provedores |
| `scripts/` | Helper scripts com relatórios |
