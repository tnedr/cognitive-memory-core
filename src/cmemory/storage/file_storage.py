"""File-based storage for knowledge blocks using Markdown and JSON."""

import hashlib
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import orjson
from markdown_it import MarkdownIt
from markdown_it.tree import SyntaxTreeNode

from cmemory.models import KnowledgeBlock


class FileStorage:
    """Handles CRUD operations for knowledge blocks stored as Markdown/JSON files."""

    def __init__(self, base_path: str = "knowledge"):
        """Initialize file storage.

        Args:
            base_path: Base directory for storing knowledge blocks.
        """
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.md_parser = MarkdownIt()

    def _calculate_hash(self, content: str) -> str:
        """Calculate SHA256 hash of content."""
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def _parse_markdown_frontmatter(self, content: str) -> Tuple[Dict, str]:
        """Parse YAML frontmatter from Markdown content.

        Returns:
            Tuple of (frontmatter_dict, body_content).
        """
        lines = content.split("\n")
        if not lines or not lines[0].strip().startswith("---"):
            return {}, content

        frontmatter_lines = []
        body_start = 1
        for i, line in enumerate(lines[1:], 1):
            if line.strip() == "---":
                body_start = i + 1
                break
            frontmatter_lines.append(line)

        frontmatter_text = "\n".join(frontmatter_lines)
        try:
            import yaml

            frontmatter = yaml.safe_load(frontmatter_text) or {}
        except Exception:
            frontmatter = {}

        body = "\n".join(lines[body_start:])
        return frontmatter, body

    def create(self, block: KnowledgeBlock, format: str = "markdown") -> str:
        """Create a new knowledge block file.

        Args:
            block: Knowledge block to store.
            format: Storage format ('markdown' or 'json').

        Returns:
            Path to created file.
        """
        if format == "markdown":
            return self._create_markdown(block)
        else:
            return self._create_json(block)

    def _create_markdown(self, block: KnowledgeBlock) -> str:
        """Create Markdown file with frontmatter."""
        frontmatter = {
            "id": block.id,
            "title": block.title,
            "tags": block.tags,
            "created": block.created.isoformat(),
            "updated": block.updated.isoformat(),
        }
        frontmatter.update(block.metadata)

        import yaml

        frontmatter_text = yaml.dump(frontmatter, default_flow_style=False, sort_keys=False)
        content = f"---\n{frontmatter_text}---\n\n{block.content}"

        file_path = self.base_path / f"{block.id}.md"
        file_path.write_text(content, encoding="utf-8")
        return str(file_path)

    def _create_json(self, block: KnowledgeBlock) -> str:
        """Create JSON file."""
        file_path = self.base_path / f"{block.id}.json"
        data = block.to_dict()
        json_bytes = orjson.dumps(data, option=orjson.OPT_INDENT_2)
        file_path.write_bytes(json_bytes)
        return str(file_path)

    def read(self, block_id: str) -> Optional[KnowledgeBlock]:
        """Read a knowledge block by ID.

        Args:
            block_id: ID of the knowledge block.

        Returns:
            KnowledgeBlock if found, None otherwise.
        """
        # Try Markdown first
        md_path = self.base_path / f"{block_id}.md"
        if md_path.exists():
            return self._read_markdown(md_path)

        # Try JSON
        json_path = self.base_path / f"{block_id}.json"
        if json_path.exists():
            return self._read_json(json_path)

        return None

    def _read_markdown(self, file_path: Path) -> KnowledgeBlock:
        """Read Markdown file with frontmatter."""
        content = file_path.read_text(encoding="utf-8")
        frontmatter, body = self._parse_markdown_frontmatter(content)

        block_id = frontmatter.get("id", file_path.stem)
        title = frontmatter.get("title", "Untitled")
        tags = frontmatter.get("tags", [])
        created_str = frontmatter.get("created")
        updated_str = frontmatter.get("updated", created_str)

        # Handle datetime parsing - created_str might be a string or already a datetime
        if created_str and isinstance(created_str, str):
            created = datetime.fromisoformat(created_str.replace("Z", "+00:00"))
        elif created_str and isinstance(created_str, datetime):
            created = created_str
        else:
            created = datetime.now(timezone.utc)

        if updated_str and isinstance(updated_str, str):
            updated = datetime.fromisoformat(updated_str.replace("Z", "+00:00"))
        elif updated_str and isinstance(updated_str, datetime):
            updated = updated_str
        else:
            updated = datetime.now(timezone.utc)

        metadata = {k: v for k, v in frontmatter.items() if k not in ["id", "title", "tags", "created", "updated"]}

        block = KnowledgeBlock(
            id=block_id,
            title=title,
            content=body.strip(),
            tags=tags if isinstance(tags, list) else [tags] if tags else [],
            created=created,
            updated=updated,
            metadata=metadata,
        )
        block.content_hash = self._calculate_hash(block.content)
        return block

    def _read_json(self, file_path: Path) -> KnowledgeBlock:
        """Read JSON file."""
        json_bytes = file_path.read_bytes()
        data = orjson.loads(json_bytes)
        block = KnowledgeBlock.from_dict(data)
        block.content_hash = self._calculate_hash(block.content)
        return block

    def update(self, block: KnowledgeBlock, format: Optional[str] = None) -> str:
        """Update an existing knowledge block.

        Args:
            block: Updated knowledge block.
            format: Storage format (auto-detected if None).

        Returns:
            Path to updated file.
        """
        # Auto-detect format
        if format is None:
            if (self.base_path / f"{block.id}.md").exists():
                format = "markdown"
            elif (self.base_path / f"{block.id}.json").exists():
                format = "json"
            else:
                format = "markdown"  # default

        block.updated = datetime.now(timezone.utc)
        return self.create(block, format)

    def delete(self, block_id: str) -> bool:
        """Delete a knowledge block.

        Args:
            block_id: ID of the knowledge block to delete.

        Returns:
            True if deleted, False if not found.
        """
        md_path = self.base_path / f"{block_id}.md"
        json_path = self.base_path / f"{block_id}.json"

        deleted = False
        if md_path.exists():
            md_path.unlink()
            deleted = True
        if json_path.exists():
            json_path.unlink()
            deleted = True

        return deleted

    def list_all(self) -> List[str]:
        """List all knowledge block IDs.

        Returns:
            List of block IDs.
        """
        ids = set()
        for file_path in self.base_path.iterdir():
            if file_path.suffix in [".md", ".json"]:
                ids.add(file_path.stem)
        return sorted(ids)

    def get_file_mtime(self, block_id: str) -> Optional[float]:
        """Get file modification time.

        Args:
            block_id: ID of the knowledge block.

        Returns:
            Modification time as timestamp, or None if not found.
        """
        md_path = self.base_path / f"{block_id}.md"
        json_path = self.base_path / f"{block_id}.json"

        if md_path.exists():
            return md_path.stat().st_mtime
        if json_path.exists():
            return json_path.stat().st_mtime
        return None

