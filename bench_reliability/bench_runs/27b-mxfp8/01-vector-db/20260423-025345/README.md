# Vector Database Proof-of-Concept

## Library Chosen: Qdrant

**Qdrant** is a vector similarity search engine and vector database. It is chosen because:

- **Native Apple Silicon support** — Qdrant provides pre-built binaries for `aarch64-darwin` (macOS on M1/M2/M3/M4 chips).
- **In-memory mode** — The Python client supports `:memory:` mode, so no server installation is needed for a quick POC.
- **Simple API** — Create collections, upsert points, and query with just a few lines of code.
- **Production-ready** — Beyond POCs, Qdrant scales to billions of vectors with filtering, pagination, and distributed deployment.

## Embedding Model

Sentences are embedded using `sentence-transformers` with the `all-MiniLM-L6-v2` model (384-dimensional vectors). This model is small, fast, and provides strong semantic similarity results.

## Distance Metric

**Cosine similarity** is used as the distance metric. Cosine similarity measures the angle between two vectors, returning a value between 0 and 1 (where 1 means identical direction/perfect similarity). It is well-suited for text embeddings because it is invariant to vector magnitude and focuses purely on directional similarity.

## How to Run

```bash
# Install dependencies
pip install -r requirements.txt

# Run the POC
uv run --with qdrant-client --with sentence-transformers python poc.py
```

## Expected Output

The query *"Where do animals go when seasons change?"* should return the top-3 most similar sentences, with the most relevant being:

1. "Migratory species follow seasonal patterns." (highest score)
2. "Birds fly south for the winter."
3. One of the remaining sentences (lowest score)
