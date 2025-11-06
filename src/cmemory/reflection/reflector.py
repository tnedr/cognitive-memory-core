"""Reflector class for LLM-based reflection on knowledge blocks."""

import logging
from pathlib import Path
from typing import List, Optional

from cmemory.models import GraphRelationship, KnowledgeBlock

logger = logging.getLogger(__name__)

# Try to import Jinja2 Template
try:
    from jinja2 import Template
except ImportError:
    Template = None


class Reflector:
    """Generates insights about knowledge blocks using LLM."""

    def __init__(
        self,
        llm=None,
        template_path: Optional[str] = None,
    ):
        """Initialize the Reflector.

        Args:
            llm: LangChain chat model instance (e.g., ChatOpenAI, ChatOllama).
            template_path: Path to Jinja2 prompt template file.
        """
        self.llm = llm
        self.template_path = template_path or str(Path(__file__).parent.parent.parent.parent / "templates" / "reflect.jinja")

    def _load_template(self) -> str:
        """Load the reflection prompt template.

        Returns:
            Template content as string.
        """
        template_file = Path(self.template_path)
        if template_file.exists():
            return template_file.read_text(encoding="utf-8")
        # Fallback template
        return """You are analyzing knowledge blocks to identify relationships and generate insights.

Knowledge blocks:
{% for block in blocks %}
- [{{ block.id }}] {{ block.title }}: {{ block.content[:200] }}...
{% endfor %}

Generate 3-4 sentences of insights about:
1. How these blocks relate to each other
2. What patterns or themes emerge
3. Potential connections or relationships

Insights:"""

    def _format_prompt(self, blocks: List[KnowledgeBlock]) -> str:
        """Format the prompt with block information.

        Args:
            blocks: List of knowledge blocks to reflect on.

        Returns:
            Formatted prompt string.
        """
        if Template is None:
            # Fallback if jinja2 not available
            logger.warning("jinja2 not available, using simple template")
            prompt = "Analyze these knowledge blocks:\n\n"
            for block in blocks:
                prompt += f"- [{block.id}] {block.title}: {block.content[:200]}...\n"
            prompt += "\nGenerate insights about relationships and patterns."
            return prompt

        template_content = self._load_template()
        template = Template(template_content)
        return template.render(blocks=blocks)

    async def reflect_async(self, blocks: List[KnowledgeBlock]) -> List[GraphRelationship]:
        """Generate reflection insights asynchronously.

        Args:
            blocks: List of knowledge blocks to reflect on.

        Returns:
            List of suggested GraphRelationship objects.
        """
        if not self.llm:
            logger.warning("No LLM configured, returning empty relationships")
            return []

        prompt = self._format_prompt(blocks)

        try:
            # Use LangChain's async invoke
            response = await self.llm.ainvoke(prompt)
            insights = response.content if hasattr(response, "content") else str(response)

            # Parse insights to extract relationships
            # This is a simplified version - in production, use structured output
            relationships = self._parse_insights(insights, blocks)
            logger.info(f"Generated {len(relationships)} relationships from reflection")
            return relationships
        except Exception as e:
            logger.error(f"Reflection failed: {e}")
            return []

    def reflect(self, blocks: List[KnowledgeBlock]) -> List[GraphRelationship]:
        """Generate reflection insights synchronously.

        Args:
            blocks: List of knowledge blocks to reflect on.

        Returns:
            List of suggested GraphRelationship objects.
        """
        if not self.llm:
            logger.warning("No LLM configured, returning empty relationships")
            return []

        prompt = self._format_prompt(blocks)

        try:
            # Use LangChain's sync invoke
            response = self.llm.invoke(prompt)
            insights = response.content if hasattr(response, "content") else str(response)

            # Parse insights to extract relationships
            relationships = self._parse_insights(insights, blocks)
            logger.info(f"Generated {len(relationships)} relationships from reflection")
            return relationships
        except Exception as e:
            logger.error(f"Reflection failed: {e}")
            return []

    def _parse_insights(self, insights: str, blocks: List[KnowledgeBlock]) -> List[GraphRelationship]:
        """Parse LLM insights into relationship suggestions.

        This is a simplified parser. In production, use structured output or
        a more sophisticated parsing strategy.

        Args:
            insights: LLM-generated insights text.
            blocks: Original knowledge blocks.

        Returns:
            List of suggested GraphRelationship objects.
        """
        relationships = []

        # Simple heuristic: if blocks are mentioned together in insights,
        # suggest a relationship
        block_ids = {block.id for block in blocks}
        insights_lower = insights.lower()

        # Check for pairs of blocks mentioned together
        for i, block1 in enumerate(blocks):
            for block2 in blocks[i + 1 :]:
                # Simple check: if both block titles/IDs appear in insights
                if block1.title.lower() in insights_lower and block2.title.lower() in insights_lower:
                    relationships.append(
                        GraphRelationship(
                            source_id=block1.id,
                            target_id=block2.id,
                            relationship_type="related_to",
                            properties={"source": "reflection", "confidence": 0.7},
                        )
                    )

        return relationships

