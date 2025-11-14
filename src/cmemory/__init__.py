"""
Cognitive Memory Core - A hybrid AI memory system.

Combines file-based storage (Markdown/JSON), graph database (Neo4j),
and vector search (ChromaDB/FAISS) for intelligent knowledge management.
"""

__version__ = "0.2.0"

from cmemory.memory import MemorySystem

__all__ = ["MemorySystem"]

