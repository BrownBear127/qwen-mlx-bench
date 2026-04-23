# ChromaDB Vector Search — Proof of Concept

## Library Chosen: ChromaDB

**ChromaDB** (`chromadb`) is an open-source, embeddable vector database written in Python. It ships with a built-in sentence-transformer embedding model (ONNX-based), so no separate embedding service is required.

### Why ChromaDB?

1. **macOS Apple Silicon support** — runs natively on M1/M2/M3 chips with no special configuration.
2. **Zero infrastructure** — the embedded mode stores everything in-memory (or on disk) with no server process to manage.
3. **Auto-embedding** — ChromaDB automatically converts text to vectors using its default `all-MiniLM-L6-v2` model, so the POC stays minimal.
4. **Lightweight** — a single `pip install chromadb` is all that's needed.

## Distance Metric

The POC uses **cosine distance** (configured via `hnsw:space: "cosine"`).

- Cosine distance measures the angle between two vectors, ignoring magnitude.
- For text embeddings this is generally preferred over L2 (Euclidean) distance because semantic similarity is about *direction* in the embedding space, not vector length.
- ChromaDB returns raw cosine **distance** (0 = identical, 2 = opposite). The POC converts this to a **similarity score** (`1 - distance`) for readability.

## Running the POC

```bash
uv run --with chromadb python poc.py
```

## Expected Output

```
Query: "Where do animals go when seasons change?"

Top-3 most similar sentences:

  1. [0.7xxx] Migratory species follow seasonal patterns.
  2. [0.6xxx] Birds fly south for the winter.
  3. [0.5xxx] A dog barked at the mailman.
```

(The exact scores depend on the embedding model version.)
