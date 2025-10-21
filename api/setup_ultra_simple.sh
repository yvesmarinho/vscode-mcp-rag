#!/bin/bash
# Ultra-Simple MCP Setup
# Usage: curl -sSL https://your-domain.com/mcp-setup.sh | bash

set -e

echo "🚀 Ultra-Simple MCP Setup"

# Create minimal MCP server
cat > mcp_simple.py << 'EOF'
import json,sys
from pathlib import Path
docs={}
for f in Path('.').rglob('*.md')+list(Path('.').rglob('*.py')):
 try:docs[str(f)]=f.read_text()[:1000]
 except:pass
for line in sys.stdin:
 r=json.loads(line)
 if r.get('method')=='initialize':print('{"jsonrpc":"2.0","id":"'+str(r['id'])+'","result":{"protocolVersion":"2024-11-05","capabilities":{"tools":{}}}}')
 elif r.get('method')=='tools/list':print('{"jsonrpc":"2.0","id":"'+str(r['id'])+'","result":{"tools":[{"name":"search","description":"Search","inputSchema":{"type":"object","properties":{"query":{"type":"string"}},"required":["query"]}}]}}')
 elif r.get('method')=='tools/call' and r.get('params',{}).get('name')=='search':
  q=r.get('params',{}).get('arguments',{}).get('query','').lower()
  res=[f+":\n"+c[:200] for f,c in docs.items() if q in c.lower()][:3]
  print('{"jsonrpc":"2.0","id":"'+str(r['id'])+'","result":{"content":[{"type":"text","text":"'+('\\n\\n'.join(res) if res else 'No results')+'"}]}}')
 sys.stdout.flush()
EOF

# Make executable
chmod +x mcp_simple.py

# Create VS Code config
mkdir -p .vscode
cat > .vscode/settings.json << 'EOF'
{
  "continue.configPath": "./continue.config.json"
}
EOF

cat > continue.config.json << 'EOF'
{
  "mcpServers": {
    "simple_rag": {
      "command": "python",
      "args": ["./mcp_simple.py"]
    }
  }
}
EOF

echo "✅ Setup complete!"
echo "📁 Files created:"
echo "   - mcp_simple.py (MCP server)"
echo "   - .vscode/settings.json"
echo "   - continue.config.json"
echo ""
echo "🎯 Usage in VS Code:"
echo "   @simple_rag search \"your query\""
echo ""
echo "🧪 Test:"
echo "   echo '{\"jsonrpc\":\"2.0\",\"method\":\"tools/call\",\"id\":\"1\",\"params\":{\"name\":\"search\",\"arguments\":{\"query\":\"test\"}}}' | python mcp_simple.py"