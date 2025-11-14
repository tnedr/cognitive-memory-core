---
status: new
change_type: expand
changed_on: 2025-11-14
---

# Project Concept – Cognitive Memory Core

## 1. High-Level Idea

The project is a **hybrid memory subsystem** for AI agents and tools.

It combines three layers:

1. **File Layer** (Markdown/JSON)

   - Human-readable knowledge blocks with YAML front-matter

   - Git-friendly and diffable

   - Directly editable by humans and AI

2. **Graph Layer** (Neo4j + in-memory fallback)

   - Nodes: `KnowledgeBlock`

   - Relationships: `related_to`, `references`, `extends`, etc.

   - Encodes long-term structure, conceptual connections, and multi-hop traversal

3. **Vector Layer** (ChromaDB/FAISS)

   - Semantic search over block content

   - Supports "retrieve by meaning", not just keywords

   - Used by reflection, context-building, and RAG flows

These layers are orchestrated by the `MemorySystem` class, which exposes a clean

Python API and is reachable via CLI today (and later via HTTP API). 

## 2. Core Responsibilities

The Cognitive Memory Core is responsible for:

- **Recording**: turning raw text + metadata into stable knowledge blocks

- **Encoding**: embedding content into the vector index

- **Linking**: creating explicit graph relationships

- **Retrieving**: semantic search + relationship-aware recall

- **Reflecting**: using an LLM to propose new connections and insights

- **Compressing**: token-aware summarisation of multiple blocks

- **Decaying**: archiving rarely-used / old blocks while keeping restoration possible

- **Materializing Context**: building a task-specific context window from relevant blocks

## 3. Intended Users

- **AI agents** (Scoper, Composer, Planner, etc.) that:

  - Need long-term memory across runs

  - Need to share memory across multiple agents

- **Human developers / analysts** who:

  - Want a transparent, inspectable memory layer

  - Prefer editing content in Markdown and versioning it in Git

- **Operations / platform teams** who:

  - Care about test coverage, CI, and predictable deployments

## 4. Non-Goals (for now)

- Full-blown knowledge-graph UI

- Multi-tenant SaaS platform

- Heavy, proprietary protocols

The focus is to provide a **solid, testable core** that can be embedded into

larger systems and grown iteratively.

## 5. Evolution Path

Short-/mid-term evolution:

1. v0.2.x – PoC + LLM-based reflection (done)

2. v0.3.x – Compression + decay, with scheduling and docs (in progress) 

3. v0.4.x – FastAPI/GraphQL API, watcher, better observability

4. v1.0.0 – Production-ready stability, APIs and docs frozen at contract level

The concept is explicitly allowed to **expand** as we add new memory capabilities

and as the agent ecosystem around it grows.

