"""Tests for reindex-all functionality."""

import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

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
                # Setup memory
                mem = MemorySystem(knowledge_path=tmpdir, use_chroma=False)

                # Create two blocks
                id1 = mem.record("Test block one about NAD boosters", {"id": "B1", "title": "Block1"})
                id2 = mem.record("Test block two about resveratrol", {"id": "B2", "title": "Block2"})

                # Verify blocks exist
                assert len(mem.file_storage.list_all()) == 2

                # Reindex all blocks
                count = mem.reindex_all()

                assert count == 2

                # Verify FAISS index was reset and contains embeddings
                assert mem.vector_index.faiss_index is not None
                assert len(mem.vector_index.faiss_index.id_to_index) == 2


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
                mem = MemorySystem(knowledge_path=tmpdir, use_chroma=True)

                # Create a block
                id1 = mem.record("Test block", {"id": "B1", "title": "Block1"})

                # Reindex
                count = mem.reindex_all()

                assert count == 1
                # Verify collection exists and was recreated
                if mem.vector_index.collection:
                    result = mem.vector_index.collection.get()
                    assert len(result.get("ids", [])) == 1


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
                mem = MemorySystem(knowledge_path=tmpdir, use_chroma=False)

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

