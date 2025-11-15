"""OpenAI embedding provider for semantic search."""

import logging
import os
from pathlib import Path
from typing import List, Optional

# Try to load .env file if python-dotenv is available
try:
    from dotenv import load_dotenv

    # Load .env from project root (parent of src/)
    env_path = Path(__file__).parent.parent.parent.parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
except ImportError:
    pass  # python-dotenv not installed, rely on system env vars

logger = logging.getLogger(__name__)


class OpenAIEmbedder:
    """OpenAI embeddings provider using text-embedding-3-small model."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize OpenAI embedder.

        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var).
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.client = None
        self.model = "text-embedding-3-small"
        self.dimension = 1536  # text-embedding-3-small dimension

        if self.api_key:
            try:
                from openai import OpenAI

                self.client = OpenAI(api_key=self.api_key)
                logger.info("OpenAI embedder initialized with API key")
            except ImportError:
                logger.warning("openai package not installed, OpenAI embeddings unavailable")
                self.client = None
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI client: {e}")
                self.client = None
        else:
            logger.debug("No OPENAI_API_KEY found, OpenAI embeddings unavailable")

    def is_available(self) -> bool:
        """Check if OpenAI embeddings are available."""
        return self.client is not None

    def embed_text(self, text: str) -> List[float]:
        """Generate embedding for text using OpenAI API.

        Args:
            text: Text to embed.

        Returns:
            List of floats representing the embedding vector.

        Raises:
            RuntimeError: If OpenAI client is not available or API call fails.
        """
        if not self.client:
            raise RuntimeError("OpenAI client not available")

        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=text,
            )
            embedding = response.data[0].embedding
            logger.debug(f"Generated OpenAI embedding (dim={len(embedding)})")
            return embedding
        except Exception as e:
            logger.error(f"OpenAI embedding failed: {e}")
            raise RuntimeError(f"OpenAI embedding failed: {e}") from e

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed.

        Returns:
            List of embedding vectors.
        """
        if not self.client:
            raise RuntimeError("OpenAI client not available")

        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=texts,
            )
            embeddings = [item.embedding for item in response.data]
            logger.debug(f"Generated {len(embeddings)} OpenAI embeddings")
            return embeddings
        except Exception as e:
            logger.error(f"OpenAI batch embedding failed: {e}")
            raise RuntimeError(f"OpenAI batch embedding failed: {e}") from e

