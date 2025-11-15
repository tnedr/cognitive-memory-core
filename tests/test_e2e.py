"""End-to-end integration tests for cognitive-memory-core.

These tests require Docker Compose services (Neo4j and ChromaDB) to be running.

To run these tests:
    docker-compose -f docker/docker-compose.yml up -d
    pytest tests/test_e2e.py -v -m e2e

Or skip Docker tests:
    SKIP_DOCKER_TESTS=1 pytest tests/test_e2e.py
"""

import logging
import os
import subprocess
import time
from pathlib import Path
from typing import Generator

import pytest

from cmemory.memory import MemorySystem

logger = logging.getLogger(__name__)


def _wait_for_service(url: str, timeout: int = 60, check_interval: int = 2) -> bool:
    """Wait for a service to become available.

    Args:
        url: Service URL to check
        timeout: Maximum time to wait in seconds
        check_interval: Time between checks in seconds

    Returns:
        True if service is available, False otherwise
    """
    import httpx
    from neo4j import GraphDatabase

    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            if url.startswith("http"):
                # HTTP service (ChromaDB)
                response = httpx.get(f"{url}/api/v1/heartbeat", timeout=2)
                if response.status_code == 200:
                    return True
            else:
                # Neo4j Bolt
                driver = GraphDatabase.driver(url, auth=("neo4j", "password"))
                with driver.session() as session:
                    session.run("RETURN 1")
                driver.close()
                return True
        except Exception:
            pass
        time.sleep(check_interval)
    return False


@pytest.fixture(scope="session")
def docker_compose_up() -> Generator[None, None, None]:
    """Start Docker Compose services for testing with health checks."""
    docker_dir = Path(__file__).parent.parent / "docker"
    compose_file = docker_dir / "docker-compose.yml"

    if not compose_file.exists():
        pytest.skip("Docker Compose file not found")

    # Start services
    try:
        result = subprocess.run(
            ["docker-compose", "-f", str(compose_file), "up", "-d"],
            cwd=docker_dir,
            check=True,
            capture_output=True,
            text=True,
        )

        # Wait for Neo4j to be ready (poll bolt://localhost:7687)
        logger.info("Waiting for Neo4j to be ready...")
        neo4j_ready = _wait_for_service("bolt://localhost:7687", timeout=60)
        if not neo4j_ready:
            pytest.fail("Neo4j did not become ready within 60 seconds")

        # Wait for ChromaDB to be ready (poll http://localhost:8000)
        logger.info("Waiting for ChromaDB to be ready...")
        chroma_ready = _wait_for_service("http://localhost:8000", timeout=60)
        if not chroma_ready:
            pytest.fail("ChromaDB did not become ready within 60 seconds")

        logger.info("All Docker services are ready")
        yield
    except subprocess.CalledProcessError as e:
        pytest.fail(f"Failed to start Docker services: {e.stderr}")
    finally:
        # Stop services
        subprocess.run(
            ["docker-compose", "-f", str(compose_file), "down"],
            cwd=docker_dir,
            check=False,
            capture_output=True,
        )


def _ingest_sample_blocks(memory_system: MemorySystem, knowledge_dir: Path) -> list[str]:
    """Ingest 5 sample knowledge blocks for testing.

    Args:
        memory_system: MemorySystem instance
        knowledge_dir: Directory containing knowledge block files

    Returns:
        List of ingested block IDs
    """
    block_files = sorted(knowledge_dir.glob("KB-20251107-*.md"))
    if len(block_files) < 5:
        # Create blocks programmatically if files don't exist
        sample_blocks = [
            {
                "id": "KB-20251107-001",
                "title": "Python Programming Fundamentals",
                "content": "Python is a high-level programming language.",
                "tags": ["python", "programming"],
            },
            {
                "id": "KB-20251107-002",
                "title": "Memory Systems in AI Agents",
                "content": "Memory systems are crucial for AI agents.",
                "tags": ["ai", "memory"],
            },
            {
                "id": "KB-20251107-003",
                "title": "Graph Databases and Neo4j",
                "content": "Graph databases store relationships efficiently.",
                "tags": ["database", "graph"],
            },
            {
                "id": "KB-20251107-004",
                "title": "Vector Embeddings and Semantic Search",
                "content": "Vector embeddings enable semantic similarity search.",
                "tags": ["vectors", "search"],
            },
            {
                "id": "KB-20251107-005",
                "title": "LangChain and LLM Integration",
                "content": "LangChain provides tools for LLM applications.",
                "tags": ["langchain", "llm"],
            },
        ]
        block_ids = []
        for block_data in sample_blocks:
            block_id = memory_system.record(block_data["content"], block_data)
            block_ids.append(block_id)
        return block_ids
    else:
        # Ingest from files
        block_ids = []
        for block_file in block_files[:5]:
            from cmemory.storage.file_storage import FileStorage

            storage = FileStorage(base_path=str(knowledge_dir))
            content = block_file.read_text(encoding="utf-8")
            frontmatter, body = storage._parse_markdown_frontmatter(content)

            meta = {
                "id": frontmatter.get("id", block_file.stem),
                "title": frontmatter.get("title", block_file.stem),
                "tags": frontmatter.get("tags", []),
            }
            meta.update({k: v for k, v in frontmatter.items() if k not in ["id", "title", "tags"]})

            block_id = memory_system.record(body, meta)
            block_ids.append(block_id)
        return block_ids


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
        # ChromaDB is now mandatory
    )


