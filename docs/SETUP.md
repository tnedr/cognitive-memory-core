# Setup Guide

## Prerequisites

1. **Python 3.10+** installed
2. **UV package manager** installed
3. **Docker Desktop** (for E2E tests and full functionality)

## Initial Setup

### 1. Install Dependencies

```bash
# Create virtual environment
python -m venv .venv --symlinks

# Install with UV (uses global cache)
uv pip install -e .
```

### 2. Start Docker Services (Optional)

For full functionality including E2E tests:

```bash
cd docker
docker-compose up -d
```

This starts:
- **Neo4j** on `http://localhost:7474` (Bolt: `bolt://localhost:7687`)
- **ChromaDB** on `http://localhost:8000`

Wait ~10-15 seconds for services to be ready.

### 3. Verify Installation

```bash
# Run unit tests
uv run pytest tests/test_file_storage.py tests/test_memory_system.py -v

# Run E2E tests (requires Docker)
uv run pytest tests/test_e2e.py -v -m e2e

# Or skip Docker tests
SKIP_DOCKER_TESTS=1 uv run pytest tests/test_e2e.py -v
```

## Development Workflow

### Running Tests

```bash
# All tests
uv run pytest tests/ -v

# With coverage
uv run pytest tests/ --cov=src/cmemory --cov-report=html

# E2E tests only
uv run pytest tests/test_e2e.py -v -m e2e
```

### Using the CLI

```bash
# Ingest a knowledge block
uv run cmemory ingest knowledge/2025-11-06-memory-design.md

# Search for blocks
uv run cmemory search "memory system"

# Materialize context
uv run cmemory context "Explain hybrid memory architecture"
```

## Troubleshooting

### Docker Not Running

If Docker Desktop is not running, you'll see:
```
error during connect: Get "http://%2F%2F.%2Fpipe%2FdockerDesktopLinuxEngine...
```

**Solution**: Start Docker Desktop, then:
```bash
cd docker
docker-compose up -d
```

### Neo4j Connection Failed

If you see warnings about Neo4j connection:
- Check Docker services are running: `docker-compose ps`
- Verify Neo4j is accessible: `curl http://localhost:7474`
- The system will fall back to in-memory graph storage

### ChromaDB Connection Failed

If ChromaDB is unavailable:
- Check Docker services: `docker-compose ps`
- The system will fall back to FAISS for vector search

### Tests Failing

1. **Unit tests**: Should work without Docker
2. **E2E tests**: Require Docker services running
   - Skip with: `SKIP_DOCKER_TESTS=1 pytest tests/test_e2e.py`

## Using OpenAI Embeddings (Required)

OpenAI embeddings are **required** for semantic search. The system uses OpenAI's `text-embedding-3-small` model for high-quality, LLM-grade semantic understanding. There are no fallbacks - the system will fail clearly if OpenAI is not configured.

### Setup

1. **Create `.env` file** in the project root:
   ```bash
   OPENAI_API_KEY=sk-your-key-here
   ```

2. **Install OpenAI package** (if not already installed):
   ```bash
   uv pip install openai
   ```

3. **That's it!** The system will automatically:
   - Detect the `OPENAI_API_KEY` environment variable
   - Use OpenAI `text-embedding-3-small` model (1536 dimensions)
   - **Fail clearly** if the API key is missing (no silent fallbacks)

### Benefits

- **No dependency conflicts**: No sentence-transformers version issues
- **High-quality embeddings**: LLM-grade semantic understanding
- **Fast and reliable**: OpenAI API is production-ready
- **Deterministic behavior**: System fails clearly if not configured, no silent fallbacks

### Verification

After setting up, test semantic search:

```bash
# Ingest some blocks
uv run cmemory ingest knowledge/your-file.md

# Basic semantic search
uv run cmemory search "your query"

# Hybrid search with keyword boosting
uv run cmemory search "your query" --boost keyword1 --boost keyword2

# Search with exclusions
uv run cmemory search "your query" --exclude unwanted --exclude test
```

You should see real semantic matches with cosine similarity scores (range -1 to +1, typically 0.0 to 1.0 for relevant results).

### Reindexing all embeddings

If you switch to OpenAI embeddings or want to refresh all vectors:

```bash
uv run cmemory reindex-all
```

This rebuilds embeddings for all knowledge blocks and clears old vectors. Useful when:
- Fixing corrupted vector indices
- After updating embedding models
- When switching between different OpenAI embedding models

**Note**: Reindexing preserves all block content and metadata - only embeddings are refreshed.

### Resetting ChromaDB (complete cleanup)

If you need a completely fresh start or vectors are corrupted:

```bash
uv run cmemory chroma-reset
uv run cmemory reindex-all
```

The `chroma-reset` command:
- Deletes the ChromaDB collection
- Removes persistent storage files
- Creates a fresh empty collection

**Use this when**: You have mixed dummy/OpenAI vectors causing "No results found" even after reindexing.

### Cost

OpenAI embeddings are very affordable:
- `text-embedding-3-small`: ~$0.02 per 1M tokens
- Typical usage: < $1/month for personal knowledge base

## Environment Variables

- `OPENAI_API_KEY`: OpenAI API key for embeddings (recommended)
- `SKIP_DOCKER_TESTS=1`: Skip Docker-dependent tests
- `UV_CACHE_DIR`: Override UV cache location (default: `E:\uv-cache`)

## Next Steps

See [ROADMAP.md](../ROADMAP.md) for Sprint 0.2.0 tasks.

