"""Tests for FileStorage."""

import tempfile
from pathlib import Path

import pytest

from cmemory.models import KnowledgeBlock
from cmemory.storage import FileStorage


@pytest.fixture
def temp_storage():
    """Create a temporary storage directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        storage = FileStorage(base_path=tmpdir)
        yield storage


def test_create_and_read_markdown(temp_storage):
    """Test creating and reading Markdown knowledge blocks."""
    block = KnowledgeBlock(
        id="KB-001",
        title="Test Block",
        content="This is test content.",
        tags=["test", "example"],
    )

    file_path = temp_storage.create(block, format="markdown")
    assert Path(file_path).exists()

    read_block = temp_storage.read("KB-001")
    assert read_block is not None
    assert read_block.id == "KB-001"
    assert read_block.title == "Test Block"
    assert read_block.content == "This is test content."
    assert "test" in read_block.tags


def test_create_and_read_json(temp_storage):
    """Test creating and reading JSON knowledge blocks."""
    block = KnowledgeBlock(
        id="KB-002",
        title="JSON Block",
        content="JSON content here.",
    )

    file_path = temp_storage.create(block, format="json")
    assert Path(file_path).exists()

    read_block = temp_storage.read("KB-002")
    assert read_block is not None
    assert read_block.id == "KB-002"
    assert read_block.title == "JSON Block"


def test_update_block(temp_storage):
    """Test updating a knowledge block."""
    block = KnowledgeBlock(
        id="KB-003",
        title="Original",
        content="Original content.",
    )
    temp_storage.create(block)

    block.content = "Updated content."
    block.title = "Updated"
    temp_storage.update(block)

    updated_block = temp_storage.read("KB-003")
    assert updated_block.content == "Updated content."
    assert updated_block.title == "Updated"


def test_delete_block(temp_storage):
    """Test deleting a knowledge block."""
    block = KnowledgeBlock(
        id="KB-004",
        title="To Delete",
        content="Will be deleted.",
    )
    temp_storage.create(block)

    assert temp_storage.delete("KB-004") is True
    assert temp_storage.read("KB-004") is None


def test_list_all(temp_storage):
    """Test listing all knowledge blocks."""
    for i in range(3):
        block = KnowledgeBlock(
            id=f"KB-{i:03d}",
            title=f"Block {i}",
            content=f"Content {i}",
        )
        temp_storage.create(block)

    all_ids = temp_storage.list_all()
    assert len(all_ids) == 3
    assert "KB-000" in all_ids
    assert "KB-001" in all_ids
    assert "KB-002" in all_ids

