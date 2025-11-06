# Reflector Module

The Reflector module provides LLM-based reflection capabilities for generating insights about knowledge blocks and their relationships.

## Overview

The `Reflector` class uses LangChain to analyze knowledge blocks and generate:
- Relationship suggestions between blocks
- Pattern identification
- Connection insights
- Summary generation

## Usage

### Basic Setup

```python
from cmemory import MemorySystem
from langchain.chat_models import ChatOpenAI

# Initialize with LLM
llm = ChatOpenAI(model="gpt-4", temperature=0.7)
memory = MemorySystem(llm=llm)

# Reflect on a block
memory.reflect("KB-001")
```

### Standalone Reflector

```python
from cmemory.reflection import Reflector
from langchain.chat_models import ChatOpenAI

llm = ChatOpenAI()
reflector = Reflector(llm=llm)

blocks = [block1, block2, block3]
relationships = reflector.reflect(blocks)
```

## Prompt Template

The reflection uses a Jinja2 template located at `templates/reflect.jinja`. The template includes:

- Block metadata (ID, title, tags)
- Block content (truncated to 500 chars)
- Analysis instructions
- Output format specification

## Configuration

### Custom Template

```python
reflector = Reflector(
    llm=llm,
    template_path="custom/path/reflect.jinja"
)
```

### Async Reflection

```python
relationships = await reflector.reflect_async(blocks)
```

## Integration with MemorySystem

When `MemorySystem` is initialized with an LLM:

1. `reflect()` finds related blocks (graph traversal)
2. Collects top 5 related blocks
3. Calls `Reflector.reflect()` with the block set
4. Automatically adds suggested relationships to the graph

## Error Handling

- If LLM is not configured, reflection returns empty list
- If LLM call fails, error is logged and empty list returned
- Template parsing errors fall back to simple text template

## Testing

Unit tests use mocked LLM to avoid API calls:

```python
from unittest.mock import MagicMock

mock_llm = MagicMock()
mock_llm.invoke.return_value = MagicMock(content="...")
reflector = Reflector(llm=mock_llm)
```

## Future Enhancements

- Structured output parsing (JSON schema)
- Confidence scoring for relationships
- Multi-model support (ensemble reflection)
- Caching of reflection results

