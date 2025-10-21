# 📖 Como Usar o MCP Vector Project

Guia de uso do MCP Vector Project após configuração completa.

## 🎯 Visão Geral

O MCP Vector Project permite busca semântica em documentos através do VS Code. Após a configuração, você pode:

- 🔍 **Buscar** conteúdo semanticamente
- 📚 **Indexar** novos documentos
- 💬 **Conversar** com o assistente sobre seu código

## 🚀 Comandos Essenciais

### Verificar Status
```bash
make diagnose              # Status completo do sistema
make qdrant-health        # Verificar se Qdrant está rodando
make mcp-status           # Status do servidor MCP
```

### Indexar Documentos
```bash
make ingest               # Indexar todo o projeto
# ou
cd mcp/qdrant_rag_server && python ingest_documents.py
```

### Testar Busca
```bash
make test-query           # Teste rápido de busca
```

## 💬 Uso no VS Code

### Continue Extension

**1. Busca Simples:**
```
@qdrant_rag query "como configurar docker"
```

**2. Busca com Filtros:**
```
@qdrant_rag query {"text": "configuração", "path_prefix": "docs/", "top_k": 5}
```

**3. Indexar Novo Diretório:**
```
@qdrant_rag ingest {"directory": "./nova_pasta", "collection": "project_docs"}
```

### Cline Extension

Mesmo uso que Continue - os comandos são idênticos:
```
@qdrant_rag query "explicar função main"
```

## 🔧 Configurações Avançadas

### Mudar Modelo de Embedding

Edite `mcp/qdrant_rag_server/.env`:
```env
# Para melhor qualidade (mais lento)
EMBEDDINGS_PROVIDER=sentence-transformers
MODEL_NAME=all-mpnet-base-v2

# Para máxima qualidade (API paga)
EMBEDDINGS_PROVIDER=openai
OPENAI_API_KEY=sk-...
OPENAI_EMBEDDING_MODEL=text-embedding-3-large
```

### Usar Qdrant Remoto

```env
QDRANT_URL=https://your-cluster.qdrant.io
QDRANT_API_KEY=your-api-key
```

### Múltiplas Coleções

Para diferentes projetos:
```env
QDRANT_COLLECTION=frontend_docs      # Para projeto frontend
QDRANT_COLLECTION=backend_docs       # Para projeto backend
QDRANT_COLLECTION=shared_docs        # Para documentação compartilhada
```

## 🛠️ Resolução de Problemas

### "Qdrant não está respondendo"
```bash
make qdrant-start         # Reiniciar Qdrant
docker ps                 # Verificar containers
```

### "MCP Server não encontrado"
```bash
make configure-vscode     # Recriar configuração
code .                    # Reabrir VS Code
```

### "Nenhum resultado encontrado"
```bash
make ingest              # Re-indexar documentos
make test-query          # Testar busca básica
```

### "Dependências faltando"
```bash
make install-fastembed   # Reinstalar dependências
source .venv/bin/activate
pip list | grep qdrant   # Verificar instalação
```

## 📊 Monitoramento

### Logs do MCP Server
```bash
make mcp-logs            # Ver logs em tempo real
```

### Estatísticas do Qdrant
```bash
curl http://localhost:6333/collections/project_docs
```

### Status Completo
```bash
make diagnose > status.txt   # Salvar diagnóstico completo
```

## 🎯 Dicas de Uso

### 1. Buscas Eficazes
- Use **termos específicos**: "configuração docker" vs "docker"
- Combine **conceitos**: "logging configuration python"
- Use **sinônimos**: "setup", "configuration", "config"

### 2. Organização
- **Uma coleção por projeto** grande
- **Coleções separadas** para docs vs código
- **Prefixos de path** para filtrar resultados

### 3. Performance
- **FastEmbed**: Rápido, CPU-only, boa qualidade
- **SentenceTransformers**: Melhor qualidade, suporte GPU
- **OpenAI**: Máxima qualidade, custo por uso

## 🚀 Próximos Passos

1. **Indexe seu projeto**: `make ingest`
2. **Teste no VS Code**: `@qdrant_rag query "test"`
3. **Explore a documentação**: [`docs/`](./docs/)
4. **Configure para outros projetos**: Copie o pacote exportado

## 📚 Documentação Completa

- [Quick Start](docs/setup/QUICKSTART.md) - Configuração rápida
- [Configuration](docs/project/CONFIGURATION.md) - Configuração detalhada  
- [Integration](docs/project/INTEGRATION.md) - Integração completa
- [Docker Guide](docs/docker/DOCKER.md) - Guia Docker completo

---

**💡 Dica:** Mantenha o Qdrant sempre rodando (`make qdrant-start`) para melhor experiência!