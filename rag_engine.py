# ─────────────────────────────────────────────
#  rag_engine.py  –  ChromaDB Vector Store
# ─────────────────────────────────────────────
from __future__ import annotations   # ← fixes | None syntax on Python 3.9
import logging
from pathlib import Path
import chromadb
from chromadb.utils import embedding_functions
from sentence_transformers import SentenceTransformer
from config import (
    CHROMA_DIR,
    CHROMA_COLLECTION,
    EMBEDDING_MODEL,
    TOP_K_RESULTS,
    RAG_CHUNKS,
)
logger = logging.getLogger(__name__)
# ── Singleton objects ────────────────────────────
_client:     chromadb.PersistentClient | None = None
_collection: chromadb.Collection       | None = None
_embedder:   SentenceTransformer       | None = None
def _get_embedder() -> SentenceTransformer:
    global _embedder
    if _embedder is None:
        _embedder = SentenceTransformer(EMBEDDING_MODEL)
    return _embedder
def _get_client() -> chromadb.PersistentClient:
    global _client
    if _client is None:
        Path(CHROMA_DIR).mkdir(parents=True, exist_ok=True)
        _client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    return _client
def _get_collection() -> chromadb.Collection:
    global _collection
    if _collection is None:
        client = _get_client()
        ef = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=EMBEDDING_MODEL
        )
        _collection = client.get_or_create_collection(
            name=CHROMA_COLLECTION,
            embedding_function=ef,
            metadata={"hnsw:space": "cosine"},
        )
    return _collection
def build_vector_store(force: bool = False) -> bool:
    """
    Populate ChromaDB with schema knowledge chunks.
    Skips if already populated (unless force=True).
    """
    try:
        col = _get_collection()
        if not force and col.count() >= len(RAG_CHUNKS):
            logger.info("✅ Vector store already populated, skipping.")
            return True
        # Clear existing data
        if col.count() > 0:
            existing_ids = col.get()["ids"]
            if existing_ids:
                col.delete(ids=existing_ids)
        ids       = [c["id"]       for c in RAG_CHUNKS]
        documents = [c["text"]     for c in RAG_CHUNKS]
        metadatas = [c["metadata"] for c in RAG_CHUNKS]
        col.add(ids=ids, documents=documents, metadatas=metadatas)
        logger.info(f"✅ Vector store built with {len(RAG_CHUNKS)} chunks.")
        return True
    except Exception as e:
        logger.error(f"❌ Vector store build failed: {e}")
        return False
def retrieve_context(query: str, top_k: int = TOP_K_RESULTS) -> str:
    """
    Retrieve the most relevant schema/example chunks for a query.
    Returns a formatted context string ready for the LLM prompt.
    """
    try:
        col = _get_collection()
        if col.count() == 0:
            build_vector_store()
        results = col.query(
            query_texts=[query],
            n_results=min(top_k, col.count()),
            include=["documents", "metadatas", "distances"],
        )
        docs      = results["documents"][0]
        distances = results["distances"][0]
        # Filter out very low-relevance hits (cosine distance > 0.8)
        relevant  = [
            doc for doc, dist in zip(docs, distances) if dist < 0.8
        ]
        if not relevant:
            relevant = docs[:3]          # fallback: take top-3
        context = "\n\n---\n\n".join(relevant)
        logger.info(f"📚 Retrieved {len(relevant)} context chunks for query.")
        return context
    except Exception as e:
        logger.error(f"❌ RAG retrieval failed: {e}")
        return ""
def get_store_stats() -> dict:
    """Return basic stats about the vector store."""
    try:
        col = _get_collection()
        return {
            "collection": CHROMA_COLLECTION,
            "total_chunks": col.count(),
            "embedding_model": EMBEDDING_MODEL,
        }
    except Exception as e:
        return {"error": str(e)}
