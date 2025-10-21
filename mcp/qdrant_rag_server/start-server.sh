#!/bin/bash
# Dynamic MCP Server starter

# Get the dynamic project directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo "Script directory: $SCRIPT_DIR"
echo "Project directory: $PROJECT_DIR"

cd "$PROJECT_DIR"

# Find Python executable dynamically
PYTHON_EXE=""
if [ -f "$PROJECT_DIR/.venv/bin/python3" ]; then
    PYTHON_EXE="$PROJECT_DIR/.venv/bin/python3"
elif [ -f "$PROJECT_DIR/.venv/bin/python" ]; then
    PYTHON_EXE="$PROJECT_DIR/.venv/bin/python"
elif command -v python3 &> /dev/null; then
    PYTHON_EXE="python3"
elif command -v python &> /dev/null; then
    PYTHON_EXE="python"
else
    echo "ERROR: No Python executable found!"
    exit 1
fi

echo "Using Python: $PYTHON_EXE"
exec "$PYTHON_EXE" mcp/qdrant_rag_server/server.py
