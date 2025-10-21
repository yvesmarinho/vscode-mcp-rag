#!/usr/bin/env python3
"""
Test script for FastAPI Qdrant RAG Server
Validates the API functionality before full deployment
"""

import time
import requests
import json
from pathlib import Path

def test_api():
    """Test the FastAPI server functionality."""
    base_url = "http://localhost:8000"
    
    print("🧪 Testing FastAPI Qdrant RAG Server...")
    
    # Wait for server to be ready
    print("⏳ Waiting for server to start...")
    for i in range(30):
        try:
            response = requests.get(f"{base_url}/health", timeout=2)
            if response.status_code == 200:
                print("✅ Server is ready!")
                break
        except requests.exceptions.RequestException:
            pass
        time.sleep(1)
        if i % 5 == 0:
            print(f"   Still waiting... ({i}s)")
    else:
        print("❌ Server did not start within 30 seconds")
        return False
    
    # Test health endpoint
    print("\n1. Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health")
        health = response.json()
        print(f"   Status: {health.get('api', 'unknown')}")
        print(f"   Qdrant: {health.get('qdrant', 'unknown')}")
        print(f"   Embeddings: {health.get('embeddings', 'unknown')}")
    except Exception as e:
        print(f"   ❌ Health check failed: {e}")
        return False
    
    # Test collections list
    print("\n2. Testing collections endpoint...")
    try:
        response = requests.get(f"{base_url}/collections")
        collections = response.json()
        print(f"   Found {len(collections)} collections")
        for col in collections:
            print(f"   - {col['name']}: {col['points_count']} points")
    except Exception as e:
        print(f"   ❌ Collections list failed: {e}")
    
    # Test query with simple text
    print("\n3. Testing query endpoint...")
    try:
        query_data = {
            "text": "test query",
            "collection": "project_docs",
            "top_k": 3
        }
        response = requests.post(f"{base_url}/query", json=query_data)
        result = response.json()
        print(f"   Query: '{result.get('query', 'N/A')}'")
        print(f"   Results: {result.get('total', 0)}")
        if result.get('results'):
            for i, doc in enumerate(result['results'][:2], 1):
                score = doc.get('score', 0)
                path = doc.get('metadata', {}).get('file_path', 'unknown')
                print(f"   {i}. {path} (score: {score:.3f})")
    except Exception as e:
        print(f"   ❌ Query test failed: {e}")
    
    # Test ingest with current directory
    print("\n4. Testing ingest endpoint...")
    try:
        # Create a test document
        test_dir = Path("test_docs")
        test_dir.mkdir(exist_ok=True)
        
        test_file = test_dir / "test.md"
        test_file.write_text("""
# Test Document

This is a test document for the FastAPI RAG server.

## Features
- Document ingestion
- Semantic search
- Vector embeddings

## Configuration
The server supports multiple embedding providers including FastEmbed.
""")
        
        ingest_data = {
            "directory": str(test_dir.absolute()),
            "collection": "test_collection",
            "project_id": "test_project"
        }
        
        print(f"   Ingesting: {test_dir.absolute()}")
        response = requests.post(f"{base_url}/ingest/sync", json=ingest_data)
        result = response.json()
        
        print(f"   Status: {result.get('status', 'unknown')}")
        print(f"   Files: {result.get('files_processed', 0)}")
        print(f"   Points: {result.get('points_added', 0)}")
        
        # Clean up
        test_file.unlink()
        test_dir.rmdir()
        
    except Exception as e:
        print(f"   ❌ Ingest test failed: {e}")
    
    # Test query on ingested data
    print("\n5. Testing query on ingested data...")
    try:
        query_data = {
            "text": "embedding providers",
            "collection": "test_collection",
            "top_k": 2
        }
        response = requests.post(f"{base_url}/query", json=query_data)
        result = response.json()
        print(f"   Found {result.get('total', 0)} results")
        if result.get('results'):
            doc = result['results'][0]
            print(f"   Best match: {doc.get('metadata', {}).get('file_path', 'unknown')}")
            print(f"   Score: {doc.get('score', 0):.3f}")
    except Exception as e:
        print(f"   ❌ Query test failed: {e}")
    
    print("\n✅ API testing completed!")
    return True

if __name__ == "__main__":
    success = test_api()
    exit(0 if success else 1)