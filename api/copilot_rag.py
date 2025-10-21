"""
GitHub Copilot Compatible RAG Server
Simple HTTP API that Copilot can query via extensions
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.parse
from pathlib import Path


class CopilotRAGHandler(BaseHTTPRequestHandler):
    """HTTP handler compatible with GitHub Copilot extensions."""
    
    def do_GET(self):
        """Handle GET requests for search."""
        parsed_url = urllib.parse.urlparse(self.path)
        query_params = urllib.parse.parse_qs(parsed_url.query)
        
        if parsed_url.path == '/search':
            query = query_params.get('q', [''])[0]
            results = self.search_documents(query)
            self.send_json_response(results)
        elif parsed_url.path == '/health':
            self.send_json_response({"status": "healthy", "server": "copilot-rag"})
        else:
            self.send_error(404, "Not found")
    
    def do_POST(self):
        """Handle POST requests."""
        if self.path == '/search':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            query = data.get('query', '')
            results = self.search_documents(query)
            self.send_json_response(results)
        else:
            self.send_error(404, "Not found")
    
    def search_documents(self, query):
        """Simple document search."""
        if not query:
            return {"results": [], "query": query}
        
        results = []
        query_lower = query.lower()
        
        # Search common file types
        extensions = ['.md', '.txt', '.py', '.js', '.ts', '.json', '.yaml', '.yml']
        
        for ext in extensions:
            for file_path in Path('.').rglob(f'*{ext}'):
                try:
                    if file_path.is_file() and file_path.stat().st_size < 1024*1024:  # Max 1MB
                        content = file_path.read_text(encoding='utf-8', errors='ignore')
                        content_lower = content.lower()
                        
                        if query_lower in content_lower:
                            # Find relevant lines
                            lines = content.split('\n')
                            relevant_lines = []
                            
                            for i, line in enumerate(lines):
                                if query_lower in line.lower():
                                    start = max(0, i-2)
                                    end = min(len(lines), i+3)
                                    context = lines[start:end]
                                    relevant_lines.extend(context)
                                    break
                            
                            snippet = '\n'.join(relevant_lines)
                            if len(snippet) > 300:
                                snippet = snippet[:300] + '...'
                            
                            results.append({
                                'file': str(file_path.relative_to('.')),
                                'content': snippet,
                                'score': content_lower.count(query_lower)
                            })
                
                except Exception:
                    continue
        
        # Sort by relevance
        results.sort(key=lambda x: x['score'], reverse=True)
        return {"results": results[:10], "query": query, "total": len(results)}
    
    def send_json_response(self, data):
        """Send JSON response with CORS headers."""
        response_json = json.dumps(data, indent=2)
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        self.wfile.write(response_json.encode('utf-8'))
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests."""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def log_message(self, format, *args):
        """Override to reduce log spam."""
        pass


def start_server(port=8080):
    """Start the HTTP server."""
    server = HTTPServer(('localhost', port), CopilotRAGHandler)
    print(f"🚀 Copilot RAG Server running on http://localhost:{port}")
    print(f"📚 Search endpoint: http://localhost:{port}/search?q=your_query")
    print(f"❤️  Health check: http://localhost:{port}/health")
    print("\n🧪 Test with:")
    print(f"   curl 'http://localhost:{port}/search?q=docker'")
    print(f"   curl -X POST http://localhost:{port}/search -d '{{\"query\":\"authentication\"}}'")
    print("\n🛑 Press Ctrl+C to stop")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Server stopped")


if __name__ == "__main__":
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    start_server(port)