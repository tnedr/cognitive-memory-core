"""User Story: Store & Retrieve NAD Booster Facts

This script demonstrates the simplest possible memory lifecycle:
1. Create knowledge blocks
2. Ingest them
3. Retrieve semantic matches
4. Add new knowledge
5. Retrieve again and see new results
"""

from cmemory import MemorySystem


def main():
    """Run the NAD boosters user story."""
    print("=" * 60)
    print("User Story: NAD Boosters Memory Demo")
    print("=" * 60)

    # Initialize memory system
    print("\n[STEP 1] Initializing memory system...")
    memory = MemorySystem(knowledge_path="stories/nad_boosters/knowledge")
    print("[OK] Memory system initialized")

    # Step 2: Record initial knowledge blocks
    print("\n[STEP 2] Recording initial knowledge blocks...")
    id1 = memory.record(
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
    print(f"[OK] Recorded block: {id1}")

    id2 = memory.record(
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
    print(f"[OK] Recorded block: {id2}")

    # Step 3: Initial retrieval
    print("\n[STEP 3] Initial retrieval: 'What boosts NAD levels?'")
    results1 = memory.retrieve("What boosts NAD levels?", top_k=5)
    print(f"[OK] Found {len(results1)} results:")
    for i, block_id in enumerate(results1, 1):
        block = memory.file_storage.read(block_id)
        if block:
            print(f"  {i}. [{block_id}] {block.title}")

    # Step 4: Add new knowledge
    print("\n[STEP 4] Adding new knowledge block (TMG)...")
    id3 = memory.record(
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
    print(f"[OK] Recorded block: {id3}")

    # Step 5: Enhanced retrieval
    print("\n[STEP 5] Enhanced retrieval: 'How to support NAD metabolism?'")
    results2 = memory.retrieve("How to support NAD metabolism?", top_k=5)
    print(f"[OK] Found {len(results2)} results:")
    for i, block_id in enumerate(results2, 1):
        block = memory.file_storage.read(block_id)
        if block:
            print(f"  {i}. [{block_id}] {block.title}")

    # Show context materialization
    print("\n[STEP 6] Materializing context for 'NAD precursors and methyl donors'...")
    context = memory.materialize_context("Explain how NAD precursors and methyl donors work together", max_tokens=1000)
    print(f"[OK] Context generated ({len(context)} characters)")
    print("\nContext preview:")
    print("-" * 60)
    print(context[:500] + "..." if len(context) > 500 else context)
    print("-" * 60)

    print("\n" + "=" * 60)
    print("User story completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()

