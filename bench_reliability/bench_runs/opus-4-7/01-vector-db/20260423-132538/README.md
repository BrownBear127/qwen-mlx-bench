# Vector Database Proof-of-Concept

## Library chosen: ChromaDB

[ChromaDB](https://www.trychroma.com/) is an open-source, embedded vector database that runs natively on macOS Apple Silicon with no external services required. It was chosen because:

- **Zero infrastructure** -- runs fully in-process; no server, Docker container, or network dependency.
- **Built-in embeddings** -- ships with a default embedding function (Sentence Transformers / `all-MiniLM-L6-v2`) so no separate model download step is needed beyond the pip install.
- **Apple Silicon support** -- pure-Python + compiled extensions that work on ARM64 macOS out of the box.

## Distance metric

The collection is configured with **cosine distance** (`hnsw:space: cosine`).

ChromaDB returns cosine *distance* (0 = identical, 2 = opposite), so the script converts it to a similarity score: `similarity = 1 - distance`.

## Running

```bash
uv run --with chromadb python poc.py
```

The script prints the top-3 most similar sentences to the query *"Where do animals go when seasons change?"* along with their cosine similarity scores.
