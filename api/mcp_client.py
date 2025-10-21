"""
MCP Server that connects to FastAPI Qdrant RAG API
Lightweight MCP wrapper for centralized RAG service
"""

import os
import sys
import json
import logging
from typing import Dict, Any
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class FastAPIRAGClient:
    """Client for connecting to FastAPI RAG service."""
    
    def __init__(self, api_url: str, timeout: int = 30):
        self.api_url = api_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
    
    def query(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Query documents via FastAPI."""
        try:
            response = self.session.post(
                f"{self.api_url}/query",
                json=params,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            result = response.json()
            
            # Format for MCP response
            if result.get("results"):
                formatted_results = []
                for doc in result["results"]:
                    formatted_results.append({
                        "file_path": doc["metadata"].get("file_path", ""),
                        "content": doc["content"][:500] + "..." if len(doc["content"]) > 500 else doc["content"],
                        "score": doc["score"]
                    })
                
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": f"Found {len(formatted_results)} results for: {result['query']}\n\n" +
                                   "\n\n".join([
                                       f"📄 **{r['file_path']}** (score: {r['score']:.3f})\n{r['content']}"
                                       for r in formatted_results
                                   ])
                        }
                    ]
                }
            else:
                return {
                    "content": [
                        {
                            "type": "text", 
                            "text": f"No results found for: {params.get('text', '')}"
                        }
                    ]
                }
                
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"❌ Error connecting to RAG API: {str(e)}"
                    }
                ]
            }
    
    def ingest(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Ingest documents via FastAPI."""
        try:
            # Use sync endpoint for immediate feedback
            response = self.session.post(
                f"{self.api_url}/ingest/sync",
                json=params,
                timeout=300  # Longer timeout for ingestion
            )
            response.raise_for_status()
            
            result = response.json()
            
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"✅ Ingestion completed!\n\n" +
                               f"📁 Directory: {result.get('directory', 'N/A')}\n" +
                               f"📚 Collection: {result.get('collection', 'N/A')}\n" +
                               f"📄 Files processed: {result.get('files_processed', 0)}\n" +
                               f"🔢 Points added: {result.get('points_added', 0)}"
                    }
                ]
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Ingestion request failed: {e}")
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"❌ Error during ingestion: {str(e)}"
                    }
                ]
            }


def mcp_response(id_: str, result: Any = None, error: str = None) -> Dict[str, Any]:
    """Format MCP JSON-RPC response."""
    if error:
        return {
            "jsonrpc": "2.0",
            "id": id_,
            "error": {"code": -1, "message": error}
        }
    else:
        return {
            "jsonrpc": "2.0",
            "id": id_,
            "result": result
        }


def handle_query(params: Dict[str, Any], client: FastAPIRAGClient) -> Dict[str, Any]:
    """Handle query tool call."""
    # Support both string and object parameters
    if isinstance(params, str):
        query_params = {"text": params}
    else:
        query_params = params.copy()
    
    # Set defaults
    if "collection" not in query_params:
        query_params["collection"] = os.getenv("QDRANT_COLLECTION", "project_docs")
    if "top_k" not in query_params:
        query_params["top_k"] = 5
    
    return client.query(query_params)


def handle_ingest(params: Dict[str, Any], client: FastAPIRAGClient) -> Dict[str, Any]:
    """Handle ingest tool call."""
    ingest_params = params.copy()
    
    # Set defaults
    if "collection" not in ingest_params:
        ingest_params["collection"] = os.getenv("QDRANT_COLLECTION", "project_docs")
    
    # Get current working directory if directory is relative
    directory = ingest_params.get("directory", ".")
    if not os.path.isabs(directory):
        # Use current working directory as base
        ingest_params["directory"] = os.path.abspath(directory)
    
    return client.ingest(ingest_params)


