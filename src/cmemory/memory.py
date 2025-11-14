"""Core MemorySystem class implementing the hybrid memory pipeline."""

import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal

from cmemory.compress import Compressor
from cmemory.decay import DecayManager
from cmemory.graph import GraphStorage
from cmemory.models import GraphNode, GraphRelationship, KnowledgeBlock, SearchResult
from cmemory.reflection import Reflector
from cmemory.storage import FileStorage
from cmemory.vector import VectorIndex

logger = logging.getLogger(__name__)


class MemorySystem:
    """Hybrid AI memory system combining file storage, graph, and vector search."""

    def __init__(
        self,
        knowledge_path: str = "knowledge",
        neo4j_uri: Optional[str] = None,
        neo4j_user: Optional[str] = None,
        neo4j_password: Optional[str] = None,
        use_chroma: bool = True,
    ):
        """Initialize the memory system.

        Args:
            knowledge_path: Base path for knowledge block files.
            neo4j_uri: Neo4j connection URI.
            neo4j_user: Neo4j username.
            neo4j_password: Neo4j password.
            use_chroma: Use ChromaDB for vector storage.
        """
        self.file_storage = FileStorage(base_path=knowledge_path)
        self.graph_storage = GraphStorage(
            uri=neo4j_uri,
            user=neo4j_user,
            password=neo4j_password,
        )
        self.vector_index = VectorIndex(use_chroma=use_chroma)

    def record(self, raw_text: str, meta: Dict) -> str:
        """Record a new knowledge block from raw text.

        Args:
            raw_text: Raw text content to store.
            meta: Metadata dictionary (must include 'id' and 'title').

        Returns:
            ID of the created knowledge block.
        """
        block_id = meta.get("id")
        if not block_id:
            # Generate ID from timestamp
            block_id = f"KB-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}"

        title = meta.get("title", "Untitled")
        tags = meta.get("tags", [])
        if isinstance(tags, str):
            tags = [tags]

        block = KnowledgeBlock(
            id=block_id,
            title=title,
            content=raw_text,
            tags=tags,
            metadata={k: v for k, v in meta.items() if k not in ["id", "title", "tags"]},
        )
        block.content_hash = self.file_storage._calculate_hash(raw_text)

        self.file_storage.create(block, format="markdown")
        logger.info(f"Recorded knowledge block: {block_id}")

        # Initialize access metadata
        self.decay_manager._update_access_metadata(block)
        self.file_storage.update(block)

        # Auto-encode and link
        self.encode(block_id)
        return block_id

    def encode(self, record_id: str) -> str:
        """Encode a knowledge block into vector embeddings.

        Args:
            record_id: ID of the knowledge block to encode.

        Returns:
            Embedding ID (same as record_id).
        """
        block = self.file_storage.read(record_id)
        if not block:
            raise ValueError(f"Knowledge block not found: {record_id}")

        # Add to vector index
        self.vector_index.add_embeddings([block.id], [block.content])
        logger.info(f"Encoded knowledge block: {record_id}")
        return record_id

    def link(self, src_id: str, dst_id: str, rel: str) -> None:
        """Create a relationship between two knowledge blocks.

        Args:
            src_id: Source block ID.
            dst_id: Target block ID.
            rel: Relationship type (e.g., 'references', 'related_to', 'extends').
        """
        # Ensure nodes exist in graph
        src_block = self.file_storage.read(src_id)
        dst_block = self.file_storage.read(dst_id)

        if not src_block or not dst_block:
            raise ValueError(f"One or both blocks not found: {src_id}, {dst_id}")

        src_node = GraphNode(
            id=src_id,
            label="KnowledgeBlock",
            properties={"title": src_block.title, "tags": src_block.tags},
        )
        dst_node = GraphNode(
            id=dst_id,
            label="KnowledgeBlock",
            properties={"title": dst_block.title, "tags": dst_block.tags},
        )

        self.graph_storage.add_node(src_node)
        self.graph_storage.add_node(dst_node)

        relationship = GraphRelationship(
            source_id=src_id,
            target_id=dst_id,
            relationship_type=rel,
        )
        self.graph_storage.add_relationship(relationship)
        logger.info(f"Linked {src_id} --[{rel}]--> {dst_id}")

    def retrieve(self, query: str, top_k: int = 5) -> List[str]:
        """Retrieve relevant knowledge blocks for a query.

        Args:
            query: Search query text.
            top_k: Number of results to return.

        Returns:
            List of block IDs ordered by relevance.
        """
        results = self.vector_index.similarity_search(query, top_k=top_k)
        block_ids = [result.block_id for result in results]

        # Record access for retrieved blocks
        for block_id in block_ids:
            self.decay_manager.record_access(block_id, self.file_storage)

        return block_ids

    def reflect(self, block_id: str) -> None:
        """Reflect on a knowledge block to generate insights or summaries.

        Args:
            block_id: ID of the knowledge block to reflect on.
        """
        block = self.file_storage.read(block_id)
        if not block:
            raise ValueError(f"Knowledge block not found: {block_id}")

        # Find related blocks
        related = self.graph_storage.find_related(block_id, max_depth=2)
        logger.info(f"Reflected on {block_id}, found {len(related)} related blocks")

        # In a full implementation, this would use an LLM to generate insights
        # For now, we just log the reflection
        if related:
            related_ids = [r[1] for r in related]
            logger.info(f"Related blocks: {related_ids}")

    def compress(self, block_ids: List[str], max_tokens: Optional[int] = None) -> str:
        """Compress multiple knowledge blocks into a single summary.

        Args:
            block_ids: List of block IDs to compress.
            max_tokens: Maximum tokens for compressed output (default: 4096).

        Returns:
            Compressed summary text.
        """
        blocks = []
        for block_id in block_ids:
            block = self.file_storage.read(block_id)
            if block:
                blocks.append(block)

        if not blocks:
            return ""

        # Use Compressor if available
        if self.compressor:
            summary = self.compressor.compress(blocks, max_tokens=max_tokens)
            logger.info(f"Compressed {len(blocks)} blocks into summary ({len(summary)} chars)")
            return summary
        else:
            # Fallback: simple concatenation
            summary_parts = []
            for block in blocks:
                summary_parts.append(f"**{block.title}**: {block.content[:200]}...")
            summary = "\n\n".join(summary_parts)
            logger.info(f"Compressed {len(blocks)} blocks into summary (fallback mode)")
            return summary

    def decay(
        self,
        policy: str = "time",
        days_threshold: int = 180,
        usage_threshold: float = 0.01,
    ) -> List[str]:
        """Apply decay policy to knowledge blocks (archive old/unused blocks).

        Args:
            policy: Decay policy ('time', 'usage', 'both', or 'none').
            days_threshold: Days since last access for time-based decay (default: 180).
            usage_threshold: Minimum access count ratio for usage-based decay (default: 0.01).

        Returns:
            List of archived block IDs.
        """
        if policy == "none":
            return []

        archived = self.decay_manager.decay(
            storage=self.file_storage,
            policy=policy,
            days_threshold=days_threshold,
            usage_threshold=usage_threshold,
        )

        # Remove from vector index (if possible)
        for block_id in archived:
            # Note: Vector index removal depends on implementation
            # For now, we just log
            logger.debug(f"Block {block_id} archived, should be removed from vector index")

        return archived

    def materialize_context(self, goal: str, max_tokens: int = 4096) -> str:
        """Materialize a context string from relevant knowledge blocks for a goal.

        Args:
            goal: Goal or query to materialize context for.
            max_tokens: Maximum token count for the context.

        Returns:
            Materialized context string.
        """
        # Retrieve relevant blocks
        relevant_ids = self.retrieve(goal, top_k=10)

        # Load blocks and build context
        context_parts = []
        current_length = 0

        for block_id in relevant_ids:
            block = self.file_storage.read(block_id)
            if not block:
                continue

            # Simple token estimation (rough: 1 token ≈ 4 characters)
            block_text = f"## {block.title}\n\n{block.content}\n\n"
            block_length = len(block_text) // 4

            if current_length + block_length > max_tokens:
                break

            context_parts.append(block_text)
            current_length += block_length

        context = "\n".join(context_parts)
        logger.info(f"Materialized context with {len(context_parts)} blocks ({current_length} tokens)")
        return context

