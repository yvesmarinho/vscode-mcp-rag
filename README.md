# MCP Vector Project

Projeto MCP (Model Context Protocol) com integração Qdrant para busca semântica e RAG (Retrieval-Augmented Generation) no VS Code.

## 🚀 Quick Start

**Quer começar em 5 minutos?** Leia [`docs/setup/QUICKSTART.md`](docs/setup/QUICKSTART.md)

## 🎯 Como Usar

### 1️⃣ Setup Automático
```bash
# Configurar tudo automaticamente
make install-fastembed      # Instalar dependências
make qdrant-start           # Iniciar Qdrant
make create-collection      # Criar coleção
python scripts/setup_vscode_config.py  # Configurar VS Code
```

### 2️⃣ Indexar Documentos
```bash
# Indexar projeto atual
cd mcp/qdrant_rag_server
python ingest_documents.py

# Ou usar o MCP tools
# No VS Code: @qdrant_rag ingest {"directory": "."}
```

### 3️⃣ Buscar no VS Code
```
# No Continue/Cline chat:
@qdrant_rag query "como configurar docker"
@qdrant_rag query "explicar função main"
```

```bash
# 1. Clonar
git clone https://github.com/yvesmarinho/vscode-mcp-rag.git
cd vscode-mcp-rag

# 2. Setup
docker-compose up -d qdrant  # Iniciar Qdrant
cd mcp/qdrant_rag_server
pip install -r requirements.txt requirements-fastembed.txt

# 3. Configurar
cp .env.example .env
nano .env  # Ajustar se necessário

# 4. Executar
python3 qdrant_create_db.py  # Criar coleção
./start-daemon-bg.sh         # Iniciar servidor
./status-daemon.sh           # Verificar status

# 5. VS Code: Configurar Continue/Cline
# Ver: mcp/qdrant_rag_server/QUICK_SETUP.md
```

## 🚀 Como usar em OUTRO projeto

**3 opções disponíveis:**

### 1️⃣ Pacote TAR.GZ (Recomendado)
```bash
# Baixar release ou gerar pacote
./export-mcp.sh  # Gera qdrant-mcp-server_*.tar.gz

# Usar em outro projeto
tar -xzf qdrant-mcp-server_*.tar.gz
cp -r qdrant_rag_server /MEU_PROJETO/mcp/
cd /MEU_PROJETO/mcp/qdrant_rag_server
# Seguir QUICK_SETUP.md
```

### 2️⃣ Cópia Direta
```bash
cp -r mcp_vector_project/mcp/qdrant_rag_server /MEU_PROJETO/mcp/
```

### 3️⃣ Git Submodule
```bash
git submodule add https://github.com/yvesmarinho/vscode-mcp-rag.git vendors/mcp-rag
cp -r vendors/mcp-rag/mcp/qdrant_rag_server /MEU_PROJETO/mcp/
```

📖 **Guias detalhados:** `mcp/qdrant_rag_server/QUICK_SETUP.md`

## 🏗️ Arquitetura

```
┌─────────────────┐    ┌──────────────┐    ┌─────────────────┐
│   VS Code       │    │ MCP Server   │    │    Qdrant      │
│ (Continue/Cline)│◄──►│  (Python)    │◄──►│ (Vector DB)     │
└─────────────────┘    └──────────────┘    └─────────────────┘
                              │
                       ┌──────────────┐
                       │  FastEmbed   │
                       │ (Embeddings) │
                       └──────────────┘
```

## 🔧 Componentes

- **MCP Server** (`server.py`) - Servidor JSON-RPC para VS Code
- **Qdrant Database** - Banco vetorial (Docker)
- **FastEmbed** - Embeddings CPU-friendly
- **Scripts de Controle** - Daemon, status, stop
- **Ferramentas MCP** - `ingest_documents`, `query_documents`

## � Documentação

- [`QUICK_SETUP.md`](mcp/qdrant_rag_server/QUICK_SETUP.md) - Setup visual
- [`CONFIG_GUIDE.md`](mcp/qdrant_rag_server/CONFIG_GUIDE.md) - Configuração
- [`USAGE_SUMMARY.md`](USAGE_SUMMARY.md) - Como usar em outros projetos
- [`docs/`](docs/) - Documentação completa

## 🎯 Funcionalidades

- ✅ **Indexação semântica** de documentos
- ✅ **Busca vetorial** com relevância
- ✅ **Integração VS Code** (Continue/Cline)
- ✅ **CPU-only** (sem necessidade de GPU)
- ✅ **Docker** para Qdrant
- ✅ **Scripts automatizados** para controle
- ✅ **Configuração flexível** (.env)

## 🔗 Integração VS Code

### Continue (`~/.continue/config.json`)
```json
{
  "mcpServers": {
    "qdrant-rag": {
      "command": "python3",
      "args": ["/caminho/para/projeto/mcp/qdrant_rag_server/server.py"]
    }
  }
}
```

### Cline
Configuração similar - ver documentação específica.

## 📊 Status do Projeto

- **Versão:** 1.0.0
- **Status:** ✅ Produção
- **Última atualização:** 18/10/2025
- **Python:** 3.8+
- **Docker:** Qdrant latest
- **Embeddings:** BAAI/bge-small-en-v1.5 (384d)

## 🏆 Características Técnicas

- **Protocol:** JSON-RPC 2.0 (MCP)
- **Vector DB:** Qdrant (localhost:6333)
- **Embeddings:** FastEmbed (CPU-optimized)
- **Dimensions:** 384
- **Distance:** Cosine similarity
- **Storage:** Persistent volumes (Docker)

---

**🎯 Resultado:** Busca semântica inteligente no VS Code!

Para questões, ver `docs/` ou abrir issue no GitHub.
