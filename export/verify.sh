#!/bin/bash
echo "🔍 Verificando integridade do arquivo..."
if sha256sum -c *.sha256 2>/dev/null; then
    echo "✅ Arquivo íntegro!"
else
    echo "❌ Arquivo corrompido!"
    exit 1
fi
