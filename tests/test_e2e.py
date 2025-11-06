"""End-to-end integration tests for cognitive-memory-core.

These tests require Docker Compose services (Neo4j and ChromaDB) to be running.
"""

import os
import subprocess
import time
from pathlib import Path
from typing import Generator

import pytest

from cmemory.memory import MemorySystem


@pytest.fixture(scope="session")
def docker_compose_up() -> Generator[None, None, None]:
    """Start Docker Compose services for testing."""
    docker_dir = Path(__file__).parent.parent / "docker"
    compose_file = docker_dir / "docker-compose.yml"

    if not compose_file.exists():
        pytest.skip("Docker Compose file not found")

    # Start services
    try:
        subprocess.run(
            ["docker-compose", "-f", str(compose_file), "up", "-d"],
            cwd=docker_dir,
            check=True,
            capture_output=True,
        )
        # Wait for services to be ready
        time.sleep(10)
        yield
    finally:
        # Stop services
        subprocess.run(
            ["docker-compose", "-f", str(compose_file), "down"],
            cwd=docker_dir,
            check=False,
            capture_output=True,
        )


@pytest.fixture
def memory_system(tmp_path: Path, docker_compose_up: None) -> MemorySystem:
    """Create a MemorySystem instance with test configuration."""
    knowledge_path = tmp_path / "knowledge"
    knowledge_path.mkdir()

    return MemorySystem(
        knowledge_path=str(knowledge_path),
        neo4j_uri="bolt://localhost:7687",
        neo4j_user="neo4j",
        neo4j_password="password",
        use_chroma=True,
    )


@pytest.mark.e2e
def test_end_to_end_ingest_encode_link_context(memory_system: MemorySystem):
    """Test complete workflow: ingest → encode → link → context."""
    # Step 1: Ingest a knowledge block
    block_id = memory_system.record(
        "Python is a high-level programming language known for its simplicity and readability. "
        "It supports multiple programming paradigms including procedural, object-oriented, and functional programming.",
        {
            "id": "KB-TEST-001",
            "title": "Python Programming Language",
            "tags": ["python", "programming", "language"],
        },
    )
    assert block_id == "KB-TEST-001"

    # Step 2: Verify encoding (should be done automatically in record)
    # The block should be in vector index
    results = memory_system.retrieve("programming language", top_k=1)
    assert len(results) > 0
    assert block_id in results

    # Step 3: Ingest another related block
    block_id_2 = memory_system.record(
        "Memory systems are crucial for AI agents to maintain context and learn from past interactions. "
        "They combine file storage, graph databases, and vector search for efficient retrieval.",
        {
            "id": "KB-TEST-002",
            "title": "AI Memory Systems",
            "tags": ["ai", "memory", "systems"],
        },
    )

    # Step 4: Link the blocks
    memory_system.link(block_id, block_id_2, "related_to")

    # Step 5: Materialize context
    context = memory_system.materialize_context("Explain programming and AI memory", max_tokens=1000)
    assert len(context) > 0
    assert "Python" in context or "programming" in context.lower()

    # Step 6: Verify graph relationship
    related = memory_system.graph_storage.find_related(block_id, max_depth=1)
    assert len(related) > 0
    assert any(r[1] == block_id_2 for r in related)


@pytest.mark.e2e
def test_autolink_workflow(memory_system: MemorySystem):
    """Test automatic linking based on similarity."""
    # Create multiple related blocks
    block_ids = []
    for i, content in enumerate(
        [
            "Machine learning is a subset of artificial intelligence.",
            "Deep learning uses neural networks with multiple layers.",
            "Natural language processing enables computers to understand human language.",
        ],
        1,
    ):
        block_id = memory_system.record(
            content,
            {
                "id": f"KB-AUTOLINK-{i:03d}",
                "title": f"AI Concept {i}",
                "tags": ["ai", "ml"],
            },
        )
        block_ids.append(block_id)

    # Auto-link first block to similar ones
    source_block = memory_system.file_storage.read(block_ids[0])
    similar_ids = memory_system.retrieve(source_block.content, top_k=3)

    # Should find at least one similar block
    assert len(similar_ids) > 0

    # Link them
    for similar_id in similar_ids[:2]:  # Link to top 2
        if similar_id != block_ids[0]:
            memory_system.link(block_ids[0], similar_id, "related_to")

    # Verify links exist
    related = memory_system.graph_storage.find_related(block_ids[0], max_depth=1)
    assert len(related) > 0


@pytest.mark.e2e
def test_vector_search_accuracy(memory_system: MemorySystem):
    """Test that vector search returns relevant results."""
    # Create blocks with different topics
    topics = {
        "KB-TOPIC-001": "Python programming language features and syntax",
        "KB-TOPIC-002": "Docker containerization and orchestration",
        "KB-TOPIC-003": "Neo4j graph database queries and relationships",
    }

    for block_id, content in topics.items():
        memory_system.record(
            content,
            {
                "id": block_id,
                "title": f"Topic {block_id}",
                "tags": ["test"],
            },
        )

    # Search for Python-related content
    results = memory_system.retrieve("Python code examples", top_k=2)
    assert len(results) > 0
    # Should prioritize Python-related block
    assert "KB-TOPIC-001" in results[:2]


@pytest.mark.e2e
def test_graph_traversal(memory_system: MemorySystem):
    """Test graph traversal and relationship queries."""
    # Create a chain of related blocks
    block_ids = []
    for i in range(3):
        block_id = memory_system.record(
            f"Concept {i} is related to concept {i+1}",
            {
                "id": f"KB-CHAIN-{i:03d}",
                "title": f"Concept {i}",
            },
        )
        block_ids.append(block_id)

        if i > 0:
            # Link to previous
            memory_system.link(block_ids[i - 1], block_id, "leads_to")

    # Traverse from first to last
    related = memory_system.graph_storage.find_related(block_ids[0], max_depth=2)
    assert len(related) >= 2  # Should find at least 2 related blocks


@pytest.mark.skipif(
    os.getenv("SKIP_DOCKER_TESTS") == "1",
    reason="Docker tests skipped via SKIP_DOCKER_TESTS=1",
)
def test_docker_services_available(docker_compose_up: None):
    """Verify Docker services are running."""
    # Check Neo4j
    try:
        from neo4j import GraphDatabase

        driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))
        with driver.session() as session:
            result = session.run("RETURN 1 as test")
            assert result.single()["test"] == 1
        driver.close()
    except Exception as e:
        pytest.skip(f"Neo4j not available: {e}")

    # Check ChromaDB (basic HTTP check)
    try:
        import httpx

        response = httpx.get("http://localhost:8000/api/v1/heartbeat", timeout=2)
        assert response.status_code == 200
    except Exception:
        pytest.skip("ChromaDB not available")

