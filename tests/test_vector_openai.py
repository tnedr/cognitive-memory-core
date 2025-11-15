"""Tests for OpenAI embedding support."""

import os
from unittest.mock import MagicMock, patch

import pytest

from cmemory.vector.openai_embedder import OpenAIEmbedder
from cmemory.vector.vector_index import VectorIndex


def test_openai_embedder_no_key():
    """Test OpenAIEmbedder when no API key is available."""
    with patch.dict(os.environ, {}, clear=True):
        embedder = OpenAIEmbedder()
        assert not embedder.is_available()
        assert embedder.client is None


def test_openai_embedder_with_key():
    """Test OpenAIEmbedder with API key."""
    mock_key = "sk-test-key-12345"
    with patch.dict(os.environ, {"OPENAI_API_KEY": mock_key}):
        with patch("openai.OpenAI") as mock_openai:
            mock_client = MagicMock()
            mock_openai.return_value = mock_client

            embedder = OpenAIEmbedder()
            assert embedder.is_available()
            assert embedder.client is not None
            assert embedder.dimension == 1536


def test_openai_embedder_embed_text():
    """Test embedding text with OpenAI."""
    mock_key = "sk-test-key-12345"
    with patch.dict(os.environ, {"OPENAI_API_KEY": mock_key}):
        with patch("openai.OpenAI") as mock_openai:
            mock_client = MagicMock()
            mock_response = MagicMock()
            mock_response.data = [MagicMock(embedding=[0.1] * 1536)]
            mock_client.embeddings.create.return_value = mock_response
            mock_openai.return_value = mock_client

            embedder = OpenAIEmbedder()
            result = embedder.embed_text("test text")
            assert len(result) == 1536
            assert all(isinstance(x, float) for x in result)
            mock_client.embeddings.create.assert_called_once()


def test_openai_embedder_embed_batch():
    """Test batch embedding with OpenAI."""
    mock_key = "sk-test-key-12345"
    with patch.dict(os.environ, {"OPENAI_API_KEY": mock_key}):
        with patch("openai.OpenAI") as mock_openai:
            mock_client = MagicMock()
            mock_response = MagicMock()
            mock_response.data = [
                MagicMock(embedding=[0.1] * 1536),
                MagicMock(embedding=[0.2] * 1536),
            ]
            mock_client.embeddings.create.return_value = mock_response
            mock_openai.return_value = mock_client

            embedder = OpenAIEmbedder()
            results = embedder.embed_batch(["text1", "text2"])
            assert len(results) == 2
            assert all(len(r) == 1536 for r in results)
            mock_client.embeddings.create.assert_called_once()


def test_vector_index_with_openai():
    """Test VectorIndex using OpenAI embeddings."""
    mock_key = "sk-test-key-12345"
    with patch.dict(os.environ, {"OPENAI_API_KEY": mock_key}):
        with patch("openai.OpenAI") as mock_openai:
            mock_client = MagicMock()
            mock_response = MagicMock()
            mock_response.data = [MagicMock(embedding=[0.1] * 1536)]
            mock_client.embeddings.create.return_value = mock_response
            mock_openai.return_value = mock_client

            index = VectorIndex(use_chroma=False, use_openai=True)
            assert index.openai_embedder is not None
            assert index.openai_embedder.is_available()
            assert index.embedding_dimension == 1536

            # Test embedding generation
            embedding = index._get_embedding("test text")
            assert len(embedding) == 1536


def test_vector_index_openai_fallback():
    """Test VectorIndex falls back when OpenAI fails."""
    mock_key = "sk-test-key-12345"
    with patch.dict(os.environ, {"OPENAI_API_KEY": mock_key}):
        with patch("openai.OpenAI") as mock_openai:
            mock_client = MagicMock()
            mock_client.embeddings.create.side_effect = Exception("API error")
            mock_openai.return_value = mock_client

            index = VectorIndex(use_chroma=False, use_openai=True)
            # Should fall back to sentence-transformers or dummy
            embedding = index._get_embedding("test text")
            # Will be dummy or sentence-transformers dimension
            assert len(embedding) > 0
            # Verify fallback worked - embedding should be generated despite OpenAI error
            # (dimension may be 1536 if OpenAI was initialized, but content is dummy/fallback)
            assert all(x == 0.0 for x in embedding) or len(embedding) == 384  # Dummy or ST


def test_vector_index_no_openai_key():
    """Test VectorIndex when no OpenAI key is available."""
    with patch.dict(os.environ, {}, clear=True):
        index = VectorIndex(use_chroma=False, use_openai=True)
        assert index.openai_embedder is None or not index.openai_embedder.is_available()
        # embedder may be None if sentence-transformers not available
        # Just verify it doesn't crash and returns an embedding
        embedding = index._get_embedding("test text")
        assert len(embedding) > 0
        # Should use fallback (sentence-transformers or dummy)
        assert index.embedding_dimension in [384, 1536]  # Accept either

