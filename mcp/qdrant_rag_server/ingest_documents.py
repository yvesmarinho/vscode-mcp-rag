#!/home/yves_marinho/DevOps/Projetos/mcp_vector_project/.venv/bin/python
"""
Script para indexar todos os documentos do projeto no Qdrant.
Usa o servidor MCP diretamente para indexação eficiente.
"""

import sys
import logging
from pathlib import Path

# Adicionar o servidor MCP ao path
project_root = Path(__file__).parent
mcp_server_path = project_root / "mcp" / "qdrant_rag_server"
sys.path.insert(0, str(mcp_server_path))

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def check_environment():
    """Verifica se o ambiente está configurado corretamente."""
    logger.info("🔍 Verificando ambiente...")
    
    # Verificar se o Qdrant está rodando
    try:
        import requests
        response = requests.get("http://localhost:6333/collections", timeout=5)
        if response.status_code == 200:
            logger.info("✅ Qdrant está rodando")
        else:
            logger.error("❌ Qdrant não está respondendo corretamente")
            return False
    except Exception as e:
        logger.error(f"❌ Não foi possível conectar ao Qdrant: {e}")
        logger.info("💡 Execute: cd docker && docker-compose up -d")
        return False
    
    # Verificar se o servidor MCP existe
    server_py = mcp_server_path / "server.py"
    if not server_py.exists():
        logger.error(f"❌ Servidor MCP não encontrado: {server_py}")
        return False
    
    logger.info("✅ Ambiente OK")
    return True


def ingest_documents():
    """Indexa todos os documentos do projeto."""
    logger.info("📚 Iniciando indexação de documentos...")
    
    try:
        # Import do servidor MCP
        from server import Embeddings, QdrantIndex, handle_ingest
        from qdrant_client import QdrantClient
        
        # Inicializar componentes
        logger.info("🔧 Inicializando componentes...")
        client = QdrantClient(url='http://localhost:6333')
        embeddings = Embeddings()
        index = QdrantIndex(client, 'project_docs')
        
        # Parâmetros de ingestão
        params = {
            'directory': str(project_root),
            'include_globs': [
                "**/*.py",
                "**/*.md",
                "**/*.txt",
                "**/*.yaml",
                "**/*.yml",
                "**/*.json"
            ],
            'exclude_globs': [
                "**/.git/**",
                "**/.venv/**",
                "**/node_modules/**",
                "**/__pycache__/**",
                "**/reports/**",
                "**/export/**"
            ],
            'chunk_size': 800,
            'overlap': 100,
            'collection': 'project_docs'
        }
        
        logger.info(f"📁 Diretório: {params['directory']}")
        logger.info(f"📄 Padrões incluídos: {params['include_globs']}")
        logger.info(f"🚫 Padrões excluídos: {params['exclude_globs']}")
        logger.info(f"📏 Tamanho do chunk: {params['chunk_size']}")
        logger.info(f"🔗 Overlap: {params['overlap']}")
        
        # Executar ingestão
        logger.info("🚀 Executando ingestão...")
        result = handle_ingest(params, embeddings, index)
        
        # Exibir resultado
        logger.info("📊 Resultado da indexação:")
        if isinstance(result, dict):
            for key, value in result.items():
                logger.info(f"  {key}: {value}")
        else:
            logger.info(f"  {result}")
        
        logger.info("✅ Indexação concluída com sucesso!")
        return True
        
    except ImportError as e:
        logger.error(f"❌ Erro ao importar módulos: {e}")
        logger.info("💡 Certifique-se de que as dependências estão instaladas:")
        logger.info("  cd mcp/qdrant_rag_server && "
                    "pip install -r requirements.txt")
        return False
    except Exception as e:
        logger.error(f"❌ Erro durante a indexação: {e}")
        return False


def get_collection_stats():
    """Obtém estatísticas da coleção após indexação."""
    logger.info("📈 Obtendo estatísticas da coleção...")
    
    try:
        from qdrant_client import QdrantClient
        
        client = QdrantClient(url='http://localhost:6333')
        collection_info = client.get_collection('project_docs')
        
        logger.info("📊 Estatísticas da coleção 'project_docs':")
        logger.info(f"  Pontos: {collection_info.points_count}")
        logger.info(f"  Vetores: {collection_info.vectors_count}")
        logger.info(f"  Status: {collection_info.status}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao obter estatísticas: {e}")
        return False


def main():
    """Função principal."""
    print("🎯 MCP Vector Project - Indexação de Documentos")
    print("=" * 50)
    
    # Verificar ambiente
    if not check_environment():
        sys.exit(1)
    
    # Executar indexação
    if not ingest_documents():
        sys.exit(1)
    
    # Mostrar estatísticas
    get_collection_stats()
    
    print("\n🎉 Indexação concluída!")
    print("💡 Agora você pode usar o MCP Server no VS Code para buscar "
          "nos documentos")
    print("📚 Consulte docs/setup/QUICKSTART.md para configurar o VS Code")


if __name__ == "__main__":
    main()
