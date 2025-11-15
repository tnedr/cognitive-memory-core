"""Command-line interface for cognitive-memory-core."""

import logging
import sys
from pathlib import Path

import click

from cmemory.memory import MemorySystem

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


@click.group()
@click.option("--knowledge-path", default="knowledge", help="Path to knowledge blocks directory")
@click.option("--neo4j-uri", default=None, help="Neo4j connection URI")
@click.option("--neo4j-user", default=None, help="Neo4j username")
@click.option("--neo4j-password", default=None, help="Neo4j password")
@click.pass_context
def cli(ctx, knowledge_path, neo4j_uri, neo4j_user, neo4j_password):
    """Cognitive Memory Core - Hybrid AI memory system CLI."""
    ctx.ensure_object(dict)
    ctx.obj["memory"] = MemorySystem(
        knowledge_path=knowledge_path,
        neo4j_uri=neo4j_uri,
        neo4j_user=neo4j_user,
        neo4j_password=neo4j_password,
    )


@cli.command()
@click.argument("file", type=click.Path(exists=True))
@click.option("--id", help="Custom block ID (auto-generated if not provided)")
@click.option("--title", help="Block title (extracted from file if not provided)")
@click.option("--information-type", help="Information type (static or dynamic)")
@click.pass_context
def ingest(ctx, file, id, title, information_type):
    """Ingest a knowledge block from a Markdown file."""
    file_path = Path(file)
    content = file_path.read_text(encoding="utf-8")

    # Parse frontmatter if present
    from cmemory.storage.file_storage import FileStorage

    storage = FileStorage()
    frontmatter, body = storage._parse_markdown_frontmatter(content)

    meta = {
        "id": id or frontmatter.get("id"),
        "title": title or frontmatter.get("title") or file_path.stem,
        "tags": frontmatter.get("tags", []),
    }
    if information_type:
        meta["information_type"] = information_type
    elif "information_type" in frontmatter:
        meta["information_type"] = frontmatter.get("information_type")
    meta.update({k: v for k, v in frontmatter.items() if k not in ["id", "title", "tags", "information_type"]})

    memory = ctx.obj["memory"]
    block_id = memory.record(body, meta)
    click.echo(f"[OK] Ingested knowledge block: {block_id}")


@cli.command()
@click.argument("source_id")
@click.option("--target-id", help="Target block ID (auto-discover if not provided)")
@click.option("--relationship", default="related_to", help="Relationship type")
@click.pass_context
def autolink(ctx, source_id, target_id, relationship):
    """Automatically link knowledge blocks based on similarity."""
    memory = ctx.obj["memory"]

    if target_id:
        # Manual link
        memory.link(source_id, target_id, relationship)
        click.echo(f"[OK] Linked {source_id} --[{relationship}]--> {target_id}")
    else:
        # Auto-discover related blocks
        source_block = memory.file_storage.read(source_id)
        if not source_block:
            click.echo(f"[ERROR] Block not found: {source_id}", err=True)
            sys.exit(1)

        # Find similar blocks
        similar_ids = memory.retrieve(source_block.content, top_k=5)
        linked_count = 0
        for similar_id in similar_ids:
            if similar_id != source_id:
                try:
                    memory.link(source_id, similar_id, relationship)
                    linked_count += 1
                    click.echo(f"[OK] Linked {source_id} --[{relationship}]--> {similar_id}")
                except Exception as e:
                    logger.warning(f"Failed to link {source_id} -> {similar_id}: {e}")

        click.echo(f"[OK] Auto-linked {linked_count} blocks")


@cli.command()
@click.argument("goal")
@click.option("--max-tokens", default=4096, help="Maximum tokens in context")
@click.option("--output", type=click.Path(), help="Output file (stdout if not provided)")
@click.pass_context
def context(ctx, goal, max_tokens, output):
    """Materialize context for a goal or query."""
    memory = ctx.obj["memory"]
    context_text = memory.materialize_context(goal, max_tokens=max_tokens)

    if output:
        Path(output).write_text(context_text, encoding="utf-8")
        click.echo(f"[OK] Context written to {output}")
    else:
        click.echo(context_text)


