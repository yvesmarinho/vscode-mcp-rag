import os
import sys
import json
import uuid
import time
from typing import List, Dict, Any, Optional, Iterable

from qdrant_client import QdrantClient
from qdrant_client.http import models as qm
from dotenv import load_dotenv


# -------------------- Embeddings --------------------
class Embeddings:
    def __init__(self):
        # Carregar variáveis do arquivo .env
        load_dotenv()
        
        self.provider = os.getenv(
            "EMBEDDINGS_PROVIDER", "fastembed"
        ).lower()
        self.model_name = os.getenv("MODEL_NAME", "all-MiniLM-L6-v2")
        self._model = None
        self._fe_model = None

        if self.provider == "openai":
            try:
                from openai import OpenAI
            except ImportError as e:
                raise ImportError(
                    "Pacote 'openai' não instalado. Instale com: "
                    "pip install -r mcp/qdrant_rag_server/"
                    "requirements-openai.txt"
                ) from e
            self._client = OpenAI()
            # model via OPENAI_EMBEDDING_MODEL
            self.openai_model = os.getenv(
                "OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"
            )
        elif self.provider == "sentence-transformers":
            # sentence-transformers (CPU-friendly, GPU opcional)
            try:
                from sentence_transformers import SentenceTransformer
            except ImportError as e:
                raise ImportError(
                    "Pacote 'sentence-transformers' não instalado. Instale com: "
                    "pip install -r mcp/qdrant_rag_server/"
                    "requirements-sentencetransformers.txt"
                ) from e
            self._model = SentenceTransformer(self.model_name)
        elif self.provider == "fastembed":
            # fastembed (leve, CPU-first)
            try:
                from fastembed import TextEmbedding
            except ImportError as e:
                raise ImportError(
                    "Pacote 'fastembed' não instalado. Instale com: "
                    "pip install -r mcp/qdrant_rag_server/"
                    "requirements-fastembed.txt"
                ) from e
            fe_model = self.model_name
            if fe_model == "all-MiniLM-L6-v2":
                # Ajuste para um modelo padrão compatível com fastembed
                fe_model = "BAAI/bge-small-en-v1.5"
            self._fe_model = TextEmbedding(model_name=fe_model)
        else:
            raise ValueError(
                "EMBEDDINGS_PROVIDER inválido. Use 'sentence-transformers', "
                "'fastembed' ou 'openai'."
            )

    def embed(self, texts: List[str]) -> List[List[float]]:
        if self.provider == "openai":
            resp = self._client.embeddings.create(
                model=self.openai_model, input=texts
            )
            return [d.embedding for d in resp.data]
        elif self.provider == "sentence-transformers":
            # Evita dependência de numpy: retorna listas de floats nativos
            vecs = self._model.encode(
                texts,
                batch_size=32,
                convert_to_numpy=False,
                show_progress_bar=False,
                normalize_embeddings=True,
            )
            return [list(map(float, v)) for v in vecs]
        else:  # fastembed
            # fastembed: converte gerador em lista de listas de float
            vectors: List[List[float]] = []
            for vec in self._fe_model.embed(texts):
                vectors.append([float(x) for x in vec])
            return vectors


# -------------------- Chunking --------------------
def chunk_text(
    text: str, chunk_size: int = 800, overlap: int = 100
) -> List[str]:
    if chunk_size <= 0:
        return [text]
    chunks: List[str] = []
    i = 0
    n = len(text)
    while i < n:
        chunk = text[i:i + chunk_size]
        chunks.append(chunk)
        if i + chunk_size >= n:
            break
        i += max(1, chunk_size - overlap)
    return chunks


# -------------------- File traversal --------------------
def match_globs(path: str, patterns: List[str]) -> bool:
    import fnmatch
    return any(fnmatch.fnmatch(path, pat) for pat in patterns)


