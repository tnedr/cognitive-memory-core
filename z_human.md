


## installation

cd E:\Repos\ai_human_collab

uv pip install -e E:\Repos\cognitive-memory-core


## How to Run / Test

uv run cmemory --help
uv run cmemory digest-inflow
uv run cmemory list-blocks
uv run cmemory reindex-all
uv run cmemory search "nad"

## search
három mód van a kereséshez (alap, explain, JSON)

uv run cmemory search "nad"
uv run cmemory search "nad" --explain
uv run cmemory search "nad" --json-output
uv run cmemory search "nad boosters" --use-rrf --explain

# Explain + RRF
uv run cmemory search "nad" --use-rrf --explain

# JSON + RRF
uv run cmemory search "nad" --use-rrf --json-output

# Boost + Explain + RRF
uv run cmemory search "nad" --boost nad --use-rrf --explain

# embedding
30-80 ms pre block
100 blocks -> 8 seconds
500 blocks -> 40 seconds
- incremental indexing
- full reindexing only if embedding model change

# memory search upgrade

## Dense Vector Intelligence (OpenAI Embeddings)
- OpenAI text-embedding-3-small (or large)
- high-quality dense vectors
- representing semantic meaning as a point in 1536-D space
- Concept-based search (“What supports methylation?”)
- Fuzzy matching (“resveratrol → sirtuins → NAD”), even if the exact word doesn’t appear
- Synonyms & paraphrases detected
- Relationship inference
- Multilingual understanding
## Keyword Relevance Awareness (Sparse Scoring)
- If the keyword appears in the title → +0.2 boost
- If it appears in the content → +0.1 boost
- If a tag matches → future boost
- If metadata matches → future boost
## Semantic Filtering (Logical + Embedding Constraints)
Unlike most retrievers, your system can now apply:
- semantic inclusion (“find NAD boosters”)
- semantic relevance scoring
- keyword or tag constraints
- metadata filtering (future)
- type-based filtering (static/dynamic, future)

search("mitochondrial boosters", exclude=["test"])
will correctly:
- filter out garbage (e.g. inflow “test note”)=
- still pick relevant items

## Negative Logic (“exclude…”)
This is incredibly important for real retrieval:
- search("NAD", exclude=["lifestyle"])
- search("supplements", exclude=["resveratrol"])
- search("longevity", exclude=["exercise"])


This is similar to:
- Structured filtering in Weaviate
- not clause in Elasticsearch
- Claude’s “negative constraints” in its RAG interface
This dramatically improves precision.

## Agent-Friendly Signals

hybrid scoring + metadata + keyword boosts produce:
→ interpretable scores

Agents can reason:
If score < 0.3, mark as low-confidence.
If score > 0.8, trust strongly.
If block has boost penalties → avoid.

→ consistent ranking
No negative garbage values.

→ multi-signal relevance
Signals available to agents:
semantic score
keyword score
excluded or not
is static/dynamic
tags
metadata
vector distance (cosine)
recency
access frequency
reliability (future)
volatility (future)

Agents can combine these into reasoning and planning.

You basically created a retrieval layer compatible with multi-agent frameworks.





You just upgraded your memory system to:
- dense vector intelligence (OpenAI)
- keyword relevance awareness
- semantic filtering
- negative logic (“exclude…”)
- cosine scoring → meaningful values
- agent-friendly signals





# situation

POC


# short term plan
Következő konkrét lépések – hogy hamar sikerélményed legyen

## Ma
Docker konténerek indítása → teljes E2E teszt	Confidence boost – látszik, hogy a POC stabil
## 1-2 nap
5 saját tudásblokk ingest + autolink	Hands-on tapasztalat a tárolás-retrieval flow-val

## 1 hét
feature/llm-reflection MVP	Először látod „gondolkodni” a rendszert (insight generálás)
## 2 hét
Minimal FastAPI wrapper + /context endpoint	Agensek már HTTP-n tudnak kérni kontextust
## 3-4 hét
Decay-scheduler + watcher	Elkezd „magától” karbantartani, élő adaton

# macro roadmap
- POC
- MVP/single agent
- multi agent core
- enterprise ready
- knowledge fabric



# journal


1106 21h
elso kesz

kiadtam kell minta md file

akarja openait implementalni
