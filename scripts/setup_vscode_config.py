#!/usr/bin/env python3
"""
Script para configurar automaticamente o VS Code com MCP Server.
Cria os arquivos de configuração necessários para Continue/Cline.
"""

import os
import json
from pathlib import Path
from dotenv import load_dotenv


def setup_vscode_config():
    """Configura VS Code para usar o MCP Server."""
    
    # Detectar diretório do projeto
    script_dir = Path(__file__).parent
    project_root = script_dir.parent if script_dir.name == "scripts" else script_dir
    
    # Carregar configuração do .env se existir
    env_file = project_root / "mcp" / "qdrant_rag_server" / ".env"
    if env_file.exists():
        load_dotenv(env_file)
    
    # Configurações do MCP
    qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
    collection = os.getenv("QDRANT_COLLECTION", "project_docs")
    provider = os.getenv("EMBEDDINGS_PROVIDER", "fastembed")
    model = os.getenv("MODEL_NAME", "BAAI/bge-small-en-v1.5")
    
    # Configuração para Continue
    continue_config = {
        "models": [
            {
                "title": "GPT-4",
                "provider": "openai",
                "model": "gpt-4"
            },
            {
                "title": "Claude 3.5 Sonnet",
                "provider": "anthropic", 
                "model": "claude-3-5-sonnet-20241022"
            }
        ],
        "mcpServers": {
            "qdrant_rag": {
                "command": "python",
                "args": [
                    str(project_root / "mcp" / "qdrant_rag_server" / "server.py")
                ],
                "cwd": str(project_root),
                "env": {
                    "QDRANT_URL": qdrant_url,
                    "QDRANT_COLLECTION": collection,
                    "EMBEDDINGS_PROVIDER": provider,
                    "MODEL_NAME": model
                }
            }
        },
        "tabAutocompleteModel": {
            "title": "Autocomplete",
            "provider": "openai",
            "model": "gpt-3.5-turbo"
        }
    }
    
    # Criar diretório .continue se não existir
    continue_dir = project_root / ".continue"
    continue_dir.mkdir(exist_ok=True)
    
    # Escrever configuração do Continue
    config_file = continue_dir / "config.json"
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(continue_config, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Configuração do Continue criada: {config_file}")
    
    # Configuração para Cline (settings.json)
    vscode_dir = project_root / ".vscode"
    vscode_dir.mkdir(exist_ok=True)
    
    settings_file = vscode_dir / "settings.json"
    
    # Ler settings.json existente ou criar novo
    settings = {}
    if settings_file.exists():
        try:
            with open(settings_file, 'r', encoding='utf-8') as f:
                settings = json.load(f)
        except json.JSONDecodeError:
            settings = {}
    
    # Adicionar configuração do Cline
    settings["cline.mcpServers"] = {
        "qdrant_rag": {
            "command": "python",
            "args": [str(project_root / "mcp" / "qdrant_rag_server" / "server.py")],
            "cwd": str(project_root),
            "env": {
                "QDRANT_URL": qdrant_url,
                "QDRANT_COLLECTION": collection,
                "EMBEDDINGS_PROVIDER": provider,
                "MODEL_NAME": model
            }
        }
    }
    
    # Escrever settings.json atualizado
    with open(settings_file, 'w', encoding='utf-8') as f:
        json.dump(settings, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Configuração do Cline adicionada: {settings_file}")
    
    # Verificar se extensions.json existe e tem as extensões recomendadas
    extensions_file = vscode_dir / "extensions.json"
    if not extensions_file.exists():
        extensions_config = {
            "recommendations": [
                "continue.continue",
                "saoudrizwan.claude-dev",
                "ms-python.python",
                "ms-python.vscode-pylance"
            ]
        }
        
        with open(extensions_file, 'w', encoding='utf-8') as f:
            json.dump(extensions_config, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Extensões recomendadas criadas: {extensions_file}")
    
    print("\n🎉 Configuração do VS Code concluída!")
    print("\n📋 Próximos passos:")
    print("1. Instale as extensões recomendadas no VS Code")
    print("2. Reinicie o VS Code")
    print("3. Use @qdrant_rag no chat do Continue/Cline")
    print("\n💡 Exemplo de uso:")
    print("   @qdrant_rag query 'como configurar docker'")

if __name__ == "__main__":
    setup_vscode_config()