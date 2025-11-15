# User Story: NAD Boosters Memory Demo

This document describes a simple, runnable user story that demonstrates the cognitive-memory-core system working end-to-end.

## Goal

Demonstrate the simplest possible memory lifecycle:
- Create knowledge blocks
- Ingest them
- Retrieve semantic matches
- Add new knowledge
- Retrieve again and see new results

This serves as a sanity check that the system works end-to-end.

## Story Overview

We'll store and retrieve information about NAD (Nicotinamide Adenine Dinucleotide) boosters - supplements that support cellular energy and longevity pathways.

## Step-by-Step Workflow

### Step 0: Setup

The knowledge blocks are located in `stories/nad_boosters/`:

- `nad_001_resveratrol.md` - Information about resveratrol
- `nad_002_nmn.md` - Information about NMN (Nicotinamide Mononucleotide)
- `nad_003_tmg.md` - Information about TMG (Trimethylglycine)

### Step 1: Ingest Initial Knowledge Blocks

```bash
uv run cmemory ingest stories/nad_boosters/nad_001_resveratrol.md
uv run cmemory ingest stories/nad_boosters/nad_002_nmn.md
```

Verify ingestion:

```bash
uv run cmemory list-blocks
```

You should see: `NAD-001`, `NAD-002`.

### Step 2: Initial Retrieval

Search for NAD boosters:

```bash
uv run cmemory search "What boosts NAD levels?"
```

Expected results:
- NAD-002 (NMN) - direct NAD precursor
- NAD-001 (Resveratrol) - indirect NAD booster

Try context materialization:

```bash
uv run cmemory context "Explain NAD boosting supplements"
```

### Step 3: Add New Knowledge

Ingest the third block:

```bash
uv run cmemory ingest stories/nad_boosters/nad_003_tmg.md
```

### Step 4: Enhanced Retrieval

Search again with a broader query:

```bash
uv run cmemory search "How to support NAD metabolism?"
```

Expected results (should now include TMG):
- NAD-003 (TMG) - methyl donor support
- NAD-002 (NMN) - direct precursor
- NAD-001 (Resveratrol) - indirect booster

Try context with the new information:

```bash
uv run cmemory context "Explain how NAD precursors and methyl donors work together"
```

This will now automatically include TMG in the context.

## Running the Python Script Version

For a programmatic version, run:

```bash
uv run python stories/nad_boosters/user_story.py
```

This script:
1. Initializes the memory system
2. Records the three knowledge blocks
3. Performs initial retrieval
4. Adds the third block
5. Performs enhanced retrieval
6. Materializes context

## Running the Automated Test

Run the test that verifies the complete workflow:

```bash
uv run pytest tests/test_user_story_nad.py -v
```

## Knowledge Blocks

### NAD-001: Resveratrol

- **Type**: Static information
- **Tags**: nad, resveratrol, longevity, supplements
- **Content**: Polyphenol compound that activates sirtuins indirectly, commonly paired with NAD precursors

### NAD-002: NMN

- **Type**: Static information
- **Tags**: nad, nmn, precursor, supplements
- **Content**: Direct NAD+ precursor, rapidly absorbed through salvage pathway

### NAD-003: TMG

- **Type**: Static information
- **Tags**: nad, tmg, methylation
- **Content**: Methyl donor that supports NAD metabolism, prevents methyl depletion

## Expected Outcomes

After completing this story, you should have:

1. ✅ Three knowledge blocks stored in the system
2. ✅ Semantic search returning relevant results
3. ✅ Context materialization including all relevant blocks
4. ✅ `information_type` field properly stored and retrieved
5. ✅ Demonstration of incremental knowledge addition

## Key Features Demonstrated

- **Storage**: Knowledge blocks stored as Markdown with YAML frontmatter
- **Semantic Search**: Vector-based similarity search finding relevant blocks
- **Context Materialization**: Automatic selection and formatting of relevant context
- **Information Types**: Static information properly categorized
- **Incremental Learning**: System improves results as new knowledge is added

## Next Steps

After running this story, you can:

- Add more NAD-related knowledge blocks
- Try different search queries
- Experiment with different `information_type` values (static, dynamic)
- Explore the graph relationships using `autolink`
- Test reflection on the blocks using `reflect`

## Related Documentation

- [Memory Information Model](../_project/information_types.md) - Understanding information types
- [CLI Usage](../../README.md#usage) - Command-line interface reference
- [API Reference](../../README.md#api) - Python API usage

