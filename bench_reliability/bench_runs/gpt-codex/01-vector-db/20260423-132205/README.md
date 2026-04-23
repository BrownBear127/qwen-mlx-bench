# Vector DB POC on macOS Apple Silicon

## Library chosen

`LanceDB`

## Why this library

- It is an embedded vector database, so the POC runs locally without starting a separate service.
- The official LanceDB docs show Python vector search and `cosine` distance configuration.
- PyPI publishes a `macosx_11_0_arm64` wheel for `lancedb`, which is what makes it a good fit for Apple Silicon Macs.

To keep the demo runnable with a single `uv run --with lancedb python poc.py` command, the script uses a tiny hand-built embedding function inside `poc.py` instead of adding a second package for embeddings.

## Distance metric

This POC uses `cosine` distance in LanceDB:

- LanceDB returns `_distance` for cosine search.
- Cosine distance is `1 - cosine similarity`.
- The script prints `similarity = 1 - _distance`, so higher scores mean a closer match.

## Run

```bash
uv run --with lancedb python poc.py
```

## Expected behavior

The script ingests these five sentences into LanceDB, runs a similarity query for:

`Where do animals go when seasons change?`

and prints the top 3 matches with similarity scores.

## Sources

- LanceDB vector search docs: https://docs.lancedb.com/search/vector-search
- LanceDB search overview: https://docs.lancedb.com/search
- LanceDB PyPI package (includes macOS ARM64 wheel): https://pypi.org/project/lancedb/
