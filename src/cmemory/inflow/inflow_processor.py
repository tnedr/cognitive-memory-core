"""Simple local inflow processor for ingesting .txt and .md files."""

import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import List

from cmemory.memory import MemorySystem


class InflowProcessor:
    """
    Simple local inflow processor for ingesting `.txt` and `.md` files.
    """

    def __init__(self, inflow_path: str = "inflow", memory: MemorySystem = None):
        self.inflow_path = Path(inflow_path)
        self.processed_path = self.inflow_path / "processed"
        self.inflow_path.mkdir(parents=True, exist_ok=True)
        self.processed_path.mkdir(parents=True, exist_ok=True)
        self.memory = memory or MemorySystem()

    def scan(self) -> List[Path]:
        """Return list of .txt and .md files in inflow folder."""
        return [
            p
            for p in self.inflow_path.iterdir()
            if p.is_file() and p.suffix.lower() in {".txt", ".md"}
        ]

    def _generate_block_id(self, filename: str) -> str:
        ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        return f"INFLOW-{ts}-{filename.replace('.', '-')}"  # safe deterministic ID

    def process_file(self, path: Path) -> str:
        """Process a single file → KnowledgeBlock, move file → processed/."""
        text = path.read_text(encoding="utf-8")
        block_id = self._generate_block_id(path.stem)
        title = path.stem.replace("_", " ").replace("-", " ").title()

        metadata = {
            "id": block_id,
            "title": title,
            "tags": ["inflow"],
            "source_file": str(path.name),
        }

        # Create & encode via MemorySystem
        new_id = self.memory.record(text, metadata)
        self.memory.encode(new_id)

        # Move file to processed folder
        dest = self.processed_path / path.name
        shutil.move(str(path), str(dest))

        return new_id

    def digest(self) -> List[str]:
        """Process all inflow files and return list of KnowledgeBlock IDs."""
        files = self.scan()
        results = []
        for f in files:
            block_id = self.process_file(f)
            results.append(block_id)
        return results

