# Vector Database Proof-of-Concept

## Library Chosen: **ChromaDB**

### Why ChromaDB?

- **Lightweight & in-process** — no separate server or Docker container needed. Everything runs in-memory (or optionally persisted to disk).
- **macOS Apple Silicon support** — works natively on ARM64 Macs. The underlying embedding model (`all-MiniLM-L6-v2`) runs on CPU or can leverage the MPS (Metal Performance Shaders) backend for GPU acceleration.
- **Simple API** — just four core functions (`create_collection`, `add`, `query`, `get`), making it ideal for quick prototyping.
- **Built-in embeddings** — ships with `SentenceTransformersEmbeddingFunction` so you don't need a separate embedding service.
- **Open-source & Apache 2.0 licensed**.

### Distance Metric

ChromaDB uses **L2 (Euclidean) distance** by default. The `query()` method returns the raw L2 distance between the query embedding and each document embedding. In this POC, we convert that distance to a similarity score using `1 / (1 + distance)` so that higher values indicate greater similarity.

### How to Run

```bash
uv run --with chromadb python poc.py
```

### Files

| File | Description |
|------|-------------|
| `poc.py` | The proof-of-concept script |
| `requirements.txt` | Python dependencies (one per line) |

### What the POC Does

1. Creates an in-memory ChromaDB collection.
2. Ingests 5 animal-related sentences with auto-generated embeddings.
3. Runs a similarity query against the sentence *"Where do animals go when seasons change?"*.
4. Prints the top-3 most similar sentences along with their distance and similarity scores.
