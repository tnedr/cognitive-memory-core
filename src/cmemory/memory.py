"""Core MemorySystem class implementing the hybrid memory pipeline."""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

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
        llm=None,
    ):
        """Initialize the memory system.

        Args:
            knowledge_path: Base path for knowledge block files.
            neo4j_uri: Neo4j connection URI.
            neo4j_user: Neo4j username.
            neo4j_password: Neo4j password.
            llm: Optional LangChain chat model for reflection.

        Raises:
            RuntimeError: If OpenAI embeddings or ChromaDB are not available.
        """
        self.file_storage = FileStorage(base_path=knowledge_path)
        self.graph_storage = GraphStorage(
            uri=neo4j_uri,
            user=neo4j_user,
            password=neo4j_password,
        )
        # ChromaDB is now mandatory, use_chroma parameter is ignored
        self.vector_index = VectorIndex()
        self.reflector = Reflector(llm=llm) if llm else None
        self.decay_manager = DecayManager(knowledge_path=knowledge_path)

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
        information_type = meta.get("information_type")

        block = KnowledgeBlock(
            id=block_id,
            title=title,
            content=raw_text,
            tags=tags,
            information_type=information_type,
            metadata={k: v for k, v in meta.items() if k not in ["id", "title", "tags", "information_type"]},
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

    def _keyword_rank(self, query: str, candidate_ids: List[str]) -> Dict[str, int]:
        """Rank candidate blocks by keyword match in title and content.

        Args:
            query: Search query text.
            candidate_ids: List of block IDs to rank.

        Returns:
            Dictionary mapping block_id to rank (1 = best, higher = worse).
        """
        query_tokens = set(query.lower().split())
        scored_blocks = []

        for block_id in candidate_ids:
            block = self.file_storage.read(block_id)
            if not block:
                continue

            title_lower = block.title.lower()
            content_lower = block.content.lower()
            score = 0

            for token in query_tokens:
                if token in title_lower:
                    score += 2  # Title matches are more important
                if token in content_lower:
                    score += 1

            if score > 0:
                scored_blocks.append((block_id, score))

        # Sort by score descending, then assign ranks
        scored_blocks.sort(key=lambda x: x[1], reverse=True)
        keyword_ranks = {}
        for rank, (block_id, _) in enumerate(scored_blocks, start=1):
            keyword_ranks[block_id] = rank

        return keyword_ranks

    def _rrf_fuse(
        self,
        semantic_results: List[SearchResult],
        keyword_ranks: Dict[str, int],
        k: int = 60,
    ) -> List[SearchResult]:
        """Apply Reciprocal Rank Fusion to combine semantic and keyword rankings.

        Args:
            semantic_results: List of SearchResult objects from semantic search.
            keyword_ranks: Dictionary mapping block_id to keyword rank (1 = best).
            k: RRF constant (default 60, common in IR literature).

        Returns:
            List of SearchResult objects with RRF scores, sorted by score descending.
        """
        # Build semantic rank map (1 = best)
        semantic_ranks = {}
        for rank, result in enumerate(semantic_results, start=1):
            semantic_ranks[result.block_id] = rank

        # Get all unique block IDs
        all_block_ids = set(semantic_ranks.keys()) | set(keyword_ranks.keys())

        # Compute RRF scores
        fused_results = []
        for block_id in all_block_ids:
            rrf_score = 0.0

            # Add semantic contribution
            if block_id in semantic_ranks:
                sem_rank = semantic_ranks[block_id]
                rrf_score += 1.0 / (k + sem_rank)

            # Add keyword contribution
            if block_id in keyword_ranks:
                kw_rank = keyword_ranks[block_id]
                rrf_score += 1.0 / (k + kw_rank)

            # Find original SearchResult to preserve metadata
            original_result = next(
                (r for r in semantic_results if r.block_id == block_id),
                None,
            )
            if original_result:
                # Create new SearchResult with RRF score
                fused_result = SearchResult(
                    block_id=block_id,
                    score=rrf_score,
                    content=original_result.content,
                    metadata=original_result.metadata,
                    semantic_score=original_result.semantic_score,
                    keyword_score=original_result.keyword_score,
                    explanation={
                        **original_result.explanation,
                        "rrf_score": rrf_score,
                        "semantic_rank": semantic_ranks.get(block_id),
                        "keyword_rank": keyword_ranks.get(block_id),
                    },
                )
                fused_results.append(fused_result)

        # Sort by RRF score descending
        fused_results.sort(key=lambda x: x.score, reverse=True)
        return fused_results

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        boost: Optional[List[str]] = None,
        exclude: Optional[List[str]] = None,
        explain: bool = False,
        use_rrf: bool = False,
        rrf_k: int = 60,
    ) -> List[SearchResult]:
        """Retrieve relevant knowledge blocks for a query with hybrid scoring.

        Args:
            query: Search query text.
            top_k: Number of results to return.
            boost: Optional list of keywords to boost scores (title: +0.2, content: +0.1).
            exclude: Optional list of keywords to exclude from results.
            explain: If True, return SearchResult objects with detailed explanations.
            use_rrf: If True, use Reciprocal Rank Fusion to combine semantic and keyword rankings.
            rrf_k: RRF constant (default 60).

        Returns:
            List of SearchResult objects (if explain=True) or block IDs (if explain=False, for backwards compatibility).
        """
        # Get semantic search results with cosine similarity
        # For RRF, we need more candidates to get good fusion
        semantic_top_k = top_k * 3 if use_rrf else (top_k * 2 if boost or exclude else top_k)
        results = self.vector_index.similarity_search(query, top_k=semantic_top_k)

        # Apply RRF fusion if enabled
        if use_rrf:
            candidate_ids = [r.block_id for r in results]
            keyword_ranks = self._keyword_rank(query, candidate_ids)
            results = self._rrf_fuse(results, keyword_ranks, k=rrf_k)

        # Apply hybrid scoring (semantic + keyword boosting)
        scored_results = []
        for result in results:
            block = self.file_storage.read(result.block_id)
            if not block:
                continue

            # Start with cosine similarity score
            semantic_score = result.semantic_score if hasattr(result, 'semantic_score') else result.score
            hybrid_score = semantic_score
            keyword_score = 0.0
            explanation = result.explanation.copy() if hasattr(result, 'explanation') else {"semantic": semantic_score}
            title_matches = []
            content_matches = []

            # Apply keyword boosting
            if boost:
                boost_lower = [kw.lower() for kw in boost]
                title_lower = block.title.lower()
                content_lower = block.content.lower()

                for keyword in boost_lower:
                    if keyword in title_lower:
                        hybrid_score += 0.2
                        keyword_score += 0.2
                        title_matches.append(keyword)
                    if keyword in content_lower:
                        hybrid_score += 0.1
                        keyword_score += 0.1
                        content_matches.append(keyword)

            # Update explanation
            if title_matches:
                explanation["title_match"] = title_matches
            if content_matches:
                explanation["content_match"] = content_matches
            explanation["keyword_score"] = keyword_score

            # Apply exclusion filter
            if exclude:
                exclude_lower = [kw.lower() for kw in exclude]
                title_lower = block.title.lower()
                content_lower = block.content.lower()

                should_exclude = False
                excluded_keywords = []
                for keyword in exclude_lower:
                    if keyword in title_lower or keyword in content_lower:
                        should_exclude = True
                        excluded_keywords.append(keyword)

                if should_exclude:
                    explanation["excluded"] = excluded_keywords
                    if not explain:
                        continue  # Skip in non-explain mode
                    # In explain mode, mark as excluded but still include
                    explanation["filtered"] = True

            if explain:
                scored_results.append(
                    SearchResult(
                        block_id=result.block_id,
                        score=hybrid_score,
                        content=result.content,
                        semantic_score=semantic_score,
                        keyword_score=keyword_score,
                        explanation=explanation,
                    )
                )
            else:
                scored_results.append((result.block_id, hybrid_score, block))

        # Sort by hybrid score (descending)
        # Note: If RRF was used, results are already sorted
        if use_rrf:
            # RRF already sorted, just take top_k
            final_results = results[:top_k]
            if not explain:
                # Convert to block IDs for backwards compatibility
                final_results = [r.block_id for r in final_results]
        elif explain:
            scored_results.sort(key=lambda x: x.score, reverse=True)
            final_results = scored_results[:top_k]
        else:
            scored_results.sort(key=lambda x: x[1], reverse=True)
            final_results = [block_id for block_id, _, _ in scored_results[:top_k]]

        # Record access for retrieved blocks
        block_ids = [r.block_id if explain else r for r in final_results]
        for block_id in block_ids:
            self.decay_manager.record_access(block_id, self.file_storage)

        return final_results

    def retrieve_structured(
        self,
        query: str,
        top_k: int = 5,
        explain: bool = True,
        boost: Optional[List[str]] = None,
        exclude: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """Return structured retrieval results suitable for agents (JSON-friendly).

        Args:
            query: Search query text.
            top_k: Number of results to return.
            explain: Include detailed explanations.
            boost: Optional list of keywords to boost scores.
            exclude: Optional list of keywords to exclude from results.

        Returns:
            List of dictionaries with structured retrieval information.
        """
        results = self.retrieve(query, top_k=top_k, explain=explain, boost=boost, exclude=exclude)
        structured = []
        for r in results:
            block = self.file_storage.read(r.block_id)
            structured.append({
                "block_id": r.block_id,
                "title": block.title if block else r.block_id,
                "tags": block.tags if block else [],
                "information_type": getattr(block, "information_type", None),
                "semantic_score": getattr(r, "semantic_score", r.score),
                "keyword_score": getattr(r, "keyword_score", 0.0),
                "final_score": r.score,
                "explanation": getattr(r, "explanation", {}),
            })
        return structured

    def reflect(self, block_id: str) -> None:
        """Reflect on a knowledge block to generate insights or summaries.

        Args:
            block_id: ID of the knowledge block to reflect on.
        """
        block = self.file_storage.read(block_id)
        if not block:
            raise ValueError(f"Knowledge block not found: {block_id}")

        # Find top-5 nearest neighbours from vector index (semantic similarity)
        similar_ids = self.retrieve(block.content, top_k=5)
        # Remove self from results
        similar_ids = [sid for sid in similar_ids if sid != block_id]

        # Also check graph for existing relationships
        graph_related = self.graph_storage.find_related(block_id, max_depth=2)
        graph_related_ids = [r[1] for r in graph_related] if graph_related else []

        # Combine vector and graph results, prioritize vector (semantic similarity)
        all_related_ids = list(dict.fromkeys(similar_ids + graph_related_ids))[:5]

        # Collect blocks for reflection
        blocks_to_reflect = [block]
        for related_id in all_related_ids:
            related_block = self.file_storage.read(related_id)
            if related_block:
                blocks_to_reflect.append(related_block)

        # Use Reflector if available
        if self.reflector:
            try:
                relationships = self.reflector.reflect(blocks_to_reflect)
                # Add suggested relationships to graph
                for rel in relationships:
                    try:
                        # Ensure nodes exist
                        source_block = self.file_storage.read(rel.source_id)
                        target_block = self.file_storage.read(rel.target_id)
                        if not source_block or not target_block:
                            logger.warning(f"Skipping relationship {rel.source_id} -> {rel.target_id}: blocks not found")
                            continue

                        self.graph_storage.add_node(
                            GraphNode(
                                id=rel.source_id,
                                label="KnowledgeBlock",
                                properties={"title": source_block.title, "tags": source_block.tags},
                            )
                        )
                        self.graph_storage.add_node(
                            GraphNode(
                                id=rel.target_id,
                                label="KnowledgeBlock",
                                properties={"title": target_block.title, "tags": target_block.tags},
                            )
                        )
                        self.graph_storage.add_relationship(rel)
                        logger.info(f"Added relationship from reflection: {rel.source_id} --[{rel.relationship_type}]--> {rel.target_id}")
                    except Exception as e:
                        logger.warning(f"Failed to add reflection relationship: {e}")
            except Exception as e:
                logger.error(f"Reflection failed: {e}")
        else:
            logger.debug("No LLM configured for reflection, skipping insight generation")

        logger.info(f"Reflected on {block_id}, found {len(all_related_ids)} related blocks (vector: {len(similar_ids)}, graph: {len(graph_related_ids)})")
        if all_related_ids:
            logger.info(f"Related blocks: {all_related_ids}")

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

    def reindex_all(self) -> int:
        """Recompute embeddings for all knowledge blocks.

        Clears the vector index first, then re-adds all embeddings.
        This is useful when switching embedding models or fixing corrupted indices.

        Returns:
            Number of blocks reindexed.
        """
        # Step 1: List all blocks
        all_ids = self.file_storage.list_all()
        if not all_ids:
            logger.info("No blocks to reindex")
            return 0

        logger.info(f"Starting reindex of {len(all_ids)} blocks")

        # Step 2: Clear ChromaDB collection (required)
        if not self.vector_index.collection:
            raise RuntimeError("ChromaDB collection is not available")

        try:
            # Delete and recreate ChromaDB collection
            self.vector_index.client.delete_collection(self.vector_index.collection_name)
            self.vector_index.collection = self.vector_index.client.create_collection(
                self.vector_index.collection_name
            )
            logger.info("Cleared ChromaDB collection")
        except Exception as e:
            logger.error(f"Failed to reset ChromaDB: {e}")
            raise RuntimeError(f"ChromaDB reset failed: {e}") from e

        # Step 3: Rebuild embeddings for all blocks
        count = 0
        for block_id in all_ids:
            block = self.file_storage.read(block_id)
            if not block:
                logger.warning(f"Block not found: {block_id}, skipping")
                continue

            self.vector_index.add_embeddings([block.id], [block.content])
            count += 1

        logger.info(f"Reindexed {count} blocks successfully")
        return count