@cli.command()
@click.argument("query")
@click.option("--top-k", default=5, help="Number of results to return")
@click.option("--boost", multiple=True, help="Keywords to boost (can be used multiple times)")
@click.option("--exclude", multiple=True, help="Keywords to exclude (can be used multiple times)")
@click.pass_context
def search(ctx, query, top_k, boost, exclude):
    """Search for knowledge blocks with hybrid scoring (semantic + keyword boosting)."""
    memory = ctx.obj["memory"]

    # Use retrieve() for hybrid scoring, or similarity_search() for raw semantic
    boost_list = list(boost) if boost else None
    exclude_list = list(exclude) if exclude else None

    if boost_list or exclude_list:
        # Use hybrid retrieval
        block_ids = memory.retrieve(query, top_k=top_k, boost=boost_list, exclude=exclude_list)
        results = []
        for block_id in block_ids:
            block = memory.file_storage.read(block_id)
            if block:
                # Recompute score for display (approximate)
                vector_results = memory.vector_index.similarity_search(query, top_k=top_k * 2)
                score = next((r.score for r in vector_results if r.block_id == block_id), 0.0)
                # Apply boosts for display
                if boost_list:
                    boost_lower = [kw.lower() for kw in boost_list]
                    title_lower = block.title.lower()
                    content_lower = block.content.lower()
                    for keyword in boost_lower:
                        if keyword in title_lower:
                            score += 0.2
                        if keyword in content_lower:
                            score += 0.1
                results.append((block_id, score, block))
    else:
        # Use raw semantic search
        vector_results = memory.vector_index.similarity_search(query, top_k=top_k)
        results = []
        for result in vector_results:
            block = memory.file_storage.read(result.block_id)
            if block:
                results.append((result.block_id, result.score, block))

    if not results:
        click.echo("No results found")
        return

    click.echo(f"Found {len(results)} results:\n")
    for i, (block_id, score, block) in enumerate(results, 1):
        click.echo(f"{i}. [{block_id}] {block.title} (score: {score:.3f})")


@cli.command()
@click.pass_context
def list_blocks(ctx):
    """List all knowledge blocks."""
    memory = ctx.obj["memory"]
    block_ids = memory.file_storage.list_all()

    if not block_ids:
        click.echo("No knowledge blocks found")
        return

    click.echo(f"Found {len(block_ids)} knowledge blocks:\n")
    for block_id in block_ids:
        block = memory.file_storage.read(block_id)
        if block:
            click.echo(f"  • {block_id}: {block.title}")


@cli.command()
@click.option("--inflow-path", default="inflow", help="Path to inflow directory")
@click.pass_context
def digest_inflow(ctx, inflow_path):
    """Digest all files in the inflow directory into memory."""
    from cmemory.inflow import InflowProcessor

    memory = ctx.obj["memory"]
    processor = InflowProcessor(inflow_path=inflow_path, memory=memory)
    results = processor.digest()

    if results:
        click.echo("Processed files into KnowledgeBlocks:")
        for rid in results:
            click.echo(f"  • {rid}")
    else:
        click.echo("No files found in inflow directory.")


@cli.command("reindex-all")
@click.pass_context
def reindex_all_cmd(ctx):
    """Recompute embeddings for all knowledge blocks (full reindex).

    This command clears the vector index and rebuilds embeddings for all blocks.
    Useful when switching embedding models (e.g., dummy -> OpenAI) or fixing corrupted indices.
    """
    memory = ctx.obj["memory"]
    click.echo("Reindexing all knowledge blocks...")
    n = memory.reindex_all()
    click.echo(f"[OK] Reindexed {n} blocks")


@cli.command("chroma-reset")
@click.pass_context
def chroma_reset_cmd(ctx):
    """Reset ChromaDB vector store (delete all embeddings).

    This command completely clears the ChromaDB collection and removes the persistent storage.
    Use this when you need a completely fresh start or when vectors are corrupted.
    After reset, run 'reindex-all' to rebuild embeddings.
    """
    memory = ctx.obj["memory"]
    from pathlib import Path

    if memory.vector_index.use_chroma and memory.vector_index.client:
        try:
            collection_name = memory.vector_index.collection_name
            chroma_path = Path.cwd() / ".chroma"

            # Delete the collection first
            try:
                memory.vector_index.client.delete_collection(collection_name)
                click.echo(f"[OK] Deleted ChromaDB collection: {collection_name}")
            except Exception as e:
                click.echo(f"[WARN] Collection may not exist: {e}")

            # Close the client to release file locks (Windows)
            try:
                # ChromaDB PersistentClient doesn't have explicit close, but we can clear the reference
                memory.vector_index.collection = None
                memory.vector_index.client = None
            except Exception:
                pass

            # Remove persistent storage directory (after closing client)
            if chroma_path.exists():
                import shutil
                import time

                # On Windows, wait a moment for file handles to release
                time.sleep(0.5)
                try:
                    shutil.rmtree(chroma_path)
                    click.echo(f"[OK] Removed ChromaDB storage: {chroma_path}")
                except PermissionError:
                    click.echo(
                        f"[WARN] Could not delete {chroma_path} (file may be locked). "
                        "Close other processes and try again, or delete manually."
                    )
            else:
                click.echo("[INFO] No persistent ChromaDB storage found")

            # Recreate client and collection
            import chromadb
            from chromadb.config import Settings

            chroma_path.mkdir(exist_ok=True)
            memory.vector_index.client = chromadb.PersistentClient(
                path=str(chroma_path),
                settings=Settings(anonymized_telemetry=False),
            )
            memory.vector_index.collection = memory.vector_index.client.create_collection(collection_name)
            click.echo(f"[OK] Created fresh ChromaDB collection: {collection_name}")
            click.echo("[INFO] Run 'reindex-all' to rebuild embeddings")
        except Exception as e:
            click.echo(f"[ERROR] Failed to reset ChromaDB: {e}", err=True)
            raise
    else:
        click.echo("[INFO] ChromaDB not in use, nothing to reset")


if __name__ == "__main__":
    cli()

