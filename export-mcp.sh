#!/bin/bash

# 📦 MCP QDRANT SERVER - EXPORT SCRIPT
# Gera pacote para distribuição em outros projetos

set -e  # Parar se houver erro

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configurações
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "${SCRIPT_DIR}" && pwd)"
MCP_SOURCE="${PROJECT_DIR}/mcp/qdrant_rag_server"
EXPORT_BASE="${PROJECT_DIR}/export"
TIMESTAMP=$(date "+%Y%m%d_%H%M%S")
PACKAGE_NAME="qdrant-mcp-server_${TIMESTAMP}"
TEMP_DIR=$(mktemp -d)
EXPORT_DIR="${TEMP_DIR}/qdrant_rag_server"

echo "════════════════════════════════════════════════════════════════"
echo "📦 MCP QDRANT SERVER - EXPORT SCRIPT"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo -e "${BLUE}📍 Projeto: ${PROJECT_DIR}${NC}"
echo -e "${BLUE}📍 Origem: ${MCP_SOURCE}${NC}"
echo ""

# 1. Verificar se origem existe
if [ ! -d "${MCP_SOURCE}" ]; then
    echo -e "${RED}❌ Diretório não encontrado: ${MCP_SOURCE}${NC}"
    exit 1
fi

# 2. Criar estrutura de export
echo -e "${YELLOW}1️⃣ Criando diretório de export...${NC}"
mkdir -p "${EXPORT_DIR}"
cd "${MCP_SOURCE}"
echo -e "${GREEN}✅ Diretório criado${NC}"
echo ""

# 3. Copiar arquivos essenciais
echo -e "${YELLOW}2️⃣ Copiando arquivos...${NC}"

# Arquivos Python principais
echo "   📄 Copiando arquivos Python..."
cp -v server.py "${EXPORT_DIR}/" 2>/dev/null || true
cp -v qdrant_create_db.py "${EXPORT_DIR}/" 2>/dev/null || true
cp -v ingest_documents.py "${EXPORT_DIR}/" 2>/dev/null || true
cp -v server-http.py "${EXPORT_DIR}/" 2>/dev/null || true

# Scripts de controle
echo "   📜 Copiando scripts de controle..."
cp -v start-daemon.sh "${EXPORT_DIR}/" 2>/dev/null || true
cp -v start-daemon-bg.sh "${EXPORT_DIR}/" 2>/dev/null || true
cp -v start-server.sh "${EXPORT_DIR}/" 2>/dev/null || true
cp -v stop-daemon.sh "${EXPORT_DIR}/" 2>/dev/null || true
cp -v status-daemon.sh "${EXPORT_DIR}/" 2>/dev/null || true

# Tornar scripts executáveis
echo "   🔧 Tornando scripts executáveis..."
chmod +x "${EXPORT_DIR}/"*.sh 2>/dev/null || true

# Configurações e documentação
echo "   📋 Copiando configurações e documentação..."
cp -v .env.example "${EXPORT_DIR}/" 2>/dev/null || true
cp -v CONFIG_GUIDE.md "${EXPORT_DIR}/" 2>/dev/null || true
cp -v README.md "${EXPORT_DIR}/" 2>/dev/null || true
cp -v QUICK_SETUP.md "${EXPORT_DIR}/" 2>/dev/null || true

# Requirements
echo "   📦 Copiando requirements..."
cp -v requirements*.txt "${EXPORT_DIR}/" 2>/dev/null || true

echo -e "${GREEN}✅ Arquivos copiados${NC}"
echo ""

# 4. Criar guia de importação
echo -e "${YELLOW}3️⃣ Criando guia de uso...${NC}"
cat > "${EXPORT_DIR}/USAGE_GUIDE.md" << 'EOF'
# 🚀 Guia de Uso - MCP Qdrant Server

## 📦 Como usar este pacote em seu projeto

### 🎯 Passo 1: Copiar para seu projeto

```bash
# Copiar para seu projeto
cp -r qdrant_rag_server /caminho/para/seu/projeto/mcp/
```

### ⚙️ Passo 2: Configurar

```bash
cd /seu/projeto/mcp/qdrant_rag_server

# Criar configuração
cp .env.example .env
nano .env  # Editar conforme necessário
```

### 📦 Passo 3: Instalar dependências

```bash
pip install -r requirements.txt
pip install -r requirements-fastembed.txt  # Para CPU-only
```

### 🚀 Passo 4: Executar

```bash
# Tornar scripts executáveis
chmod +x *.sh

# Criar coleção no Qdrant
python3 qdrant_create_db.py

# Iniciar servidor MCP
./start-daemon-bg.sh

# Verificar status
./status-daemon.sh
```

### 🔗 Passo 5: Configurar VS Code

Adicionar em `~/.continue/config.json`:

