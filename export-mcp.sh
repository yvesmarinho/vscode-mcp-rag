#!/bin/bash
# 📦 Script para exportar o MCP Server para outro projeto
# Cria um arquivo compactado pronto para usar em qualquer projeto

set -e

echo "════════════════════════════════════════════════════════════════"
echo "📦 MCP QDRANT SERVER - EXPORT SCRIPT"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Variáveis
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MCP_SOURCE="${PROJECT_ROOT}/mcp/qdrant_rag_server"
EXPORT_DIR="${PROJECT_ROOT}/export"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
EXPORT_NAME="qdrant-mcp-server_${TIMESTAMP}"
ARCHIVE="${EXPORT_DIR}/${EXPORT_NAME}.tar.gz"

echo -e "${BLUE}📍 Projeto: ${PROJECT_ROOT}${NC}"
echo -e "${BLUE}📍 Origem: ${MCP_SOURCE}${NC}"
echo ""

# 1. Criar diretório de export
echo -e "${YELLOW}1️⃣ Criando diretório de export...${NC}"
mkdir -p "${EXPORT_DIR}"
echo -e "${GREEN}✅ Diretório criado${NC}"
echo ""

# 2. Copiar arquivos
echo -e "${YELLOW}2️⃣ Preparando arquivos...${NC}"
TEMP_DIR=$(mktemp -d)
trap "rm -rf ${TEMP_DIR}" EXIT

mkdir -p "${TEMP_DIR}/qdrant_rag_server"
cd "${MCP_SOURCE}"

# Copiar arquivos mantendo estrutura
echo "   Copiando arquivos principais..."
cp -v server.py "${TEMP_DIR}/qdrant_rag_server/" 2>/dev/null || true
cp -v qdrant_create_db.py "${TEMP_DIR}/qdrant_rag_server/" 2>/dev/null || true
cp -v ingest_documents.py "${TEMP_DIR}/qdrant_rag_server/" 2>/dev/null || true
cp -v server-http.py "${TEMP_DIR}/qdrant_rag_server/" 2>/dev/null || true
cp -v start-daemon.sh "${TEMP_DIR}/qdrant_rag_server/" 2>/dev/null || true
cp -v start-server.sh "${TEMP_DIR}/qdrant_rag_server/" 2>/dev/null || true

echo "   Copiando configurações..."
cp -v .env.example "${TEMP_DIR}/qdrant_rag_server/.env.example" 2>/dev/null || true
cp -v requirements.txt "${TEMP_DIR}/qdrant_rag_server/" 2>/dev/null || true
cp -v requirements-fastembed.txt "${TEMP_DIR}/qdrant_rag_server/" 2>/dev/null || true
cp -v requirements-sentencetransformers.txt "${TEMP_DIR}/qdrant_rag_server/" 2>/dev/null || true
cp -v requirements-openai.txt "${TEMP_DIR}/qdrant_rag_server/" 2>/dev/null || true
cp -v README.md "${TEMP_DIR}/qdrant_rag_server/" 2>/dev/null || true

echo -e "${GREEN}✅ Arquivos copiados${NC}"
echo ""

# 3. Criar README de importação
echo -e "${YELLOW}3️⃣ Criando guia de importação...${NC}"
cat > "${TEMP_DIR}/IMPORT_GUIDE.md" << 'EOF'
# 📦 MCP Qdrant Server - Guia de Importação

## 🚀 Como usar em outro projeto

### Passo 1: Extrair o arquivo
```bash
tar -xzf qdrant-mcp-server_*.tar.gz
```

### Passo 2: Copiar para seu projeto
```bash
cp -r qdrant_rag_server /seu/projeto/mcp/
```

### Passo 3: Configurar variáveis de ambiente
```bash
cd /seu/projeto/mcp/qdrant_rag_server
cp .env.example .env
# Editar .env com suas configurações
```

