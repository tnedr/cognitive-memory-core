"""Automated test for the NAD boosters user story.

This test reproduces the user story workflow:
1. Initialize memory
2. Record initial knowledge blocks
3. Retrieve information
4. Add new knowledge
5. Retrieve again and verify improved results
"""

import tempfile

import pytest

from cmemory import MemorySystem


@pytest.fixture
def temp_memory():
    """Create a memory system with temporary storage."""
    with tempfile.TemporaryDirectory() as tmpdir:
        memory = MemorySystem(
            knowledge_path=tmpdir,
            use_chroma=False,  # Use FAISS fallback for tests
        )
        yield memory


def test_nad_boosters_user_story(temp_memory):
    """Test the complete NAD boosters user story workflow."""
    # Step 1: Record initial knowledge blocks
    id1 = temp_memory.record(
        "Resveratrol is a polyphenol compound found in grapes and red wine. "
        "It activates sirtuins indirectly and is commonly paired with NAD precursor supplements. "
        "Studies suggest that resveratrol may enhance mitochondrial function and longevity pathways.",
        {
            "id": "NAD-001",
            "title": "Resveratrol as an NAD Booster",
            "tags": ["nad", "resveratrol", "longevity", "supplements"],
            "information_type": "static",
        },
    )
    assert id1 == "NAD-001"

    id2 = temp_memory.record(
        "NMN is a direct precursor to NAD+. "
        "It is rapidly absorbed and converted into NAD through the salvage pathway. "
        "NMN supplementation has been linked to improved energy metabolism and cellular repair.",
        {
            "id": "NAD-002",
            "title": "NMN as a Direct NAD Precursor",
            "tags": ["nad", "nmn", "precursor", "supplements"],
            "information_type": "static",
        },
    )
    assert id2 == "NAD-002"

    # Step 2: Initial retrieval
    results1 = temp_memory.retrieve("What boosts NAD levels?", top_k=5)
    assert len(results1) >= 2
    assert "NAD-001" in results1 or "NAD-002" in results1

    # Step 3: Add new knowledge
    id3 = temp_memory.record(
        "TMG (trimethylglycine) supports methylation pathways. "
        "It is often recommended when taking NMN or NR because NAD metabolism consumes methyl groups. "
        "TMG helps prevent methyl donor depletion.",
        {
            "id": "NAD-003",
            "title": "TMG as a Methyl Donor Supporting NAD Pathways",
            "tags": ["nad", "tmg", "methylation"],
            "information_type": "static",
        },
    )
    assert id3 == "NAD-003"

    # Step 4: Enhanced retrieval
    results2 = temp_memory.retrieve("How to support NAD metabolism?", top_k=5)
    assert len(results2) >= 3
    # Should now include TMG
    assert "NAD-003" in results2

    # Verify all blocks are stored with information_type
    block1 = temp_memory.file_storage.read("NAD-001")
    assert block1 is not None
    assert block1.information_type == "static"
    assert "Resveratrol" in block1.title

    block2 = temp_memory.file_storage.read("NAD-002")
    assert block2 is not None
    assert block2.information_type == "static"
    assert "NMN" in block2.title

    block3 = temp_memory.file_storage.read("NAD-003")
    assert block3 is not None
    assert block3.information_type == "static"
    assert "TMG" in block3.title

    # Step 5: Test context materialization
    context = temp_memory.materialize_context("Explain how NAD precursors and methyl donors work together", max_tokens=1000)
    assert len(context) > 0
    # Context should mention relevant concepts
    context_lower = context.lower()
    assert "nad" in context_lower or "nmn" in context_lower or "tmg" in context_lower

