# 📁 ESTRUTURA: ./mcp/qdrant_rag_server

**Localização:** `/home/yves_marinho/Documentos/DevOps/Projetos/ai_project_template/mcp/qdrant_rag_server`

Sim! Esta pasta contém **TODOS** os códigos e configurações da integração entre:
- 🤖 **Code/Continue** (VS Code extension)
- 🌐 **Qdrant** (Vector Database)
- ⚡ **FastEmbed** (Embeddings)

---

## 📋 ARQUIVOS E SUAS FUNÇÕES

### 🔴 ARQUIVOS PRINCIPAIS (MCP Server)

#### 1. **server.py** ⭐ PRINCIPAL
```
📄 Tamanho: ~425 linhas
🎯 Função: MCP Server - Interpreta JSON-RPC 2.0 do VS Code
```

**O que faz:**
- Recebe requisições JSON-RPC via stdin
- Implementa os tools: `ingest` e `query`
- Conecta com Qdrant para busca semântica
- Suporta 3 providers: FastEmbed, SentenceTransformers, OpenAI
- Retorna resultados estruturados

**Estrutura interna:**
```python
class Embeddings:           # Gerencia embeddings
def chunk_text():          # Divide textos em chunks
def ingest_documents():    # Indexa arquivos
def search_documents():    # Busca semântica
def handle_ingest():       # Tool: ingest
def handle_query():        # Tool: query
def mcp_list_tools():      # Lista tools disponíveis
def main():                # Loop JSON-RPC principal
```

---

#### 2. **qdrant_create_db.py** 🗄️
```
📄 Tamanho: ~100 linhas
🎯 Função: Inicializar/Recriar a collection no Qdrant
```

**O que faz:**
- Cria collection `project_docs` se não existir
- Configura vector size (384 para FastEmbed)
- Define distance metric (Cosine)
- Pode recriar a collection do zero com `force_recreate=True`

**Uso:**
```bash
python3 mcp/qdrant_rag_server/qdrant_create_db.py
```

---

#### 3. **server-http.py** 🌐 (Alternativa)
```
📄 Tamanho: ~175 linhas
🎯 Função: Versão HTTP do MCP Server (alternativa ao stdin)
```

**O que faz:**
- Servidor HTTP em vez de JSON-RPC stdin
- Roda na porta 8765 (configurável)
- Endpoints: `/health`, `/` (POST com JSON)
- Experimental (não é usado no deploy atual)

**Uso (experimental):**
```bash
python3 mcp/qdrant_rag_server/server-http.py
```

---

### 🟡 SCRIPTS DE EXECUÇÃO

#### 4. **start-daemon.sh** 🔄
```bash
📄 Tamanho: ~30 linhas
🎯 Função: Wrapper que mantém MCP rodando como daemon
```

**O que faz:**
- Loop infinito que reinicia o servidor se cair
- Usa named pipe para manter stdin aberto
- Timeout de 3600s (1 hora) por iteração
- Registra logs com timestamp

**Usado por:** `systemd` service `qdrant-mcp-server.service`

---

#### 5. **start-server.sh** 🚀
```bash
📄 Tamanho: ~10 linhas
🎯 Função: Script simples para iniciar o servidor
```

**O que faz:**
- Muda para diretório do projeto
- Executa server.py com Python do venv

**Uso:**
```bash
bash mcp/qdrant_rag_server/start-server.sh
```

---

### 🟢 CONFIGURAÇÃO & DEPENDÊNCIAS

#### 6. **.env** 🔐 CONFIGURAÇÃO
```ini
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=J7fR-pO*rA4w1SEcaq*BOTheCUthuCuP94qIklxobicHuwU#u=9TlRes5t3TUFAz
QDRANT_COLLECTION=project_docs
EMBEDDINGS_PROVIDER=fastembed
MODEL_NAME=BAAI/bge-small-en-v1.5
VECTOR_SIZE=384
DISTANCE=COSINE
```

**Variáveis importantes:**
- `QDRANT_URL` - Endereço do Qdrant
- `QDRANT_API_KEY` - Autenticação (opcional)
- `EMBEDDINGS_PROVIDER` - Qual provider usar
- `MODEL_NAME` - Modelo de embeddings

---

#### 7. **.env.example** 📋
```
Cópia de .env como template
Use como referência para criar novo .env
```

---

#### 8. **requirements.txt** 📦 BASE
```
qdrant-client
python-dotenv
```

**Dependências comuns a todos os providers**

---

#### 9. **requirements-fastembed.txt** 📦 CPU-ONLY
```
fastembed
```

**Para provider: FastEmbed (recomendado)**

---

#### 10. **requirements-sentencetransformers.txt** 📦 COM GPU
```
sentence-transformers
torch
```

**Para provider: SentenceTransformers (com GPU opcional)**

---

#### 11. **requirements-openai.txt** 📦 CLOUD
```
openai
```

**Para provider: OpenAI (custos em cloud)**

---

### 📚 DOCUMENTAÇÃO

#### 12. **README.md** 📖
```
Documentação local do MCP Server
Instruções de setup e uso
```

---

### 📊 LOGS & CACHE

#### 13. **server.log** 📋
```
Logs da execução do servidor
Gerado em tempo real quando rodando
```

#### 14. **__pycache__/** 💾
```
Cache Python compilado
Gerado automaticamente
Seguro deletar (será recriado)
```

---

## 🔄 FLUXO DE FUNCIONAMENTO

