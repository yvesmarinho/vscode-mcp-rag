"""
Ultra-Simple MCP Server with HTTP endpoint
One file, zero config, works everywhere
"""

import os
import sys
import json
import uuid
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from threading import Thread
import time

# Simple in-memory storage for demo
documents = {}
embeddings_cache = {}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SimpleRAGHandler(BaseHTTPRequestHandler):
    """Simple HTTP handler for RAG operations."""
    
    def do_GET(self):
        """Handle GET requests."""
        path = urlparse(self.path).path
        
        if path == '/health':
            self.send_json({"status": "healthy", "documents": len(documents)})
        elif path == '/search':
            query = parse_qs(urlparse(self.path).query).get('q', [''])[0]
            results = self.simple_search(query)
            self.send_json({"query": query, "results": results})
        else:
            self.send_error(404)
    
    def do_POST(self):
        """Handle POST requests."""
        path = urlparse(self.path).path
        
        if path == '/add':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            data = json.loads(post_data)
            
            doc_id = str(uuid.uuid4())
            documents[doc_id] = {
                "content": data.get("content", ""),
                "metadata": data.get("metadata", {})
            }
            
            self.send_json({"id": doc_id, "status": "added"})
        else:
            self.send_error(404)
    
    def simple_search(self, query):
        """Ultra-simple text search (no embeddings needed)."""
        results = []
        query_lower = query.lower()
        
        for doc_id, doc in documents.items():
            content = doc["content"].lower()
            if query_lower in content:
                # Simple scoring based on frequency
                score = content.count(query_lower) / len(content.split())
                results.append({
                    "id": doc_id,
                    "content": doc["content"][:200] + "...",
                    "metadata": doc["metadata"],
                    "score": round(score, 4)
                })
        
        # Sort by score
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:5]
    
    def send_json(self, data):
        """Send JSON response."""
        response = json.dumps(data).encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(response)))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(response)


def start_http_server():
    """Start simple HTTP server."""
    port = int(os.getenv("PORT", "8000"))
    server = HTTPServer(('localhost', port), SimpleRAGHandler)
    logger.info(f"🚀 Simple RAG server at http://localhost:{port}")
    server.serve_forever()


def mcp_response(id_: str, result=None, error=None):
    """MCP JSON-RPC response."""
    if error:
        return {"jsonrpc": "2.0", "id": id_, "error": {"code": -1, "message": error}}
    else:
        return {"jsonrpc": "2.0", "id": id_, "result": result}


def main():
    """Main function - can work as MCP server OR HTTP server."""
    
    # Check if we should run as HTTP server
    if len(sys.argv) > 1 and sys.argv[1] == "--http":
        start_http_server()
        return
    
    # Auto-index current directory
    logger.info("📚 Auto-indexing current directory...")
    for root, dirs, files in os.walk("."):
        for file in files:
            if file.endswith(('.md', '.txt', '.py', '.js', '.ts')):
                try:
                    file_path = os.path.join(root, file)
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    doc_id = str(uuid.uuid4())
                    documents[doc_id] = {
                        "content": content,
                        "metadata": {"file_path": file_path}
                    }
                except:
                    continue
    
    logger.info(f"✅ Indexed {len(documents)} documents")
    
    # MCP Server mode
    logger.info("🔌 MCP Server ready")
    
    try:
        for line in sys.stdin:
            try:
                req = json.loads(line.strip())
                method = req.get("method")
                id_ = req.get("id")
                
                if method == "initialize":
                    result = {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {"tools": {}},
                        "serverInfo": {"name": "ultra-simple-rag", "version": "1.0.0"}
                    }
                    sys.stdout.write(json.dumps(mcp_response(id_, result)) + "\n")
                    sys.stdout.flush()
                
                elif method == "tools/list":
                    tools = [{
                        "name": "search",
                        "description": "Search documents",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "query": {"type": "string", "description": "Search query"}
                            },
                            "required": ["query"]
                        }
                    }]
                    sys.stdout.write(json.dumps(mcp_response(id_, {"tools": tools})) + "\n")
                    sys.stdout.flush()
                
                elif method == "tools/call":
                    params = req.get("params", {})
                    name = params.get("name")
                    args = params.get("arguments", {})
                    
                    if name == "search":
                        query = args.get("query", "")
                        results = []
                        query_lower = query.lower()
                        
                        for doc_id, doc in documents.items():
                            content = doc["content"].lower()
                            if query_lower in content:
                                score = content.count(query_lower) / max(len(content.split()), 1)
                                results.append({
                                    "file": doc["metadata"].get("file_path", "unknown"),
                                    "content": doc["content"][:300] + "...",
                                    "score": round(score, 4)
                                })
                        
                        results.sort(key=lambda x: x["score"], reverse=True)
                        
                        if results:
                            text = f"Found {len(results)} results for '{query}':\n\n"
                            for i, r in enumerate(results[:3], 1):
                                text += f"{i}. **{r['file']}** (score: {r['score']:.3f})\n"
                                text += f"   {r['content']}\n\n"
                        else:
                            text = f"No results found for '{query}'"
                        
                        result = {"content": [{"type": "text", "text": text}]}
                        sys.stdout.write(json.dumps(mcp_response(id_, result)) + "\n")
                        sys.stdout.flush()
                    
                    else:
                        sys.stdout.write(json.dumps(mcp_response(id_, error="Unknown tool")) + "\n")
                        sys.stdout.flush()
                
                else:
                    sys.stdout.write(json.dumps(mcp_response(id_, error="Method not supported")) + "\n")
                    sys.stdout.flush()
                    
            except Exception as e:
                sys.stdout.write(json.dumps(mcp_response(id_, error=str(e))) + "\n")
                sys.stdout.flush()
                
    except KeyboardInterrupt:
        logger.info("Server stopped")


if __name__ == "__main__":
    main()