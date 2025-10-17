# Docker Configuration Guide

Documentação sobre como usar o Qdrant via Docker com o MCP Server.

## Overview

O arquivo `docker/docker-compose.yaml` foi otimizado para produção com as seguintes melhorias:

| Aspecto | Antes | Depois | Benefício |
|---------|-------|--------|-----------|
| **Volume** | Bind mount (path absoluto) | Named volume | Portável entre máquinas |
| **Network** | External (pré-requisito) | Bridge (self-contained) | Sem dependências externas |
| **Health Check** | ❌ Nenhum | ✅ curl /health | Monitora disponibilidade automática |
| **API Key** | ❌ Não suportado | ✅ Env var `QDRANT_API_KEY` | Segurança em produção |
| **Logs** | Padrão | JSON com rotação | Easier debugging & retention |
| **Restart** | `always` | `unless-stopped` | Controle manual over restarts |

---

## Quick Start

### Prerequisites

```bash
# Ensure Docker and Docker Compose are installed
docker --version       # Expected: Docker version 20+
docker-compose --version  # Expected: Docker Compose version 2+
```

### Start Qdrant

```bash
# Navigate to docker directory
cd docker/

# Start container in background
docker-compose up -d

# Verify it's running
docker-compose ps

# Expected output:
# NAME      IMAGE              STATUS              PORTS
# qdrant    qdrant/qdrant:...  Up 10 seconds       6333->6333, 6334->6334
```

### Test Connection

```bash
# HTTP health check
curl http://localhost:6333/health

# Expected: {"status":"ok"}

# If using API key:
curl -H "api-key: your-secure-key" http://localhost:6333/health
```

### Stop Qdrant

```bash
# Stop but keep data
docker-compose stop

# Stop and remove container (data persists in volume)
docker-compose down

# Stop and delete everything including data
docker-compose down -v
```

---

## Configuration

### Environment Variables

Create `docker/.env` file (optional, for API key security):

```properties
# Optional: Enable API key authentication
# If set, all API calls must include: -H "api-key: your-key"
QDRANT_API_KEY=your-secure-key-here
```

Then run:
```bash
docker-compose up -d
```

Or pass directly:
```bash
QDRANT_API_KEY=your-key docker-compose up -d
```

### Modify docker-compose.yaml

**Key sections:**

1. **Health Check** (lines ~17-23):
   - Automatically detects if service is ready
   - Fails after 3 retries of 10s each
   - Use `docker-compose ps` to see health status

2. **Storage** (lines ~31-32):
   - `qdrant_storage` = named volume (Docker managed)
   - Data persists on `docker-compose down`
   - Use `docker volume ls` to see volumes

3. **Environment** (lines ~35-37):
   - `QDRANT_API_KEY`: Set to enable authentication
   - Leave empty for local development (default)

4. **Resource Limits** (lines ~43-50):
   - Uncomment to limit CPU and memory
   - Example: `cpus: '2'`, `memory: 2G`
   - Useful for shared hosting

5. **Logging** (lines ~52-56):
   - JSON format with rotation
   - Max 100MB per file
   - Keeps last 10 files (~1GB total)

---

## Network Setup

### Bridge Network (Current)

```yaml
networks:
  app-network:
    driver: bridge
    name: app-network
```

**Characteristics:**
- ✅ Self-contained (no external requirement)
- ✅ Isolated from other Docker networks
- ✅ Services communicate via container names
- ✅ Host can access via `localhost:6333`

**Connection from MCP Server:**
```python
# Both work:
client = QdrantClient(url="http://localhost:6333")  # From host
client = QdrantClient(url="http://qdrant:6333")     # From another container
```

### External Network (Alternative)

If you have multiple compose files and want shared network:

```yaml
networks:
  app-network:
    external: true
    name: app-network
```

Create first:
```bash
docker network create app-network
```

---

## Storage & Volumes

### Named Volume (Current)

```yaml
volumes:
  qdrant_storage:
    driver: local
```

**Location:** Docker's default volume storage:
- Linux: `/var/lib/docker/volumes/docker_qdrant_storage/_data/`
- macOS: `~/Library/Containers/com.docker.docker/Data/vms/0/data/Docker.raw`
- Windows: `C:\ProgramData\Docker\volumes\docker_qdrant_storage\_data\`

**Advantages:**
- ✅ Portable (works across machines)
- ✅ Managed by Docker (automatic backups possible)
- ✅ No absolute paths
- ✅ Easy to clean (`docker volume rm`)

### Backup

```bash
# Create backup
docker run --rm -v docker_qdrant_storage:/data -v $(pwd):/backup \
  alpine tar czf /backup/qdrant-backup.tar.gz -C /data .