```
┌─────────────────────────────────────────────────┐
│  VS Code (Continue Extension)                   │
│  User Type: "Como funciona o embeddings?"       │
└────────────────┬────────────────────────────────┘
                 │
                 │ JSON-RPC via stdin
                 │ {"method": "tools/call", "name": "query", ...}
                 ▼
┌─────────────────────────────────────────────────┐
│  server.py (MCP Server)                         │
│  • Recebe JSON-RPC                              │
│  • Parse da requisição                          │
│  • Chama handle_query()                         │
└────────────────┬────────────────────────────────┘
                 │
                 │ Processa query
                 │ 1. FastEmbed: gera embedding (384 dims)
                 │ 2. Qdrant: busca vetorial (top-3)
                 │ 3. Retorna resultados com scores
                 ▼
┌─────────────────────────────────────────────────┐
│  Qdrant (Vector Database)                       │
│  • Query embedding vs 35 documentos             │
│  • Retorna top-3 mais similares                 │
│  • Scores: 70.1%, 69.9%, 67.9%                 │
└────────────────┬────────────────────────────────┘
                 │
                 │ Resultados estruturados
                 ▼
┌─────────────────────────────────────────────────┐
│  server.py (Formata resposta)                   │
│  • JSON-RPC response                            │
│  • Inclui trechos de código                     │
│  • Inclui metadata (arquivo, score)             │
└────────────────┬────────────────────────────────┘
                 │
                 │ JSON-RPC via stdout
                 ▼
┌─────────────────────────────────────────────────┐
│  Continue Extension                             │
│  • Recebe resultados                            │
│  • Inclui no contexto do chat                   │
│  • Envia para ChatGPT com contexto              │
│  • Exibe resposta ao usuário                    │
└─────────────────────────────────────────────────┘
```

---

## 🎯 RESPONSABILIDADES DE CADA ARQUIVO

| Arquivo | Responsabilidade | Crítico? |
|---------|-----------------|----------|
| `server.py` | Lógica MCP + busca | ✅ SIM |
| `qdrant_create_db.py` | Setup da DB | ⚠️ Uma vez |
| `server-http.py` | Alternativa HTTP | ❌ NÃO (experimental) |
| `start-daemon.sh` | Manter rodando | ✅ SIM |
| `start-server.sh` | Iniciar simples | ⚠️ Opcional |
| `.env` | Configuração | ✅ SIM |
| `requirements*.txt` | Dependências | ✅ SIM |
| `README.md` | Documentação | ❌ NÃO |
| `server.log` | Logs | ❌ NÃO (info) |

---

## 📝 COMO USAR CADA ARQUIVO

### Setup Inicial
```bash
# 1. Instalar dependências
pip install -r mcp/qdrant_rag_server/requirements.txt
pip install -r mcp/qdrant_rag_server/requirements-fastembed.txt

# 2. Criar database
python3 mcp/qdrant_rag_server/qdrant_create_db.py

# 3. Verificar .env está configurado
cat mcp/qdrant_rag_server/.env
```

### Iniciar Servidor (Standalone)
```bash
# Simples
python3 mcp/qdrant_rag_server/server.py

# Via script
bash mcp/qdrant_rag_server/start-server.sh

# Via daemon wrapper
bash mcp/qdrant_rag_server/start-daemon.sh
```

### Iniciar via Systemd (Production)
```bash
# Systemd usa start-daemon.sh automaticamente
make mcp-start
```

### Testar Manualmente
```bash
# Send JSON-RPC request
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}' | \
  python3 mcp/qdrant_rag_server/server.py
```

---

## 🔗 INTEGRAÇÃO COM O PROJETO

### Continue Configuration
```json
{
  "mcpServers": {
    "qdrant-mcp": {
      "command": "bash",
      "args": ["...", "mcp/qdrant_rag_server/server.py"]
    }
  }
}
```

### Systemd Service
```ini
[Service]
ExecStart=/bin/bash mcp/qdrant_rag_server/start-daemon.sh
```

### Docker (Futuro)
```dockerfile
COPY mcp/qdrant_rag_server /app/mcp
ENTRYPOINT ["python3", "/app/mcp/server.py"]
```

---

## 🚀 RESUMO RÁPIDO

| Pergunta | Resposta |
|----------|----------|
| **Onde está o servidor MCP?** | `server.py` |
| **Como iniciar?** | `make mcp-start` ou `python3 server.py` |
| **Como parar?** | `make mcp-stop` ou Ctrl+C |
| **Como testar?** | `echo '...' \| python3 server.py` |
| **Como ver logs?** | `make mcp-logs` ou `cat server.log` |
| **Qual provider usar?** | FastEmbed (recomendado) em `.env` |
| **Como recriar DB?** | `python3 qdrant_create_db.py` |
| **Está tudo aqui?** | ✅ SIM! Todos os códigos da integração |

---

## ✅ CONCLUSÃO

**SIM!** Tudo que é relativo à integração entre **Continue (VS Code) ↔ Qdrant** está nesta pasta:

✅ **MCP Server** - server.py  
✅ **Configuração** - .env  
✅ **Database Setup** - qdrant_create_db.py  
✅ **Scripts de Execução** - start-*.sh  
✅ **Dependências** - requirements*.txt  
✅ **Documentação** - README.md  

**Esta é a pasta central de toda a integração!** 🎯

---

**Criado em:** 17 de outubro de 2025  
**Última atualização:** Hoje  
**Status:** ✅ Documentado e Funcional
