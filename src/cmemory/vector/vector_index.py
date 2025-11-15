"""Vector index using ChromaDB with FAISS fallback."""

import logging
from typing import List, Optional, Tuple

import numpy as np

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

    @staticmethod
    def _cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors.

        Args:
            vec1: First vector.
            vec2: Second vector.

        Returns:
            Cosine similarity score in range [-1, 1].
        """
        v1 = np.array(vec1, dtype=np.float32)
        v2 = np.array(vec2, dtype=np.float32)
        denom = np.linalg.norm(v1) * np.linalg.norm(v2)
        if denom == 0:
            return 0.0
        return float(np.dot(v1, v2) / denom)

    def __init__(
        self,
        collection_name: str = "knowledge_blocks",
        use_chroma: bool = True,
        use_openai: bool = True,
    ):
        """Initialize vector index.

        Args:
            collection_name: Name of the ChromaDB collection.
            use_chroma: Use ChromaDB if available, otherwise FAISS.
            use_openai: Use OpenAI embeddings (required, default: True).

        Raises:
            RuntimeError: If OpenAI embeddings are not available.
        """
        self.collection_name = collection_name
        self.use_chroma = use_chroma
        self.collection = None
        self.faiss_index = None
        self.openai_embedder = None
        self.embedding_dimension = 1536  # OpenAI text-embedding-3-small dimension

        # Initialize OpenAI embedder (required)
        if use_openai:
            from cmemory.vector.openai_embedder import OpenAIEmbedder

            self.openai_embedder = OpenAIEmbedder()
            if not self.openai_embedder.is_available():
                raise RuntimeError(
                    "OpenAI embeddings are required but not available. "
                    "Please set OPENAI_API_KEY environment variable or provide it in .env file."
                )
            logger.info("Using OpenAI embeddings for semantic search")
        else:
            raise RuntimeError("OpenAI embeddings are required. Set use_openai=True.")

        # Initialize vector store
        if use_chroma:
            try:
                import chromadb
                from chromadb.config import Settings
                from pathlib import Path

                # Use persistent ChromaDB storage in .chroma directory
                chroma_path = Path.cwd() / ".chroma"
                chroma_path.mkdir(exist_ok=True)
                self.client = chromadb.PersistentClient(
                    path=str(chroma_path),
                    settings=Settings(anonymized_telemetry=False),
                )
                try:
                    self.collection = self.client.get_collection(collection_name)
                except Exception:
                    self.collection = self.client.create_collection(collection_name)
                logger.info(f"Using ChromaDB for vector storage (persistent: {chroma_path})")
            except Exception as e:
                logger.warning(f"ChromaDB not available, using FAISS fallback: {e}")
                self.use_chroma = False

        if not self.use_chroma:
            self.faiss_index = FAISSIndex(dimension=self.embedding_dimension)
            logger.info(f"Using FAISS for vector storage (dim={self.embedding_dimension})")

    def _get_embedding(self, text: str) -> List[float]:
        """Get embedding for text using OpenAI.

        Args:
            text: Text to embed.

        Returns:
            Embedding vector (1536 dimensions for text-embedding-3-small).

        Raises:
            RuntimeError: If OpenAI embeddings are not available or API call fails.
        """
        if not self.openai_embedder or not self.openai_embedder.is_available():
            raise RuntimeError(
                "OpenAI embeddings are required but not available. "
                "Please set OPENAI_API_KEY environment variable."
            )

        try:
            return self.openai_embedder.embed_text(text)
        except Exception as e:
            logger.error(f"OpenAI embedding failed: {e}")
            raise RuntimeError(f"Failed to generate OpenAI embedding: {e}") from e

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
                dimension = len(embeddings[0]) if embeddings else self.embedding_dimension
                self.faiss_index = FAISSIndex(dimension=dimension)
                self.faiss_index.add(block_ids, embeddings)
        else:
            if self.faiss_index is None:
                dimension = len(embeddings[0]) if embeddings else self.embedding_dimension
                self.faiss_index = FAISSIndex(dimension=dimension)
            self.faiss_index.add(block_ids, embeddings)

    def similarity_search(
        self, query: str, top_k: int = 5, keyword_boost: Optional[List[str]] = None
    ) -> List[SearchResult]:
        """Search for similar blocks using cosine similarity.

        Args:
            query: Search query text.
            top_k: Number of results to return.
            keyword_boost: Optional list of keywords to boost scores (not used here, passed to MemorySystem).

        Returns:
            List of SearchResult objects with cosine similarity scores.
        """
        query_embedding = self._get_embedding(query)

        if self.use_chroma and self.collection:
            try:
                # Get more results than needed to compute accurate cosine similarity
                results = self.collection.query(
                    query_embeddings=[query_embedding],
                    n_results=min(top_k * 2, 100),  # Get more candidates for better scoring
                    include=["embeddings", "documents"],
                )
                search_results = []
                if results["ids"] and len(results["ids"][0]) > 0:
                    # Get stored embeddings from ChromaDB
                    # ChromaDB returns: {"embeddings": [numpy_array]} where numpy_array has shape (n_results, 1536)
                    stored_embeddings_list = results.get("embeddings", [])
                    stored_embeddings_array = stored_embeddings_list[0] if stored_embeddings_list else None
                    
                    # Also get distances for fallback
                    distances_list = results.get("distances", [])
                    distances = distances_list[0] if distances_list else []
                    
                    for i, block_id in enumerate(results["ids"][0]):
                        # Compute cosine similarity manually
                        score = 0.0
                        try:
                            if stored_embeddings_array is not None and i < stored_embeddings_array.shape[0]:
                                # Extract i-th embedding from numpy array (shape: (n, 1536))
                                stored_embedding_raw = stored_embeddings_array[i]
                                
                                # Convert numpy array to list
                                if hasattr(stored_embedding_raw, 'tolist'):
                                    stored_embedding = stored_embedding_raw.tolist()
                                elif hasattr(stored_embedding_raw, 'flatten'):
                                    stored_embedding = stored_embedding_raw.flatten().tolist()
                                else:
                                    stored_embedding = list(stored_embedding_raw)
                                
                                if stored_embedding and len(stored_embedding) == len(query_embedding):
                                    score = self._cosine_similarity(query_embedding, stored_embedding)
                                else:
                                    raise ValueError(f"Embedding dimension mismatch: {len(stored_embedding) if stored_embedding else 0} != {len(query_embedding)}")
                            else:
                                raise ValueError("No embedding available")
                        except (ValueError, IndexError, TypeError, AttributeError) as e:
                            # Fallback: use distance if embeddings not available
                            if distances and i < len(distances):
                                distance = float(distances[i])
                                # Convert L2 distance to approximate similarity
                                # L2 distance is typically 0-2 for normalized vectors, convert to 0-1 range
                                score = max(0.0, 1.0 - (distance / 2.0))
                            else:
                                score = 0.0
                            logger.debug(f"Using distance fallback for {block_id}: {e}")

                        content = results["documents"][0][i] if results.get("documents") else ""
                        search_results.append(
                            SearchResult(
                                block_id=block_id,
                                score=float(score),
                                content=content,
                                semantic_score=float(score),
                                keyword_score=0.0,
                                explanation={"semantic": float(score)},
                            )
                        )
                # Sort by score descending and return top_k
                search_results.sort(key=lambda x: x.score, reverse=True)
                return search_results[:top_k]
            except Exception as e:
                logger.error(f"ChromaDB search failed: {e}")
                # Fallback to FAISS
                if self.faiss_index is None:
                    return []

        if self.faiss_index:
            # For FAISS, compute cosine similarity from cached embeddings
            results = self.faiss_index.search(query_embedding, top_k * 2)
            search_results = []
            for block_id, _ in results:
                if block_id in self.faiss_index.embeddings_cache:
                    stored_embedding = self.faiss_index.embeddings_cache[block_id]
                    score = self._cosine_similarity(query_embedding, stored_embedding)
                    search_results.append(
                        SearchResult(
                            block_id=block_id,
                            score=float(score),
                            content="",
                            semantic_score=float(score),
                            keyword_score=0.0,
                            explanation={"semantic": float(score)},
                        )
                    )
            search_results.sort(key=lambda x: x.score, reverse=True)
            return search_results[:top_k]

        return []

