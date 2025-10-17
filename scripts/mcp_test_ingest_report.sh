#!/usr/bin/env bash
# Purpose: Test ingest of sample files into Qdrant and generate a report
# Usage: scripts/mcp_test_ingest_report.sh [--dry-run]
# - Without flag: performs actual ingest via Python server
# - With --dry-run: shows plan without calling server

set -euo pipefail

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
REPORT_DIR="reports"
REPORT_FILE="$REPORT_DIR/mcp_test_ingest_${TIMESTAMP}.md"
mkdir -p "$REPORT_DIR"

log() { echo "$1" | tee -a "$REPORT_FILE"; }
header() { echo -e "\n## $1\n" | tee -a "$REPORT_FILE"; }
section() { echo -e "\n### $1\n" | tee -a "$REPORT_FILE"; }
kv() { echo "- $1: $2" | tee -a "$REPORT_FILE"; }
code_block() { echo '```' | tee -a "$REPORT_FILE"; echo "$1" | tee -a "$REPORT_FILE"; echo '```' | tee -a "$REPORT_FILE"; }

DRY_RUN="${1:-}"
if [[ "$DRY_RUN" == "--dry-run" ]]; then
  DRY_RUN="true"
else
  DRY_RUN="false"
fi

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
SRV_DIR="$ROOT_DIR/mcp/qdrant_rag_server"

header "MCP Test Ingest Report"
kv "Generated" "$(date -Is)"
kv "Dry-run mode" "$DRY_RUN"
kv "Project root" "$ROOT_DIR"

# ============================================================================
section "Prerequisites Check"

if ! command -v python3 >/dev/null 2>&1; then
  kv "Error" "python3 not found; cannot proceed"
  log "Report saved: $REPORT_FILE"
  exit 1
fi

if [[ ! -f "$SRV_DIR/server.py" ]]; then
  kv "Error" "server.py not found at $SRV_DIR/server.py"
  log "Report saved: $REPORT_FILE"
  exit 1
fi

kv "python3" "$(python3 --version 2>&1 | tr -d '\n')"
kv "server.py" "found at $SRV_DIR/server.py"

# Check if Qdrant is accessible
QDRANT_URL="${QDRANT_URL:-http://localhost:6333}"
kv "QDRANT_URL" "$QDRANT_URL"

if command -v curl >/dev/null 2>&1; then
  if curl -fsSL "$QDRANT_URL/health" >/dev/null 2>&1; then
    kv "Qdrant health" "OK"
  else
    kv "Qdrant health" "UNREACHABLE (may fail)"
  fi
fi

# ============================================================================
section "Test Ingest Plan"

INGEST_DIR="$ROOT_DIR"  # Ingest repo root as test
INCLUDE_GLOBS='["**/*.py","**/*.md","**/*.txt","**/*.yaml"]'
CHUNK_SIZE=800
OVERLAP=100
COLLECTION="project_docs"

log "Configuration:"
kv "Directory to ingest" "$INGEST_DIR"
kv "Include patterns" "$INCLUDE_GLOBS"
kv "Chunk size" "$CHUNK_SIZE"
kv "Overlap" "$OVERLAP"
kv "Collection" "$COLLECTION"

section "Python Ingest Command"
code_block "python3 << 'EOF'
import sys
import json
sys.path.insert(0, '$SRV_DIR')

# Import server module
from server import Embeddings, QdrantIndex
from qdrant_client import QdrantClient

# Initialize
client = QdrantClient(url='$QDRANT_URL')
embeddings = Embeddings()
index = QdrantIndex(client, '$COLLECTION')

# Ingest
params = {
    'directory': '$INGEST_DIR',
    'include_globs': $INCLUDE_GLOBS,
    'chunk_size': $CHUNK_SIZE,
    'overlap': $OVERLAP,
    'collection': '$COLLECTION'
}

from server import handle_ingest
result = handle_ingest(params, embeddings, index)
print(json.dumps(result, indent=2))
EOF"

# ============================================================================
if [[ "$DRY_RUN" == "true" ]]; then
  header "Dry-Run: Completed"
  log "No ingest was performed. Review the plan above and run without --dry-run to execute."
else
  header "Executing Ingest"
  
  section "Running Ingest..."
  if python3 << 'PYEOF'
import sys
import json
import os

sys.path.insert(0, '$SRV_DIR')

try:
    from server import Embeddings, QdrantIndex
    from qdrant_client import QdrantClient

    client = QdrantClient(url=os.getenv('QDRANT_URL', 'http://localhost:6333'))
    embeddings = Embeddings()
    index = QdrantIndex(client, os.getenv('QDRANT_COLLECTION', 'project_docs'))

    params = {
        'directory': '$INGEST_DIR',
        'include_globs': $INCLUDE_GLOBS,
        'chunk_size': $CHUNK_SIZE,
        'overlap': $OVERLAP,
        'collection': os.getenv('QDRANT_COLLECTION', 'project_docs')
    }

    from server import handle_ingest
    result = handle_ingest(params, embeddings, index)
    print(json.dumps(result, indent=2))
except Exception as e:
    print(f"ERROR: {e}", file=sys.stderr)
    sys.exit(1)
PYEOF
  then
    kv "Ingest status" "SUCCESS"
  else
    kv "Ingest status" "FAILED (check error above)"
  fi
fi

# ============================================================================
header "Report"
log "Full report saved to: $REPORT_FILE"
log "\nNext steps:"
log "1. If ingest succeeded, run a test query: \`scripts/mcp_test_query_report.sh\`"
log "2. For troubleshooting, check: \`INTEGRATION.md\` → Troubleshooting section"
log "3. Review: \`scripts/mcp_qdrant_report.sh\` for full diagnostics"
