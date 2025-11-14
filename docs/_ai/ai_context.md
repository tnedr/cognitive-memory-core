---
status: current
updated: 2025-11-14
origin: ai/worker
---

# AI Context - Cognitive Memory Core

## Project Purpose

Cognitive Memory Core is a **hybrid AI memory system** that provides robust, auditable context management for both AI agents and human users. It combines three storage layers:

1. **File Layer**: Human-editable Markdown/JSON knowledge blocks
2. **Graph Layer**: Neo4j for relationship tracking
3. **Vector Layer**: ChromaDB/FAISS for semantic search

## Core Architecture

The system is orchestrated by `MemorySystem` class (`src/cmemory/memory.py`), which coordinates:

- **FileStorage**: Manages knowledge blocks as Markdown/JSON files
- **GraphStorage**: Maintains relationships in Neo4j (with in-memory fallback)
- **VectorIndex**: Provides semantic search via embeddings
- **Reflector**: Uses LLM to discover relationships and generate insights
- **Compressor**: Token-aware summarization of multiple blocks
- **DecayManager**: Archives old/unused blocks with restoration support

## Key Concepts

### Knowledge Blocks

- Stored as Markdown files with YAML front-matter
- Contain: `id`, `title`, `content`, `tags`, `metadata`
- Automatically encoded into vector embeddings
- Can be linked via graph relationships

### Memory Operations

1. **record()**: Create new knowledge block from raw text
2. **encode()**: Generate embeddings and add to vector index
3. **link()**: Create explicit graph relationships
4. **retrieve()**: Semantic search for relevant blocks
5. **reflect()**: LLM-based relationship discovery
6. **compress()**: Summarize multiple blocks with token limits
7. **decay()**: Archive blocks based on time/usage policies
8. **materialize_context()**: Build context window for queries

## Current State (v0.2.0)

- ✅ Core pipeline fully functional
- ✅ LLM-based reflection implemented
- ✅ Compression and decay modules (v0.3.0 in progress)
- ✅ E2E tests with Docker Compose
- ✅ 5 sample knowledge blocks for testing

## Integration Points

### For AI Agents

- Use `MemorySystem` class directly in Python code
- CLI available for scripting: `uv run python -m src.cli`
- Future: REST/GraphQL API (v0.4.0 planned)

### Dependencies

- Requires Neo4j and ChromaDB (via Docker Compose)
- Optional LLM for reflection/compression (OpenAI, Ollama, etc.)
- Python 3.10+ with UV package manager

## Important Constraints

- Knowledge blocks are **Markdown-first** (JSON secondary)
- Vector index uses dummy embeddings if ChromaDB unavailable
- Graph storage falls back to in-memory if Neo4j unavailable
- Compression requires LLM for high-quality results (fallback: truncation)

## Information Reliability Model

The system recognizes that information has different properties:

- **Volatility**: Information can be fast-changing (code status, sensor data) or slow-changing (documentation, design decisions)
- **Reliability**: Information has a reliability score (0.0-1.0) based on source:
  - Code-based information: **per definition unreliable** (code changes)
  - Sensor-based information: Medium reliability (depends on sensor accuracy)
  - Human-verified information: High reliability (but may become outdated)
- **Validation**: Information has validation dates, expiration dates, and sensor dependencies
- **Sensor-Based Verification**: System supports sensor plugins (code_sensor, weather_sensor, test_agent, etc.) for re-validation

**Critical Rule**: Before using information, check:
1. `reliability` field (if < 0.7, re-validate)
2. `validated_at` and `validity_window` (if expired, re-validate)
3. `sensor_dependency` (if set, verify sensor is available)

For fast-changing information, prefer real-time sensor lookup over cached blocks.

See `docs/_project/information_types.md` for the complete Memory Information Model.

## File Locations

- Source code: `src/cmemory/`
- Tests: `tests/`
- Knowledge blocks: `knowledge/`
- Docker config: `docker/docker-compose.yml`
- Templates: `templates/`
- Documentation: `docs/`

