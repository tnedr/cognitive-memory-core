# Roadmap - Cognitive Memory Core

## Current Status (v0.1.0)

✅ **Completed:**
- Core memory system with file storage, graph, and vector layers
- CLI interface with basic commands
- Docker Compose setup for Neo4j and ChromaDB
- Basic test suite
- UV cache workflow

⚠️ **Stubs/Placeholders:**
- `reflect()` - Only logs, no real LLM integration
- `compress()` - Simple concatenation, no token-aware RAG
- `decay()` - Placeholder, no actual policy implementation

## Sprint 0.2.0 - MVP Enhancement

### Priority 1: End-to-End Smoke Test ✅ (In Progress)

**Status**: Test file created, needs Docker validation

**Tasks:**
- [x] Create `tests/test_e2e.py` with Docker Compose fixtures
- [ ] Validate tests with running Docker services
- [ ] Add CI/CD integration for E2E tests

**Acceptance Criteria:**
- All E2E tests pass with real Neo4j and ChromaDB
- Tests cover: ingest → encode → link → context workflow
- Tests verify vector search accuracy
- Tests validate graph traversal

### Priority 2: Real LLM Reflection

**Branch**: `feature/llm-reflection`

**Tasks:**
- [ ] Integrate LangChain with OpenAI/local LLM
- [ ] Create prompt template for reflection (`templates/reflect.jinja`)
- [ ] Implement `reflect()` to generate 3-4 sentence insights
- [ ] Add unit tests with mocked LLM
- [ ] Update README with reflection feature

**Acceptance Criteria:**
- `reflect()` generates meaningful insights about block relationships
- Works with both OpenAI API and local LLM (Ollama, etc.)
- Unit tests with 90%+ coverage
- Documentation updated

### Priority 3: Token-Aware Compression

**Branch**: `feature/compress-rag`

**Tasks:**
- [ ] Implement token counting (tiktoken or similar)
- [ ] Create RAG-based summarization pipeline
- [ ] Add token limit enforcement in `compress()`
- [ ] Test with various block sizes
- [ ] Update `materialize_context()` to use compression

**Acceptance Criteria:**
- Compression respects max_tokens parameter
- Summaries maintain key information
- Works with blocks of varying sizes
- Performance acceptable (< 5s for 10 blocks)

### Priority 4: Decay Policy Implementation

**Branch**: `feature/decay-scheduler`

**Tasks:**
- [ ] Add `last_access` tracking to KnowledgeBlock metadata
- [ ] Implement `usage` policy (archive low-access blocks)
- [ ] Implement `time` policy (delete old, unused blocks)
- [ ] Add cron scheduler or Celery worker
- [ ] Create archival system (`archive/` directory)

**Acceptance Criteria:**
- Blocks track access count and last access time
- Decay policies work as specified
- Archived blocks can be restored
- Scheduler runs weekly (configurable)

### Priority 5: File Watcher

**Branch**: `feature/fs-watch`

**Tasks:**
- [ ] Integrate `watchdog` package
- [ ] Implement debounced re-encode on file changes
- [ ] Add background thread for file monitoring
- [ ] Handle file deletion and renames
- [ ] Test with multiple concurrent edits

**Acceptance Criteria:**
- File changes trigger re-encoding within 5 seconds
- Debouncing prevents excessive re-encodes
- Works on Windows, Linux, macOS
- Thread-safe implementation

### Priority 6: REST/GraphQL API

**Branch**: `api/rest-graphql`

**Tasks:**
- [ ] Set up FastAPI application
- [ ] Create REST endpoints for all CLI commands
- [ ] Add GraphQL schema (optional)
- [ ] Generate OpenAPI/Swagger documentation
- [ ] Add authentication middleware

**Acceptance Criteria:**
- All CLI commands accessible via API
- Swagger UI available at `/docs`
- API tests with 90%+ coverage
- Authentication works (API keys or OAuth)

### Priority 7: CI/CD Pipeline

**Branch**: `infra/gha-pipeline`

**Tasks:**
- [x] Create GitHub Actions workflow
- [ ] Add test matrix (Python 3.10, 3.11, 3.12)
- [ ] Add coverage reporting (Codecov)
- [ ] Add Docker build and push
- [ ] Add pre-commit checks

**Acceptance Criteria:**
- All tests run on push/PR
- Coverage reported to Codecov
- Docker images built and pushed
- Pre-commit hooks validated

## Future Considerations (v0.3.0+)

- **Multi-agent context routing**: Share memory across multiple AI agents
- **Meta-memory**: System learns about its own memory patterns
- **Self-critique**: Memory system evaluates its own retrievals
- **Front-end UI**: Next.js or Streamlit interface
- **Advanced graph queries**: Cypher query builder
- **Vector index optimization**: HNSW or other advanced indexes
- **Distributed storage**: Support for S3, GCS, etc.

## Issue Templates

Use the following templates for creating issues:

- **Feature Request**: `.github/ISSUE_TEMPLATE/feature_request.md`
- **Sprint 0.2 Backlog**: `.github/ISSUE_TEMPLATE/sprint_0.2_backlog.md`

## Contributing

1. Pick an issue from the backlog
2. Create a feature branch (`feature/name` or `infra/name`)
3. Implement with tests
4. Ensure CI passes
5. Submit PR with description

## Milestones

- **v0.2.0**: MVP Enhancement (Current Sprint)
- **v0.3.0**: Production Ready
- **v1.0.0**: Stable Release

