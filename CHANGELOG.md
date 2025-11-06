# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
  - `reflect()` - Reflect on blocks to find relationships
  - `compress()` - Compress multiple blocks into summaries
  - `decay()` - Apply decay policies to old blocks
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

