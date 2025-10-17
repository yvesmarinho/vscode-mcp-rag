#!/usr/bin/env bash
# Purpose: Install minimal deps for MCP + Qdrant (CPU-only) with a full report.
# Usage:
#   scripts/mcp_install_deps_report.sh [fastembed|sentence-transformers|openai] [--check]
# Notes:
#   - If --check is provided, no installation is performed; only environment and plan are reported.
#   - Respects the project's imperative directives: script prints to stdout and saves a report in reports/; no secrets are leaked.
set -euo pipefail

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
REPORT_DIR="reports"
REPORT_FILE="$REPORT_DIR/mcp_install_deps_${TIMESTAMP}.md"
mkdir -p "$REPORT_DIR"

log() { echo "$1" | tee -a "$REPORT_FILE"; }
header() { echo -e "\n## $1\n" | tee -a "$REPORT_FILE"; }
kv() { echo "- $1: $2" | tee -a "$REPORT_FILE"; }

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
SRV_DIR="$ROOT_DIR/mcp/qdrant_rag_server"
BASE_REQ="$SRV_DIR/requirements.txt"
FE_REQ="$SRV_DIR/requirements-fastembed.txt"
ST_REQ="$SRV_DIR/requirements-sentencetransformers.txt"
OA_REQ="$SRV_DIR/requirements-openai.txt"

PROVIDER="${1:-${EMBEDDINGS_PROVIDER:-fastembed}}"
MODE_CHECK="false"
if [[ "${2:-}" == "--check" ]]; then MODE_CHECK="true"; fi

header "Contexto"
kv "Data" "$(date -Is)"
kv "Root dir" "$ROOT_DIR"
kv "Provider selecionado" "$PROVIDER"
kv "Modo check-only" "$MODE_CHECK"

header "Python/Pip"
if command -v python3 >/dev/null 2>&1; then
  kv "python3" "$(python3 --version 2>&1 | tr -d '\n')"
else
  kv "python3" "não encontrado"
fi
if command -v pip >/dev/null 2>&1; then
  kv "pip" "$(pip --version 2>&1 | tr -d '\n')"
else
  kv "pip" "não encontrado"
fi

header "Arquivos de requirements"
kv "Base" "$BASE_REQ"
kv "FastEmbed" "$FE_REQ"
kv "SentenceTransformers" "$ST_REQ"
kv "OpenAI" "$OA_REQ"

header "Plano de instalação"
case "$PROVIDER" in
  fastembed)
    kv "Base" "pip install -r $BASE_REQ"
    kv "Provider" "pip install -r $FE_REQ"
    INSTALL_LIST=("$BASE_REQ" "$FE_REQ")
    ;;
  sentence-transformers)
    kv "Base" "pip install -r $BASE_REQ"
    kv "Provider" "pip install -r $ST_REQ"
    INSTALL_LIST=("$BASE_REQ" "$ST_REQ")
    ;;
  openai)
    kv "Base" "pip install -r $BASE_REQ"
    kv "Provider" "pip install -r $OA_REQ"
    INSTALL_LIST=("$BASE_REQ" "$OA_REQ")
    ;;
  *)
    kv "Erro" "Provider desconhecido: $PROVIDER (use fastembed | sentence-transformers | openai)"
    exit 1
    ;;
esac

if [[ "$MODE_CHECK" == "true" ]]; then
  header "Resultado"
  log "Check-only: nenhuma instalação foi realizada."
  log "Relatório salvo em: $REPORT_FILE"
  exit 0
fi

header "Instalação (execução)"
if ! command -v pip >/dev/null 2>&1; then
  kv "Falha" "pip não encontrado; instale pip antes de continuar."
  log "Relatório salvo em: $REPORT_FILE"
  exit 1
fi

for REQ in "${INSTALL_LIST[@]}"; do
  if [[ -f "$REQ" ]]; then
    log "\n### pip install -r $REQ"
    pip install -r "$REQ" 2>&1 | tee -a "$REPORT_FILE" || true
  else
    kv "Aviso" "Arquivo não encontrado: $REQ"
  fi
done

header "Resumo"
kv "Status" "Concluído (verifique erros acima, se houver)"
log "\nRelatório salvo em: $REPORT_FILE"
