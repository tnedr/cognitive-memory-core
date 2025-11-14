"""Decay manager for applying decay policies to knowledge blocks."""

import logging
import shutil
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import List, Optional

from cmemory.models import KnowledgeBlock

logger = logging.getLogger(__name__)


class DecayManager:
    """Manages decay policies for knowledge blocks."""

    def __init__(self, knowledge_path: str, archive_path: Optional[str] = None):
        """Initialize the DecayManager.

        Args:
            knowledge_path: Base path for knowledge blocks.
            archive_path: Path for archived blocks (default: knowledge_path/archive).
        """
        self.knowledge_path = Path(knowledge_path)
        self.archive_path = Path(archive_path) if archive_path else self.knowledge_path / "archive"
        self.archive_path.mkdir(parents=True, exist_ok=True)

    def _get_last_access(self, block: KnowledgeBlock) -> datetime:
        """Get last access time from block metadata.

        Args:
            block: Knowledge block.

        Returns:
            Last access datetime, or created time if not set.
        """
        if "last_access" in block.metadata:
            access_str = block.metadata["last_access"]
            if isinstance(access_str, str):
                return datetime.fromisoformat(access_str.replace("Z", "+00:00"))
            elif isinstance(access_str, datetime):
                return access_str
        return block.created

    def _get_access_count(self, block: KnowledgeBlock) -> int:
        """Get access count from block metadata.

        Args:
            block: Knowledge block.

        Returns:
            Access count, default 0.
        """
        return block.metadata.get("access_count", 0)

    def _update_access_metadata(self, block: KnowledgeBlock) -> None:
        """Update access metadata for a block.

        Args:
            block: Knowledge block to update.
        """
        current_count = self._get_access_count(block)
        block.metadata["access_count"] = current_count + 1
        block.metadata["last_access"] = datetime.now(timezone.utc).isoformat()
        block.updated = datetime.now(timezone.utc)

    def record_access(self, block_id: str, storage) -> None:
        """Record access to a knowledge block.

        Args:
            block_id: ID of the accessed block.
            storage: FileStorage instance to update the block.
        """
        block = storage.read(block_id)
        if block:
            self._update_access_metadata(block)
            storage.update(block)

    def decay(
        self,
        storage,
        policy: str = "time",
        days_threshold: int = 180,
        usage_threshold: float = 0.01,
    ) -> List[str]:
        """Apply decay policy to knowledge blocks.

        Args:
            storage: FileStorage instance.
            policy: Decay policy ('time', 'usage', or 'both').
            days_threshold: Days since last access for time-based decay.
            usage_threshold: Minimum access count ratio for usage-based decay.

        Returns:
            List of archived block IDs.
        """
        all_ids = storage.list_all()
        if not all_ids:
            return []

        # Calculate statistics
        total_access = sum(self._get_access_count(storage.read(bid)) for bid in all_ids)
        archived = []

        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_threshold)

        for block_id in all_ids:
            block = storage.read(block_id)
            if not block:
                continue

            should_archive = False

            if policy in ["time", "both"]:
                last_access = self._get_last_access(block)
                if last_access < cutoff_date:
                    should_archive = True
                    logger.info(f"Archiving {block_id}: last accessed {last_access} (>{days_threshold} days ago)")

            if policy in ["usage", "both"] and not should_archive:
                access_count = self._get_access_count(block)
                if total_access > 0:
                    usage_ratio = access_count / total_access
                    if usage_ratio < usage_threshold:
                        should_archive = True
                        logger.info(f"Archiving {block_id}: usage ratio {usage_ratio:.2%} < {usage_threshold:.2%}")

            if should_archive:
                self._archive_block(block, storage)
                archived.append(block_id)

        logger.info(f"Decay policy '{policy}' archived {len(archived)} blocks")
        return archived

    def _archive_block(self, block: KnowledgeBlock, storage) -> None:
        """Archive a knowledge block.

        Args:
            block: Knowledge block to archive.
            storage: FileStorage instance.
        """
        # Find source file
        md_path = storage.base_path / f"{block.id}.md"
        json_path = storage.base_path / f"{block.id}.json"

        source_path = None
        if md_path.exists():
            source_path = md_path
        elif json_path.exists():
            source_path = json_path

        if source_path:
            # Copy to archive
            archive_file = self.archive_path / source_path.name
            shutil.copy2(source_path, archive_file)

            # Delete original
            source_path.unlink()
            logger.info(f"Archived {block.id} to {archive_file}")

    def restore(self, block_id: str, storage) -> bool:
        """Restore an archived block.

        Args:
            block_id: ID of block to restore.
            storage: FileStorage instance.

        Returns:
            True if restored, False otherwise.
        """
        # Look for archived file
        md_archive = self.archive_path / f"{block_id}.md"
        json_archive = self.archive_path / f"{block_id}.json"

        source_path = None
        if md_archive.exists():
            source_path = md_archive
        elif json_archive.exists():
            source_path = json_archive

        if source_path:
            # Copy back to knowledge directory
            restore_path = storage.base_path / source_path.name
            shutil.copy2(source_path, restore_path)
            logger.info(f"Restored {block_id} from archive")
            return True

        return False

