# ✅ Docker Setup Checklist

Use este checklist para verificar se tudo está pronto para usar Qdrant.

---

## 📋 Pre-Flight Check

- [ ] Docker está instalado (`docker --version`)
- [ ] Docker Compose está instalado (`docker-compose --version`)
- [ ] Portas 6333 e 6334 estão livres
- [ ] Você tem permissão para criar volumes Docker

---

## 🚀 Quick Start (5 min)

### 1. Navegar para pasta Docker
```bash
cd docker/
```
- [ ] Confirmado: você está em `/docker/` (mesmo nível do `docker-compose.yaml`)

### 2. Iniciar Container
```bash
docker-compose up -d
```
- [ ] Sem erros de saída
- [ ] Container iniciado

### 3. Verificar Status
```bash
docker-compose ps
```
- [ ] STATUS mostra: "Up X seconds (healthy)" ✅
- [ ] Se não, aguarde 30+ segundos e tente novamente

### 4. Testar Saúde
```bash
curl http://localhost:6333/health
```
- [ ] Resposta: `{"status":"ok"}`
- [ ] Se recusar conexão, aguarde mais 30 segundos

---

## 🔧 Configuration Check

### 5. API Key (Opcional)

**Para desenvolvimento local (SEM API key):**
```bash
# Deixe a variável vazia ou não configure
# docker-compose.yaml já tem QDRANT_API_KEY vazio
```
- [ ] Nada a fazer (padrão seguro)

**Para produção (COM API key):**
```bash
# Crie arquivo docker/.env
QDRANT_API_KEY=your-secure-key-here

# Reinicie
docker-compose down
docker-compose up -d
```
- [ ] `.env` criado em `docker/`
- [ ] `QDRANT_API_KEY` definido
- [ ] Container reiniciado
- [ ] Health check passa: `curl -H "api-key: your-key" http://localhost:6333/health`

---

## 🧪 Integration Check

### 6. Python MCP Server Setup

```bash
# Navegar para mcp server
cd ../mcp/qdrant_rag_server/

# Criar virtual environment (se não existir)
python3 -m venv ../../.venv

# Ativar
source ../../.venv/bin/activate  # macOS/Linux
# ou
.venv\Scripts\activate           # Windows

# Instalar dependências
pip install -r requirements.txt
pip install -r requirements-fastembed.txt  # ou outro provider
```
- [ ] venv criado e ativado
- [ ] Dependências instaladas sem erro

### 7. Configurar MCP Server

```bash
# Copiar template
cp .env.example .env

# Editar .env (ajustar se necessário)
# QDRANT_URL=http://localhost:6333
# EMBEDDINGS_PROVIDER=fastembed
# etc.
```
- [ ] `.env` criado em `mcp/qdrant_rag_server/`
- [ ] Valores confirmados (QDRANT_URL, EMBEDDINGS_PROVIDER, etc.)

### 8. Criar Coleção no Qdrant

```bash
QDRANT_URL=http://localhost:6333 \
QDRANT_COLLECTION=project_docs \
VECTOR_SIZE=384 \
python3 qdrant_create_db.py
```
- [ ] Comando executado sem erro
- [ ] Confirmação de coleção criada

### 9. Testar Ingestão

```bash
# Plano (sem fazer alterações)
bash ../../scripts/mcp_test_ingest_report.sh --dry-run

# Ingestão real
bash ../../scripts/mcp_test_ingest_report.sh
```
- [ ] Arquivos encontrados
- [ ] Embeddings gerados
- [ ] Dados ingeridos no Qdrant
- [ ] Relatório salvo em `reports/`

### 10. Testar Query

```bash
# Executar manual (ou via VS Code client)
python3 -c "
from qdrant_client import QdrantClient
c = QdrantClient('http://localhost:6333')
result = c.search(
    collection_name='project_docs',
    query_vector=[0.1]*384,  # dummy vector
    limit=5
)
print(f'Search result: {len(result)} items')
"
```
- [ ] Conexão bem-sucedida
- [ ] Search retorna resultados (mesmo que dummy vector)

---

## 🎯 VS Code Integration Check

### 11. Configurar Continue (ou Cline)

```bash
# Abrir VS Code
code .

# Instalar extensões (se não tiver):
# - Python (Microsoft)
# - Pylance (Microsoft)
# - Continue (Continue)
# ou
# - Cline (Saoud Rizwan)
```
- [ ] VS Code aberto
- [ ] Extensões instaladas

### 12. Configurar MCP Server em Continue

