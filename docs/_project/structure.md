---
status: new
change_type: expand
changed_on: 2025-11-14
---

# Repository Structure (Human Overview)

This is a high-level map of the `cognitive-memory-core` repo, focused on the

main moving parts.

```text
cognitive-memory-core/

├── src/
│   ├── cmemory/
│   │   ├── memory.py          # MemorySystem orchestrator
│   │   ├── models.py          # Core dataclasses (KnowledgeBlock, GraphNode, etc.)
│   │   ├── storage/           # FileStorage (Markdown/JSON)
│   │   ├── graph/             # GraphStorage (Neo4j + in-memory fallback)
│   │   ├── vector/            # VectorIndex (ChromaDB + FAISS)
│   │   ├── reflection/        # Reflector + LLM-based insights
│   │   ├── compress/          # Compressor (token-aware summarisation)
│   │   └── decay/             # DecayManager (archival policies)
│   └── cli.py                 # CLI entrypoint (cmemory)

├── tests/                     # Unit + E2E tests

├── knowledge/                 # Sample knowledge blocks (Markdown)

├── docker/                    # docker-compose for Neo4j + ChromaDB

├── docs/                      # Project, usage, and feature docs

├── templates/                 # Jinja templates (e.g. reflect.jinja)

├── README.md                  # High-level overview

├── CHANGELOG.md               # Version history

└── pyproject.toml             # Package metadata, deps, pytest config
```

## Key Modules

* **MemorySystem (`src/cmemory/memory.py`)**

  Orchestrates file, graph, vector, reflection, compression, and decay.

  Public methods include: `record`, `encode`, `link`, `retrieve`, `reflect`,

  `compress`, `decay`, `materialize_context`. 

* **Reflection (`src/cmemory/reflection/reflector.py`)**

  Uses an LLM + Jinja prompt to generate insights and suggested relationships

  between blocks. Integrated with `MemorySystem.reflect()`.

* **Compression (`src/cmemory/compress/compressor.py`)**

  Token-aware summarisation over multiple knowledge blocks using tiktoken and,

  when available, a LangChain map-reduce chain.

* **Decay (`src/cmemory/decay/decay_manager.py`)**

  Tracks `last_access` / `access_count` and archives low-usage or old blocks

  into an `archive/` folder, with restoration support.

* **CLI (`src/cli.py`)**

  Provides `ingest`, `autolink`, `context`, `search`, `list-blocks` commands

  for humans and scripts.

This file is for humans to understand "where things live" at a glance. For AI

agents, the equivalent is `docs/_ai/ai_project_map.yaml` (to be created).

