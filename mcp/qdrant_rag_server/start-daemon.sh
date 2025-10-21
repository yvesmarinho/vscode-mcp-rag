#!/bin/bash
# Wrapper script to keep MCP server running as daemon

# Get the dynamic project directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo "Script directory: $SCRIPT_DIR"
echo "Project directory: $PROJECT_DIR"

cd "$PROJECT_DIR"

# Set up logging
LOG_FILE="$SCRIPT_DIR/server.log"
PID_FILE="$SCRIPT_DIR/server.pid"
mkdir -p "$(dirname "$LOG_FILE")"

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

echo "Using Python: $PYTHON_EXE" >> "$LOG_FILE"

# Function to start daemon
start_daemon() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting MCP daemon..." >> "$LOG_FILE"
    
    # Create daemon function
    daemon_loop() {
        while true; do
            echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting MCP server..." >> "$LOG_FILE"
            
            # Create a unique named pipe for communication
            FIFO="/tmp/mcp_fifo_$$"
            mkfifo "$FIFO" 2>/dev/null || true
            
            # Start server with timeout
            timeout 3600 "$PYTHON_EXE" \
                mcp/qdrant_rag_server/server.py < "$FIFO" >> "$LOG_FILE" 2>&1 &
            
            SERVER_PID=$!
            echo $SERVER_PID > "$PID_FILE"
            
            # Keep the named pipe open
            exec 3> "$FIFO"
            
            # Wait for process
            wait $SERVER_PID
            EXIT_CODE=$?
            
            exec 3>&-
            rm -f "$FIFO"
            
            echo "[$(date '+%Y-%m-%d %H:%M:%S')] MCP server stopped (exit code: $EXIT_CODE), restarting in 5s..." >> "$LOG_FILE"
            sleep 5
        done
    }
    
    # Run daemon in background, detached from terminal
    nohup bash -c "$(declare -f daemon_loop); daemon_loop" > /dev/null 2>&1 &
    DAEMON_PID=$!
    echo $DAEMON_PID > "${PID_FILE}.daemon"
    
    echo "MCP Daemon started with PID: $DAEMON_PID"
    echo "Logs: $LOG_FILE"
    echo "PID file: $PID_FILE"
    echo ""
    echo "To stop: pkill -F ${PID_FILE}.daemon"
    echo "To check logs: tail -f $LOG_FILE"
}

# Check if already running
if [ -f "${PID_FILE}.daemon" ]; then
    DAEMON_PID=$(cat "${PID_FILE}.daemon")
    if kill -0 $DAEMON_PID 2>/dev/null; then
        echo "MCP Daemon already running (PID: $DAEMON_PID)"
        echo "To stop: pkill -F ${PID_FILE}.daemon"
        exit 0
    else
        echo "Stale PID file found, removing..."
        rm -f "${PID_FILE}.daemon" "$PID_FILE"
    fi
fi

# Start the daemon
start_daemon
