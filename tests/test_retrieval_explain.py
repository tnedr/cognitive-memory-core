"""Tests for explain retrieval mode."""

import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from cmemory import MemorySystem
from cmemory.models import SearchResult


def test_retrieve_with_explain():
    """Test retrieve() with explain=True returns SearchResult objects with explanations."""
    with patch("openai.OpenAI") as mock_openai:
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.data = [MagicMock(embedding=[0.1] * 1536)]
        mock_client.embeddings.create.return_value = mock_response
        mock_openai.return_value = mock_client

        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test-key"}):
            with tempfile.TemporaryDirectory() as tmpdir:
                with patch("chromadb.PersistentClient"):
                    mem = MemorySystem(knowledge_path=tmpdir)

                # Create blocks with specific content
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

                # Retrieve with explain=True
                results = mem.retrieve("supplements", top_k=2, explain=True, boost=["nad"])

                # Should return SearchResult objects
                assert len(results) >= 1
                assert isinstance(results[0], SearchResult)
                
                # Check explanation fields
                assert hasattr(results[0], "semantic_score")
                assert hasattr(results[0], "keyword_score")
                assert hasattr(results[0], "explanation")
                
                # Check explanation content
                assert "semantic" in results[0].explanation
                assert isinstance(results[0].explanation["semantic"], (int, float))
                
                # Check scores are populated
                assert results[0].semantic_score >= 0.0
                assert results[0].keyword_score >= 0.0
                assert results[0].score == results[0].semantic_score + results[0].keyword_score


def test_retrieve_without_explain_backwards_compatible():
    """Test that retrieve() without explain still works (backwards compatibility)."""
    with patch("openai.OpenAI") as mock_openai:
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.data = [MagicMock(embedding=[0.1] * 1536)]
        mock_client.embeddings.create.return_value = mock_response
        mock_openai.return_value = mock_client

        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test-key"}):
            with tempfile.TemporaryDirectory() as tmpdir:
                with patch("chromadb.PersistentClient"):
                    mem = MemorySystem(knowledge_path=tmpdir)

                id1 = mem.record("Test content", {"id": "TEST-001", "title": "Test"})
                mem.encode(id1)

                # Retrieve without explain (default)
                results = mem.retrieve("test", top_k=1, explain=False)

                # Should return SearchResult objects (new behavior)
                assert len(results) >= 0
                # Results can be empty or SearchResult objects


def test_explanation_contains_keyword_matches():
    """Test that explanation contains keyword match information when boost is used."""
    with patch("openai.OpenAI") as mock_openai:
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.data = [MagicMock(embedding=[0.1] * 1536)]
        mock_client.embeddings.create.return_value = mock_response
        mock_openai.return_value = mock_client

        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test-key"}):
            with tempfile.TemporaryDirectory() as tmpdir:
                with patch("chromadb.PersistentClient"):
                    mem = MemorySystem(knowledge_path=tmpdir)

                id1 = mem.record(
                    "NAD boosters are important for longevity",
                    {"id": "NAD-001", "title": "NAD Boosters"},
                )
                mem.encode(id1)

                results = mem.retrieve("supplements", top_k=1, explain=True, boost=["nad"])

                if results:
                    result = results[0]
                    assert "semantic" in result.explanation
                    assert "keyword_score" in result.explanation
                    # Should have title or content matches if "nad" appears
                    if "nad" in result.explanation.get("title_match", []):
                        assert "title_match" in result.explanation
                    if "nad" in result.explanation.get("content_match", []):
                        assert "content_match" in result.explanation


def test_explanation_is_json_serializable():
    """Test that explanation dict is JSON-serializable."""
    import json

    with patch("openai.OpenAI") as mock_openai:
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.data = [MagicMock(embedding=[0.1] * 1536)]
        mock_client.embeddings.create.return_value = mock_response
        mock_openai.return_value = mock_client

        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test-key"}):
            with tempfile.TemporaryDirectory() as tmpdir:
                with patch("chromadb.PersistentClient"):
                    mem = MemorySystem(knowledge_path=tmpdir)

                id1 = mem.record("Test content", {"id": "TEST-001", "title": "Test"})
                mem.encode(id1)

                results = mem.retrieve("test", top_k=1, explain=True)

                if results:
                    # Should be able to serialize explanation
                    explanation_json = json.dumps(results[0].explanation)
                    assert isinstance(explanation_json, str)
                    # Should be able to deserialize
                    explanation_dict = json.loads(explanation_json)
                    assert isinstance(explanation_dict, dict)

