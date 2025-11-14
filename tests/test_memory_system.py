"""Tests for MemorySystem."""

import tempfile

import pytest

from cmemory.memory import MemorySystem


@pytest.fixture
def temp_memory():
    """Create a memory system with temporary storage."""
    with tempfile.TemporaryDirectory() as tmpdir:
        memory = MemorySystem(
            knowledge_path=tmpdir,
            use_chroma=False,  # Use FAISS fallback for tests
        )
        yield memory


def test_record_and_retrieve(temp_memory):
    """Test recording and retrieving knowledge blocks."""
    block_id = temp_memory.record(
        "This is a test knowledge block about Python programming.",
        {"id": "KB-TEST-001", "title": "Python Test", "tags": ["python", "test"]},
    )

    assert block_id == "KB-TEST-001"

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
    temp_memory.record(
        "Python is a high-level programming language.",
        {"id": "KB-001", "title": "Python Intro"},
    )
    temp_memory.record(
        "Memory systems store and retrieve information.",
        {"id": "KB-002", "title": "Memory Systems"},
    )

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

    # Retrieve the block and verify information_type
    block = temp_memory.file_storage.read(block_id)
    assert block is not None
    assert block.information_type == "dynamic"

    # Test retrieval includes information_type
    results = temp_memory.retrieve("code status", top_k=1)
    assert len(results) > 0
    assert "KB-INFO-001" in results

    # Verify block still has information_type after retrieval
    retrieved_block = temp_memory.file_storage.read(block_id)
    assert retrieved_block.information_type == "dynamic"

