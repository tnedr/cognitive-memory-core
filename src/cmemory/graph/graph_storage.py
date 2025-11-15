"""Graph storage using Neo4j with in-memory fallback."""

import logging
from typing import Dict, List, Optional, Tuple

from cmemory.models import GraphNode, GraphRelationship

logger = logging.getLogger(__name__)


class InMemoryGraph:
    """In-memory graph storage fallback when Neo4j is unavailable."""

    def __init__(self):
        """Initialize in-memory graph."""
        self.nodes: Dict[str, GraphNode] = {}
        self.relationships: List[GraphRelationship] = []

    def add_node(self, node: GraphNode) -> None:
        """Add a node to the graph."""
        self.nodes[node.id] = node

    def add_relationship(self, rel: GraphRelationship) -> None:
        """Add a relationship to the graph."""
        self.relationships.append(rel)

    def query(self, cypher: str, params: Optional[Dict] = None) -> List[Dict]:
        """Simple query implementation (limited support)."""
        # Very basic pattern matching for demo
        if "MATCH" in cypher.upper() and "RETURN" in cypher.upper():
            results = []
            for rel in self.relationships:
                if rel.source_id in self.nodes and rel.target_id in self.nodes:
                    results.append(
                        {
                            "source": self.nodes[rel.source_id].properties,
                            "target": self.nodes[rel.target_id].properties,
                            "rel": rel.relationship_type,
                        }
                    )
            return results
        return []


class GraphStorage:
    """Handles graph operations using Neo4j with in-memory fallback."""

    def __init__(
        self,
        uri: Optional[str] = None,
        user: Optional[str] = None,
        password: Optional[str] = None,
        use_fallback: bool = False,
    ):
        """Initialize graph storage.

        Args:
            uri: Neo4j connection URI (default: bolt://localhost:7687).
            user: Neo4j username (default: neo4j).
            password: Neo4j password (default: password).
            use_fallback: Force use of in-memory fallback.
        """
        self.uri = uri or "bolt://localhost:7687"
        self.user = user or "neo4j"
        self.password = password or "password"
        self.driver = None
        self.fallback = InMemoryGraph()
        self.use_fallback = use_fallback

        if not use_fallback:
            try:
                from neo4j import GraphDatabase

                self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
                # Test connection
                with self.driver.session() as session:
                    session.run("RETURN 1")
                logger.info("Connected to Neo4j")
            except Exception as e:
                # Only log at DEBUG level to reduce noise when Neo4j is not available
                # The system will work fine with in-memory fallback
                logger.debug(f"Neo4j connection failed, using fallback: {e}")
                self.use_fallback = True

    def _is_using_fallback(self) -> bool:
        """Check if using fallback storage."""
        if self.use_fallback:
            return True
        if self.driver is None:
            return True
        try:
            with self.driver.session() as session:
                session.run("RETURN 1")
            return False
        except Exception:
            return True

    def add_node(self, node: GraphNode) -> None:
        """Add a node to the graph.

        Args:
            node: Graph node to add.
        """
        if self._is_using_fallback():
            self.fallback.add_node(node)
            return

        try:
            with self.driver.session() as session:
                query = """
                MERGE (n:KnowledgeBlock {id: $id})
                SET n += $properties
                """
                session.run(
                    query,
                    id=node.id,
                    properties={**node.properties, "label": node.label},
                )
        except Exception as e:
            logger.error(f"Failed to add node: {e}")
            self.fallback.add_node(node)

    def add_relationship(self, rel: GraphRelationship) -> None:
        """Add a relationship between nodes.

        Args:
            rel: Graph relationship to add.
        """
        if self._is_using_fallback():
            self.fallback.add_relationship(rel)
            return

        try:
            with self.driver.session() as session:
                query = f"""
                MATCH (a:KnowledgeBlock {{id: $source_id}})
                MATCH (b:KnowledgeBlock {{id: $target_id}})
                MERGE (a)-[r:{rel.relationship_type}]->(b)
                SET r += $properties
                """
                session.run(
                    query,
                    source_id=rel.source_id,
                    target_id=rel.target_id,
                    properties=rel.properties,
                )
        except Exception as e:
            logger.error(f"Failed to add relationship: {e}")
            self.fallback.add_relationship(rel)

    def query(self, cypher: str, params: Optional[Dict] = None) -> List[Dict]:
        """Execute a Cypher query.

        Args:
            cypher: Cypher query string.
            params: Query parameters.

        Returns:
            List of result records as dictionaries.
        """
        if self._is_using_fallback():
            return self.fallback.query(cypher, params)

        try:
            with self.driver.session() as session:
                result = session.run(cypher, params or {})
                return [dict(record) for record in result]
        except Exception as e:
            logger.error(f"Query failed: {e}")
            return self.fallback.query(cypher, params)

    def find_related(self, block_id: str, max_depth: int = 2) -> List[Tuple[str, str, str]]:
        """Find related blocks up to max_depth.

        Args:
            block_id: Source block ID.
            max_depth: Maximum relationship depth.

        Returns:
            List of (source_id, target_id, relationship_type) tuples.
        """
        cypher = f"""
        MATCH path = (start:KnowledgeBlock {{id: $block_id}})-[*1..{max_depth}]->(end:KnowledgeBlock)
        RETURN start.id as source, end.id as target, 
               [r in relationships(path) | type(r)] as rels
        """
        results = self.query(cypher, {"block_id": block_id})
        related = []
        for record in results:
            rels = record.get("rels", [])
            if rels:
                related.append((record["source"], record["target"], rels[0]))
        return related

    def close(self) -> None:
        """Close the database connection."""
        if self.driver:
            self.driver.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()

