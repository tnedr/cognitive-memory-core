"""Data models and DTOs for the memory system."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


@dataclass
class KnowledgeBlock:
    """Represents a knowledge block with metadata."""

    id: str
    title: str
    content: str
    tags: List[str] = field(default_factory=list)
    created: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = field(default_factory=dict)
    content_hash: Optional[str] = None
    information_type: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "tags": self.tags,
            "created": self.created.isoformat(),
            "updated": self.updated.isoformat(),
            "metadata": self.metadata,
            "content_hash": self.content_hash,
            "information_type": self.information_type,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "KnowledgeBlock":
        """Create from dictionary."""
        return cls(
            id=data["id"],
            title=data["title"],
            content=data["content"],
            tags=data.get("tags", []),
            created=datetime.fromisoformat(data.get("created", datetime.now(timezone.utc).isoformat())),
            updated=datetime.fromisoformat(data.get("updated", datetime.now(timezone.utc).isoformat())),
            metadata=data.get("metadata", {}),
            content_hash=data.get("content_hash"),
            information_type=data.get("information_type"),
        )


@dataclass
class GraphNode:
    """Represents a node in the knowledge graph."""

    id: str
    label: str
    properties: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GraphRelationship:
    """Represents a relationship in the knowledge graph."""

    source_id: str
    target_id: str
    relationship_type: str
    properties: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SearchResult:
    """Represents a search result with relevance score."""

    block_id: str
    score: float
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    semantic_score: float = 0.0
    keyword_score: float = 0.0
    explanation: Dict[str, Any] = field(default_factory=dict)

