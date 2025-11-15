"""Tests for MemorySystem."""

import tempfile

import pytest

from cmemory.memory import MemorySystem


@pytest.fixture
def temp_memory():
    """Create a memory system with temporary storage."""
    import os
    from unittest.mock import MagicMock, patch

    # Mock OpenAI embeddings for tests
    with patch("openai.OpenAI") as mock_openai:
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.data = [MagicMock(embedding=[0.1] * 1536)]
        mock_client.embeddings.create.return_value = mock_response
        mock_openai.return_value = mock_client

        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test-key"}, clear=False):
            with tempfile.TemporaryDirectory() as tmpdir:
                # Mock ChromaDB for tests
                with patch("chromadb.PersistentClient"):
                    memory = MemorySystem(knowledge_path=tmpdir)
                    yield memory


def test_record_and_retrieve(temp_memory):
    """Test recording and retrieving knowledge blocks."""
    block_id = temp_memory.record(
        "This is a test knowledge block about Python programming.",
        {"id": "KB-TEST-001", "title": "Python Test", "tags": ["python", "test"]},
    )

    assert block_id == "KB-TEST-001"
    
    # Encode the block to add it to vector index
    temp_memory.encode(block_id)

    # Mock ChromaDB query to return the block we just added
    from unittest.mock import MagicMock
    import numpy as np
    
    # Create a mock embedding for the query result
    mock_embedding = np.array([[0.1] * 1536])
    temp_memory.vector_index.collection.query = MagicMock(return_value={
        "ids": [["KB-TEST-001"]],
        "embeddings": [mock_embedding],
        "documents": [["This is a test knowledge block about Python programming."]],
    })

    # Retrieve similar content
    results = temp_memory.retrieve("Python programming language", top_k=1)
    assert len(results) > 0
    assert "KB-TEST-001" in results


def test_link_blocks(temp_memory):
    """Test linking knowledge blocks."""
    id1 = temp_memory.record("First block", {"id": "KB-001", "title": "First"})
    id2 = temp_memory.record("Second block", {"id": "KB-002", "title": "Second"})

    temp_memory.link(id1, id2, "references")
    # Link should not raise exception
    assert True


def test_materialize_context(temp_memory):
    """Test materializing context for a goal."""
    # Add some knowledge blocks
    id1 = temp_memory.record(
        "Python is a high-level programming language.",
        {"id": "KB-001", "title": "Python Intro"},
    )
    id2 = temp_memory.record(
        "Memory systems store and retrieve information.",
        {"id": "KB-002", "title": "Memory Systems"},
    )
    
    # Encode blocks
    temp_memory.encode(id1)
    temp_memory.encode(id2)

    # Mock ChromaDB query to return the blocks
    from unittest.mock import MagicMock
    import numpy as np
    
    mock_embedding = np.array([[0.1] * 1536, [0.1] * 1536])
    temp_memory.vector_index.collection.query = MagicMock(return_value={
        "ids": [["KB-001", "KB-002"]],
        "embeddings": [mock_embedding],
        "documents": [["Python is a high-level programming language.", "Memory systems store and retrieve information."]],
    })

    context = temp_memory.materialize_context("programming languages", max_tokens=1000)
    assert len(context) > 0
    assert "Python" in context


def test_encode_block(temp_memory):
    """Test encoding a knowledge block."""
    block_id = temp_memory.record(
        "Test content for encoding",
        {"id": "KB-ENCODE-001", "title": "Encode Test"},
    )

    # Encoding should not raise exception
    encoded_id = temp_memory.encode(block_id)
    assert encoded_id == block_id


def test_information_type_storage(temp_memory):
    """Test storing and retrieving information_type."""
    # Record with information_type
    block_id = temp_memory.record(
        "This is a dynamic knowledge block about code status.",
        {"id": "KB-INFO-001", "title": "Code Status", "information_type": "dynamic"},
    )

    assert block_id == "KB-INFO-001"
    
    # Encode the block
    temp_memory.encode(block_id)

    # Retrieve the block and verify information_type
    block = temp_memory.file_storage.read(block_id)
    assert block is not None
    assert block.information_type == "dynamic"

    # Mock ChromaDB query to return the block
    from unittest.mock import MagicMock
    import numpy as np
    
    mock_embedding = np.array([[0.1] * 1536])
    temp_memory.vector_index.collection.query = MagicMock(return_value={
        "ids": [["KB-INFO-001"]],
        "embeddings": [mock_embedding],
        "documents": [["This is a dynamic knowledge block about code status."]],
    })

    # Test retrieval includes information_type
    results = temp_memory.retrieve("code status", top_k=1)
    assert len(results) > 0
    assert "KB-INFO-001" in results

    # Verify block still has information_type after retrieval
    retrieved_block = temp_memory.file_storage.read(block_id)
    assert retrieved_block.information_type == "dynamic"

