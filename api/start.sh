#!/bin/bash
# Start FastAPI Qdrant RAG Server

set -e

echo "🚀 Starting FastAPI Qdrant RAG Server..."

# Get the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source .venv/bin/activate

# Upgrade pip first
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚙️  Creating .env from example..."
    cp .env.example .env
    echo "✏️  Please edit .env with your configuration if needed"
fi

# Load environment variables
if [ -f ".env" ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Check if Qdrant is running
echo "🔍 Checking Qdrant connection..."
QDRANT_URL=${QDRANT_URL:-http://localhost:6333}
if curl -s "$QDRANT_URL/collections" > /dev/null 2>&1; then
    echo "✅ Qdrant is running at $QDRANT_URL"
else
    echo "⚠️  Warning: Cannot connect to Qdrant at $QDRANT_URL"
    echo "   Make sure Qdrant is running: docker run -p 6333:6333 qdrant/qdrant"
fi

# Start the server
echo "🚀 Starting FastAPI server..."
API_HOST=${API_HOST:-0.0.0.0}
API_PORT=${API_PORT:-8000}

echo "📡 Server will be available at: http://$API_HOST:$API_PORT"
echo "📚 API docs available at: http://$API_HOST:$API_PORT/docs"
echo ""
echo "Press Ctrl+C to stop the server"

python main.py