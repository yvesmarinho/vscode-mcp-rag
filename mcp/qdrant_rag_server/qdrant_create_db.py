#!/usr/bin/env python3
"""
Cria (ou recria) uma coleção no Qdrant para armazenar embeddings.

Variáveis de ambiente:
- QDRANT_URL            (ex.: http://localhost:6333)
- QDRANT_API_KEY        (opcional; Qdrant local geralmente não precisa)
- QDRANT_COLLECTION     (ex.: project_docs)
- VECTOR_SIZE           (ex.: 384 para FastEmbed / MiniLM; 1536 para OpenAI text-embedding-3-small)
- DISTANCE              (COSINE | DOT | EUCLID) — default: COSINE

Uso:
- Ajuste as variáveis de ambiente e execute este script.
- Ele cria a coleção se não existir. Use `force_recreate=True` abaixo para recriar do zero.
"""

import os
from qdrant_client import QdrantClient
from qdrant_client.http import models as qm


def ensure_collection(
    client: QdrantClient,
    collection_name: str,
    vector_size: int,
    distance: str = "COSINE",
    force_recreate: bool = False,
) -> None:
    """Garante que a coleção exista com o tamanho e distância informados."""
    distance_enum = {
        "COSINE": qm.Distance.COSINE,
        "DOT": qm.Distance.DOT,
        "EUCLID": qm.Distance.EUCLID,
    }.get(distance.upper(), qm.Distance.COSINE)

    def create():
        client.create_collection(
            collection_name=collection_name,
            vectors_config=qm.VectorParams(
                size=vector_size,
                distance=distance_enum,
            ),
        )

    try:
        info = client.get_collection(collection_name)
        if force_recreate:
            client.recreate_collection(
                collection_name=collection_name,
                vectors_config=qm.VectorParams(
                    size=vector_size,
                    distance=distance_enum,
                ),
            )
            print(f"[ok] Coleção '{collection_name}' recriada.")
        else:
            # Já existe — apenas informa
            print(f"[ok] Coleção '{collection_name}' já existe.")
            # Opcional: você pode validar se o 'size' e 'distance' batem
            # com o desejado e, se não, usar recreate_collection.
    except Exception:
        # Não existe — criar
        create()
        print(f"[ok] Coleção '{collection_name}' criada.")


def main():
    qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
    qdrant_key = os.getenv("QDRANT_API_KEY")
    collection = os.getenv("QDRANT_COLLECTION", "project_docs")

    # Dica de dimensões:
    # - FastEmbed (BAAI/bge-small-en-v1.5) e MiniLM: 384
    # - SentenceTransformers base maiores: 768 (depende do modelo)
    # - OpenAI text-embedding-3-small: 1536
    vector_size = int(os.getenv("VECTOR_SIZE", "384"))
    distance = os.getenv("DISTANCE", "COSINE")

    # Para localhost, não usar API key para evitar warning de conexão insegura
    if "localhost" in qdrant_url or "127.0.0.1" in qdrant_url:
        client = QdrantClient(url=qdrant_url)
    else:
        client = QdrantClient(url=qdrant_url, api_key=qdrant_key)

    # force_recreate=False cria apenas se não existir; troque para True se quiser recriar do zero
    ensure_collection(
        client=client,
        collection_name=collection,
        vector_size=vector_size,
        distance=distance,
        force_recreate=False,
    )

    # (Opcional) Mostra status da coleção
    info = client.get_collection(collection)
    print("[info] Status da coleção:")
    print(f"  name: {collection}")
    print(f"  vectors_count: {getattr(info, 'vectors_count', 'N/A')}")
    print(f"  config: {info.config}")


if __name__ == "__main__":
    main()