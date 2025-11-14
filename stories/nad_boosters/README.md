# NAD Boosters User Story

A simple, runnable demonstration of the cognitive-memory-core system.

## Quick Start

### Option 1: CLI Commands

```bash
# Ingest initial blocks
uv run python -m src.cli ingest nad_001_resveratrol.md
uv run python -m src.cli ingest nad_002_nmn.md

# Search
uv run python -m src.cli search "What boosts NAD levels?"

# Add new block
uv run python -m src.cli ingest nad_003_tmg.md

# Search again
uv run python -m src.cli search "How to support NAD metabolism?"
```

### Option 2: Python Script

```bash
uv run python user_story.py
```

### Option 3: Automated Test

```bash
uv run pytest ../../tests/test_user_story_nad.py -v
```

## Files

- `nad_001_resveratrol.md` - Resveratrol as NAD booster
- `nad_002_nmn.md` - NMN as direct NAD precursor
- `nad_003_tmg.md` - TMG as methyl donor support
- `user_story.py` - Python script version of the story

## Documentation

See `docs/stories/nad_boosters_story.md` for complete documentation.

