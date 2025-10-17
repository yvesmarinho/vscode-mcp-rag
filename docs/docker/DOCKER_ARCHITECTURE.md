# Docker Architecture Diagram

## Overall Integration

```
┌────────────────────────────────────────────────────────────────────┐
│                     VS Code + MCP Client                           │
│  (Continue Extension / Cline)                                      │
└──────────────────────────┬───────────────────────────────────────────┘
                           │
                           │ MCP Protocol (stdio)
                           │
┌──────────────────────────▼───────────────────────────────────────────┐
│              MCP Server (Python)                                      │
│        mcp/qdrant_rag_server/server.py                               │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │ • ingest tool     → chunks files → generate embeddings     │    │
│  │ • query tool      → search vectors → return results        │    │
│  │ • Providers: FastEmbed, SentenceTransformers, OpenAI       │    │
│  └─────────────────────────────────────────────────────────────┘    │
└──────────────────────────┬───────────────────────────────────────────┘
                           │
                           │ HTTP/gRPC Connections
                           │ (qdrant_client library)
                           │
                ┌──────────┴──────────┐
                │                     │
                │ Port 6333 (REST)    │
                │ Port 6334 (gRPC)    │
                ▼                     ▼
    ┌───────────────────────────────────────────┐
    │      Docker Container: qdrant             │
    │  ┌───────────────────────────────────────┐│
    │  │  Qdrant Server                        ││
    │  │  • Vector store                       ││
    │  │  • Collections storage                ││
    │  │  • HTTP REST API                      ││
    │  │  • gRPC API                           ││
    │  │  • Health check (/health)             ││
    │  └───────────────────────────────────────┘│
    │                                           │
    │  Volume: qdrant_storage (Named Volume)   │
    │  └─ /qdrant/storage (persistent)         │
    │                                           │
    │  Network: app-network (bridge)           │
    │  Health Check: curl /health (30s)        │
    │  Logging: JSON rotation (100MB/10 files) │
    │                                           │
    │  Environment: QDRANT_API_KEY (optional)  │
    └───────────────────────────────────────────┘
```

---

## Data Flow: Ingest

```
User in VS Code
  │
  ├─ "Index my project"
  │
  ▼
MCP Server (ingest tool)
  │
  ├─ 1. Read files from directory
  │    └─ mcp/qdrant_rag_server/iter_files()
  │
  ├─ 2. Split into chunks
  │    └─ chunk_text(text, 800 chars, 100 overlap)
  │
  ├─ 3. Generate embeddings
  │    └─ FastEmbed / SentenceTransformers / OpenAI
  │       └─ 384-dim vector (FastEmbed default)
  │
  ├─ 4. Upsert to Qdrant
  │    └─ HTTP POST /collections/project_docs/points
  │
  ▼
Qdrant Storage (Docker volume)
  │
  └─ Collections
      └─ project_docs (384-dim vectors)
          ├─ Point 1: metadata + embedding
          ├─ Point 2: metadata + embedding
          └─ ... N points
```

---

## Data Flow: Query

```
User asks question in VS Code
  │
  │ "Tell me about authentication in this project"
  │
  ▼
MCP Server (query tool)
  │
  ├─ 1. Embed the question
  │    └─ FastEmbed / SentenceTransformers / OpenAI
  │       └─ 384-dim vector
  │
  ├─ 2. Search in Qdrant
  │    └─ HTTP POST /collections/project_docs/points/search
  │       └─ Semantic similarity search
  │
  ├─ 3. Get top-k results (usually top 5)
  │    └─ Each result: text + score + metadata
  │
  ▼
MCP Server returns to VS Code
  │
  ├─ Relevant code snippets
  ├─ Documentation sections
  ├─ Similarity scores
  │
  ▼
VS Code Chat
  │
  └─ User sees results + can ask follow-up questions
```

---

## Component Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         HOST MACHINE                            │
│                                                                 │
│  ┌──────────────────┐                                          │
│  │   VS Code IDE    │                                          │
│  │ ┌────────────────┐                                          │
│  │ │ Continue Ext   │ (or Cline)                               │
│  │ └────────────────┘                                          │
│  └──────────┬──────────────────────────────────────────┐       │
│             │                                          │       │
│  ┌──────────▼─────────────────────────────────────────┐       │
│  │  Python Virtual Environment (.venv)                │       │
│  │                                                     │       │
│  │  ┌───────────────────────────────────────────────┐ │       │
│  │  │ MCP Server Script                             │ │       │
│  │  │ mcp/qdrant_rag_server/server.py               │ │       │
│  │  │ ┌─────────────────────────────────────────┐   │ │       │
│  │  │ │ Dependencies:                           │   │ │       │
│  │  │ │ • qdrant-client (core)                 │   │ │       │
│  │  │ │ • python-dotenv (config)               │   │ │       │
│  │  │ │ • fastembed (provider 1) OR            │   │ │       │
│  │  │ │   sentence-transformers (provider 2)   │   │ │       │
│  │  │ │   openai (provider 3)                  │   │ │       │
│  │  │ └─────────────────────────────────────────┘   │ │       │
│  │  │ Config: mcp/qdrant_rag_server/.env            │ │       │
│  │  └───────────────────────────────────────────────┘ │       │
│  └──────────┬──────────────────────────────────────────┘       │
│             │                                                  │
│             │ HTTP Requests (localhost:6333)                  │
│             │                                                  │
│  ┌──────────▼──────────────────────────────────────────────┐  │
│  │         Docker Container (Qdrant)                        │  │
│  │                                                          │  │
│  │  qdrant/qdrant:latest                                   │  │
│  │  ┌──────────────────────────────────────────────────┐   │  │
│  │  │ Qdrant Service                                   │   │  │
│  │  │ • Port 6333 ◄─── localhost:6333 (REST API)     │   │  │
│  │  │ • Port 6334 ◄─── localhost:6334 (gRPC)        │   │  │
│  │  │ • Port 6335        (internal cluster)          │   │  │
│  │  │                                                 │   │  │
│  │  │ Health Check: /health endpoint ✅              │   │  │
│  │  └─────────────┬────────────────────────────────────┘   │  │
│  │                │                                        │  │
│  │  ┌─────────────▼────────────────────────────────────┐   │  │
│  │  │ Named Volume: qdrant_storage                     │   │  │
│  │  │ └─ /qdrant/storage (persistent data)            │   │  │
│  │  │    └─ Collections with vectors                  │   │  │
│  │  │       └─ project_docs (384 dims)                │   │  │
│  │  └────────────────────────────────────────────────────┘   │  │
│  │                                                          │  │
│  │  Restart Policy: unless-stopped                         │  │
│  │  Logging: JSON rotation (100MB/file, 10 files)         │  │
│  │  API Key: Optional (QDRANT_API_KEY env var)             │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Configuration Hierarchy

