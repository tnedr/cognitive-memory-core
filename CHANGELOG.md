# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0-UNRELEASED]

### Added
- LLM-based reflection with `Reflector` class
  - LangChain integration for insight generation
  - Jinja2 prompt templates (`templates/reflect.jinja`)
  - Automatic relationship suggestion from LLM analysis
  - Async reflection support
- End-to-end integration tests (`tests/test_e2e.py`)
- CI/CD improvements:
  - E2E tests run on all PRs (not just main branch)
  - Improved Docker health checks
  - Increased service startup wait time

### In Progress
- Token-aware `compress()` with RAG summarization
- Decay policy with `last_access` tracking
- File watcher for auto re-encode

### Planned
- REST/GraphQL API with FastAPI
- Front-end UI (optional)

## [0.1.0] - 2025-11-06

### Added
- Initial release of cognitive-memory-core
- FileStorage class for Markdown/JSON knowledge block management
- GraphStorage class with Neo4j integration and in-memory fallback
- VectorIndex class with ChromaDB and FAISS support
- MemorySystem core class with full pipeline implementation:
  - `record()` - Record new knowledge blocks
  - `encode()` - Encode blocks into vector embeddings
  - `link()` - Create relationships between blocks
  - `retrieve()` - Semantic search for relevant blocks
  - `reflect()` - Reflect on blocks to find relationships (stub)
  - `compress()` - Compress multiple blocks into summaries (stub)
  - `decay()` - Apply decay policies to old blocks (stub)
  - `materialize_context()` - Build context for goals/queries
- CLI interface with commands:
  - `ingest` - Ingest knowledge blocks from files
  - `autolink` - Automatically link related blocks
  - `context` - Materialize context for goals
  - `search` - Search for knowledge blocks
  - `list-blocks` - List all knowledge blocks
- Docker Compose configuration for Neo4j and ChromaDB
- Test suite with pytest
- Documentation and README
- UV cache workflow configuration

