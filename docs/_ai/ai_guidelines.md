---
status: current
updated: 2025-11-14
origin: ai/worker
---

# AI Guidelines - Cognitive Memory Core

## Code Modification Guidelines

### File Structure

- **DO NOT** modify core models (`src/cmemory/models.py`) without careful consideration
- **DO** add new modules in appropriate subdirectories (`storage/`, `graph/`, `vector/`, etc.)
- **DO** follow existing patterns for new features

### Testing Requirements

- **MUST** write unit tests for new features (`tests/test_*.py`)
- **MUST** ensure E2E tests pass if modifying core pipeline
- **SHOULD** maintain ≥90% coverage for new code
- **MUST** use `pytest` with appropriate markers (`@pytest.mark.e2e` for integration tests)

### Documentation

- **MUST** update `CHANGELOG.md` for user-facing changes
- **SHOULD** add docstrings to all public methods
- **SHOULD** update relevant docs in `docs/` directory
- **MUST** update `docs/_project/status_human.md` for significant changes

### Dependencies

- **DO NOT** add heavy dependencies without discussion
- **DO** use existing dependencies when possible
- **MUST** update `pyproject.toml` and `requirements.txt` for new deps
- **SHOULD** prefer lightweight alternatives

## API Contract Guidelines

### MemorySystem Methods

- **DO NOT** change method signatures without version bump
- **DO** maintain backward compatibility within major version
- **MUST** handle missing optional dependencies gracefully (fallbacks)
- **SHOULD** provide clear error messages

### Data Models

- **DO NOT** remove fields from `KnowledgeBlock`, `GraphNode`, `GraphRelationship`
- **DO** add new optional fields when needed
- **MUST** maintain serialization compatibility

## Integration Guidelines

### Docker Services

- **MUST** handle cases where Neo4j/ChromaDB are unavailable
- **SHOULD** provide in-memory fallbacks
- **MUST** not fail hard if services are down (graceful degradation)

### LLM Integration

- **MUST** handle LLM unavailability gracefully
- **SHOULD** provide fallback behavior (e.g., truncation for compression)
- **MUST** handle timeouts and rate limits
- **SHOULD** log LLM errors clearly

## Code Style

- **MUST** follow existing code style (black, isort, flake8)
- **MUST** run pre-commit hooks before committing
- **DO** use type hints for all function signatures
- **DO** use `logging` module (not `print`)

## Git Workflow

- **DO** create feature branches (`feature/description`)
- **DO** write clear commit messages
- **MUST** ensure CI passes before merging
- **SHOULD** squash commits when merging to main

## Error Handling

- **MUST** use appropriate exception types
- **SHOULD** log errors with context
- **MUST** not expose sensitive information in error messages
- **DO** provide actionable error messages

## Performance Considerations

- **SHOULD** avoid blocking operations in hot paths
- **DO** use async where appropriate (reflection, LLM calls)
- **SHOULD** cache expensive operations (embeddings, graph queries)
- **MUST** respect token limits in compression

## Security Guidelines

- **MUST NOT** commit API keys or secrets
- **SHOULD** use environment variables for configuration
- **MUST** validate user input
- **SHOULD** sanitize file paths to prevent directory traversal

## Knowledge Block Guidelines

- **MUST** preserve YAML front-matter format
- **DO NOT** modify `id` fields after creation
- **SHOULD** maintain `content_hash` for change detection
- **MUST** handle both Markdown and JSON formats

