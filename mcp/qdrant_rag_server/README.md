Qdrant RAG MCP Server

Este é um servidor MCP (Model Context Protocol) simples para fazer RAG (ingestão e busca semântica) sobre um projeto usando Qdrant como vector database.

**Para integração completa com VS Code, leia `../../INTEGRATION.md`.**

Recursos principais
- Ferramentas MCP expostas:
  - ingest: lê arquivos de um diretório, cria chunks, gera embeddings e upserta no Qdrant.
  - query: embedda a consulta e retorna trechos mais relevantes com metadados.

Requisitos
- Python 3.10+
- Qdrant rodando (ex.: Docker em http://localhost:6333)

Instalação (CPU-only)
1) Crie e ative um venv (opcional, recomendado)
2) Instale dependências mínimas:
   - Base: `pip install -r mcp/qdrant_rag_server/requirements.txt`
   - Escolha um provedor de embeddings:
     - SentenceTransformers (offline/CPU): `pip install -r mcp/qdrant_rag_server/requirements-sentencetransformers.txt`
     - FastEmbed (leve/CPU): `pip install -r mcp/qdrant_rag_server/requirements-fastembed.txt`
     - OpenAI (requere chave): `pip install -r mcp/qdrant_rag_server/requirements-openai.txt`

Configuração
Crie um arquivo .env (opcional) ou exporte variáveis de ambiente:
- QDRANT_URL (ex.: http://localhost:6333)
- QDRANT_API_KEY (se aplicável; Qdrant local default não precisa)
- QDRANT_COLLECTION (default: project_docs)
- EMBEDDINGS_PROVIDER (opções: sentence-transformers, openai; default: sentence-transformers)
- MODEL_NAME (para sentence-transformers; default: all-MiniLM-L6-v2)
- OPENAI_API_KEY (se usar openai)

Uso como servidor MCP (stdio)
- Aponte seu cliente MCP (ex.: Continue, Cline) para executar este servidor via stdio.
  - command: python
  - args: ["mcp/qdrant_rag_server/server.py"]
  - env: conforme .env

Exemplo de configuração (Continue)
No arquivo de configuração do Continue (~/.continue/config.json), adicione:

{
  "mcpServers": {
    "qdrant_rag": {
      "command": "python",
      "args": [
        "mcp/qdrant_rag_server/server.py"
      ],
      "env": {
        "QDRANT_URL": "http://localhost:6333",
        "QDRANT_COLLECTION": "project_docs",
        "EMBEDDINGS_PROVIDER": "sentence-transformers",
        "MODEL_NAME": "all-MiniLM-L6-v2"
      }
    }
  }
}

Ferramentas
1) ingest
   - Parâmetros:
     - directory (str): diretório base para varrer
     - include_globs (list[str], opcional): padrões a incluir; default ["**/*.py","**/*.md","**/*.txt","**/*.json","**/*.yaml","**/*.yml"]
     - exclude_globs (list[str], opcional): padrões a excluir; default ["**/.git/**","**/.venv/**","**/node_modules/**","**/*.ipynb"]
     - chunk_size (int, opcional): tamanho do chunk em caracteres; default 800
     - overlap (int, opcional): sobreposição; default 100
     - collection (str, opcional): coleção do Qdrant; default QDRANT_COLLECTION
   - Retorno: contagem de arquivos indexados e chunks upsertados

2) query
   - Parâmetros:
     - text (str): consulta
     - top_k (int, opcional): default 5
     - collection (str, opcional): default QDRANT_COLLECTION
     - path_prefix (str, opcional): filtra por prefixo de caminho
   - Retorno: lista de hits com score, path, trecho e metadata

Rodando manualmente (debug local)
- Você pode executar o servidor diretamente (não via MCP) para testar ingest e query pelos métodos Python, mas o fluxo esperado é via um cliente MCP.

Notas
- Embeddings default usam sentence-transformers (offline/CPU). Como alternativa leve, você pode usar FastEmbed (EMBEDDINGS_PROVIDER=fastembed). Para resultados melhores, use OpenAI (defina OPENAI_API_KEY e EMBEDDINGS_PROVIDER=openai). Não é necessária GPU.

Diretivas Imperativas
- Nunca executar comandos no terminal automaticamente a partir do VS Code/Copilot (bug conhecido que pode causar loops).
- Sempre gerar scripts de shell idempotentes para operações (setup/diagnóstico/execução) e solicitar que o usuário rode manualmente.
- Os scripts devem imprimir um relatório no stdout e salvar uma cópia em reports/ para análise posterior.
- Não imprimir valores de segredos; apenas indicar se estão definidos.

Script de diagnóstico (não executado automaticamente)
- Após gerar o script, rode manualmente no shell:
  - scripts/mcp_qdrant_report.sh
- O script coleta:
  - Variáveis relevantes (.env e ambiente) sem vazar segredos
  - Saúde do Qdrant, coleções existentes e configuração
  - Situação do Docker (se aplicável)
  - Versões de Python e pacotes, checagem de arquivos do servidor MCP
  - Sugestões de configuração do cliente MCP