```json
{
  "mcpServers": {
    "meu-projeto-rag": {
      "command": "python3",
      "args": ["/caminho/absoluto/para/seu/projeto/mcp/qdrant_rag_server/server.py"],
      "env": {
        "QDRANT_URL": "http://localhost:6333",
        "QDRANT_COLLECTION": "meu_projeto_docs"
      }
    }
  }
}
```

## 📁 Estrutura final esperada

```
seu_projeto/
├── src/                    ← Seu código
├── docs/                   ← Sua documentação
├── mcp/                    ← Pasta MCP
│   └── qdrant_rag_server/  ← Este pacote
│       ├── server.py
│       ├── .env
│       ├── start-daemon-bg.sh
│       └── ...
└── README.md               ← Seu README
```

## ✅ Verificação rápida

```bash
# Qdrant rodando?
curl http://localhost:6333/health

# Servidor MCP ativo?
./status-daemon.sh

# Testar ferramenta
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}' | python3 server.py
```

---

**🎯 Pronto! Agora você tem busca semântica no seu projeto.**
EOF

echo -e "${GREEN}✅ Guia criado${NC}"
echo ""

# 5. Gerar script de verificação
echo -e "${YELLOW}4️⃣ Criando script de verificação...${NC}"
cat > "${EXPORT_DIR}/verify.sh" << 'EOF'
#!/bin/bash
echo "🔍 Verificando instalação..."

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não encontrado"
    exit 1
fi

# Verificar pip
if ! command -v pip &> /dev/null; then
    echo "❌ pip não encontrado"
    exit 1
fi

# Verificar Qdrant
if ! curl -s http://localhost:6333/health > /dev/null; then
    echo "❌ Qdrant não está rodando em localhost:6333"
    echo "   Inicie com: docker run -p 6333:6333 qdrant/qdrant"
    exit 1
fi

echo "✅ Tudo ok! Pronto para usar."
EOF

chmod +x "${EXPORT_DIR}/verify.sh"
echo -e "${GREEN}✅ Script de verificação criado${NC}"
echo ""

# 6. Empacotar
echo -e "${YELLOW}5️⃣ Criando pacote...${NC}"
mkdir -p "${EXPORT_BASE}"
cd "${TEMP_DIR}"

# Criar tarball
tar -czf "${EXPORT_BASE}/${PACKAGE_NAME}.tar.gz" qdrant_rag_server/

# Gerar hash
cd "${EXPORT_BASE}"
sha256sum "${PACKAGE_NAME}.tar.gz" > "${PACKAGE_NAME}.sha256"

echo -e "${GREEN}✅ Pacote criado${NC}"
echo ""

# 7. Gerar relatório
echo -e "${YELLOW}6️⃣ Gerando relatório...${NC}"
cat > "${EXPORT_BASE}/EXPORT_REPORT.txt" << EOF
📦 MCP QDRANT SERVER - RELATÓRIO DE EXPORT
════════════════════════════════════════════════════════════════

🕐 Data/Hora: $(date)
📁 Pacote: ${PACKAGE_NAME}.tar.gz
📊 Tamanho: $(du -h "${PACKAGE_NAME}.tar.gz" | cut -f1)
🔐 SHA256: $(cat "${PACKAGE_NAME}.sha256" | cut -d' ' -f1)

📂 CONTEÚDO:
$(tar -tzf "${PACKAGE_NAME}.tar.gz" | sed 's/^/   /')

🚀 COMO USAR:
1. tar -xzf ${PACKAGE_NAME}.tar.gz
2. cp -r qdrant_rag_server /seu/projeto/mcp/
3. cd /seu/projeto/mcp/qdrant_rag_server
4. Seguir USAGE_GUIDE.md

✅ PRONTO PARA DISTRIBUIÇÃO!
EOF

echo -e "${GREEN}✅ Relatório gerado${NC}"
echo ""

# 8. Limpeza
rm -rf "${TEMP_DIR}"

# 9. Resultado final
echo "════════════════════════════════════════════════════════════════"
echo -e "${GREEN}🎉 EXPORT COMPLETO!${NC}"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo -e "${BLUE}📦 Arquivo: ${EXPORT_BASE}/${PACKAGE_NAME}.tar.gz${NC}"
echo -e "${BLUE}📊 Tamanho: $(du -h "${EXPORT_BASE}/${PACKAGE_NAME}.tar.gz" | cut -f1)${NC}"
echo -e "${BLUE}🔐 Hash: ${EXPORT_BASE}/${PACKAGE_NAME}.sha256${NC}"
echo -e "${BLUE}📋 Relatório: ${EXPORT_BASE}/EXPORT_REPORT.txt${NC}"
echo ""
echo -e "${YELLOW}Para usar:${NC}"
echo -e "   tar -xzf ${PACKAGE_NAME}.tar.gz"
echo -e "   cp -r qdrant_rag_server /SEU_PROJETO/mcp/"
echo -e "   Seguir: qdrant_rag_server/USAGE_GUIDE.md"
echo ""
echo -e "${GREEN}✨ Pronto para distribuir!${NC}"