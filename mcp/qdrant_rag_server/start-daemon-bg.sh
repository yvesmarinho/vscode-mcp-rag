#!/bin/bash
# Wrapper script to keep MCP server running as daemon in background

# Get the dynamic project directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo "Script directory: $SCRIPT_DIR"
echo "Project directory: $PROJECT_DIR"

cd "$PROJECT_DIR"

# Set up logging and PID file
LOG_FILE="$SCRIPT_DIR/server.log"
PID_FILE="$SCRIPT_DIR/daemon.pid"
mkdir -p "$(dirname "$LOG_FILE")"

# Check if daemon is already running
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if kill -0 "$PID" 2>/dev/null; then
        echo "MCP daemon is already running (PID: $PID)"
        exit 1
    else
        echo "Removing stale PID file"
        rm -f "$PID_FILE"
    fi
fi

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
    echo "ERROR: No Python executable found!" >> "$LOG_FILE"
    exit 1
fi

echo "Using Python: $PYTHON_EXE"

# Start daemon in background and detach from terminal
nohup bash -c '
    echo "$$" > "'"$PID_FILE"'"
    echo "[$(date "+%Y-%m-%d %H:%M:%S")] MCP daemon started (PID: $$)" >> "'"$LOG_FILE"'"
    
    # Keep server running with restart on failure
    while true; do
        echo "[$(date "+%Y-%m-%d %H:%M:%S")] Starting MCP server..." >> "'"$LOG_FILE"'"
        
        # Create a unique named pipe for communication
        FIFO="/tmp/mcp_fifo_$$"
        mkfifo "$FIFO" 2>/dev/null || true
        
        # Start server with timeout
        timeout 3600 "'"$PYTHON_EXE"'" \
            mcp/qdrant_rag_server/server.py < "$FIFO" >> "'"$LOG_FILE"'" 2>&1 &
        
        SERVER_PID=$!
        
        # Keep the named pipe open
        exec 3> "$FIFO"
        
        # Wait for process
        wait $SERVER_PID
        EXIT_CODE=$?
        
        exec 3>&-
        rm -f "$FIFO"
        
        echo "[$(date "+%Y-%m-%d %H:%M:%S")] MCP server stopped (exit code: $EXIT_CODE), restarting in 5s..." >> "'"$LOG_FILE"'"
        sleep 5
    done
' &>/dev/null &

DAEMON_PID=$!
sleep 1  # Give daemon time to write PID file

echo "MCP daemon started in background (PID: $DAEMON_PID)"
echo "Log file: $LOG_FILE"
echo "PID file: $PID_FILE"
echo ""
echo "To stop the daemon, run: ./stop-daemon.sh"
echo "To view logs, run: tail -f $LOG_FILE"
echo "To check status, run: ./status-daemon.sh"