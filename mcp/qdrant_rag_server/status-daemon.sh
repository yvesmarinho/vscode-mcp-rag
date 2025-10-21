#!/bin/bash
# Check MCP daemon status

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_FILE="$SCRIPT_DIR/daemon.pid"
LOG_FILE="$SCRIPT_DIR/server.log"

echo "=== MCP Daemon Status ==="

if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if kill -0 "$PID" 2>/dev/null; then
        echo "✅ Daemon is running (PID: $PID)"
        
        # Check for server processes
        SERVER_PIDS=$(pgrep -f "mcp/qdrant_rag_server/server.py")
        if [ -n "$SERVER_PIDS" ]; then
            echo "✅ MCP server processes: $SERVER_PIDS"
        else
            echo "⚠️  No MCP server processes found"
        fi
        
        # Show recent log entries
        echo ""
        echo "=== Recent Log Entries ==="
        if [ -f "$LOG_FILE" ]; then
            tail -n 5 "$LOG_FILE"
        else
            echo "No log file found"
        fi
        
    else
        echo "❌ Daemon not running (stale PID file)"
        echo "Removing stale PID file: $PID_FILE"
        rm -f "$PID_FILE"
    fi
else
    echo "❌ Daemon not running (no PID file)"
fi

echo ""
echo "=== Files ==="
echo "PID file: $PID_FILE"
echo "Log file: $LOG_FILE"