---
id: KB-20251106-001
title: Memory System Architecture
tags: [memory, hybrid, Neo4j, vector]
created: 2025-11-06T14:32:00Z
---

# Hybrid Memory System Architecture

A hybrid memory system combines plain-text blocks with a graph and vector layer to enable intelligent knowledge management.

## Components

1. **File Storage**: Markdown/JSON files for human-readable knowledge blocks
2. **Graph Layer**: Neo4j for relationship tracking and semantic connections
3. **Vector Layer**: ChromaDB/FAISS for semantic similarity search

## Benefits

- **Human-editable**: Knowledge blocks can be edited directly in Markdown
- **Semantic search**: Vector embeddings enable natural language queries
- **Relationship tracking**: Graph database maintains connections between concepts
- **Scalable**: Each layer can scale independently

## Use Cases

- Long-term memory for AI agents
- Knowledge base management
- Research note organization
- Document relationship mapping

