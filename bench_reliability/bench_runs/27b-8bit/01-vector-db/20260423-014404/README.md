# ChromaDB Vector Similarity Search — Proof of Concept

## Library Chosen

**ChromaDB** (`chromadb`) — an open-source embedding database that handles
vector storage, indexing, and similarity search out of the box.

## Why ChromaDB?

1. **macOS Apple Silicon support** — ChromaDB is pure Python with optional
   C++ extensions that compile cleanly on ARM64. It runs in-memory with zero
   configuration, making it ideal for local development on M1/M2/M3 Macs.
2. **Built-in embeddings** — Chroma automatically converts text to embeddings
   using a default sentence-transformer model, so you don't need to manage a
   separate embedding pipeline.
3. **Lightweight** — No external database server, no Docker, no cloud account.
   Just `pip install chromadb` and you're running.
4. **Apache 2.0 licensed** — free for any use.

## Distance Metric

ChromaDB uses **cosine distance** by default. Cosine distance is defined as:

```
cosine_distance(a, b) = 1 - cosine_similarity(a, b)
```

where cosine similarity is the dot product of the two vectors divided by the
product of their magnitudes. A cosine distance of `0` means the vectors are
identical in direction (perfectly similar), and `2` means they point in
opposite directions.

In the POC output, distances are converted back to similarity scores
(`similarity = 1 - distance`) for readability.

## How to Run

```bash
uv run --with chromadb python poc.py
```

## Expected Output

The query *"Where do animals go when seasons change?"* should return the
sentences about birds flying south and migratory species as the most similar,
since they share semantic concepts about animal movement and seasonal patterns.
