# 🔧 Configuração .env para Outros Projetos

## 📋 Setup Rápido

### 1. Copiar template
```bash
cd /seu/projeto/mcp/qdrant_rag_server
cp .env.example .env
```

### 2. Configurar básico para localhost
```bash
# .env
QDRANT_URL=http://localhost:6333
QDRANT_COLLECTION=project_docs
EMBEDDINGS_PROVIDER=fastembed
MODEL_NAME=BAAI/bge-small-en-v1.5
VECTOR_SIZE=384
DISTANCE=COSINE
```

### 3. Inicializar banco
```bash
python3 qdrant_create_db.py
```

### 4. Testar servidor
```bash
./start-server.sh
```

---

## 🌍 Configurações por Ambiente

### 🖥️ Desenvolvimento Local
```bash
# .env
QDRANT_URL=http://localhost:6333
# QDRANT_API_KEY=           # Vazio para localhost
QDRANT_COLLECTION=project_docs
EMBEDDINGS_PROVIDER=fastembed
MODEL_NAME=BAAI/bge-small-en-v1.5
VECTOR_SIZE=384
DISTANCE=COSINE
```

### ☁️ Qdrant Cloud (Produção)
```bash
# .env
QDRANT_URL=https://xyz-abc.eu-central-1.aws.cloud.qdrant.io:6333
QDRANT_API_KEY=your-cloud-api-key-here
QDRANT_COLLECTION=production_docs
EMBEDDINGS_PROVIDER=fastembed
MODEL_NAME=BAAI/bge-base-en-v1.5
VECTOR_SIZE=384
DISTANCE=COSINE
```

### 🤖 OpenAI Embeddings
```bash
# .env
QDRANT_URL=http://localhost:6333
QDRANT_COLLECTION=project_docs
EMBEDDINGS_PROVIDER=openai
OPENAI_API_KEY=sk-proj-your-key-here
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
VECTOR_SIZE=1536
DISTANCE=COSINE
```

### 🔥 GPU Acelerado
```bash
# .env
QDRANT_URL=http://localhost:6333
QDRANT_COLLECTION=project_docs
EMBEDDINGS_PROVIDER=sentence-transformers
MODEL_NAME=all-mpnet-base-v2
VECTOR_SIZE=768
DISTANCE=COSINE
```

---

## 📊 Dimensões por Modelo

| Provider | Model | Vector Size | Performance |
|----------|-------|-------------|-------------|
| **fastembed** | BAAI/bge-small-en-v1.5 | 384 | ⚡ Rápido |
| **fastembed** | BAAI/bge-base-en-v1.5 | 768 | ⚖️ Balanceado |
| **sentence-transformers** | all-MiniLM-L6-v2 | 384 | ⚡ Rápido |
| **sentence-transformers** | all-mpnet-base-v2 | 768 | 🎯 Preciso |
| **openai** | text-embedding-3-small | 1536 | 💰 Pago |

---

## 🛡️ Variáveis Essenciais

### Para server.py (MCP Server)
```bash
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=               # Opcional para localhost
QDRANT_COLLECTION=project_docs
EMBEDDINGS_PROVIDER=fastembed
MODEL_NAME=BAAI/bge-small-en-v1.5
```

### Para qdrant_create_db.py (Criar coleção)
```bash
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=               # Opcional para localhost
QDRANT_COLLECTION=project_docs
VECTOR_SIZE=384
DISTANCE=COSINE
```

---

## 🔗 Integração VS Code

### Continue (.continue/config.json)
```json
{
  "mcpServers": {
    "qdrant-rag": {
      "command": "python3",
      "args": ["/caminho/absoluto/para/mcp/qdrant_rag_server/server.py"],
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

### Cline
```json
{
  "mcpServers": {
    "qdrant": {
      "command": "bash",
      "args": [
        "-c", 
        "cd /seu/projeto && python3 mcp/qdrant_rag_server/server.py"
      ]
    }
  }
}
```

---

## 🆘 Troubleshooting

### ❌ "Connection refused"
```bash
# Verificar se Qdrant está rodando
curl http://localhost:6333/health

# Iniciar Qdrant
docker-compose up -d qdrant
```

### ❌ "Collection not found"
```bash
# Criar coleção
python3 qdrant_create_db.py
```

### ❌ "Module not found"
```bash
# Instalar dependências
pip install -r requirements.txt
pip install -r requirements-fastembed.txt
```

### ❌ "Api key warning"
```bash
# Para localhost, deixar QDRANT_API_KEY vazio
QDRANT_API_KEY=
# ou comentar a linha:
# QDRANT_API_KEY=
```

---

## 📁 Arquivos Relacionados

- `.env.example` - Template de configuração
- `qdrant_create_db.py` - Script para criar coleção
- `server.py` - Servidor MCP principal
- `requirements*.txt` - Dependências por provider

---

## ✅ Checklist de Setup

- [ ] Copiar `.env.example` para `.env`
- [ ] Configurar `QDRANT_URL`
- [ ] Configurar `EMBEDDINGS_PROVIDER`
- [ ] Definir `VECTOR_SIZE` correto para o modelo
- [ ] Executar `python3 qdrant_create_db.py`
- [ ] Testar com `./start-server.sh`
- [ ] Configurar VS Code (Continue/Cline)
- [ ] Adicionar `.env` ao `.gitignore`

---

**🎯 Resultado:** Servidor MCP funcionando com busca semântica!