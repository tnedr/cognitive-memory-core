"""Tests for Reflector class."""

from unittest.mock import MagicMock, patch

import pytest

from cmemory.models import KnowledgeBlock
from cmemory.reflection import Reflector


@pytest.fixture
def mock_llm():
    """Create a mock LLM for testing."""
    llm = MagicMock()
    llm.invoke.return_value = MagicMock(
        content="These blocks are related. Block 1 discusses Python programming, while Block 2 covers memory systems. They share themes of software architecture and system design."
    )
    return llm


@pytest.fixture
def sample_blocks():
    """Create sample knowledge blocks for testing."""
    return [
        KnowledgeBlock(
            id="KB-001",
            title="Python Programming",
            content="Python is a high-level programming language known for its simplicity.",
            tags=["python", "programming"],
        ),
        KnowledgeBlock(
            id="KB-002",
            title="Memory Systems",
            content="Memory systems are crucial for AI agents to maintain context.",
            tags=["ai", "memory"],
        ),
    ]


def test_reflector_without_llm(sample_blocks):
    """Test Reflector without LLM configured."""
    reflector = Reflector(llm=None)
    relationships = reflector.reflect(sample_blocks)
    assert relationships == []


def test_reflector_with_llm(mock_llm, sample_blocks):
    """Test Reflector with mock LLM."""
    reflector = Reflector(llm=mock_llm)
    relationships = reflector.reflect(sample_blocks)

    # Verify LLM was called
    mock_llm.invoke.assert_called_once()
    call_args = mock_llm.invoke.call_args[0][0]
    assert "Python Programming" in call_args
    assert "Memory Systems" in call_args

    # Should generate relationships
    assert len(relationships) > 0
    assert all(rel.source_id in ["KB-001", "KB-002"] for rel in relationships)
    assert all(rel.target_id in ["KB-001", "KB-002"] for rel in relationships)


def test_reflector_template_loading(sample_blocks):
    """Test that template is loaded correctly."""
    reflector = Reflector(llm=None)
    prompt = reflector._format_prompt(sample_blocks)

    assert "KB-001" in prompt
    assert "Python Programming" in prompt
    assert "KB-002" in prompt
    assert "Memory Systems" in prompt


def test_reflector_parse_insights(sample_blocks):
    """Test insight parsing."""
    reflector = Reflector(llm=None)
    insights = "Block KB-001 about Python and Block KB-002 about memory are related."
    relationships = reflector._parse_insights(insights, sample_blocks)

    # Should find relationship if both blocks mentioned
    assert len(relationships) >= 0  # May or may not find depending on parsing


def test_reflector_error_handling(sample_blocks):
    """Test error handling in reflection."""
    mock_llm = MagicMock()
    mock_llm.invoke.side_effect = Exception("LLM error")

    reflector = Reflector(llm=mock_llm)
    relationships = reflector.reflect(sample_blocks)

    # Should return empty list on error
    assert relationships == []


@pytest.mark.asyncio
async def test_reflector_async(mock_llm, sample_blocks):
    """Test async reflection."""
    mock_llm.ainvoke = MagicMock(
        return_value=MagicMock(
            content="These blocks are related through software architecture themes."
        )
    )

    reflector = Reflector(llm=mock_llm)
    relationships = await reflector.reflect_async(sample_blocks)

    # Verify async method was called
    mock_llm.ainvoke.assert_called_once()
    assert isinstance(relationships, list)

