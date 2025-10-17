#!/usr/bin/env python3
"""
MCP Qdrant Server - HTTP version for daemon/systemd deployment
This version runs an HTTP server instead of waiting for stdin,
making it suitable for systemd services and background operation.
"""
import os
import sys
import json
import uuid
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import List, Dict, Any, Optional
from threading import Thread

from qdrant_client import QdrantClient
from qdrant_client.http import models as qm
from dotenv import load_dotenv

# Load environment
load_dotenv()

# -------------------- HTTP Server --------------------
class MCPRequestHandler(BaseHTTPRequestHandler):
    """HTTP handler for MCP requests (tools/list and tools/call)"""
    
    server_embeddings = None
    server_indexes = {}
    server_client = None
    server_collection = None
    
    def do_POST(self):
        """Handle POST requests with JSON-RPC 2.0"""
        if self.path != "/":
            self.send_error(404, "Not Found")
            return
        
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            req = json.loads(body.decode('utf-8'))
        except Exception as e:
            self.send_error(400, f"Bad Request: {e}")
            return
        
        id_ = req.get("id")
        method = req.get("method")
        params = req.get("params") or {}
        
        try:
            if method == "tools/list":
                res = self.list_tools()
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(self.mcp_response(id_, res)).encode())
            elif method == "tools/call":
                name = params.get("name")
                args = params.get("arguments") or {}
                
                if name == "ingest":
                    res = self.handle_ingest(args)
                elif name == "query":
                    res = self.handle_query(args)
                else:
                    raise ValueError(f"Tool not found: {name}")
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(self.mcp_response(id_, res)).encode())
            else:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(self.mcp_response(id_, error="Method not supported")).encode())
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(self.mcp_response(id_, error=str(e))).encode())
    
    def do_GET(self):
        """Health check endpoint"""
        if self.path == "/health":
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok"}).encode())
        else:
            self.send_error(404, "Not Found")
    
    def log_message(self, format, *args):
        """Suppress logging to stderr"""
        pass
    
    @staticmethod
    def mcp_response(id_: str, result: Any = None, error: str = None) -> Dict:
        """Format a JSON-RPC 2.0 response"""
        resp = {"jsonrpc": "2.0"}
        if id_ is not None:
            resp["id"] = id_
        if error:
            resp["error"] = {"code": -1, "message": error}
        else:
            resp["result"] = result
        return resp
    
    @staticmethod
    def list_tools() -> Dict:
        """List available tools"""
        return {
            "tools": [
                {
                    "name": "ingest",
                    "description": "Ingest documents into Qdrant",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "collection": {"type": "string", "description": "Collection name"},
                            "documents": {"type": "array", "description": "List of documents"},
                        },
                        "required": ["documents"],
                    },
                },
                {
                    "name": "query",
                    "description": "Search documents in Qdrant",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "collection": {"type": "string", "description": "Collection name"},
                            "query": {"type": "string", "description": "Query text"},
                            "limit": {"type": "number", "description": "Max results"},
                        },
                        "required": ["query"],
                    },
                },
            ]
        }
    
    def handle_ingest(self, params: Dict) -> Dict:
        """Handle ingest tool call"""
        # Placeholder - would implement actual ingest logic
        return {"status": "ok", "message": "Ingest tool called"}
    
    def handle_query(self, params: Dict) -> Dict:
        """Handle query tool call"""
        # Placeholder - would implement actual query logic
        return {"status": "ok", "message": "Query tool called"}


def run_http_server(host: str = "127.0.0.1", port: int = 8765):
    """Run HTTP server for MCP"""
    server = HTTPServer((host, port), MCPRequestHandler)
    print(f"MCP HTTP Server running on {host}:{port}")
    print(f"Health: GET http://{host}:{port}/health")
    print(f"Tools: POST http://{host}:{port}/ with JSON-RPC 2.0 requests")
    server.serve_forever()


if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    
    # Initialize Qdrant client
    qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
    qdrant_key = os.getenv("QDRANT_API_KEY")
    
    try:
        client = QdrantClient(url=qdrant_url, api_key=qdrant_key)
        MCPRequestHandler.server_client = client
        print(f"✅ Connected to Qdrant at {qdrant_url}")
    except Exception as e:
        print(f"❌ Failed to connect to Qdrant: {e}")
        sys.exit(1)
    
    # Run server
    run_http_server(host="127.0.0.1", port=8765)