def main():
    """Main MCP server loop."""
    # Get API URL from environment
    api_url = os.getenv("FASTAPI_RAG_URL", "http://localhost:8000")
    
    logger.info(f"🚀 MCP FastAPI RAG Client starting...")
    logger.info(f"🔗 Connecting to API: {api_url}")
    
    # Initialize client
    client = FastAPIRAGClient(api_url)
    
    # Test connection
    try:
        response = client.session.get(f"{api_url}/health", timeout=5)
        response.raise_for_status()
        health = response.json()
        logger.info(f"✅ API connection successful: {health}")
    except Exception as e:
        logger.error(f"❌ Cannot connect to API: {e}")
        logger.error("Make sure the FastAPI server is running!")
        sys.exit(1)
    
    logger.info("📡 MCP server ready - waiting for requests...")
    
    # MCP stdio loop
    try:
        for line in sys.stdin:
            try:
                req = json.loads(line.strip())
                method = req.get("method")
                id_ = req.get("id")
                
                if method == "initialize":
                    sys.stdout.write(
                        json.dumps(
                            mcp_response(
                                id_,
                                {
                                    "protocolVersion": "2024-11-05",
                                    "capabilities": {
                                        "tools": {}
                                    },
                                    "serverInfo": {
                                        "name": "fastapi-rag-client",
                                        "version": "1.0.0"
                                    }
                                }
                            )
                        ) + "\n"
                    )
                    sys.stdout.flush()
                
                elif method == "tools/list":
                    tools = [
                        {
                            "name": "query",
                            "description": "Search documents using semantic similarity",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "text": {
                                        "type": "string",
                                        "description": "Search query text"
                                    },
                                    "collection": {
                                        "type": "string", 
                                        "description": "Collection name (optional)"
                                    },
                                    "top_k": {
                                        "type": "integer",
                                        "description": "Number of results (optional)"
                                    },
                                    "path_prefix": {
                                        "type": "string",
                                        "description": "Filter by path prefix (optional)"
                                    },
                                    "project_id": {
                                        "type": "string",
                                        "description": "Filter by project ID (optional)"
                                    }
                                },
                                "required": ["text"]
                            }
                        },
                        {
                            "name": "ingest",
                            "description": "Ingest documents from a directory",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "directory": {
                                        "type": "string",
                                        "description": "Directory path to ingest"
                                    },
                                    "collection": {
                                        "type": "string",
                                        "description": "Collection name (optional)"
                                    },
                                    "project_id": {
                                        "type": "string",
                                        "description": "Project identifier (optional)"
                                    },
                                    "file_extensions": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                        "description": "File extensions to include (optional)"
                                    }
                                },
                                "required": ["directory"]
                            }
                        }
                    ]
                    
                    sys.stdout.write(
                        json.dumps(mcp_response(id_, {"tools": tools})) + "\n"
                    )
                    sys.stdout.flush()
                
                elif method == "tools/call":
                    params = req.get("params", {})
                    name = params.get("name")
                    args = params.get("arguments", {})
                    
                    if name == "query":
                        res = handle_query(args, client)
                    elif name == "ingest":
                        res = handle_ingest(args, client)
                    else:
                        logger.error(f"Unknown tool: {name}")
                        raise ValueError(f"Tool not found: {name}")
                    
                    logger.debug(f"Tool '{name}' executed successfully")
                    sys.stdout.write(json.dumps(mcp_response(id_, res)) + "\n")
                    sys.stdout.flush()
                
                else:
                    logger.warning(f"Method not supported: {method}")
                    sys.stdout.write(
                        json.dumps(
                            mcp_response(id_, error="Method not supported")
                        ) + "\n"
                    )
                    sys.stdout.flush()
                    
            except Exception as e:
                logger.error(f"Error processing request: {str(e)}")
                sys.stdout.write(
                    json.dumps(mcp_response(id_, error=str(e))) + "\n"
                )
                sys.stdout.flush()
                
    except (OSError, ValueError) as e:
        logger.info(f"MCP client stopping: {str(e)}")
    except KeyboardInterrupt:
        logger.info("MCP client interrupted by user")
    except Exception as e:
        logger.error(f"Unexpected error in MCP client: {str(e)}")
    
    logger.info("MCP client shutdown complete")


if __name__ == "__main__":
    main()