# Restore
docker volume create docker_qdrant_storage
docker run --rm -v docker_qdrant_storage:/data -v $(pwd):/backup \
  alpine tar xzf /backup/qdrant-backup.tar.gz -C /data
```

---

## Monitoring & Debugging

### Health Status

```bash
# Check if healthy
docker-compose ps
# Look for "healthy" or "unhealthy" in STATUS

# View health logs
docker-compose logs qdrant | grep -i health

# Manual health test
curl -s http://localhost:6333/health | jq .
```

### Logs

```bash
# View all logs
docker-compose logs qdrant

# Follow logs (live)
docker-compose logs -f qdrant

# Last 100 lines
docker-compose logs --tail=100 qdrant

# Filter by time
docker-compose logs --since 5m qdrant

# Pretty print (requires jq)
docker-compose logs qdrant | jq .
```

### Container Shell

```bash
# Enter running container
docker-compose exec qdrant sh

# View Qdrant config
cat /qdrant/config/production.yaml

# List collections
curl http://localhost:6333/collections
```

### Resource Usage

```bash
# Real-time stats
docker stats qdrant

# Check volume size
docker volume inspect docker_qdrant_storage

# Disk usage
docker exec qdrant du -sh /qdrant/storage
```

---

## Troubleshooting

### Container Won't Start

```bash
# View error logs
docker-compose logs qdrant

# Common causes:
# - Port already in use: lsof -i :6333
# - Volume permission issue: docker-compose down -v && docker-compose up -d
# - Disk space: df -h
```

### Connection Refused

```bash
# Verify service is running
docker-compose ps

# Verify port is open
netstat -tln | grep 6333
# or
ss -tln | grep 6333

# Test from container
docker-compose exec qdrant curl http://localhost:6333/health
```

### Slow Performance

```bash
# Check resource limits
docker stats qdrant

# Increase if CPU/memory maxed out:
# Uncomment resource limits in docker-compose.yaml
# Restart: docker-compose down && docker-compose up -d
```

### API Key Issues

```bash
# If API key enabled, include in requests:
curl -H "api-key: your-key" http://localhost:6333/health

# Error: "Forbidden" = wrong key
# Error: "Unauthorized" = missing key
```

### Volume Permission Error

```bash
# Fix permissions
docker-compose down
docker volume rm docker_qdrant_storage
docker-compose up -d
```

---

## Advanced Configuration

### Resource Limits

Uncomment in `docker-compose.yaml`:

```yaml
deploy:
  resources:
    limits:
      cpus: '2'           # Max 2 CPUs
      memory: 2G          # Max 2GB RAM
    reservations:
      cpus: '1'           # Reserve 1 CPU
      memory: 1G          # Reserve 1GB RAM
```

Then restart:
```bash
docker-compose down && docker-compose up -d
```

### Custom Config

Modify `configs` section for fine-tuning:

```yaml
configs:
  qdrant_config:
    content: |
      log_level: DEBUG          # More verbose logs
      telemetry_disabled: true  # Disable telemetry
```

### Multiple Instances

For staging + production:

```bash
# docker-compose-staging.yaml
cd docker/
docker-compose -f docker-compose-staging.yaml up -d

# Separate containers: qdrant-prod, qdrant-staging
```

---

## Integration with MCP Server

### Connection String

```python
from qdrant_client import QdrantClient

# Standard (default in .env.example)
client = QdrantClient(url="http://localhost:6333")

# With API key
client = QdrantClient(
    url="http://localhost:6333",
    api_key="your-secure-key"
)

# From another Docker container
client = QdrantClient(url="http://qdrant:6333")
```

### .env Configuration

```properties
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=your-key-if-set
QDRANT_COLLECTION=project_docs
```

### Testing Connection

```bash
# From host
python3 -c "from qdrant_client import QdrantClient; \
  c = QdrantClient('http://localhost:6333'); \
  print(f'Connected: {c.get_collections()}')"

# Should show: Connected: CollectionsResponse(...)
```

---

## Production Checklist

- [ ] Set `QDRANT_API_KEY` for authentication
- [ ] Configure resource limits if on shared host
- [ ] Set up volume backups
- [ ] Monitor logs and health regularly
- [ ] Test failover/restart behavior
- [ ] Document any custom config changes
- [ ] Set up monitoring/alerting for health checks

---

## References

- [Qdrant Docker Docs](https://qdrant.tech/documentation/guides/deployment/)
- [Docker Compose Spec](https://github.com/compose-spec/compose-spec)
- [Health Checks](https://docs.docker.com/compose/compose-file/compose-file-v3/#healthcheck)
