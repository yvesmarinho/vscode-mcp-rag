#!/bin/bash
# Stop MCP daemon script

# Get the dynamic project directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

PID_FILE="$SCRIPT_DIR/server.pid"
DAEMON_PID_FILE="$SCRIPT_DIR/server.pid.daemon"

echo "Stopping MCP daemon..."

# Stop daemon process
if [ -f "$DAEMON_PID_FILE" ]; then
    DAEMON_PID=$(cat "$DAEMON_PID_FILE")
    if kill -0 $DAEMON_PID 2>/dev/null; then
        echo "Stopping daemon (PID: $DAEMON_PID)..."
        kill $DAEMON_PID
        sleep 2
        
        # Force kill if still running
        if kill -0 $DAEMON_PID 2>/dev/null; then
            echo "Force killing daemon..."
            kill -9 $DAEMON_PID
        fi
        
        echo "Daemon stopped."
    else
        echo "Daemon not running."
    fi
    rm -f "$DAEMON_PID_FILE"
else
    echo "No daemon PID file found."
fi

# Stop server process
if [ -f "$PID_FILE" ]; then
    SERVER_PID=$(cat "$PID_FILE")
    if kill -0 $SERVER_PID 2>/dev/null; then
        echo "Stopping server (PID: $SERVER_PID)..."
        kill $SERVER_PID
        sleep 2
        
        # Force kill if still running
        if kill -0 $SERVER_PID 2>/dev/null; then
            echo "Force killing server..."
            kill -9 $SERVER_PID
        fi
        
        echo "Server stopped."
    fi
    rm -f "$PID_FILE"
fi

# Clean up any remaining processes
pkill -f "mcp/qdrant_rag_server/server.py" 2>/dev/null || true
pkill -f "start-daemon.sh" 2>/dev/null || true

# Clean up named pipes
rm -f /tmp/mcp_fifo_* 2>/dev/null || true

echo "MCP daemon cleanup complete."