# Pull Request: Fix MCP Qdrant RAG Server - Environment & Indexing Issues

## 📋 **Resumo**
Este PR corrige problemas críticos no MCP Qdrant RAG Server relacionados a dependências Python, configuração de ambiente e indexação de documentos, especialmente para arquivos `.vscode`.

## 🔍 **Problemas Identificados**
1. **Dependências circulares** em `pyproject.toml` e `requirements2.txt`
2. **Parsing incorreto** do arquivo `.env` com comentários inline
3. **Nomes de collections hardcoded** causando indexação em collections erradas
4. **Scripts de verificação** usando campos de payload incorretos
5. **Detecção inconsistente** de arquivos `.vscode` durante indexação
6. **Arquivos corrompidos** com sintaxe inválida

## 🛠️ **Mudanças Implementadas**

### 1. **Correção de Dependências Python**
#### `pyproject.toml`
```diff
- name = "audrey-influencer-management"
+ name = "influencer-mgnt"

- readme = "README_OLD.md"
+ readme = "README.md"

[project.optional-dependencies]
all = [
-    "audrey-influencer-management[dev,prod,social]",
+    # Removed self-dependency to prevent circular reference
     "fastapi>=0.104.0",
     "uvicorn>=0.24.0",
     # ... other dependencies
]
```

#### `requirements2.txt`
```diff
- -e .[dev,prod,social]
+ # Removed self-referencing editable install
```

### 2. **Correção do Arquivo de Ambiente**
#### `.env`
```diff
# Para qdrant_create_db.py (criar coleção)
- VECTOR_SIZE=384  # 384=FastEmbed/MiniLM, 768=SentenceTransformers, 1536=OpenAI
- DISTANCE=COSINE  # COSINE | DOT | EUCLID
+ # 384=FastEmbed/MiniLM, 768=SentenceTransformers, 1536=OpenAI
+ VECTOR_SIZE=384
+ # COSINE | DOT | EUCLID
+ DISTANCE=COSINE
```

### 3. **Correção de Collections Hardcoded**
#### `qdrant_create_db.py`
```diff
+ def load_env_file(env_path):
+     """Carrega variáveis de ambiente de um arquivo .env"""
+     if path.exists(env_path):
+         with open(env_path, 'r', encoding='utf-8') as f:
+             for line in f:
+                 line = line.strip()
+                 if line and not line.startswith('#') and '=' in line:
+                     key, value = line.split('=', 1)
+                     os.environ[key] = value

+ # Detecta dinamicamente o diretório usando __file__
+ SCRIPT_DIR = path.dirname(path.abspath(__file__))
+ env_file = path.join(SCRIPT_DIR, '.env')
+ load_env_file(env_file)
```

#### `ingest_documents.py`
```diff
- collection="project_docs",
+ collection=collection_name,
```

### 4. **Correção dos Scripts de Verificação**
#### `scripts/debug_collection.py`
```diff
- filename = payload.get("filename", "N/A")
- content_size = len(payload.get("content", ""))
- chunk_index = payload.get("chunk_index", "N/A")
+ path_name = payload.get("path", "N/A")
+ content_size = len(payload.get("text", ""))

# Detecção robusta de arquivos .vscode
+ basename = path_name.split("/")[-1] if path_name != "N/A" else ""
+ vscode_dir = path.join(PROJECT_DIR, ".vscode")
+ is_vscode = (
+     is_vscode
+     or (basename and path.exists(path.join(vscode_dir, basename)))
+ )
```

#### `check_vscode_files.py` - **Reescrito Completamente**
- Removido código duplicado e corrompido
- Implementada detecção robusta de arquivos `.vscode`
- Adicionado tratamento de erros adequado
- Corrigidos campos de payload (`path`/`text` em vez de `filename`/`content`)

### 5. **Melhorias nos Scripts de Ingestão**
#### `scripts/ingest_vscode_only.py`
```diff
+ # Detecta dinamicamente o diretório do script usando __file__
+ SCRIPT_DIR = path.dirname(path.abspath(__file__))
+ PARENT_DIR = path.dirname(SCRIPT_DIR)
+ PROJECT_DIR = path.dirname(path.dirname(PARENT_DIR))

+ def load_env_file(env_path):
+     """Carrega variáveis de ambiente de um arquivo .env"""
+     # Implementation for dynamic environment loading
```

