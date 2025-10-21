# 🚀 Como Usar MCP Qdrant em Outro Projeto

## 📝 **TL;DR (Resumo Rápido)**

```bash
# 1. Extrair pacote
tar -xzf qdrant-mcp-server_*.tar.gz

# 2. Copiar para seu projeto
cp -r qdrant_rag_server /MEU/PROJETO/mcp/

# 3. Configurar
cd /MEU/PROJETO/mcp/qdrant_rag_server
cp .env.example .env
nano .env  # Editar QDRANT_URL, etc.

# 4. Instalar e executar
pip install -r requirements.txt requirements-fastembed.txt
python3 qdrant_create_db.py
chmod +x *.sh && ./start-daemon-bg.sh
```

---

## 🎯 **3 Formas de Integrar**

### **FORMA 1: Pacote (Distribuição)**
✅ **Use quando:** Recebeu um arquivo `.tar.gz`

```bash
# Extrair
tar -xzf qdrant-mcp-server_20251018_164606.tar.gz

# Copiar para MEU projeto
cp -r qdrant_rag_server /home/meu_user/meu_projeto_ai/mcp/
```

### **FORMA 2: Cópia Direta (Desenvolvimento)**  
✅ **Use quando:** Tem acesso ao projeto `mcp_vector_project`

```bash
# Copiar diretamente
cp -r /caminho/para/mcp_vector_project/mcp/qdrant_rag_server \
      /home/meu_user/meu_projeto_ai/mcp/
```

### **FORMA 3: Git Clone**
✅ **Use quando:** Quer sempre a versão mais atualizada

```bash
# Baixar projeto completo
git clone https://github.com/yvesmarinho/vscode-mcp-rag.git /tmp/mcp-source

# Copiar só o que precisa
cp -r /tmp/mcp-source/mcp/qdrant_rag_server /home/meu_user/meu_projeto_ai/mcp/

# Limpar
rm -rf /tmp/mcp-source
```

---

## 📁 **Estrutura Final Esperada**

```
/home/meu_user/meu_projeto_ai/          ← SEU PROJETO
├── src/                                ← Seu código
├── docs/                               ← Sua documentação
├── mcp/                                ← Pasta MCP
│   └── qdrant_rag_server/              ← COPIADO do pacote
│       ├── server.py                   ← Servidor MCP
│       ├── qdrant_create_db.py         ← Criar coleção
│       ├── .env                        ← VOCÊ CRIA (cp .env.example .env)
│       ├── .env.example                ← Template
│       ├── start-daemon-bg.sh          ← Scripts de controle
│       └── requirements*.txt           ← Dependências
├── README.md                           ← Seu README
└── .gitignore                          ← ADICIONAR: mcp/qdrant_rag_server/.env
```

---

## ⚙️ **Setup Completo (Copie e Cole)**

```bash
# 1. NAVEGAR para sua pasta copiada
cd /MEU/PROJETO/mcp/qdrant_rag_server

# 2. CONFIGURAR ambiente
cp .env.example .env
nano .env  # Editar: QDRANT_URL, COLLECTION, etc.

# 3. INSTALAR dependências
pip install -r requirements.txt
pip install -r requirements-fastembed.txt  # CPU-only

# 4. TORNAR scripts executáveis  
chmod +x *.sh

# 5. VERIFICAR Qdrant rodando
curl http://localhost:6333/health

# 6. CRIAR coleção no Qdrant
python3 qdrant_create_db.py

# 7. INICIAR servidor MCP
./start-daemon-bg.sh

# 8. VERIFICAR status
./status-daemon.sh
```

---

## 🔧 **Configuração .env Mínima**

```bash
# Conteúdo do arquivo .env
QDRANT_URL=http://localhost:6333
QDRANT_COLLECTION=meu_projeto_docs
EMBEDDINGS_PROVIDER=fastembed
MODEL_NAME=BAAI/bge-small-en-v1.5
VECTOR_SIZE=384
DISTANCE=COSINE
```

---

## 🔗 **Integração VS Code**

### **Continue** (`~/.continue/config.json`)
```json
{
  "mcpServers": {
    "meu-projeto-rag": {
      "command": "python3",
      "args": ["/CAMINHO/ABSOLUTO/PARA/MEU/PROJETO/mcp/qdrant_rag_server/server.py"],
      "env": {
        "QDRANT_URL": "http://localhost:6333",
        "QDRANT_COLLECTION": "meu_projeto_docs"
      }
    }
  }
}
```

### **Cline**
```json
{
  "mcpServers": {
    "meu-projeto": {
      "command": "bash", 
      "args": ["-c", "cd /MEU/PROJETO && python3 mcp/qdrant_rag_server/server.py"]
    }
  }
}
```

---

## ✅ **Checklist de Verificação**

- [ ] ✅ Pasta copiada para `/MEU/PROJETO/mcp/qdrant_rag_server/`
- [ ] ✅ Arquivo `.env` criado e editado
- [ ] ✅ Dependências instaladas
- [ ] ✅ Qdrant rodando (`curl http://localhost:6333/health`)
- [ ] ✅ Coleção criada (`python3 qdrant_create_db.py`)
- [ ] ✅ Servidor iniciado (`./start-daemon-bg.sh`)
- [ ] ✅ Status OK (`./status-daemon.sh`)
- [ ] ✅ VS Code configurado
- [ ] ✅ `.env` no `.gitignore`

---

## 🆘 **Problemas Comuns**

### ❌ "Pasta não encontrada"
```bash
# Verificar onde está
find ~ -name "qdrant_rag_server" -type d 2>/dev/null

# Criar estrutura correta
mkdir -p /MEU/PROJETO/mcp
cp -r qdrant_rag_server /MEU/PROJETO/mcp/
```

### ❌ "Connection refused"
```bash
# Iniciar Qdrant
docker run -p 6333:6333 qdrant/qdrant

# OU se tem docker-compose
docker-compose up -d qdrant
```

### ❌ "Collection not found"
```bash
cd /MEU/PROJETO/mcp/qdrant_rag_server
python3 qdrant_create_db.py
```

### ❌ "Module not found"
```bash
cd /MEU/PROJETO/mcp/qdrant_rag_server
pip install -r requirements.txt
pip install -r requirements-fastembed.txt
```

---

## 🎯 **Exemplo Prático Completo**

```bash
# EXEMPLO: Integrar em projeto chamado "minha_ia"

# 1. Extrair pacote
cd ~/Downloads
tar -xzf qdrant-mcp-server_20251018_164606.tar.gz

# 2. Copiar para projeto
cp -r qdrant_rag_server ~/projetos/minha_ia/mcp/

# 3. Configurar
cd ~/projetos/minha_ia/mcp/qdrant_rag_server
cp .env.example .env
echo "QDRANT_COLLECTION=minha_ia_docs" >> .env

# 4. Setup
pip install -r requirements.txt requirements-fastembed.txt
chmod +x *.sh
python3 qdrant_create_db.py
./start-daemon-bg.sh

# 5. Configurar Continue
cat >> ~/.continue/config.json << 'EOF'
{
  "mcpServers": {
    "minha-ia-rag": {
      "command": "python3",
      "args": ["/home/meu_user/projetos/minha_ia/mcp/qdrant_rag_server/server.py"]
    }
  }
}
EOF

# 6. Testar
./status-daemon.sh
echo "✅ Pronto! Use no VS Code: 'Index my project'"
```

---

**🎯 Resultado:** MCP funcionando no seu projeto com busca semântica!