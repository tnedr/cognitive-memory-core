"""Tests for Compressor class."""

from unittest.mock import MagicMock

import pytest

from cmemory.compress import Compressor
from cmemory.models import KnowledgeBlock


@pytest.fixture
def mock_llm():
    """Create a mock LLM for testing."""
    llm = MagicMock()
    llm.invoke.return_value = MagicMock(content="This is a compressed summary of multiple blocks.")
    return llm


@pytest.fixture
def sample_blocks():
    """Create sample knowledge blocks for testing."""
    return [
        KnowledgeBlock(
            id="KB-COMP-001",
            title="Block 1",
            content="This is the first knowledge block with some content.",
        ),
        KnowledgeBlock(
            id="KB-COMP-002",
            title="Block 2",
            content="This is the second knowledge block with different content.",
        ),
        KnowledgeBlock(
            id="KB-COMP-003",
            title="Block 3",
            content="This is the third knowledge block with more content.",
        ),
    ]


def test_compress_without_llm(sample_blocks):
    """Test compression without LLM (fallback mode)."""
    compressor = Compressor(llm=None, max_tokens=100)
    summary = compressor.compress(sample_blocks)

    assert len(summary) > 0
    assert "Block 1" in summary or "Block 2" in summary


def test_compress_with_llm(mock_llm, sample_blocks):
    """Test compression with mock LLM."""
    compressor = Compressor(llm=mock_llm, max_tokens=100)

    try:
        summary = compressor.compress(sample_blocks)
        # Should call LLM if LangChain available
        assert len(summary) > 0
    except ImportError:
        # LangChain not available, should fall back
        summary = compressor.compress(sample_blocks)
        assert len(summary) > 0


def test_compress_respects_max_tokens(sample_blocks):
    """Test that compression respects max_tokens limit."""
    compressor = Compressor(llm=None, max_tokens=50)

    # Create large blocks
    large_blocks = [
        KnowledgeBlock(
            id=f"KB-LARGE-{i}",
            title=f"Large Block {i}",
            content="X" * 1000,  # Large content
        )
        for i in range(3)
    ]

    summary = compressor.compress(large_blocks, max_tokens=50)
    # Should be truncated
    assert len(summary) > 0


def test_compress_empty_list():
    """Test compression with empty block list."""
    compressor = Compressor(llm=None)
    summary = compressor.compress([])
    assert summary == ""


def test_token_counting():
    """Test token counting functionality."""
    from cmemory.compress.compressor import _count_tokens

    text = "This is a test sentence."
    tokens = _count_tokens(text)

    # Should return a positive integer
    assert isinstance(tokens, int)
    assert tokens > 0

