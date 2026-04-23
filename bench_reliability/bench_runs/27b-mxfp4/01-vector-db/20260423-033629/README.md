# ChromaDB Proof-of-Concept

## Library Chosen: ChromaDB

**ChromaDB** is an open-source (Apache 2.0) vector database designed as
"the data infrastructure for AI." It provides a simple Python SDK for storing,
indexing, and querying embeddings.

### Why ChromaDB?

1. **macOS Apple Silicon support** — ChromaDB runs natively on macOS (including
   M1/M2/M3 chips). It uses a lightweight in-memory mode by default, requiring
   no external server or Docker container.
2. **Zero-configuration** — `chromadb.Client()` creates an in-memory database
   instantly. No setup, no API keys, no cloud account needed.
3. **Built-in embeddings** — Chroma automatically tokenizes, embeds, and indexes
   text using a default sentence-transformer model. You don't need to manage
   separate embedding pipelines.
4. **Small dependency footprint** — A single `pip install chromadb` is all that's
   required.

## Distance Metric

ChromaDB uses **cosine distance** as its default similarity metric. Cosine
distance measures the angle between two vectors in embedding space:

- **Cosine distance** = 1 − cosine similarity
- Range: 0 (identical direction) to 2 (opposite direction)
- In this POC, the raw distance is converted back to a similarity score via
  `similarity = 1 − distance`, yielding values in the range [0, 1] where
  higher is more similar.

## Running the POC

```bash
uv run --with chromadb python poc.py
```

This will ingest the 5 sentences, run the query
*"Where do animals go when seasons change?"*, and print the top-3 most
similar sentences with their similarity scores.
