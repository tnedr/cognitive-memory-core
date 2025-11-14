"""Tests for DecayManager class."""

import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from cmemory.decay import DecayManager
from cmemory.models import KnowledgeBlock
from cmemory.storage import FileStorage


@pytest.fixture
def temp_decay_manager():
    """Create a temporary DecayManager for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        manager = DecayManager(knowledge_path=tmpdir)
        yield manager


@pytest.fixture
def temp_storage():
    """Create a temporary storage for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        storage = FileStorage(base_path=tmpdir)
        yield storage


def test_record_access(temp_decay_manager, temp_storage):
    """Test recording access to a block."""
    block = KnowledgeBlock(
        id="KB-ACCESS-001",
        title="Test Block",
        content="Test content",
    )
    temp_storage.create(block)

    # Record access
    temp_decay_manager.record_access("KB-ACCESS-001", temp_storage)

    # Verify metadata updated
    updated_block = temp_storage.read("KB-ACCESS-001")
    assert updated_block.metadata.get("access_count", 0) == 1
    assert "last_access" in updated_block.metadata


def test_decay_time_policy(temp_decay_manager, temp_storage):
    """Test time-based decay policy."""
    # Create old block
    old_date = datetime.now(timezone.utc) - timedelta(days=200)
    old_block = KnowledgeBlock(
        id="KB-OLD-001",
        title="Old Block",
        content="Old content",
        created=old_date,
    )
    old_block.metadata["last_access"] = old_date.isoformat()
    temp_storage.create(old_block)

    # Create recent block
    recent_block = KnowledgeBlock(
        id="KB-RECENT-001",
        title="Recent Block",
        content="Recent content",
    )
    temp_storage.create(recent_block)

    # Apply decay (180 days threshold)
    archived = temp_decay_manager.decay(temp_storage, policy="time", days_threshold=180)

    # Old block should be archived
    assert "KB-OLD-001" in archived
    assert "KB-RECENT-001" not in archived

    # Verify old block is in archive
    archive_file = temp_decay_manager.archive_path / "KB-OLD-001.md"
    assert archive_file.exists()


def test_decay_usage_policy(temp_decay_manager, temp_storage):
    """Test usage-based decay policy."""
    # Create blocks with different access counts
    high_usage = KnowledgeBlock(
        id="KB-HIGH-001",
        title="High Usage",
        content="Content",
    )
    high_usage.metadata["access_count"] = 100
    temp_storage.create(high_usage)

    low_usage = KnowledgeBlock(
        id="KB-LOW-001",
        title="Low Usage",
        content="Content",
    )
    low_usage.metadata["access_count"] = 1
    temp_storage.create(low_usage)

    # Apply decay (1% threshold)
    archived = temp_decay_manager.decay(temp_storage, policy="usage", usage_threshold=0.01)

    # Low usage block should be archived
    assert "KB-LOW-001" in archived
    assert "KB-HIGH-001" not in archived


def test_restore_archived_block(temp_decay_manager, temp_storage):
    """Test restoring an archived block."""
    block = KnowledgeBlock(
        id="KB-RESTORE-001",
        title="Restore Test",
        content="Test content",
    )
    temp_storage.create(block)

    # Archive it
    temp_decay_manager._archive_block(block, temp_storage)

    # Verify archived
    assert not (temp_storage.base_path / "KB-RESTORE-001.md").exists()
    assert (temp_decay_manager.archive_path / "KB-RESTORE-001.md").exists()

    # Restore it
    restored = temp_decay_manager.restore("KB-RESTORE-001", temp_storage)
    assert restored is True
    assert (temp_storage.base_path / "KB-RESTORE-001.md").exists()


def test_decay_none_policy(temp_decay_manager, temp_storage):
    """Test that 'none' policy doesn't archive anything."""
    block = KnowledgeBlock(
        id="KB-NONE-001",
        title="Test",
        content="Content",
    )
    temp_storage.create(block)

    archived = temp_decay_manager.decay(temp_storage, policy="none")
    assert len(archived) == 0

