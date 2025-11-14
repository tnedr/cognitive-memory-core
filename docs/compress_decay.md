# Compression and Decay

## Compression

The `Compressor` class provides token-aware summarization of multiple knowledge blocks.

### Features

- **Token Counting**: Uses tiktoken for accurate token counting
- **LLM-based Compression**: LangChain map-reduce strategy for intelligent summarization
- **Fallback Mode**: Truncation when LLM unavailable
- **Strict Token Limits**: Never exceeds max_tokens parameter

### Usage

```python
from cmemory import MemorySystem
from langchain.chat_models import ChatOpenAI

llm = ChatOpenAI()
memory = MemorySystem(llm=llm)

# Compress multiple blocks
block_ids = ["KB-001", "KB-002", "KB-003"]
summary = memory.compress(block_ids, max_tokens=2000)
```

### How It Works

1. **Token Calculation**: Counts tokens in all blocks
2. **Within Limit**: Returns concatenated content if under limit
3. **Over Limit**: Uses LLM map-reduce:
   - **Map**: Summarize each block individually
   - **Reduce**: Combine summaries into final compressed version
4. **Verification**: Ensures output doesn't exceed max_tokens

## Decay

The `DecayManager` class manages knowledge block lifecycle through archival.

### Policies

#### Time-based Decay

Archives blocks not accessed within a threshold (default: 180 days).

```python
# Archive blocks not accessed in 180 days
archived = memory.decay(policy="time", days_threshold=180)
```

#### Usage-based Decay

Archives blocks with low access ratio (default: < 1%).

```python
# Archive blocks with usage < 1%
archived = memory.decay(policy="usage", usage_threshold=0.01)
```

#### Combined Policy

```python
# Archive if either condition met
archived = memory.decay(policy="both", days_threshold=180, usage_threshold=0.01)
```

### Access Tracking

Blocks automatically track:
- `access_count`: Number of times accessed
- `last_access`: ISO timestamp of last access

Access is recorded when:
- Block is retrieved via `retrieve()`
- Block is read via `file_storage.read()`

### Archival

- Blocks are moved to `archive/` subdirectory
- Original files are deleted
- Metadata preserved for restoration

### Restoration

```python
# Restore an archived block
restored = memory.decay_manager.restore("KB-001", memory.file_storage)
```

## Scheduler Integration

Use APScheduler for automatic decay:

```python
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()
scheduler.add_job(
    memory.decay,
    trigger="cron",
    day_of_week="sun",
    hour=2,
    args=["time"],
    kwargs={"days_threshold": 180}
)
scheduler.start()
```

## Best Practices

1. **Compression**: Use for context materialization when token limits matter
2. **Decay**: Run weekly/monthly to maintain knowledge base size
3. **Restoration**: Review archived blocks before permanent deletion
4. **Access Tracking**: Ensure `retrieve()` is used for proper tracking

