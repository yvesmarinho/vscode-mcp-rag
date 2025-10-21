.PHONY: help venv install install-fastembed install-sentencetransformers install-openai qdrant-start qdrant-stop qdrant-health create-collection mcp-start mcp-stop mcp-status mcp-logs test-ingest test-query diagnose quickstart clean

help:
	@echo "MCP + Qdrant Commands:"
	@echo ""
	@echo "🚀 Quick Setup:"
	@echo "  make setup                   Complete setup (all-in-one)"
	@echo "  make install-fastembed       Install MCP + FastEmbed (recommended)"
	@echo "  make configure-vscode        Configure VS Code automatically"
	@echo ""
	@echo "🐳 Qdrant:"
	@echo "  make qdrant-start            Start Qdrant in Docker"
	@echo "  make qdrant-stop             Stop Qdrant"
	@echo "  make qdrant-health           Check Qdrant health"
	@echo "  make create-collection       Create project_docs collection"
	@echo ""
	@echo "📚 Indexing:"
	@echo "  make ingest                  Index all project documents"
	@echo "  make test-query              Test semantic search"
	@echo ""
	@echo "🔧 MCP Server:"
	@echo "  make mcp-start               Start MCP Server daemon"
	@echo "  make mcp-stop                Stop MCP Server daemon"
	@echo "  make mcp-status              Show MCP Server status"
	@echo "  make mcp-logs                Show MCP Server logs"
	@echo ""
	@echo "🩺 Diagnostics:"
	@echo "  make diagnose                Run full diagnostics"
	@echo "  make quickstart              Show quick-start steps"

venv:
	python3 -m venv .venv
	@echo "✓ venv created. Activate with: source .venv/bin/activate"

setup: venv install-fastembed qdrant-start create-collection configure-vscode
	@echo "🎉 Complete setup finished!"
	@echo "Next: Open VS Code and use @qdrant_rag in Continue/Cline chat"

configure-vscode:
	.venv/bin/python scripts/setup_vscode_config.py
	@echo "✓ VS Code configuration created"

ingest:
	cd mcp/qdrant_rag_server && ../../.venv/bin/python ingest_documents.py
	@echo "✓ Documents indexed"

test-query:
	@echo "Testing semantic search..."
	@echo '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"query","arguments":{"text":"docker configuration","top_k":3}}}' | .venv/bin/python mcp/qdrant_rag_server/server.py

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
