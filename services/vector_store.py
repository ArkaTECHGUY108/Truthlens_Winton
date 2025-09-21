import os
import faiss
import json
import numpy as np
import hashlib
import threading
from datetime import datetime
from sentence_transformers import SentenceTransformer
from core.logger import setup_logger

logger = setup_logger()

# ==============================
# Configurable Paths
# ==============================
DATA_DIR = os.getenv("VECTOR_STORE_DIR", "data")
INDEX_PATH = os.path.join(DATA_DIR, "faiss_index.bin")
META_PATH = os.path.join(DATA_DIR, "faiss_metadata.json")

os.makedirs(DATA_DIR, exist_ok=True)

# ==============================
# Embedding Model (Lazy Loaded)
# ==============================
_embedding_model = None
dimension = 384
_index_lock = threading.Lock()

def get_model():
    """Load embedding model only once (lazy load)."""
    global _embedding_model
    if _embedding_model is None:
        logger.info("Loading embedding model: all-MiniLM-L6-v2")
        _embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
    return _embedding_model

# ==============================
# FAISS Index + Metadata
# ==============================
index = faiss.IndexFlatIP(dimension)  # cosine via inner product
metadata = []  # parallel metadata list

# ==============================
# Utility Functions
# ==============================
def normalize(vec: np.ndarray) -> np.ndarray:
    """Normalize vector for cosine similarity."""
    return vec / np.linalg.norm(vec)

def embed_text(text: str) -> np.ndarray:
    """Convert text into normalized embedding vector."""
    model = get_model()
    vector = model.encode([text], normalize_embeddings=True)[0].astype("float32")
    return vector

def text_hash(text: str) -> str:
    """Stable SHA256 hash for deduplication."""
    return hashlib.sha256(text.strip().lower().encode("utf-8")).hexdigest()

# ==============================
# Document Management
# ==============================
def add_document(text: str, url: str, source: str, labels: list[str] = None, auto_save: bool = True):
    """Add a new document to FAISS index + metadata store."""
    global index, metadata
    doc_hash = text_hash(text)

    if any(m.get("hash") == doc_hash for m in metadata):
        logger.info("Duplicate skipped in FAISS store.")
        return

    vector = embed_text(text)

    with _index_lock:
        index.add(np.array([vector]))
        metadata.append({
            "text": text,
            "url": url,
            "source": source,
            "labels": labels or [],
            "hash": doc_hash,
            "score": None,
            "timestamp": datetime.utcnow().isoformat()
        })

    logger.info(f"Added doc to FAISS: {text[:60]}...")

    if auto_save:
        save_index()

def add_bulk(docs: list[dict], auto_save: bool = True):
    """Efficiently add multiple documents at once."""
    global index, metadata
    new_vectors, new_meta = [], []

    for doc in docs:
        text = doc["text"]
        doc_hash = text_hash(text)
        if any(m.get("hash") == doc_hash for m in metadata):
            continue
        new_vectors.append(embed_text(text))
        new_meta.append({
            "text": text,
            "url": doc.get("url", ""),
            "source": doc.get("source", "unknown"),
            "labels": doc.get("labels", []),
            "hash": doc_hash,
            "timestamp": datetime.utcnow().isoformat()
        })

    if new_vectors:
        with _index_lock:
            index.add(np.array(new_vectors))
            metadata.extend(new_meta)
        logger.info(f"Bulk added {len(new_vectors)} docs to FAISS.")

    if auto_save:
        save_index()

# ==============================
# Search
# ==============================
def search_similar(query: str, top_k: int = 5) -> list[dict]:
    """Search FAISS index for top-k similar documents."""
    if index.ntotal == 0:
        return []

    query_vec = embed_text(query)
    with _index_lock:
        D, I = index.search(np.array([query_vec]), top_k)

    results = []
    for idx, score in zip(I[0], D[0]):
        if idx < len(metadata):
            doc = metadata[idx].copy()
            doc["score"] = float(score)
            results.append(doc)

    return results

# ==============================
# Persistence
# ==============================
def save_index():
    """Persist FAISS index + metadata to disk."""
    global index, metadata
    with _index_lock:
        faiss.write_index(index, INDEX_PATH)
        with open(META_PATH, "w") as f:
            json.dump(metadata, f, indent=2)
    logger.info(f"FAISS index + metadata saved ({len(metadata)} docs).")

def load_index():
    """Load FAISS index + metadata from disk if available."""
    global index, metadata
    try:
        if os.path.exists(INDEX_PATH):
            index = faiss.read_index(INDEX_PATH)
            logger.info("FAISS index loaded.")
        if os.path.exists(META_PATH):
            with open(META_PATH, "r") as f:
                metadata = json.load(f)
            logger.info(f"Loaded {len(metadata)} metadata entries.")
    except Exception as e:
        logger.error(f"Failed to load FAISS index/metadata: {e}")
        index = faiss.IndexFlatIP(dimension)
        metadata = []

# ==============================
# Auto-load on import
# ==============================
load_index()