## 📊 **Resultados dos Testes**

### **Antes das Correções:**
- ❌ Erro de dependência circular: `pip install` falhava
- ❌ `.env` parsing error: comentários inline causavam problemas
- ❌ Collections erradas: documentos indexados em `project_docs` em vez de `influencer-mgnt`
- ❌ Verificação falhava: 0 arquivos `.vscode` detectados apesar de 25 pontos indexados
- ❌ Scripts corrompidos: sintaxe inválida bloqueava execução

### **Depois das Correções:**
- ✅ **Ambiente Python**: Instalação sem erros, dependências resolvidas
- ✅ **Conexão Qdrant**: http://localhost:6333 funcionando corretamente
- ✅ **Indexação completa**: 395 arquivos, 6.474 chunks, 242 pontos
- ✅ **Arquivos .vscode**: 12 arquivos únicos com 100% de cobertura
- ✅ **Scripts funcionais**: Todos executam sem erros de sintaxe

### **Comando de Validação:**
```bash
# Execução bem-sucedida
cd mcp/qdrant_rag_server
python3 ingest_documents.py
# Resultado: 395 files_indexed, 6474 chunks, 242 points

python3 check_vscode_files.py
# Resultado: 12/12 arquivos (100.0% coverage)
```

## 🔧 **Arquivos Modificados**

1. **`pyproject.toml`** - Correção de nome do projeto e dependências
2. **`requirements2.txt`** - Remoção de auto-dependência
3. **`.env`** - Correção de comentários inline
4. **`qdrant_create_db.py`** - Adição de detecção dinâmica de paths
5. **`ingest_documents.py`** - Correção de collection hardcoded
6. **`scripts/debug_collection.py`** - Correção de campos de payload e detecção .vscode
7. **`check_vscode_files.py`** - Reescrita completa do arquivo
8. **`scripts/ingest_vscode_only.py`** - Melhorias na detecção de ambiente

## 🧪 **Como Testar**

1. **Instalar dependências:**
   ```bash
   cd mcp/qdrant_rag_server
   pip install -r requirements.txt
   ```

2. **Verificar ambiente:**
   ```bash
   python3 -c "import os; print('✅ Environment OK')"
   ```

3. **Executar indexação:**
   ```bash
   python3 ingest_documents.py
   ```

4. **Validar .vscode:**
   ```bash
   python3 check_vscode_files.py
   ```

5. **Debug detalhado:**
   ```bash
   python3 scripts/debug_collection.py
   ```

## 🎯 **Impacto**

- **Confiabilidade**: Sistema agora funciona consistentemente
- **Manutenibilidade**: Código limpo, sem dependências circulares
- **Precisão**: 100% de cobertura de arquivos .vscode
- **Escalabilidade**: Detecção dinâmica de paths facilita portabilidade
- **Debugging**: Scripts de verificação funcionais para troubleshooting

## ✅ **Critérios de Aceitação**

- [x] Dependências Python instaladas sem erros
- [x] Arquivo .env parseado corretamente
- [x] Qdrant conecta em http://localhost:6333
- [x] Indexação completa funciona (395 arquivos)
- [x] Arquivos .vscode detectados (100% cobertura)
- [x] Scripts de verificação executam sem erros
- [x] Collection `influencer-mgnt` operacional
- [x] Todos os testes passam

## 🚀 **Próximos Passos**

Após merge deste PR, o MCP Qdrant RAG Server estará pronto para:
1. Configuração no VS Code
2. Queries semânticas na base de conhecimento
3. Integração com workflow de desenvolvimento
4. Expansion para novos tipos de documentos

---

**Reviewers:** @team-leads
**Labels:** `bugfix`, `environment`, `indexing`, `mcp-server`
**Priority:** High
**Estimated Review Time:** 30 minutes
