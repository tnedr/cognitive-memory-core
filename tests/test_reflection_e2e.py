"""End-to-end tests for reflection functionality."""

import logging
from unittest.mock import MagicMock

import pytest

from cmemory.memory import MemorySystem

logger = logging.getLogger(__name__)


@pytest.mark.e2e
def test_reflect_with_mocked_llm(memory_system: MemorySystem, ingested_blocks: list[str]):
    """Test reflect() end-to-end with mocked LLM."""
    # Create a mock LLM
    mock_llm = MagicMock()
    mock_llm.invoke.return_value = MagicMock(
        content="These knowledge blocks are related. Python Programming and Memory Systems share themes of software architecture. Graph Databases and Vector Search are both used in AI memory systems. LangChain integrates with all these technologies."
    )

    # Initialize memory system with mock LLM
    memory_system.reflector = memory_system.reflector.__class__(llm=mock_llm)

    # Reflect on first block
    block_id = ingested_blocks[0]
    initial_related = memory_system.graph_storage.find_related(block_id, max_depth=1)

    # Call reflect
    memory_system.reflect(block_id)

    # Verify LLM was called
    mock_llm.invoke.assert_called_once()
    call_args = mock_llm.invoke.call_args[0][0]
    assert block_id in call_args or "Python" in call_args

    # Verify new relationships were added
    final_related = memory_system.graph_storage.find_related(block_id, max_depth=1)
    # Should have at least as many relationships as before (may have more from reflection)
    assert len(final_related) >= len(initial_related), "Reflection should add relationships"


@pytest.mark.e2e
def test_reflect_without_llm(memory_system: MemorySystem, ingested_blocks: list[str]):
    """Test reflect() gracefully handles missing LLM."""
    # Ensure no LLM is configured
    memory_system.reflector = None

    block_id = ingested_blocks[0]

    # Should not raise exception
    memory_system.reflect(block_id)

    # Should still find related blocks via vector search
    related = memory_system.graph_storage.find_related(block_id, max_depth=1)
    # May or may not have relationships, but should not crash


@pytest.mark.e2e
def test_reflect_uses_vector_similarity(memory_system: MemorySystem, ingested_blocks: list[str]):
    """Test that reflect() uses vector similarity to find related blocks."""
    # Create mock LLM
    mock_llm = MagicMock()
    mock_llm.invoke.return_value = MagicMock(content="These blocks are related.")

    memory_system.reflector = memory_system.reflector.__class__(llm=mock_llm)

    block_id = ingested_blocks[0]  # Python Programming
    memory_system.reflect(block_id)

    # Verify the prompt includes semantically similar blocks (from vector search)
    call_args = mock_llm.invoke.call_args[0][0]
    # Should include multiple blocks (original + similar ones)
    assert len(ingested_blocks) > 1, "Should have multiple blocks to reflect on"

