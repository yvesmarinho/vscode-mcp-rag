#!/usr/bin/env bash
# Purpose: Quick-start guide to set up Qdrant + MCP for VS Code
# This script generates a step-by-step plan and verifies prerequisites,
# then saves the full plan to a report file.
# Usage: scripts/mcp_quickstart_report.sh [--setup]
# - Without --setup: shows plan and checks environment
# - With --setup: generates setup files (.env, etc.)

set -euo pipefail

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
REPORT_DIR="reports"
REPORT_FILE="$REPORT_DIR/mcp_quickstart_${TIMESTAMP}.md"
mkdir -p "$REPORT_DIR"

log() { echo "$1" | tee -a "$REPORT_FILE"; }
header() { echo -e "\n## $1\n" | tee -a "$REPORT_FILE"; }
section() { echo -e "\n### $1\n" | tee -a "$REPORT_FILE"; }
kv() { echo "- $1: $2" | tee -a "$REPORT_FILE"; }
code_block() { echo '```' | tee -a "$REPORT_FILE"; echo "$1" | tee -a "$REPORT_FILE"; echo '```' | tee -a "$REPORT_FILE"; }

MODE_SETUP="${1:-}"
if [[ "$MODE_SETUP" == "--setup" ]]; then
  MODE_SETUP="true"
else
  MODE_SETUP="false"
fi

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
SRV_DIR="$ROOT_DIR/mcp/qdrant_rag_server"
ENV_FILE="$SRV_DIR/.env"
ENV_EXAMPLE="$SRV_DIR/.env.example"

header "MCP + Qdrant Quick-Start Guide"
kv "Generated" "$(date -Is)"
kv "Project root" "$ROOT_DIR"
kv "Setup mode" "$MODE_SETUP"

# ============================================================================
header "Prerequisites Check"

section "1. Docker & Qdrant"
if command -v docker >/dev/null 2>&1; then
  kv "docker" "installed"
  RUNNING=$(docker ps --format '{{.Names}}' | grep -i qdrant || true)
  if [[ -n "$RUNNING" ]]; then
    kv "Qdrant container" "running"
  else
    kv "Qdrant container" "NOT running (need to start)"
  fi
else
  kv "docker" "NOT installed (required)"
fi

section "2. Python Environment"
if command -v python3 >/dev/null 2>&1; then
  PY_VER=$(python3 --version 2>&1 | cut -d' ' -f2)
  kv "python3" "v$PY_VER"
else
  kv "python3" "NOT found"
fi

if [[ -d "$ROOT_DIR/.venv" ]]; then
  kv ".venv" "exists"
else
  kv ".venv" "does not exist (create with: python3 -m venv .venv)"
fi

section "3. Configuration Files"
if [[ -f "$ENV_FILE" ]]; then
  kv ".env" "exists at $ENV_FILE"
else
  kv ".env" "NOT found (will create from .env.example if --setup)"
fi

if [[ -f "$ENV_EXAMPLE" ]]; then
  kv ".env.example" "exists"
else
  kv ".env.example" "NOT found"
fi

# ============================================================================
header "Step-by-Step Setup Plan"

section "Step 1: Ensure Qdrant is Running"
log "Start Qdrant container (if not already running):"
code_block "docker run -d -p 6333:6333 -p 6334:6334 \\
  -v qdrant_storage:/qdrant/storage \\
  --name qdrant_local \\
  qdrant/qdrant:latest"
log "Verify health:"
code_block "curl http://localhost:6333/health"

section "Step 2: Create Python Virtual Environment"
log "Activate venv (one-time):"
code_block "python3 -m venv .venv
source .venv/bin/activate  # macOS/Linux"

section "Step 3: Install MCP Server Dependencies"
log "Choose ONE embeddings provider:"
log "\n**Option A: FastEmbed (lightweight, CPU-friendly, recommended)**"
code_block "pip install -r mcp/qdrant_rag_server/requirements.txt
pip install -r mcp/qdrant_rag_server/requirements-fastembed.txt"

log "\n**Option B: SentenceTransformers (offline, good quality)**"
code_block "pip install -r mcp/qdrant_rag_server/requirements.txt
pip install -r mcp/qdrant_rag_server/requirements-sentencetransformers.txt"

log "\n**Option C: OpenAI (cloud, requires API key)**"
code_block "pip install -r mcp/qdrant_rag_server/requirements.txt
pip install -r mcp/qdrant_rag_server/requirements-openai.txt"

section "Step 4: Configure MCP Server (.env)"
log "Copy template and edit:"
code_block "cp mcp/qdrant_rag_server/.env.example mcp/qdrant_rag_server/.env
# Edit .env with your QDRANT_URL, EMBEDDINGS_PROVIDER, MODEL_NAME, etc."

section "Step 5: Create Qdrant Collection"
log "Initialize collection:"
code_block "QDRANT_URL=http://localhost:6333 \\
QDRANT_COLLECTION=project_docs \\
VECTOR_SIZE=384 \\
python3 mcp/qdrant_rag_server/qdrant_create_db.py"

section "Step 6: Configure VS Code Client"
log "Choose ONE: Continue or Cline extension"

log "\n**For Continue:**"
code_block "Edit ~/.continue/config.json:
{
  \"mcpServers\": {
    \"qdrant_rag\": {
      \"command\": \"python\",
      \"args\": [\"mcp/qdrant_rag_server/server.py\"],
      \"env\": {
        \"QDRANT_URL\": \"http://localhost:6333\",
        \"QDRANT_COLLECTION\": \"project_docs\",
        \"EMBEDDINGS_PROVIDER\": \"fastembed\",
        \"MODEL_NAME\": \"BAAI/bge-small-en-v1.5\"
      }
    }
  }
}"

log "\n**For Cline:**"
log "Use Cline settings UI or \`cline_config.json\` to register MCP server with same params."

section "Step 7: Test Ingest"
log "Ask your AI agent (Continue/Cline) in VS Code:"
code_block "Use the ingest tool to index my project starting from the repo root.
Include .py, .md, .yaml files."

section "Step 8: Test Query"
log "Ask a question to verify Qdrant search works:"
code_block "What are the main classes and modules in this project?"

# ============================================================================
if [[ "$MODE_SETUP" == "true" ]]; then
  header "Automatic Setup (--setup mode)"
  
  if [[ ! -f "$ENV_FILE" ]]; then
    section "Creating .env from .env.example"
    if [[ -f "$ENV_EXAMPLE" ]]; then
      cp "$ENV_EXAMPLE" "$ENV_FILE"
      kv ".env created" "$ENV_FILE"
      log "**Edit $ENV_FILE with your actual configuration before use.**"
    else
      kv "Error" ".env.example not found; cannot auto-create .env"
    fi
  else
    kv ".env already exists" "skipping creation"
  fi
fi

# ============================================================================
header "Next Steps"
log "1. Follow the Step-by-Step Setup Plan above"
log "2. Run diagnostic to verify everything: \`scripts/mcp_qdrant_report.sh\`"
log "3. Check \`INTEGRATION.md\` for detailed reference and troubleshooting"
log "4. Review report saved here: $REPORT_FILE"
