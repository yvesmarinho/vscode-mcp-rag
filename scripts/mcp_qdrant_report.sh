#!/usr/bin/env bash
# Purpose: Diagnostic report for MCP Qdrant RAG setup without executing commands automatically from the assistant.
# This script is intended to be run manually by the user.
set -euo pipefail

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
REPORT_DIR="reports"
REPORT_FILE="$REPORT_DIR/mcp_qdrant_report_${TIMESTAMP}.md"

mkdir -p "$REPORT_DIR"

log() {
  echo "$1" | tee -a "$REPORT_FILE"
}

header() {
  echo "\n## $1\n" | tee -a "$REPORT_FILE"
}

kv() {
  local k="$1"; shift
  local v="$1"; shift || true
  echo "- $k: $v" | tee -a "$REPORT_FILE"
}

bool_has() {
  if [ -n "${1:-}" ]; then echo "true"; else echo "false"; fi
}

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
SERVER_DIR="$ROOT_DIR/mcp/qdrant_rag_server"
ENV_FILE="$SERVER_DIR/.env"

header "Contexto"
kv "Data" "$(date -Is)"
kv "Host" "$(uname -a)"
kv "Shell" "${SHELL:-unknown}"
kv "Root dir" "$ROOT_DIR"

header "Variáveis de Ambiente (.env e ambiente)"
if [ -f "$ENV_FILE" ]; then
  kv ".env encontrado" "$ENV_FILE"
else
  kv ".env encontrado" "não"
fi

# Carrega env file sem exportar segredos
QDRANT_URL_VAL="${QDRANT_URL:-}"
QDRANT_API_KEY_SET="$(bool_has "${QDRANT_API_KEY:-}")"
QDRANT_COLLECTION_VAL="${QDRANT_COLLECTION:-project_docs}"
EMBEDDINGS_PROVIDER_VAL="${EMBEDDINGS_PROVIDER:-sentence-transformers}"
MODEL_NAME_VAL="${MODEL_NAME:-all-MiniLM-L6-v2}"
OPENAI_API_KEY_SET="$(bool_has "${OPENAI_API_KEY:-}")"
OPENAI_EMBEDDING_MODEL_VAL="${OPENAI_EMBEDDING_MODEL:-text-embedding-3-small}"

if [ -f "$ENV_FILE" ]; then
  # shellcheck disable=SC2046
  set -a && . "$ENV_FILE" && set +a || true
  # Reload masked values after .env
  QDRANT_URL_VAL="${QDRANT_URL:-$QDRANT_URL_VAL}"
  QDRANT_API_KEY_SET="$(bool_has "${QDRANT_API_KEY:-}")"
  QDRANT_COLLECTION_VAL="${QDRANT_COLLECTION:-$QDRANT_COLLECTION_VAL}"
  EMBEDDINGS_PROVIDER_VAL="${EMBEDDINGS_PROVIDER:-$EMBEDDINGS_PROVIDER_VAL}"
  MODEL_NAME_VAL="${MODEL_NAME:-$MODEL_NAME_VAL}"
  OPENAI_API_KEY_SET="$(bool_has "${OPENAI_API_KEY:-}")"
  OPENAI_EMBEDDING_MODEL_VAL="${OPENAI_EMBEDDING_MODEL:-$OPENAI_EMBEDDING_MODEL_VAL}"
fi

kv "QDRANT_URL" "${QDRANT_URL_VAL:-unset}"
kv "QDRANT_API_KEY set" "$QDRANT_API_KEY_SET"
kv "QDRANT_COLLECTION" "$QDRANT_COLLECTION_VAL"
kv "EMBEDDINGS_PROVIDER" "$EMBEDDINGS_PROVIDER_VAL"
kv "MODEL_NAME" "$MODEL_NAME_VAL"
kv "OPENAI_API_KEY set" "$OPENAI_API_KEY_SET"
kv "OPENAI_EMBEDDING_MODEL" "$OPENAI_EMBEDDING_MODEL_VAL"

header "Qdrant (Docker/Serviço)"
# Tentativa de detectar docker e container qdrant
if command -v docker >/dev/null 2>&1; then
  kv "docker disponível" "sim"
  QDRANT_CONTAINERS=$(docker ps --format '{{.ID}}\t{{.Image}}\t{{.Names}}\t{{.Ports}}' | grep -i qdrant || true)
  if [ -n "$QDRANT_CONTAINERS" ]; then
    log "\nContainers Qdrant em execução:"
    echo "$QDRANT_CONTAINERS" | tee -a "$REPORT_FILE"
  else
    kv "container qdrant em execução" "não detectado"
  fi
else
  kv "docker disponível" "não"
fi

# Healthcheck via HTTP (sem segredos)
header "Qdrant Health"
if command -v curl >/dev/null 2>&1; then
  if [ -n "${QDRANT_URL_VAL:-}" ]; then
    kv "Endpoint" "$QDRANT_URL_VAL/healthz"
    curl -fsSL "$QDRANT_URL_VAL/healthz" | tee -a "$REPORT_FILE" || echo "(falha)" | tee -a "$REPORT_FILE"
  else
    log "QDRANT_URL não definido; pulando healthcheck"
  fi
else
  kv "curl disponível" "não"
fi

header "Coleções do Qdrant"
if command -v curl >/dev/null 2>&1 && [ -n "${QDRANT_URL_VAL:-}" ]; then
  curl -fsSL "$QDRANT_URL_VAL/collections" | tee -a "$REPORT_FILE" || echo "(falha)" | tee -a "$REPORT_FILE"
else
  log "curl indisponível ou QDRANT_URL não definido; pulando"
fi

header "Python e Pacotes"
if command -v python3 >/dev/null 2>&1; then
  kv "python3" "$(python3 --version 2>&1 | tr -d '\n')"
  if [ -f "$SERVER_DIR/requirements.txt" ]; then
    kv "requirements.txt" "$SERVER_DIR/requirements.txt"
  fi
  if command -v pip >/dev/null 2>&1; then
    kv "pip" "$(pip --version 2>&1 | tr -d '\n')"
  fi
else
  kv "python3" "não encontrado"
fi

header "Arquivos do servidor MCP"
kv "server.py" "$(test -f "$SERVER_DIR/server.py" && echo 'existe' || echo 'não encontrado')"
kv "README.md" "$(test -f "$SERVER_DIR/README.md" && echo 'existe' || echo 'não encontrado')"
kv "requirements.txt" "$(test -f "$SERVER_DIR/requirements.txt" && echo 'existe' || echo 'não encontrado')"
kv ".env.example" "$(test -f "$SERVER_DIR/.env.example" && echo 'existe' || echo 'não encontrado')"

header "Sugestões de Próximos Passos"
cat <<'EOF' | tee -a "$REPORT_FILE"
- Verifique se o Qdrant está acessível na URL informada.
- Ajuste .env no diretório do servidor MCP com as variáveis necessárias.
- Configure o cliente MCP no VS Code/extension para executar server.py via stdio.
- Use a tool "ingest" para indexar seu projeto e "query" para buscar.
EOF

log "\nRelatório salvo em: $REPORT_FILE"
