#!/bin/bash
# Wrapper script to keep MCP server running as daemon

cd /home/yves_marinho/Documentos/DevOps/Projetos/ai_project_template

# Set up logging
LOG_FILE="mcp/qdrant_rag_server/server.log"
mkdir -p "$(dirname "$LOG_FILE")"

# Keep server running with restart on failure
while true; do
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting MCP server..." >> "$LOG_FILE"
    
    # Create a named pipe for communication
    mkfifo /tmp/mcp_fifo 2>/dev/null || true
    
    # Keep stdin open with empty reader and start server
    timeout 3600 /home/yves_marinho/Documentos/DevOps/Projetos/ai_project_template/.venv/bin/python3 \
        mcp/qdrant_rag_server/server.py < /tmp/mcp_fifo >> "$LOG_FILE" 2>&1 &
    
    PID=$!
    
    # Keep the named pipe open
    exec 3> /tmp/mcp_fifo
    
    # Wait for process
    wait $PID
    EXIT_CODE=$?
    
    exec 3>&-
    rm -f /tmp/mcp_fifo
    
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] MCP server stopped (exit code: $EXIT_CODE), restarting in 5s..." >> "$LOG_FILE"
    sleep 5
done
