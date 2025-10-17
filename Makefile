.PHONY: help venv install install-fastembed install-sentencetransformers install-openai qdrant-start qdrant-stop qdrant-health create-collection mcp-start mcp-stop mcp-status mcp-logs test-ingest test-query diagnose quickstart clean

help:
	@echo "MCP + Qdrant Commands:"
	@echo ""
	@echo "Setup:"
	@echo "  make venv                    Create Python venv"
	@echo "  make install-fastembed       Install MCP + FastEmbed (recommended for CPU)"
	@echo "  make install-sentencetransformers  Install MCP + SentenceTransformers"
	@echo "  make install-openai          Install MCP + OpenAI"
	@echo ""
	@echo "Qdrant:"
	@echo "  make qdrant-start            Start Qdrant in Docker"
	@echo "  make qdrant-stop             Stop Qdrant"
	@echo "  make qdrant-health           Check Qdrant health"
	@echo "  make create-collection       Create project_docs collection"
	@echo ""
	@echo "MCP Server:"
	@echo "  make mcp-start               Start MCP Server daemon"
	@echo "  make mcp-stop                Stop MCP Server daemon"
	@echo "  make mcp-status              Show MCP Server status"
	@echo "  make mcp-logs                Show MCP Server logs"
	@echo ""
	@echo "Testing & Diagnostics:"
	@echo "  make test-ingest             Test ingest (dry-run first, then real)"
	@echo "  make diagnose                Run full diagnostics"
	@echo "  make quickstart              Show quick-start steps"

venv:
	python3 -m venv .venv
	@echo "✓ venv created. Activate with: source .venv/bin/activate"

install-fastembed: venv
	.venv/bin/pip install -r mcp/qdrant_rag_server/requirements.txt
	.venv/bin/pip install -r mcp/qdrant_rag_server/requirements-fastembed.txt
	@echo "✓ FastEmbed provider installed"

install-sentencetransformers: venv
	.venv/bin/pip install -r mcp/qdrant_rag_server/requirements.txt
	.venv/bin/pip install -r mcp/qdrant_rag_server/requirements-sentencetransformers.txt
	@echo "✓ SentenceTransformers provider installed"

install-openai: venv
	.venv/bin/pip install -r mcp/qdrant_rag_server/requirements.txt
	.venv/bin/pip install -r mcp/qdrant_rag_server/requirements-openai.txt
	@echo "✓ OpenAI provider installed"

qdrant-start:
	docker run -d -p 6333:6333 -p 6334:6334 \
		-v qdrant_storage:/qdrant/storage \
		--name qdrant_local \
		qdrant/qdrant:latest || docker start qdrant_local
	@echo "✓ Qdrant started at http://localhost:6333"

qdrant-stop:
	docker stop qdrant_local || true
	@echo "✓ Qdrant stopped"

qdrant-health:
	@curl -s http://localhost:6333/health | jq . || echo "Qdrant not responding"

create-collection:
	QDRANT_URL=http://localhost:6333 \
	QDRANT_COLLECTION=project_docs \
	VECTOR_SIZE=384 \
	python3 mcp/qdrant_rag_server/qdrant_create_db.py

mcp-start:
	systemctl --user start qdrant-mcp-server.service
	@echo "✓ MCP Server starting..."
	@sleep 2
	@systemctl --user status qdrant-mcp-server.service --no-pager

mcp-stop:
	systemctl --user stop qdrant-mcp-server.service
	@echo "✓ MCP Server stopped"

mcp-status:
	systemctl --user status qdrant-mcp-server.service --no-pager

mcp-logs:
	journalctl --user -u qdrant-mcp-server.service -n 50 -f

test-ingest:
	@echo "Dry-run:"
	scripts/mcp_test_ingest_report.sh --dry-run
	@echo ""
	@echo "Real ingest (uncomment below to run):"
	@echo "# scripts/mcp_test_ingest_report.sh"

diagnose:
	scripts/mcp_qdrant_report.sh

quickstart:
	@cat docs/setup/QUICKSTART.md
