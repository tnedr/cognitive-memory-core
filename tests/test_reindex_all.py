"""Tests for reindex-all functionality."""

import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from cmemory import MemorySystem


def test_reindex_all():
    """Test reindexing all blocks."""
    with patch("openai.OpenAI") as mock_openai:
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.data = [MagicMock(embedding=[0.123] * 1536)]
        mock_client.embeddings.create.return_value = mock_response
        mock_openai.return_value = mock_client

        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test-key"}):
            with tempfile.TemporaryDirectory() as tmpdir:
                with patch("chromadb.PersistentClient") as mock_chroma:
                    mock_collection = MagicMock()
                    mock_client_instance = MagicMock()
                    mock_client_instance.get_collection.side_effect = Exception("Not found")
                    mock_client_instance.create_collection.return_value = mock_collection
                    mock_client_instance.delete_collection.return_value = None
                    mock_chroma.return_value = mock_client_instance

                    mem = MemorySystem(knowledge_path=tmpdir)
                    id1 = mem.record("Test block one about NAD boosters", {"id": "B1", "title": "Block1"})
                    id2 = mem.record("Test block two about resveratrol", {"id": "B2", "title": "Block2"})
                    assert len(mem.file_storage.list_all()) == 2
                    count = mem.reindex_all()
                    assert count == 2
                    # Verify ChromaDB collection was reset
                    assert mock_client_instance.delete_collection.called
                    assert mock_client_instance.create_collection.called


def test_reindex_all_empty():
    """Test reindexing when no blocks exist."""
    with patch("openai.OpenAI") as mock_openai:
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.data = [MagicMock(embedding=[0.123] * 1536)]
        mock_client.embeddings.create.return_value = mock_response
        mock_openai.return_value = mock_client

        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test-key"}):
            with tempfile.TemporaryDirectory() as tmpdir:
                with patch("chromadb.PersistentClient"):
                    mem = MemorySystem(knowledge_path=tmpdir)
                    count = mem.reindex_all()
                    assert count == 0


def test_reindex_all_with_chroma():
    """Test reindexing with ChromaDB."""
    with patch("openai.OpenAI") as mock_openai:
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.data = [MagicMock(embedding=[0.123] * 1536)]
        mock_client.embeddings.create.return_value = mock_response
        mock_openai.return_value = mock_client

        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test-key"}):
            with tempfile.TemporaryDirectory() as tmpdir:
                with patch("chromadb.PersistentClient") as mock_chroma:
                    mock_collection = MagicMock()
                    mock_collection.get.return_value = {"ids": ["B1"]}
                    mock_client_instance = MagicMock()
                    mock_client_instance.get_collection.side_effect = Exception("Not found")
                    mock_client_instance.create_collection.return_value = mock_collection
                    mock_client_instance.delete_collection.return_value = None
                    mock_chroma.return_value = mock_client_instance

                    mem = MemorySystem(knowledge_path=tmpdir)
                    id1 = mem.record("Test block", {"id": "B1", "title": "Block1"})
                    count = mem.reindex_all()
                    assert count == 1
                    # Verify collection operations
                    assert mock_collection.add.called


def test_reindex_all_preserves_blocks():
    """Test that reindexing preserves block content and metadata."""
    with patch("openai.OpenAI") as mock_openai:
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.data = [MagicMock(embedding=[0.123] * 1536)]
        mock_client.embeddings.create.return_value = mock_response
        mock_openai.return_value = mock_client

        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test-key"}):
            with tempfile.TemporaryDirectory() as tmpdir:
                with patch("chromadb.PersistentClient"):
                    mem = MemorySystem(knowledge_path=tmpdir)

                    # Create a block with metadata
                    id1 = mem.record(
                        "Test content",
                        {"id": "B1", "title": "Test Block", "tags": ["test", "nad"], "information_type": "static"},
                    )

                    # Verify block exists
                    block_before = mem.file_storage.read("B1")
                    assert block_before is not None
                    assert block_before.title == "Test Block"
                    assert block_before.tags == ["test", "nad"]
                    assert block_before.information_type == "static"

                    # Reindex
                    mem.reindex_all()

                    # Verify block content and metadata are preserved
                    block_after = mem.file_storage.read("B1")
                    assert block_after is not None
                    assert block_after.title == "Test Block"
                    assert block_after.tags == ["test", "nad"]
                    assert block_after.information_type == "static"
                    assert block_after.content == "Test content"
