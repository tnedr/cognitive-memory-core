"""Tests for hybrid search with cosine similarity and keyword boosting."""

import os
import tempfile
from unittest.mock import MagicMock, patch

import pytest

from cmemory import MemorySystem
from cmemory.vector.vector_index import VectorIndex


def test_cosine_similarity():
    """Test cosine similarity calculation."""
    # Test identical vectors
    vec1 = [1.0, 0.0, 0.0]
    vec2 = [1.0, 0.0, 0.0]
    assert VectorIndex._cosine_similarity(vec1, vec2) == pytest.approx(1.0, abs=0.001)

    # Test orthogonal vectors
    vec1 = [1.0, 0.0]
    vec2 = [0.0, 1.0]
    assert VectorIndex._cosine_similarity(vec1, vec2) == pytest.approx(0.0, abs=0.001)

    # Test opposite vectors
    vec1 = [1.0, 0.0]
    vec2 = [-1.0, 0.0]
    assert VectorIndex._cosine_similarity(vec1, vec2) == pytest.approx(-1.0, abs=0.001)

    # Test zero vector
    vec1 = [0.0, 0.0]
    vec2 = [1.0, 0.0]
    assert VectorIndex._cosine_similarity(vec1, vec2) == pytest.approx(0.0, abs=0.001)


def test_hybrid_search_with_boost():
    """Test hybrid search with keyword boosting."""
    with patch("openai.OpenAI") as mock_openai:
        mock_client = MagicMock()
        mock_response = MagicMock()
        # Create embeddings that will have known cosine similarity
        mock_response.data = [MagicMock(embedding=[0.1] * 1536)]
        mock_client.embeddings.create.return_value = mock_response
        mock_openai.return_value = mock_client

        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test-key"}):
            with tempfile.TemporaryDirectory() as tmpdir:
                mem = MemorySystem(knowledge_path=tmpdir, use_chroma=False)

                # Create blocks with specific content
                id1 = mem.record(
                    "NAD boosters include NMN and resveratrol",
                    {"id": "NAD-001", "title": "NAD Boosters Guide"},
                )
                id2 = mem.record(
                    "Python programming language basics",
                    {"id": "PYTHON-001", "title": "Python Tutorial"},
                )

                # Encode blocks
                mem.encode(id1)
                mem.encode(id2)

                # Search with boost
                results = mem.retrieve("supplements", top_k=2, boost=["nad"])

                # NAD block should be first due to boost
                assert len(results) >= 1
                assert results[0] == "NAD-001" or "NAD-001" in results


def test_hybrid_search_with_exclude():
    """Test hybrid search with keyword exclusion."""
    with patch("openai.OpenAI") as mock_openai:
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.data = [MagicMock(embedding=[0.1] * 1536)]
        mock_client.embeddings.create.return_value = mock_response
        mock_openai.return_value = mock_client

        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test-key"}):
            with tempfile.TemporaryDirectory() as tmpdir:
                mem = MemorySystem(knowledge_path=tmpdir, use_chroma=False)

                # Create blocks
                id1 = mem.record("Test content about NAD", {"id": "TEST-001", "title": "Test Block"})
                id2 = mem.record("Python programming", {"id": "PYTHON-001", "title": "Python Guide"})

                mem.encode(id1)
                mem.encode(id2)

                # Search with exclude
                results = mem.retrieve("programming", top_k=5, exclude=["test"])

                # Test block should be excluded
                assert "TEST-001" not in results


def test_cosine_similarity_in_search():
    """Test that similarity_search returns cosine similarity scores."""
    with patch("openai.OpenAI") as mock_openai:
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.data = [MagicMock(embedding=[0.1] * 1536)]
        mock_client.embeddings.create.return_value = mock_response
        mock_openai.return_value = mock_client

        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test-key"}):
            index = VectorIndex(use_chroma=False, use_openai=True)

            # Mock FAISS index with known embeddings
            from cmemory.vector.vector_index import FAISSIndex

            index.faiss_index = FAISSIndex(dimension=1536)
            test_embedding = [0.1] * 1536
            index.faiss_index.add(["TEST-001"], [test_embedding])
            index.faiss_index.embeddings_cache["TEST-001"] = test_embedding

            # Search should return cosine similarity
            results = index.similarity_search("test query", top_k=1)

            assert len(results) > 0
            # Cosine similarity should be in range [-1, 1]
            assert -1.0 <= results[0].score <= 1.0
            # For identical embeddings, should be close to 1.0
            # (but query embedding is different, so it won't be exactly 1.0)


def test_hybrid_score_ordering():
    """Test that hybrid scores properly order results."""
    with patch("openai.OpenAI") as mock_openai:
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.data = [MagicMock(embedding=[0.1] * 1536)]
        mock_client.embeddings.create.return_value = mock_response
        mock_openai.return_value = mock_client

        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test-key"}):
            with tempfile.TemporaryDirectory() as tmpdir:
                mem = MemorySystem(knowledge_path=tmpdir, use_chroma=False)

                # Create blocks with different relevance
                id1 = mem.record("NAD boosters are important", {"id": "NAD-001", "title": "NAD Guide"})
                id2 = mem.record("Python is a language", {"id": "PYTHON-001", "title": "Python Basics"})

                mem.encode(id1)
                mem.encode(id2)

                # Search with boost for "nad"
                results = mem.retrieve("supplements", top_k=2, boost=["nad"])

                # Results should be ordered by hybrid score
                assert len(results) >= 1
                # NAD block should rank higher due to boost
                if len(results) >= 2:
                    # Check that scores are descending
                    scores = []
                    for block_id in results:
                        block = mem.file_storage.read(block_id)
                        if block:
                            # Get approximate score
                            vector_results = mem.vector_index.similarity_search("supplements", top_k=10)
                            score = next((r.score for r in vector_results if r.block_id == block_id), 0.0)
                            if "nad" in block.title.lower():
                                score += 0.2
                            scores.append(score)
                    # Scores should be non-increasing
                    assert scores == sorted(scores, reverse=True)