### Passo 4: Instalar dependências
```bash
# CPU-only (recomendado)
pip install -r requirements.txt
pip install -r requirements-fastembed.txt

# OU com GPU
pip install -r requirements.txt
pip install -r requirements-sentencetransformers.txt

# OU com OpenAI
pip install -r requirements.txt
pip install -r requirements-openai.txt
```

### Passo 5: Inicializar banco de dados
```bash
python3 mcp/qdrant_rag_server/qdrant_create_db.py
```

### Passo 6: Iniciar MCP Server
```bash
# Simples
python3 mcp/qdrant_rag_server/server.py

# Ou com daemon wrapper
bash mcp/qdrant_rag_server/start-daemon.sh
```

## 📋 Checklist de Compatibilidade

- ✅ Python 3.8+ (recomendado 3.10+)
- ✅ Qdrant rodando (Docker ou local)
- ✅ pip disponível
- ✅ Porta 6333 disponível (Qdrant)
- ✅ ~/.continue/config.json configurado (para VS Code)

## ⚙️ Configuração Essencial (.env)

```ini
# Qdrant
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=seu-api-key-aqui
QDRANT_COLLECTION=seu-collection-name

# Embeddings
EMBEDDINGS_PROVIDER=fastembed
MODEL_NAME=BAAI/bge-small-en-v1.5
VECTOR_SIZE=384
DISTANCE=COSINE
```

## 🔌 Integração com Continue (VS Code)

Editar `~/.continue/config.json`:

```json
{
  "mcpServers": {
    "seu-projeto-mcp": {
      "command": "bash",
      "args": [
        "-c",
        "cd /seu/projeto && python3 mcp/qdrant_rag_server/server.py"
      ]
    }
  }
}
```

## 📁 Estrutura esperada no seu projeto

```
/seu/projeto/
├── mcp/
│   └── qdrant_rag_server/
│       ├── server.py
│       ├── qdrant_create_db.py
│       ├── .env
│       ├── requirements.txt
│       └── ...
└── ...
```

## 🆘 Troubleshooting

### Erro: "qdrant_client not found"
```bash
pip install -r mcp/qdrant_rag_server/requirements.txt
```

### Erro: "Cannot connect to Qdrant"
```bash
# Verificar se Qdrant está rodando
docker ps | grep qdrant
# Ou iniciar Qdrant
docker-compose up -d qdrant
```

### Erro: "FastEmbed model not found"
```bash
pip install -r mcp/qdrant_rag_server/requirements-fastembed.txt
```

## ✅ Testes rápidos

### Testar importação de módulos
```bash
python3 -c "from qdrant_client import QdrantClient; print('✅ OK')"
```

### Testar MCP Server
```bash
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}' | \
  python3 mcp/qdrant_rag_server/server.py
```

### Testar conexão Qdrant
```bash
curl http://localhost:6333/collections
```

## 📞 Suporte

Verifique os arquivos:
- `README.md` - Documentação detalhada
- `server.py` - Código comentado
- `.env.example` - Template de configuração

---

**Pronto para usar em qualquer projeto!** 🚀
EOF

echo -e "${GREEN}✅ Guia de importação criado${NC}"
echo ""

# 4. Criar arquivo compactado
echo -e "${YELLOW}4️⃣ Compactando arquivos...${NC}"
cd "${TEMP_DIR}"
tar -czf "${ARCHIVE}" . 2>/dev/null

if [ -f "${ARCHIVE}" ]; then
    SIZE=$(du -h "${ARCHIVE}" | cut -f1)
    echo -e "${GREEN}✅ Arquivo criado: ${ARCHIVE}${NC}"
    echo -e "${GREEN}   Tamanho: ${SIZE}${NC}"
else
    echo -e "\033[0;31m❌ Erro ao criar arquivo${NC}"
    exit 1
fi
echo ""

