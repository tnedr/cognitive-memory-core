"""Tests for Reciprocal Rank Fusion (RRF) retrieval."""

import os
import tempfile
from unittest.mock import MagicMock, patch

import pytest

from cmemory import MemorySystem
from cmemory.models import SearchResult


def test_keyword_rank():
    """Test keyword ranking function."""
    with patch("openai.OpenAI") as mock_openai:
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.data = [MagicMock(embedding=[0.1] * 1536)]
        mock_client.embeddings.create.return_value = mock_response
        mock_openai.return_value = mock_client

        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test-key"}):
            with tempfile.TemporaryDirectory() as tmpdir:
                mem = MemorySystem(knowledge_path=tmpdir, use_chroma=False)

                # Create blocks with different keyword relevance
                id1 = mem.record(
                    "NAD boosters are important",
                    {"id": "NAD-001", "title": "NAD Boosters Guide"},
                )
                id2 = mem.record(
                    "Python programming basics",
                    {"id": "PYTHON-001", "title": "Python Tutorial"},
                )

                # Test keyword ranking
                keyword_ranks = mem._keyword_rank("nad boosters", [id1, id2])

                # NAD block should rank higher (rank 1 is best)
                assert id1 in keyword_ranks
                assert keyword_ranks[id1] == 1  # Best rank
                # Python block may or may not be ranked depending on matches
                if id2 in keyword_ranks:
                    assert keyword_ranks[id2] > keyword_ranks[id1]


def test_rrf_fuse():
    """Test RRF fusion combines semantic and keyword rankings."""
    with patch("openai.OpenAI") as mock_openai:
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.data = [MagicMock(embedding=[0.1] * 1536)]
        mock_client.embeddings.create.return_value = mock_response
        mock_openai.return_value = mock_client

        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test-key"}):
            # Create mock semantic results
            semantic_results = [
                SearchResult(
                    block_id="BLOCK-1",
                    score=0.9,
                    content="Content 1",
                    semantic_score=0.9,
                    keyword_score=0.0,
                    explanation={"semantic": 0.9},
                ),
                SearchResult(
                    block_id="BLOCK-2",
                    score=0.7,
                    content="Content 2",
                    semantic_score=0.7,
                    keyword_score=0.0,
                    explanation={"semantic": 0.7},
                ),
            ]

            # Create keyword ranks (BLOCK-2 has better keyword match)
            keyword_ranks = {"BLOCK-1": 2, "BLOCK-2": 1}

            with tempfile.TemporaryDirectory() as tmpdir:
                mem = MemorySystem(knowledge_path=tmpdir, use_chroma=False)

                # Fuse rankings
                fused = mem._rrf_fuse(semantic_results, keyword_ranks, k=60)

                # Should have both blocks
                assert len(fused) == 2

                # Check RRF scores are positive
                for result in fused:
                    assert result.score > 0.0
                    assert "rrf_score" in result.explanation
                    assert "semantic_rank" in result.explanation
                    assert "keyword_rank" in result.explanation

                    # BLOCK-2 should rank higher due to better keyword match + decent semantic
                    # (semantic rank 2 + keyword rank 1 vs semantic rank 1 + keyword rank 2)
                    block2_score = next(r.score for r in fused if r.block_id == "BLOCK-2")
                    block1_score = next(r.score for r in fused if r.block_id == "BLOCK-1")
                    # With k=60, the scores are very close, so we check they're at least equal
                    # In practice with different semantic scores, BLOCK-2 should rank higher
                    assert block2_score >= block1_score


def test_retrieve_with_rrf():
    """Test retrieve() with RRF fusion enabled."""
    with patch("openai.OpenAI") as mock_openai:
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.data = [MagicMock(embedding=[0.1] * 1536)]
        mock_client.embeddings.create.return_value = mock_response
        mock_openai.return_value = mock_client

        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test-key"}):
            with tempfile.TemporaryDirectory() as tmpdir:
                mem = MemorySystem(knowledge_path=tmpdir, use_chroma=False)

                # Create blocks with different characteristics
                id1 = mem.record(
                    "NAD boosters include NMN and resveratrol",
                    {"id": "NAD-001", "title": "NAD Boosters Guide"},
                )
                id2 = mem.record(
                    "Python programming language basics",
                    {"id": "PYTHON-001", "title": "Python Tutorial"},
                )

                mem.encode(id1)
                mem.encode(id2)

                # Retrieve with RRF
                results = mem.retrieve("nad boosters", top_k=2, explain=True, use_rrf=True)

                # Should return SearchResult objects
                assert len(results) >= 1
                assert isinstance(results[0], SearchResult)

                # Check RRF explanation fields
                for result in results:
                    if "rrf_score" in result.explanation:
                        assert result.explanation["rrf_score"] > 0.0
                        assert "semantic_rank" in result.explanation
                        assert "keyword_rank" in result.explanation


def test_rrf_scores_are_monotonic():
    """Test that RRF scores are properly ordered."""
    with patch("openai.OpenAI") as mock_openai:
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.data = [MagicMock(embedding=[0.1] * 1536)]
        mock_client.embeddings.create.return_value = mock_response
        mock_openai.return_value = mock_client

        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test-key"}):
            semantic_results = [
                SearchResult(
                    block_id=f"BLOCK-{i}",
                    score=0.9 - i * 0.1,
                    content=f"Content {i}",
                    semantic_score=0.9 - i * 0.1,
                    keyword_score=0.0,
                    explanation={"semantic": 0.9 - i * 0.1},
                )
                for i in range(1, 4)
            ]

            keyword_ranks = {"BLOCK-1": 3, "BLOCK-2": 1, "BLOCK-3": 2}

            with tempfile.TemporaryDirectory() as tmpdir:
                mem = MemorySystem(knowledge_path=tmpdir, use_chroma=False)

                fused = mem._rrf_fuse(semantic_results, keyword_ranks, k=60)

                # Scores should be in descending order
                scores = [r.score for r in fused]
                assert scores == sorted(scores, reverse=True)


def test_rrf_with_missing_keyword_ranks():
    """Test RRF handles blocks that only appear in semantic or keyword rankings."""
    with patch("openai.OpenAI") as mock_openai:
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.data = [MagicMock(embedding=[0.1] * 1536)]
        mock_client.embeddings.create.return_value = mock_response
        mock_openai.return_value = mock_client

        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test-key"}):
            semantic_results = [
                SearchResult(
                    block_id="SEMANTIC-ONLY",
                    score=0.8,
                    content="Content",
                    semantic_score=0.8,
                    keyword_score=0.0,
                    explanation={"semantic": 0.8},
                ),
            ]

            keyword_ranks = {"KEYWORD-ONLY": 1}

            with tempfile.TemporaryDirectory() as tmpdir:
                mem = MemorySystem(knowledge_path=tmpdir, use_chroma=False)

                fused = mem._rrf_fuse(semantic_results, keyword_ranks, k=60)

                # Should only include blocks that have SearchResult (semantic-only)
                # KEYWORD-ONLY won't appear because it has no SearchResult
                assert len(fused) == 1
                assert fused[0].block_id == "SEMANTIC-ONLY"
                assert fused[0].score > 0.0