def iter_files(
    base_dir: str, include_globs: List[str], exclude_globs: List[str]
) -> Iterable[str]:
    base_dir = os.path.abspath(base_dir)
    for root, dirs, files in os.walk(base_dir):
        # Apply directory-level excludes
        rel_root = os.path.relpath(root, base_dir)
        if rel_root == ".":
            rel_root = ""
        full_root = root
        # filter out typical heavy dirs
        skip_dirs = {
            ".git",
            ".hg",
            ".svn",
            "node_modules",
            ".venv",
            "venv",
            "__pycache__",
        }
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        for f in files:
            path = os.path.join(full_root, f)
            rel = os.path.relpath(path, base_dir)
            rel_for_match = rel.replace(os.sep, "/")
            if include_globs and not match_globs(rel_for_match, include_globs):
                continue
            if exclude_globs and match_globs(rel_for_match, exclude_globs):
                continue
            yield path


# -------------------- Qdrant wrapper --------------------
class QdrantIndex:
    def __init__(
        self, client: QdrantClient, collection: str,
        vector_size: Optional[int] = None
    ):
        self.client = client
        self.collection = collection
        self.vector_size = vector_size

    def ensure(self, vector_size: int) -> None:
        """Ensure collection exists with the given vector size."""
        exists = False
        try:
            info = self.client.get_collection(self.collection)
            if info and getattr(info, "vectors_count", None) is not None:
                exists = True
        except Exception:
            exists = False
        if not exists:
            self.client.recreate_collection(
                collection_name=self.collection,
                vectors_config=qm.VectorParams(
                    size=vector_size, distance=qm.Distance.COSINE
                ),
            )
        self.vector_size = vector_size

    def upsert(
        self, ids: List[str], vectors: List[List[float]],
        payloads: List[Dict[str, Any]], vector_size: int
    ) -> None:
        self.ensure(vector_size)
        points = [
            qm.PointStruct(id=id_, vector=vec, payload=payload)
            for id_, vec, payload in zip(ids, vectors, payloads)
        ]
        self.client.upsert(
            collection_name=self.collection, points=points, wait=True
        )

    def search(
        self, vector: List[float], top_k: int,
        filter_: Optional[Any] = None
    ) -> List[Any]:
        return self.client.search(
            collection_name=self.collection,
            query_vector=vector,
            limit=top_k,
            query_filter=filter_,
        )


# -------------------- MCP protocol (simplified) --------------------
def mcp_response(
    id_: Any, result: Any = None, error: Optional[str] = None
) -> Dict[str, Any]:
    if error:
        return {
            "jsonrpc": "2.0",
            "id": id_,
            "error": {"code": -32000, "message": error},
        }
    return {"jsonrpc": "2.0", "id": id_, "result": result}


def mcp_list_tools() -> List[Dict[str, Any]]:
    return [
        {
            "name": "ingest",
            "description": (
                "Indexa arquivos de um diretório no Qdrant com embeddings"
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "directory": {"type": "string"},
                    "include_globs": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                    "exclude_globs": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                    "chunk_size": {"type": "integer"},
                    "overlap": {"type": "integer"},
                    "collection": {"type": "string"},
                },
                "required": ["directory"],
            },
        },
        {
            "name": "query",
            "description": "Busca semântica de trechos no Qdrant",
            "input_schema": {
                "type": "object",
                "properties": {
                    "text": {"type": "string"},
                    "top_k": {"type": "integer"},
                    "collection": {"type": "string"},
                    "path_prefix": {"type": "string"},
                },
                "required": ["text"],
            },
        },
    ]


def build_filter(path_prefix: Optional[str]) -> Optional[Any]:
    if not path_prefix:
        return None
    return qm.Filter(
        should=[
            qm.FieldCondition(
                key="path", match=qm.MatchText(text=path_prefix)
            )
        ]
    )


