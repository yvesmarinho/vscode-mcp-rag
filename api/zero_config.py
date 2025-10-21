#!/usr/bin/env python3
"""
Zero-Config MCP RAG Server
Usage: python zero_config.py
"""

import os
import sys
import json
import re
from pathlib import Path


def search_files(query, directory="."):
    """Simple file search without embeddings."""
    results = []
    query_words = query.lower().split()
    
    # Find files
    for ext in ['.md', '.txt', '.py', '.js', '.ts', '.json', '.yaml']:
        for file_path in Path(directory).rglob(f'*{ext}'):
            try:
                content = file_path.read_text(encoding='utf-8', errors='ignore')
                content_lower = content.lower()
                
                # Score based on word matches
                score = sum(content_lower.count(word) for word in query_words)
                if score > 0:
                    # Get relevant snippet
                    lines = content.split('\n')
                    relevant_lines = []
                    for i, line in enumerate(lines):
                        if any(word in line.lower() for word in query_words):
                            start = max(0, i-1)
                            end = min(len(lines), i+2)
                            relevant_lines.extend(lines[start:end])
                            if len(relevant_lines) > 10:
                                break
                    
                    snippet = '\n'.join(relevant_lines[:10])
                    results.append({
                        'file': str(file_path),
                        'score': score,
                        'snippet': snippet[:400] + '...' if len(snippet) > 400 else snippet
                    })
            except Exception:
                continue
    
    return sorted(results, key=lambda x: x['score'], reverse=True)[:5]


def mcp_server():
    """Minimal MCP server."""
    for line in sys.stdin:
        try:
            req = json.loads(line.strip())
            id_ = req.get("id")
            method = req.get("method")
            
            if method == "initialize":
                response = {
                    "jsonrpc": "2.0",
                    "id": id_,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {"tools": {}},
                        "serverInfo": {"name": "zero-config-rag", "version": "1.0.0"}
                    }
                }
            elif method == "tools/list":
                response = {
                    "jsonrpc": "2.0",
                    "id": id_,
                    "result": {
                        "tools": [{
                            "name": "search",
                            "description": "Search project files",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "query": {"type": "string", "description": "Search query"}
                                },
                                "required": ["query"]
                            }
                        }]
                    }
                }
            elif method == "tools/call":
                params = req.get("params", {})
                if params.get("name") == "search":
                    query = params.get("arguments", {}).get("query", "")
                    results = search_files(query)
                    
                    if results:
                        text = f"🔍 Found {len(results)} matches for '{query}':\n\n"
                        for i, r in enumerate(results, 1):
                            text += f"**{i}. {r['file']}** (matches: {r['score']})\n"
                            text += f"```\n{r['snippet']}\n```\n\n"
                    else:
                        text = f"❌ No matches found for '{query}'"
                    
                    response = {
                        "jsonrpc": "2.0",
                        "id": id_,
                        "result": {"content": [{"type": "text", "text": text}]}
                    }
                else:
                    response = {
                        "jsonrpc": "2.0",
                        "id": id_,
                        "error": {"code": -1, "message": "Unknown tool"}
                    }
            else:
                response = {
                    "jsonrpc": "2.0",
                    "id": id_,
                    "error": {"code": -1, "message": "Method not supported"}
                }
            
            print(json.dumps(response))
            sys.stdout.flush()
            
        except Exception as e:
            error_response = {
                "jsonrpc": "2.0",
                "id": req.get("id") if 'req' in locals() else None,
                "error": {"code": -1, "message": str(e)}
            }
            print(json.dumps(error_response))
            sys.stdout.flush()


if __name__ == "__main__":
    # Check if running as HTTP server for testing
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        query = input("Enter search query: ")
        results = search_files(query)
        for r in results:
            print(f"📄 {r['file']} (score: {r['score']})")
            print(f"   {r['snippet'][:100]}...")
            print()
    else:
        mcp_server()