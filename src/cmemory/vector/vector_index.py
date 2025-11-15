"""Vector index using ChromaDB (required) with OpenAI embeddings (required)."""

import logging
from pathlib import Path
from typing import List, Optional

import numpy as np

from cmemory.models import SearchResult

logger = logging.getLogger(__name__)


class VectorIndex:
    """Handles vector embeddings and similarity search using ChromaDB and OpenAI."""

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
    ):
        """Initialize vector index with ChromaDB and OpenAI embeddings.

        Args:
            collection_name: Name of the ChromaDB collection.

        Raises:
            RuntimeError: If OpenAI embeddings or ChromaDB are not available.
        """
        self.collection_name = collection_name
        self.collection = None
        self.embedding_dimension = 1536  # OpenAI text-embedding-3-small dimension

        # Initialize OpenAI embedder (required)
        from cmemory.vector.openai_embedder import OpenAIEmbedder

        self.openai_embedder = OpenAIEmbedder()
        if not self.openai_embedder.is_available():
            raise RuntimeError(
                "OpenAI embeddings are required but not available. "
                "Please set OPENAI_API_KEY environment variable or provide it in .env file. "
                "Install openai package with: uv pip install openai"
            )
        logger.info("Using OpenAI embeddings for semantic search")

        # Initialize ChromaDB (required)
        try:
            import chromadb
            from chromadb.config import Settings

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
        except ImportError as e:
            raise RuntimeError(
                f"ChromaDB is required but not installed. Install with: uv pip install chromadb"
            ) from e
        except Exception as e:
            raise RuntimeError(
                f"ChromaDB is required but failed to initialize: {e}"
            ) from e

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
                "OpenAI embeddings required: set OPENAI_API_KEY and install openai package"
            )

        return self.openai_embedder.embed_text(text)

    def add_embeddings(self, block_ids: List[str], texts: List[str]) -> None:
        """Add embeddings for knowledge blocks.

        Args:
            block_ids: List of block IDs.
            texts: List of text contents to embed.

        Raises:
            RuntimeError: If ChromaDB operation fails.
        """
        embeddings = [self._get_embedding(text) for text in texts]

        if not self.collection:
            raise RuntimeError("ChromaDB collection is not available")

        try:
            self.collection.add(
                ids=block_ids,
                embeddings=embeddings,
                documents=texts,
            )
        except Exception as e:
            logger.error(f"Failed to add to ChromaDB: {e}")
            raise RuntimeError(f"ChromaDB operation failed: {e}") from e

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

        Raises:
            RuntimeError: If ChromaDB operation fails.
        """
        if not self.collection:
            raise RuntimeError("ChromaDB collection is not available")

        query_embedding = self._get_embedding(query)

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
                                raise ValueError(
                                    f"Embedding dimension mismatch: {len(stored_embedding) if stored_embedding else 0} != {len(query_embedding)}"
                                )
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
            raise RuntimeError(f"ChromaDB search failed: {e}") from e
