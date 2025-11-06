"""Vector index using ChromaDB with FAISS fallback."""

import logging
from typing import List, Optional, Tuple

from cmemory.models import SearchResult

logger = logging.getLogger(__name__)


class FAISSIndex:
    """FAISS-based vector index fallback."""

    def __init__(self, dimension: int = 384):
        """Initialize FAISS index.

        Args:
            dimension: Embedding dimension (default: 384 for sentence-transformers).
        """
        self.dimension = dimension
        self.index = None
        self.id_to_index: dict = {}
        self.index_to_id: dict = {}
        self.embeddings_cache: dict = {}

    def _ensure_index(self):
        """Ensure FAISS index is initialized."""
        if self.index is None:
            try:
                import faiss

                self.index = faiss.IndexFlatL2(self.dimension)
            except ImportError:
                logger.warning("FAISS not available, using dummy index")
                self.index = None

    def add(self, ids: List[str], embeddings: List[List[float]]) -> None:
        """Add embeddings to index.

        Args:
            ids: List of block IDs.
            embeddings: List of embedding vectors.
        """
        self._ensure_index()
        if self.index is None:
            return

        import numpy as np

        start_idx = len(self.id_to_index)
        for i, (block_id, embedding) in enumerate(zip(ids, embeddings)):
            idx = start_idx + i
            self.id_to_index[block_id] = idx
            self.index_to_id[idx] = block_id
            self.embeddings_cache[block_id] = embedding

        if embeddings:
            embeddings_array = np.array(embeddings, dtype=np.float32)
            self.index.add(embeddings_array)

    def search(self, query_embedding: List[float], top_k: int = 5) -> List[Tuple[str, float]]:
        """Search for similar embeddings.

        Args:
            query_embedding: Query embedding vector.
            top_k: Number of results to return.

        Returns:
            List of (block_id, distance) tuples.
        """
        self._ensure_index()
        if self.index is None or len(self.id_to_index) == 0:
            return []

        import numpy as np

        query_array = np.array([query_embedding], dtype=np.float32)
        distances, indices = self.index.search(query_array, min(top_k, len(self.id_to_index)))

        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx < len(self.index_to_id):
                block_id = self.index_to_id[idx]
                # Convert L2 distance to similarity score (lower distance = higher similarity)
                score = 1.0 / (1.0 + float(dist))
                results.append((block_id, score))

        return results


class VectorIndex:
    """Handles vector embeddings and similarity search."""

    def __init__(
        self,
        collection_name: str = "knowledge_blocks",
        use_chroma: bool = True,
        embedding_model: str = "all-MiniLM-L6-v2",
    ):
        """Initialize vector index.

        Args:
            collection_name: Name of the ChromaDB collection.
            use_chroma: Use ChromaDB if available, otherwise FAISS.
            embedding_model: Name of the sentence transformer model.
        """
        self.collection_name = collection_name
        self.use_chroma = use_chroma
        self.embedding_model = embedding_model
        self.collection = None
        self.faiss_index = None
        self.embedder = None

        # Initialize embedder
        try:
            from sentence_transformers import SentenceTransformer

            self.embedder = SentenceTransformer(embedding_model)
            logger.info(f"Loaded embedding model: {embedding_model}")
        except ImportError:
            logger.warning("sentence-transformers not available, embeddings will be dummy")

        # Initialize vector store
        if use_chroma:
            try:
                import chromadb
                from chromadb.config import Settings

                self.client = chromadb.Client(Settings(anonymized_telemetry=False))
                try:
                    self.collection = self.client.get_collection(collection_name)
                except Exception:
                    self.collection = self.client.create_collection(collection_name)
                logger.info("Using ChromaDB for vector storage")
            except Exception as e:
                logger.warning(f"ChromaDB not available, using FAISS fallback: {e}")
                self.use_chroma = False

        if not self.use_chroma:
            self.faiss_index = FAISSIndex()
            logger.info("Using FAISS for vector storage")

    def _get_embedding(self, text: str) -> List[float]:
        """Get embedding for text.

        Args:
            text: Text to embed.

        Returns:
            Embedding vector.
        """
        if self.embedder is None:
            # Dummy embedding for testing
            return [0.0] * 384
        return self.embedder.encode(text, show_progress_bar=False).tolist()

    def add_embeddings(self, block_ids: List[str], texts: List[str]) -> None:
        """Add embeddings for knowledge blocks.

        Args:
            block_ids: List of block IDs.
            texts: List of text contents to embed.
        """
        embeddings = [self._get_embedding(text) for text in texts]

        if self.use_chroma and self.collection:
            try:
                self.collection.add(
                    ids=block_ids,
                    embeddings=embeddings,
                    documents=texts,
                )
            except Exception as e:
                logger.error(f"Failed to add to ChromaDB: {e}")
                # Fallback to FAISS
                self.use_chroma = False
                self.faiss_index = FAISSIndex(dimension=len(embeddings[0]) if embeddings else 384)
                self.faiss_index.add(block_ids, embeddings)
        else:
            if self.faiss_index is None:
                dimension = len(embeddings[0]) if embeddings else 384
                self.faiss_index = FAISSIndex(dimension=dimension)
            self.faiss_index.add(block_ids, embeddings)

    def similarity_search(self, query: str, top_k: int = 5) -> List[SearchResult]:
        """Search for similar blocks.

        Args:
            query: Search query text.
            top_k: Number of results to return.

        Returns:
            List of SearchResult objects.
        """
        query_embedding = self._get_embedding(query)

        if self.use_chroma and self.collection:
            try:
                results = self.collection.query(
                    query_embeddings=[query_embedding],
                    n_results=top_k,
                )
                search_results = []
                if results["ids"] and len(results["ids"][0]) > 0:
                    for i, block_id in enumerate(results["ids"][0]):
                        score = 1.0 - (results["distances"][0][i] if results.get("distances") else 0.0)
                        content = results["documents"][0][i] if results.get("documents") else ""
                        search_results.append(
                            SearchResult(
                                block_id=block_id,
                                score=float(score),
                                content=content,
                            )
                        )
                return search_results
            except Exception as e:
                logger.error(f"ChromaDB search failed: {e}")
                # Fallback to FAISS
                if self.faiss_index is None:
                    return []

        if self.faiss_index:
            results = self.faiss_index.search(query_embedding, top_k)
            return [
                SearchResult(
                    block_id=block_id,
                    score=score,
                    content="",  # Content will be loaded separately
                )
                for block_id, score in results
            ]

        return []

