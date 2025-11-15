---
status: specification
change_type: new
changed_on: 2025-11-14
---

# Remote + Mobile Accessible Memory System Specification

This spec describes what the system needs, how it should behave, and what minimal endpoints or UX it must provide so you can use it from your phone, laptop, or other agents.

## 1. Purpose

To run the cognitive-memory-core on a remote machine (a rented server), and expose it in a way that:

- can be used from mobile (browser, mobile SSH, shortcuts)
- can be used by agents
- can ingest text files from an inflow folder
- can retrieve context and search results on demand (RAG)
- remains lightweight and simple

## 2. Requirements

### Functional Requirements

#### Memory Initialization

Start MemorySystem with file storage, graph storage (optional Neo4j), and vector index.

#### Inflow Folder

A folder on the server (e.g. `/srv/inflow`) where the user can drop `.md` or `.txt` files from any device.

#### Digest Pipeline

A command or API endpoint that:

- scans the inflow folder
- converts each file into a knowledge block
- records, encodes, and links them
- moves processed files into an `archive/processed/` folder

#### Retrieval

Ability to retrieve blocks by:

- search query (semantic search)
- context request (goal-based retrieval)
- list-all

#### API Access (mobile-friendly)

Minimal REST API:

- `POST /digest` — process inflow folder
- `POST /search` — return top-k blocks
- `POST /context` — return context bundle
- `POST /record` — manually add text
- Optional UI endpoint: `/ui` returning a tiny HTML page.

#### Authentication (optional)

Simple API key passed in header.

### Non-Functional Requirements

- **Lightweight**: must run alongside other workloads (e.g., crypto bot)
- **Resilient**: fallback to in-memory graph/vector if services unavailable
- **Safe for mobile networks** (HTTPS optional but recommended)
- **Expandable later** to support:
  - reliability
  - sensors
  - decay
  - personal long-term memory

## 3. Architecture Overview

```
[ Mobile Device ]   --->   [ REST API ]   --->  [ MemorySystem ]
                 (phone)       (FastAPI)         (file + graph + vector)

                                      ↘️ ingest ↙️
                                 [ inflow folder ]
```

### Components

- **MemorySystem** — main orchestrator
- **FileStorage** — reads/writes Markdown files
- **InflowProcessor** — NEW component (scans folder, converts to blocks)
- **REST API** — minimal, mobile-friendly
- **Optional Neo4j & ChromaDB** for full features

## 4. Endpoints (Minimal API)

### POST /digest

Scan inflow folder → create blocks → return summary.

**Request:**
```json
{
  "inflow_path": "/srv/inflow",
  "archive_path": "/srv/inflow/archive/processed"
}
```

**Response:**
```json
{
  "processed": 5,
  "blocks_created": ["KB-001", "KB-002", "KB-003", "KB-004", "KB-005"],
  "errors": []
}
```

### POST /search

**Request:**
```json
{
  "query": "nad boosters",
  "top_k": 5
}
```

**Returns:**
- list of block IDs
- small text previews
- scores

**Response:**
```json
{
  "results": [
    {
      "block_id": "NAD-001",
      "title": "Resveratrol as an NAD Booster",
      "score": 0.85,
      "preview": "Resveratrol is a polyphenol compound found in grapes..."
    },
    {
      "block_id": "NAD-002",
      "title": "NMN as a Direct NAD Precursor",
      "score": 0.82,
      "preview": "NMN is a direct precursor to NAD+..."
    }
  ]
}
```

### POST /context

**Request:**
```json
{
  "goal": "Explain NAD precursors",
  "max_tokens": 4000
}
```

**Returns:**
- context bundle (merged blocks)
- provenance metadata

**Response:**
```json
{
  "context": "## Resveratrol as an NAD Booster\n\nResveratrol is a polyphenol...\n\n## NMN as a Direct NAD Precursor\n\nNMN is a direct precursor...",
  "blocks_used": ["NAD-001", "NAD-002"],
  "token_count": 342,
  "max_tokens": 4000
}
```

### POST /record

**Request:**
```json
{
  "id": "KB-20251114-001",
  "title": "Example Knowledge Block",
  "tags": ["example", "test"],
  "content": "raw text content here...",
  "information_type": "static"
}
```

Stores a block without requiring a Markdown file.

**Response:**
```json
{
  "block_id": "KB-20251114-001",
  "status": "created",
  "encoded": true
}
```

### GET /list

**Request:** None (query params optional)

**Response:**
```json
{
  "blocks": [
    {
      "id": "NAD-001",
      "title": "Resveratrol as an NAD Booster",
      "created": "2025-11-14T10:00:00Z",
      "tags": ["nad", "resveratrol"]
    }
  ],
  "total": 1
}
```

### GET /ui (Optional)

Returns a tiny HTML page for mobile-friendly interaction.

## 5. Minimal Deployment Requirements

On your rented machine:

```bash
python -m venv .venv
source .venv/bin/activate
uv pip install -e .
uvicorn src.api:app --host 0.0.0.0 --port 8008
```

You can access from your phone:

```
http://<your-server-ip>:8008/search
```

Later we can build a tiny `/ui` endpoint.

## 6. Implementation Considerations

### InflowProcessor Component

New component to handle:

- File watching or periodic scanning
- File format detection (Markdown vs plain text)
- Automatic block ID generation
- Metadata extraction from filenames or frontmatter
- Error handling for malformed files
- Archive management

### API Security

- Optional API key authentication via header: `X-API-Key: <key>`
- Rate limiting for mobile networks
- Input validation and sanitization

### Error Handling

- Graceful degradation if Neo4j/ChromaDB unavailable
- Clear error messages for mobile clients
- Retry logic for transient failures

### Mobile Optimization

- Lightweight JSON responses
- Minimal payload sizes
- Fast response times
- Clear, simple error messages

## 7. Future Enhancements

- WebSocket support for real-time updates
- File upload endpoint (multipart/form-data)
- Batch operations for multiple files
- Webhook notifications for processed files
- Admin dashboard at `/admin`
- GraphQL alternative to REST
- OAuth2 authentication
- Rate limiting per API key
- Request logging and analytics

## 8. Example Usage Scenarios

### Scenario 1: Mobile Note Taking

1. User writes note in mobile app
2. App saves to `/srv/inflow/note_20251114.md`
3. User calls `POST /digest` or system auto-processes
4. Note becomes searchable knowledge block

### Scenario 2: Agent Context Retrieval

1. Agent needs context for task
2. Agent calls `POST /context` with goal
3. System returns relevant blocks
4. Agent uses context for task completion

### Scenario 3: Quick Search from Phone

1. User opens mobile browser
2. Navigates to `http://server:8008/ui`
3. Enters search query
4. Gets results instantly

## 9. Related Documentation

- [Project Goal](./goal.md) - Overall project objectives
- [Memory Information Model](./information_types.md) - Information type handling
- [API Reference](../api/README.md) - Detailed API documentation (when created)