1. Abrir Continue settings
2. Adicionar MCP Server:
   ```json
   {
     "mcpServers": {
       "qdrant_rag": {
         "command": "python",
         "args": [
           "/absolute/path/to/mcp/qdrant_rag_server/server.py"
         ],
         "env": {
           "QDRANT_URL": "http://localhost:6333",
           "QDRANT_COLLECTION": "project_docs",
           "EMBEDDINGS_PROVIDER": "fastembed"
         }
       }
     }
   }
   ```
- [ ] MCP Server adicionado
- [ ] Path absoluto correto
- [ ] Variáveis de ambiente configuradas

### 13. Testar Ingestão via Chat

1. Abrir Chat do Continue
2. Executar: `@qdrant_rag ingest /path/to/files`
3. Verificar resposta
- [ ] Tool executada sem erro
- [ ] Mensagem de sucesso retornada
- [ ] Dados aparecem em `curl http://localhost:6333/collections/project_docs`

### 14. Testar Query via Chat

1. Abrir Chat do Continue
2. Executar: `@qdrant_rag query "search term"`
3. Verificar resultados
- [ ] Query retorna resultados relevantes
- [ ] Snippets de código aparecem
- [ ] Scores de relevância mostrados

---

## 📊 Verification Summary

### Data Flow Check
```
VS Code Chat
    ↓
MCP Server (Continue/Cline)
    ↓
Embeddings (FastEmbed/etc)
    ↓
Qdrant (Docker)
    ↓
Collections storage
```
- [ ] Cada etapa funcionando
- [ ] Dados fluindo corretamente

### Storage Check
```bash
# Verificar volume
docker volume inspect docker_qdrant_storage

# Verificar coleção
curl http://localhost:6333/collections
# Esperado: collections contém "project_docs"

# Verificar pontos
curl http://localhost:6333/collections/project_docs
# Esperado: points_count > 0
```
- [ ] Volume existe
- [ ] Coleção criada
- [ ] Pontos ingeridos

### Health Check
```bash
# Status
docker-compose ps
# Esperado: Status = "Up X (healthy)"

# Health endpoint
curl http://localhost:6333/health
# Esperado: {"status":"ok"}
```
- [ ] Container saudável
- [ ] Endpoint acessível

---

## 🆘 Troubleshooting

Se algo não funcionar, use este guia:

| Problema | Solução | Verificar |
|----------|---------|-----------|
| Container não inicia | `docker-compose logs qdrant` | Mensagem de erro |
| Connection refused | Aguarde 30s + `docker-compose ps` | Status = healthy |
| Porta em uso | `lsof -i :6333` | Qual processo? |
| Dados perdidos | Check volume: `docker volume ls` | Existe? |
| MCP não conecta | Verify path absolutizado em config | Path correto? |
| Query não retorna | Check: coleção existe + dados ingeridos | `curl .../collections` |

---

## 📚 Documentation Reference

| Situação | Leia |
|----------|------|
| Preciso de quick start | DOCKER_QUICK_REF.md |
| Quero entender mudanças | DOCKER_IMPROVEMENTS.md |
| Preciso de referência completa | DOCKER.md |
| Quero ver diagramas | DOCKER_ARCHITECTURE.md |
| Preciso de índice | DOCKER_INDEX.md |

---

## ✨ Success Criteria

When this checklist is complete:

✅ **Docker Container**
- Qdrant rodando em `localhost:6333`
- Health check passando
- Volumes persistindo dados

✅ **MCP Server**
- Python venv configurado
- Dependências instaladas
- Coleção criada no Qdrant
- Ingestão funcionando

✅ **VS Code Integration**
- Continue/Cline configurado
- MCP Server conectado
- Query/ingestão funcionando no chat

✅ **Full Workflow**
- Dados ingerindo → Qdrant
- Queries retornando resultados
- VS Code chat acessando dados

---

## 🎉 Next Steps

After completing this checklist:

1. **Start indexing your project:**
   ```bash
   # Via CLI
   bash scripts/mcp_test_ingest_report.sh
   
   # Via VS Code
   # @qdrant_rag ingest /path/to/your/project
   ```

2. **Test queries:**
   ```bash
   # Via CLI (manual test)
   python3 -c "..."
   
   # Via VS Code
   # @qdrant_rag query "your question"
   ```

3. **Use in chat workflow:**
   - Ask questions in Continue/Cline
   - Results include relevant code
   - Context from your project available

---

## 📝 Status

- [ ] All checks complete
- [ ] No errors encountered
- [ ] System ready for production

**Date Completed:** _________________

**Status:** _____ Ready / _____ Needs Work

---

Print this checklist or save as PDF for reference! 📋