@pytest.fixture
def ingested_blocks(memory_system: MemorySystem, tmp_path: Path) -> list[str]:
    """Ingest 5 sample knowledge blocks for E2E tests."""
    knowledge_dir = Path(__file__).parent.parent / "knowledge"
    return _ingest_sample_blocks(memory_system, knowledge_dir)


@pytest.mark.e2e
def test_end_to_end_ingest_encode_link_context(memory_system: MemorySystem, ingested_blocks: list[str]):
    """Test complete workflow: ingest → encode → link → context."""
    # Use ingested blocks
    block_id = ingested_blocks[0]  # Python Programming
    block_id_2 = ingested_blocks[1]  # Memory Systems

    # Step 1: Verify encoding (should be done automatically in record)
    # The block should be in vector index
    results = memory_system.retrieve("programming language", top_k=3)
    assert len(results) > 0, "No results from vector search"
    assert block_id in results, f"Block {block_id} not found in search results"

    # Step 2: Link the blocks
    memory_system.link(block_id, block_id_2, "related_to")

    # Step 3: Materialize context
    context = memory_system.materialize_context("Explain programming and AI memory", max_tokens=1000)
    assert len(context) > 0, "Context should not be empty"
    # Should contain relevant content
    assert "Python" in context or "programming" in context.lower() or "memory" in context.lower()

    # Step 4: Verify graph relationship
    related = memory_system.graph_storage.find_related(block_id, max_depth=1)
    assert len(related) > 0, "No related blocks found in graph"
    assert any(r[1] == block_id_2 for r in related), f"Relationship {block_id} -> {block_id_2} not found"


@pytest.mark.e2e
def test_autolink_workflow(memory_system: MemorySystem, ingested_blocks: list[str]):
    """Test automatic linking based on similarity."""
    # Use ingested blocks
    source_block_id = ingested_blocks[0]  # Python Programming
    source_block = memory_system.file_storage.read(source_block_id)
    assert source_block is not None, f"Block {source_block_id} not found"

    # Find similar blocks
    similar_ids = memory_system.retrieve(source_block.content, top_k=5)
    assert len(similar_ids) > 0, "Should find similar blocks"

    # Link to top similar blocks (excluding self)
    linked_count = 0
    for similar_id in similar_ids[:3]:
        if similar_id != source_block_id:
            try:
                memory_system.link(source_block_id, similar_id, "related_to")
                linked_count += 1
            except Exception as e:
                logger.warning(f"Failed to link {source_block_id} -> {similar_id}: {e}")

    assert linked_count > 0, "Should have linked at least one block"

    # Verify links exist in graph
    related = memory_system.graph_storage.find_related(source_block_id, max_depth=1)
    assert len(related) > 0, "Should have relationships in graph"


@pytest.mark.e2e
def test_vector_search_accuracy(memory_system: MemorySystem, ingested_blocks: list[str]):
    """Test that vector search returns relevant results."""
    # Search for Python-related content
    results = memory_system.retrieve("Python programming language", top_k=3)
    assert len(results) > 0, "Should return search results"
    # Should find Python-related block (KB-20251107-001)
    assert any("001" in block_id for block_id in results), "Should find Python-related block"

    # Search for memory/AI related content
    results = memory_system.retrieve("AI memory systems", top_k=3)
    assert len(results) > 0, "Should return search results"
    # Should find memory-related block (KB-20251107-002)
    assert any("002" in block_id for block_id in results), "Should find memory-related block"


@pytest.mark.e2e
def test_graph_traversal(memory_system: MemorySystem, ingested_blocks: list[str]):
    """Test graph traversal and relationship queries."""
    # Create a chain of relationships between ingested blocks
    block_ids = ingested_blocks[:3]  # Use first 3 blocks

    # Link them in a chain
    for i in range(1, len(block_ids)):
        memory_system.link(block_ids[i - 1], block_ids[i], "leads_to")

    # Traverse from first to last
    related = memory_system.graph_storage.find_related(block_ids[0], max_depth=2)
    assert len(related) >= 1, "Should find at least one related block"
    # Verify we can reach the last block
    assert any(r[1] == block_ids[-1] for r in related), f"Should be able to traverse to {block_ids[-1]}"


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
        pytest.fail(f"Neo4j not available: {e}")

    # Check ChromaDB (basic HTTP check)
    try:
        import httpx

        response = httpx.get("http://localhost:8000/api/v1/heartbeat", timeout=2)
        assert response.status_code == 200, f"ChromaDB heartbeat returned {response.status_code}"
    except Exception as e:
        pytest.fail(f"ChromaDB not available: {e}")
