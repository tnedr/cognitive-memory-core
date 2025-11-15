"""Tests for InflowProcessor."""

import tempfile
from pathlib import Path

import pytest

from cmemory.inflow import InflowProcessor
from cmemory.memory import MemorySystem


def test_inflow_digest():
    """Test digesting files from inflow directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        inflow = Path(tmpdir) / "inflow"
        inflow.mkdir()

        # Create sample files
        file1 = inflow / "note1.txt"
        file1.write_text("Resveratrol is a polyphenol.", encoding="utf-8")

        file2 = inflow / "idea_nad.md"
        file2.write_text("# NAD Idea\nNMN boosts NAD levels.", encoding="utf-8")

        with patch("chromadb.PersistentClient"):
            memory = MemorySystem(knowledge_path=str(Path(tmpdir) / "knowledge"))

        processor = InflowProcessor(inflow_path=str(inflow), memory=memory)
        ids = processor.digest()

        # Should generate 2 blocks
        assert len(ids) == 2

        # Check processed folder
        processed_files = list((inflow / "processed").iterdir())
        assert len(processed_files) == 2

        # Check blocks stored
        for bid in ids:
            blk = memory.file_storage.read(bid)
            assert blk is not None
            assert "inflow" in blk.tags
            assert blk.metadata.get("source_file") is not None