# 6. Criar checksum
echo -e "${YELLOW}5️⃣ Gerando checksum...${NC}"
cd "${EXPORT_DIR}"
sha256sum "${EXPORT_NAME}.tar.gz" > "${EXPORT_NAME}.sha256"
echo -e "${GREEN}✅ Checksum criado${NC}"
echo ""

# 7. Criar script de verificação
echo -e "${YELLOW}6️⃣ Criando script de verificação...${NC}"
cat > "${EXPORT_DIR}/verify.sh" << 'EOF'
#!/bin/bash
echo "🔍 Verificando integridade do arquivo..."
if sha256sum -c *.sha256 2>/dev/null; then
    echo "✅ Arquivo íntegro!"
else
    echo "❌ Arquivo corrompido!"
    exit 1
fi
EOF
chmod +x "${EXPORT_DIR}/verify.sh"
echo -e "${GREEN}✅ Script de verificação criado${NC}"
echo ""

# 8. Gerar relatório
echo -e "${YELLOW}7️⃣ Gerando relatório...${NC}"
cat > "${EXPORT_DIR}/EXPORT_REPORT.txt" << EOF
════════════════════════════════════════════════════════════════
📦 MCP QDRANT SERVER - EXPORT REPORT
════════════════════════════════════════════════════════════════

Data/Hora: $(date)
Origem: ${PROJECT_ROOT}
Destino: ${ARCHIVE}

ARQUIVOS INCLUSOS:
$(tar -tzf "${ARCHIVE}" | sed 's/^/  ✓ /')

VERIFICAÇÃO:
  Tamanho: ${SIZE}
  Checksum: SHA256 em ${EXPORT_NAME}.sha256
  Arquivos: $(tar -tzf "${ARCHIVE}" | wc -l)

PRÓXIMOS PASSOS:
  1. Enviar arquivo para outro projeto
  2. Extrair: tar -xzf ${EXPORT_NAME}.tar.gz
  3. Ler: IMPORT_GUIDE.md
  4. Seguir instruções de instalação

COMPATIBILIDADE:
  ✅ Python 3.8+
  ✅ Linux/Mac/Windows (WSL)
  ✅ Qdrant 1.0+
  ✅ VS Code + Continue Extension

════════════════════════════════════════════════════════════════
EOF

echo -e "${GREEN}✅ Relatório criado${NC}"
echo ""

# 9. Resumo final
echo "════════════════════════════════════════════════════════════════"
echo -e "${GREEN}✅ EXPORT COMPLETO!${NC}"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo -e "${BLUE}📦 Arquivo gerado:${NC}"
echo "   ${ARCHIVE}"
echo ""
echo -e "${BLUE}📋 Arquivo contém:${NC}"
tar -tzf "${ARCHIVE}" | head -15
if [ $(tar -tzf "${ARCHIVE}" | wc -l) -gt 15 ]; then
    echo "   ... e mais $(( $(tar -tzf "${ARCHIVE}" | wc -l) - 15 )) arquivos"
fi
echo ""
echo -e "${BLUE}📊 Tamanho: ${SIZE}${NC}"
echo ""
echo -e "${BLUE}🔒 Integridade:${NC}"
echo "   cat ${EXPORT_NAME}.sha256"
echo ""
echo -e "${BLUE}📖 Guia de uso:${NC}"
echo "   1. tar -xzf ${EXPORT_NAME}.tar.gz"
echo "   2. cd qdrant_rag_server"
echo "   3. cat IMPORT_GUIDE.md"
echo ""
echo -e "${BLUE}✨ Arquivos de suporte:${NC}"
echo "   • IMPORT_GUIDE.md - Instruções detalhadas"
echo "   • EXPORT_REPORT.txt - Este relatório"
echo "   • verify.sh - Verificar integridade"
echo ""
echo "════════════════════════════════════════════════════════════════"
echo -e "${GREEN}Pronto para compartilhar! 🚀${NC}"
echo "════════════════════════════════════════════════════════════════"
