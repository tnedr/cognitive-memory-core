"""Pytest configuration for cognitive-memory-core tests."""

import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Add src directory to Python path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))


@pytest.fixture(autouse=True)
def mock_openai_embeddings():
    """Auto-mock OpenAI embeddings and ChromaDB for all tests that need it."""
    # Only mock if OPENAI_API_KEY is not set (for CI/local testing)
    if not os.getenv("OPENAI_API_KEY"):
        with patch("openai.OpenAI") as mock_openai:
            mock_client = MagicMock()
            mock_response = MagicMock()
            mock_response.data = [MagicMock(embedding=[0.1] * 1536)]
            mock_client.embeddings.create.return_value = mock_response
            mock_openai.return_value = mock_client
            # Set a fake API key so OpenAIEmbedder initializes
            with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test-key"}):
                # Also mock ChromaDB for all tests
                with patch("chromadb.PersistentClient") as mock_chroma:
                    mock_collection = MagicMock()
                    mock_collection.query.return_value = {"ids": [[]], "embeddings": [[]], "documents": [[]]}
                    mock_client_instance = MagicMock()
                    mock_client_instance.get_collection.side_effect = Exception("Not found")
                    mock_client_instance.create_collection.return_value = mock_collection
                    mock_chroma.return_value = mock_client_instance
                    yield
    else:
        # Real API key exists, but still mock ChromaDB for tests
        with patch("chromadb.PersistentClient") as mock_chroma:
            mock_collection = MagicMock()
            mock_collection.query.return_value = {"ids": [[]], "embeddings": [[]], "documents": [[]]}
            mock_client_instance = MagicMock()
            mock_client_instance.get_collection.side_effect = Exception("Not found")
            mock_client_instance.create_collection.return_value = mock_collection
            mock_chroma.return_value = mock_client_instance
            yield

