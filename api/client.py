"""
Python client for Qdrant RAG API
Simplifies interaction with the centralized FastAPI server
"""

import json
import requests
from typing import List, Dict, Any, Optional
from pathlib import Path


class QdrantRAGClient:
    """Client for interacting with the Qdrant RAG API."""
    
    def __init__(self, base_url: str = "http://localhost:8000", timeout: int = 30):
        """Initialize the client.
        
        Args:
            base_url: Base URL of the FastAPI server
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
    
    def health_check(self) -> Dict[str, Any]:
        """Check API health status."""
        response = self.session.get(
            f"{self.base_url}/health",
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()
    
    def query(
        self,
        text: str,
        collection: str = "project_docs",
        top_k: int = 5,
        path_prefix: Optional[str] = None,
        project_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Search for documents using semantic similarity.
        
        Args:
            text: Query text
            collection: Collection name to search in
            top_k: Number of results to return
            path_prefix: Filter results by file path prefix
            project_id: Filter results by project ID
            
        Returns:
            Dictionary with search results
        """
        payload = {
            "text": text,
            "collection": collection,
            "top_k": top_k
        }
        
        if path_prefix:
            payload["path_prefix"] = path_prefix
        if project_id:
            payload["project_id"] = project_id
        
        response = self.session.post(
            f"{self.base_url}/query",
            json=payload,
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()
    
    def ingest(
        self,
        directory: str,
        collection: str = "project_docs",
        project_id: Optional[str] = None,
        file_extensions: Optional[List[str]] = None,
        sync: bool = False
    ) -> Dict[str, Any]:
        """Ingest documents from a directory.
        
        Args:
            directory: Path to directory to ingest
            collection: Collection name to store documents
            project_id: Project identifier for filtering
            file_extensions: File extensions to include
            sync: Whether to wait for completion (True) or run async (False)
            
        Returns:
            Dictionary with ingestion status
        """
        if file_extensions is None:
            file_extensions = [".md", ".txt", ".py", ".js", ".ts", ".json", ".yaml", ".yml"]
        
        payload = {
            "directory": str(directory),
            "collection": collection,
            "file_extensions": file_extensions
        }
        
        if project_id:
            payload["project_id"] = project_id
        
        endpoint = "/ingest/sync" if sync else "/ingest"
        
        response = self.session.post(
            f"{self.base_url}{endpoint}",
            json=payload,
            timeout=self.timeout if sync else 10  # Shorter timeout for async
        )
        response.raise_for_status()
        return response.json()
    
    def list_collections(self) -> List[Dict[str, Any]]:
        """List all collections with statistics."""
        response = self.session.get(
            f"{self.base_url}/collections",
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()
    
    def get_collection_stats(self, collection: str) -> Dict[str, Any]:
        """Get detailed statistics for a collection."""
        response = self.session.get(
            f"{self.base_url}/collections/{collection}/stats",
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()
    
    def delete_collection(self, collection: str) -> Dict[str, Any]:
        """Delete a collection and all its data."""
        response = self.session.delete(
            f"{self.base_url}/collections/{collection}",
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()


# -------------------- CLI Interface --------------------
def main():
    """Command-line interface for the RAG client."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Qdrant RAG API Client")
    parser.add_argument("--url", default="http://localhost:8000", help="API base URL")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Health check command
    subparsers.add_parser("health", help="Check API health")
    
    # Query command
    query_parser = subparsers.add_parser("query", help="Search documents")
    query_parser.add_argument("text", help="Search query")
    query_parser.add_argument("--collection", default="project_docs", help="Collection name")
    query_parser.add_argument("--top-k", type=int, default=5, help="Number of results")
    query_parser.add_argument("--path-prefix", help="Filter by path prefix")
    query_parser.add_argument("--project-id", help="Filter by project ID")
    
    # Ingest command
    ingest_parser = subparsers.add_parser("ingest", help="Ingest documents")
    ingest_parser.add_argument("directory", help="Directory to ingest")
    ingest_parser.add_argument("--collection", default="project_docs", help="Collection name")
    ingest_parser.add_argument("--project-id", help="Project identifier")
    ingest_parser.add_argument("--sync", action="store_true", help="Wait for completion")
    ingest_parser.add_argument("--extensions", nargs="+", help="File extensions to include")
    
    # Collections command
    collections_parser = subparsers.add_parser("collections", help="List collections")
    collections_parser.add_argument("--stats", metavar="COLLECTION", help="Get stats for specific collection")
    collections_parser.add_argument("--delete", metavar="COLLECTION", help="Delete collection")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    client = QdrantRAGClient(base_url=args.url)
    
    try:
        if args.command == "health":
            result = client.health_check()
            print(json.dumps(result, indent=2))
        
        elif args.command == "query":
            result = client.query(
                text=args.text,
                collection=args.collection,
                top_k=args.top_k,
                path_prefix=args.path_prefix,
                project_id=args.project_id
            )
            
            print(f"Query: {result['query']}")
            print(f"Collection: {result['collection']}")
            print(f"Total results: {result['total']}")
            print("-" * 50)
            
            for i, doc in enumerate(result['results'], 1):
                print(f"{i}. Score: {doc['score']:.4f}")
                print(f"   File: {doc['metadata'].get('file_path', 'Unknown')}")
                print(f"   Content: {doc['content'][:200]}...")
                print()
        
        elif args.command == "ingest":
            result = client.ingest(
                directory=args.directory,
                collection=args.collection,
                project_id=args.project_id,
                file_extensions=args.extensions,
                sync=args.sync
            )
            print(json.dumps(result, indent=2))
        
        elif args.command == "collections":
            if args.stats:
                result = client.get_collection_stats(args.stats)
                print(json.dumps(result, indent=2))
            elif args.delete:
                result = client.delete_collection(args.delete)
                print(json.dumps(result, indent=2))
            else:
                result = client.list_collections()
                print(f"{'Collection':<20} {'Points':<10} {'Status':<15}")
                print("-" * 50)
                for collection in result:
                    print(f"{collection['name']:<20} {collection['points_count']:<10} {collection['status']:<15}")
    
    except requests.exceptions.RequestException as e:
        print(f"❌ API Error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()