```
┌─────────────────────────────────────────────────────┐
│   docker-compose.yaml                              │
│   (Container + Networking + Storage)                │
│   ├─ Image: qdrant/qdrant:latest                   │
│   ├─ Ports: 6333, 6334                             │
│   ├─ Health: /health endpoint                      │
│   ├─ Volume: qdrant_storage (named)                │
│   ├─ Network: app-network (bridge)                 │
│   ├─ Environment: QDRANT_API_KEY                   │
│   └─ Logging: JSON rotation                        │
└──────────────┬──────────────────────────────────────┘
               │
    ┌──────────┴─────────────┐
    │                        │
    ▼                        ▼
┌──────────────────────┐  ┌──────────────────────┐
│ .env (docker/)       │  │ .env (mcp/)          │
│ (Optional)           │  │ (MCP Config)         │
│                      │  │                      │
│ QDRANT_API_KEY=...   │  │ QDRANT_URL=http://..│
│                      │  │ QDRANT_API_KEY=...  │
│                      │  │ QDRANT_COLLECTION=..│
│                      │  │ EMBEDDINGS_PROVIDER │
│                      │  │ MODEL_NAME           │
└──────────────────────┘  └──────────────────────┘
```

---

## Storage Architecture

```
┌─────────────────────────────────────────────────────────┐
│          Docker Named Volume: qdrant_storage            │
│                                                         │
│  Location: Docker's default volume storage              │
│  • Linux: /var/lib/docker/volumes/...                  │
│  • macOS: Docker VM's internal storage                 │
│  • Windows: Docker VM's C:\ProgramData\...             │
│                                                         │
│  Mounted Inside Container:                              │
│  └─ /qdrant/storage                                    │
│                                                         │
│  Structure:                                             │
│  ├─ snapshots/ (backups)                               │
│  ├─ collections/                                       │
│  │  └─ project_docs/                                   │
│  │     ├─ payload_index/                               │
│  │     ├─ vector_storage/                              │
│  │     └─ collection.json                              │
│  └─ wal/ (write-ahead logs)                            │
│                                                         │
│  Persistence:                                           │
│  ✅ Survives: docker-compose stop/down                 │
│  ✅ Survives: container restart                        │
│  ✅ Survives: image update                             │
│  ❌ Lost only by: docker-compose down -v               │
│                                                         │
│  Backup:                                                │
│  docker volume inspect docker_qdrant_storage          │
│  └─ Shows: Mountpoint location for backup              │
└─────────────────────────────────────────────────────────┘
```

---

## Health Check Timeline

```
Container Start
    │
    ├─ 0s     Container launching
    │
    ├─ 5-10s  Qdrant server starting
    │         Health check START_PERIOD (grace period)
    │         └─ Checks pause (allow server boot)
    │
    ├─ 10s    START_PERIOD ends, health checks begin
    │         
    ├─ 10s    First health check: curl /health
    │         └─ FAIL (server still starting)
    │
    ├─ 40s    Check 2 (interval: 30s) → FAIL
    │
    ├─ 70s    Check 3 (interval: 30s) → PASS ✅
    │         Status changes to "healthy"
    │
    └─ Running
      All subsequent checks pass
      Status remains "healthy" ✅
      (unless check fails 3 times → "unhealthy")
```

---

## Network Connectivity

```
┌─────────────────────────────────────────────┐
│         Docker Bridge Network: app-network  │
│  (driver: bridge, internal only)            │
│                                             │
│  ┌───────────────────────────────────────┐ │
│  │ Container: qdrant                     │ │
│  │ hostname: qdrant                      │ │
│  │ IP: 172.18.0.2 (internal, dynamic)   │ │
│  │ Ports: 6333, 6334 (exposed)          │ │
│  └───────────────────────────────────────┘ │
│                                             │
│  Available from:                            │
│  • Host: localhost:6333 (port forward)     │
│  • Other containers: qdrant:6333 (DNS)    │
│                                             │
└─────────────────────────────────────────────┘
```

---

## Summary

- **Portable:** Named volumes work on any machine
- **Self-contained:** Bridge network, no external prerequisites  
- **Monitored:** Health checks every 30s (visible in `ps`)
- **Secure:** Optional API key authentication
- **Resilient:** Auto-restart on failure
- **Observable:** JSON logging with rotation
- **Flexible:** Resource limits (optional)