def handle_ingest(
    params: Dict[str, Any], embeddings: Embeddings, index: QdrantIndex
) -> Dict[str, Any]:
    directory = params.get("directory")
    include_globs = params.get("include_globs") or [
        "**/*.py", "**/*.md", "**/*.txt", "**/*.json", "**/*.yaml", "**/*.yml"
    ]
    exclude_globs = params.get("exclude_globs") or [
        "**/.git/**",
        "**/.hg/**",
        "**/node_modules/**",
        "**/.venv/**",
        "**/*.ipynb",
    ]
    chunk_size = int(params.get("chunk_size") or 800)
    overlap = int(params.get("overlap") or 100)

    assert isinstance(directory, str), "directory must be provided"
    base_dir = os.path.abspath(directory)
    files = list(iter_files(base_dir, include_globs, exclude_globs))
    total_chunks = 0
    batch_vectors: List[List[float]] = []
    batch_payloads: List[Dict[str, Any]] = []
    batch_ids: List[str] = []

    for path in files:
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()
        except Exception:
            continue
        chunks = chunk_text(text, chunk_size=chunk_size, overlap=overlap)
        chunk_vectors = embeddings.embed(chunks)
        rel = os.path.relpath(path, base_dir).replace(os.sep, "/")
        for chunk_text_val, vec in zip(chunks, chunk_vectors):
            cid = str(uuid.uuid4())
            payload = {
                "path": rel,
                "text": chunk_text_val,
            }
            batch_ids.append(cid)
            batch_vectors.append(vec)
            batch_payloads.append(payload)
            total_chunks += 1
        if len(batch_ids) >= 256:
            # Ensure collection and upsert batch
            index.upsert(
                batch_ids, batch_vectors, batch_payloads,
                vector_size=len(batch_vectors[0])
            )
            batch_vectors, batch_payloads, batch_ids = [], [], []

    # Flush remaining
    if batch_ids:
        index.upsert(
            batch_ids, batch_vectors, batch_payloads,
            vector_size=len(batch_vectors[0])
        )
    return {"files_indexed": len(files), "chunks": total_chunks}


def handle_query(
    params: Dict[str, Any], embeddings: Embeddings, index: QdrantIndex
) -> Dict[str, Any]:
    text = params["text"]
    top_k = int(params.get("top_k") or 5)
    path_prefix = params.get("path_prefix")
    vec = embeddings.embed([text])[0]
    flt = build_filter(path_prefix)
    hits = index.search(vec, top_k=top_k, filter_=flt)
    out = []
    for h in hits:
        payload = h.payload or {}
        out.append({
            "id": h.id,
            "score": h.score,
            "path": payload.get("path"),
            "text": payload.get("text", "")[:600],
        })
    return {"hits": out}


def main():
    load_dotenv()
    qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
    qdrant_key = os.getenv("QDRANT_API_KEY")
    collection = os.getenv("QDRANT_COLLECTION", "project_docs")

    client = QdrantClient(url=qdrant_url, api_key=qdrant_key)
    emb: Optional[Embeddings] = None
    indexes: Dict[str, QdrantIndex] = {}

    def get_embeddings() -> Embeddings:
        nonlocal emb
        if emb is None:
            emb = Embeddings()
        return emb

    def get_index(coll: str) -> QdrantIndex:
        idx = indexes.get(coll)
        if idx is None:
            idx = QdrantIndex(client, coll)
            indexes[coll] = idx
        return idx

    # MCP stdio loop (jsonrpc 2.0 minimal)
    try:
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            try:
                req = json.loads(line)
            except Exception:
                # Not JSON -> ignore
                continue
            id_ = req.get("id")
            method = req.get("method")
            params = req.get("params") or {}

            try:
                if method == "tools/list":
                    res = mcp_list_tools()
                    sys.stdout.write(json.dumps(mcp_response(id_, res)) + "\n")
                    sys.stdout.flush()
                elif method == "tools/call":
                    name = params.get("name")
                    args = params.get("arguments") or {}
                    if name == "ingest":
                        coll = args.get("collection") or collection
                        idx = get_index(coll)
                        res = handle_ingest(args, get_embeddings(), idx)
                    elif name == "query":
                        coll = args.get("collection") or collection
                        idx = get_index(coll)
                        res = handle_query(args, get_embeddings(), idx)
                    else:
                        raise ValueError(f"Tool not found: {name}")
                    sys.stdout.write(json.dumps(mcp_response(id_, res)) + "\n")
                    sys.stdout.flush()
                else:
                    sys.stdout.write(
                        json.dumps(
                            mcp_response(id_, error="Method not supported")
                        )
                        + "\n"
                    )
                    sys.stdout.flush()
            except Exception as e:
                sys.stdout.write(
                    json.dumps(mcp_response(id_, error=str(e))) + "\n"
                )
                sys.stdout.flush()
    except (OSError, ValueError):
        # stdin not available (running as daemon) - exit gracefully
        pass


if __name__ == "__main__":
    main()
