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
@click.pass_context
def ingest(ctx, file, id, title):
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
    meta.update({k: v for k, v in frontmatter.items() if k not in ["id", "title", "tags"]})

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
@click.pass_context
def search(ctx, query, top_k):
    """Search for knowledge blocks."""
    memory = ctx.obj["memory"]
    results = memory.vector_index.similarity_search(query, top_k=top_k)

    if not results:
        click.echo("No results found")
        return

    click.echo(f"Found {len(results)} results:\n")
    for i, result in enumerate(results, 1):
        block = memory.file_storage.read(result.block_id)
        title = block.title if block else result.block_id
        click.echo(f"{i}. [{result.block_id}] {title} (score: {result.score:.3f})")


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


if __name__ == "__main__":
    cli()

