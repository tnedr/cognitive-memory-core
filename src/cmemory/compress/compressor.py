"""Compressor class for token-aware RAG summarization."""

import logging
from typing import List, Optional

from cmemory.models import KnowledgeBlock

logger = logging.getLogger(__name__)


def _count_tokens(text: str, model: str = "gpt-3.5-turbo") -> int:
    """Count tokens in text using tiktoken.

    Args:
        text: Text to count tokens for.
        model: Model name for tokenizer.

    Returns:
        Number of tokens.
    """
    try:
        import tiktoken

        encoding = tiktoken.encoding_for_model(model)
        return len(encoding.encode(text))
    except ImportError:
        # Fallback: rough estimate (1 token ≈ 4 characters)
        logger.warning("tiktoken not available, using character-based estimation")
        return len(text) // 4
    except Exception as e:
        logger.warning(f"Token counting failed: {e}, using fallback")
        return len(text) // 4


class Compressor:
    """Compresses multiple knowledge blocks into summaries with token limits."""

    def __init__(self, llm=None, max_tokens: int = 4096):
        """Initialize the Compressor.

        Args:
            llm: LangChain chat model instance (optional).
            max_tokens: Maximum tokens for compressed output.
        """
        self.llm = llm
        self.max_tokens = max_tokens

    def compress(self, blocks: List[KnowledgeBlock], max_tokens: Optional[int] = None) -> str:
        """Compress multiple knowledge blocks into a single summary.

        Args:
            blocks: List of knowledge blocks to compress.
            max_tokens: Maximum tokens (overrides instance default).

        Returns:
            Compressed summary text.
        """
        if not blocks:
            return ""

        max_tokens = max_tokens or self.max_tokens

        # Calculate total tokens
        total_content = "\n\n".join([f"## {b.title}\n\n{b.content}" for b in blocks])
        total_tokens = _count_tokens(total_content)

        # If within limit, return simple concatenation
        if total_tokens <= max_tokens:
            return total_content

        # Need to compress - use LLM if available
        if self.llm:
            return self._compress_with_llm(blocks, max_tokens)
        else:
            # Fallback: truncate and concatenate
            logger.warning("No LLM available, using truncation fallback")
            return self._compress_truncate(blocks, max_tokens)

    def _compress_with_llm(self, blocks: List[KnowledgeBlock], max_tokens: int) -> str:
        """Compress using LLM with map-reduce strategy.

        Args:
            blocks: Knowledge blocks to compress.
            max_tokens: Maximum tokens for output.

        Returns:
            Compressed summary.
        """
        try:
            from langchain.chains import MapReduceDocumentsChain
            from langchain.chains.combine_documents.stuff import StuffDocumentsChain
            from langchain.chains.llm import LLMChain
            from langchain.prompts import PromptTemplate

            # Map step: summarize each block
            map_template = """Summarize the following knowledge block in 2-3 sentences, preserving key information:

{content}

Summary:"""
            map_prompt = PromptTemplate.from_template(map_template)
            map_chain = LLMChain(llm=self.llm, prompt=map_prompt)

            # Reduce step: combine summaries
            reduce_template = """Combine the following summaries into a coherent summary of approximately {max_tokens} tokens:

{summaries}

Combined summary:"""
            reduce_prompt = PromptTemplate.from_template(reduce_template)
            reduce_chain = LLMChain(llm=self.llm, prompt=reduce_prompt)
            combine_documents_chain = StuffDocumentsChain(
                llm_chain=reduce_chain, document_variable_name="summaries"
            )

            # Create map-reduce chain
            map_reduce_chain = MapReduceDocumentsChain(
                llm_chain=map_chain,
                combine_document_chain=combine_documents_chain,
                document_variable_name="content",
            )

            # Convert blocks to documents
            from langchain.schema import Document

            documents = [Document(page_content=b.content, metadata={"title": b.title}) for b in blocks]

            # Run compression
            result = map_reduce_chain.run(documents)
            summary = result if isinstance(result, str) else str(result)

            # Verify token count
            summary_tokens = _count_tokens(summary)
            if summary_tokens > max_tokens:
                logger.warning(f"Compressed summary ({summary_tokens} tokens) exceeds limit ({max_tokens})")
                # Truncate if needed
                summary = self._truncate_to_tokens(summary, max_tokens)

            return summary
        except ImportError:
            logger.warning("LangChain map-reduce not available, using fallback")
            return self._compress_truncate(blocks, max_tokens)
        except Exception as e:
            logger.error(f"LLM compression failed: {e}")
            return self._compress_truncate(blocks, max_tokens)

    def _compress_truncate(self, blocks: List[KnowledgeBlock], max_tokens: int) -> str:
        """Fallback compression by truncation.

        Args:
            blocks: Knowledge blocks to compress.
            max_tokens: Maximum tokens.

        Returns:
            Truncated summary.
        """
        parts = []
        current_tokens = 0

        for block in blocks:
            block_text = f"## {block.title}\n\n{block.content[:200]}...\n\n"
            block_tokens = _count_tokens(block_text)

            if current_tokens + block_tokens > max_tokens:
                break

            parts.append(block_text)
            current_tokens += block_tokens

        return "\n".join(parts)

    def _truncate_to_tokens(self, text: str, max_tokens: int) -> str:
        """Truncate text to fit within token limit.

        Args:
            text: Text to truncate.
            max_tokens: Maximum tokens.

        Returns:
            Truncated text.
        """
        current_tokens = _count_tokens(text)
        if current_tokens <= max_tokens:
            return text

        # Binary search for truncation point
        ratio = max_tokens / current_tokens
        target_length = int(len(text) * ratio * 0.9)  # 90% to be safe

        truncated = text[:target_length]
        while _count_tokens(truncated) > max_tokens and target_length > 0:
            target_length = int(target_length * 0.9)
            truncated = text[:target_length]

        return truncated + "... [truncated]"

