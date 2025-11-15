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
    """Auto-mock OpenAI embeddings for all tests that need it."""
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
                yield
    else:
        # Real API key exists, don't mock
        yield

