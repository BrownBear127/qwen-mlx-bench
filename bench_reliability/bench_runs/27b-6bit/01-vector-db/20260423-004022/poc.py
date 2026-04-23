"""
Minimal proof-of-concept: ingest 5 sentences into ChromaDB and run a similarity query.

Usage:
    uv run --with chromadb python poc.py
"""

import chromadb

# ── 1. Set up an in-memory ChromaDB client ──────────────────────────────────
client = chromadb.Client()

# Use cosine distance (best for text embeddings).
# ChromaDB's default is L2; we explicitly set cosine here.
collection = client.create_collection(
    name="sentences",
    metadata={"hnsw:space": "cosine"},
)

# ── 2. Define the sentences to ingest ───────────────────────────────────────
sentences = [
    "The cat sat on the mat.",
    "A dog barked at the mailman.",
    "Birds fly south for the winter.",
    "The kitten purred contentedly.",
    "Migratory species follow seasonal patterns.",
]

# ── 3. Ingest sentences (ChromaDB auto-embeds via its default onnx model) ──
collection.add(
    documents=sentences,
    ids=[f"id-{i}" for i in range(len(sentences))],
)

# ── 4. Run a similarity query ──────────────────────────────────────────────
query = "Where do animals go when seasons change?"

results = collection.query(
    query_texts=[query],
    n_results=3,
)

# ── 5. Print top-3 results with similarity scores ──────────────────────────
print(f"Query: \"{query}\"\n")
print("Top-3 most similar sentences:\n")

docs = results["documents"][0]
distances = results["distances"][0]

for rank, (doc, distance) in enumerate(zip(docs, distances), start=1):
    # ChromaDB returns distance (lower = more similar).
    # Convert to a 0-1 similarity score for readability.
    similarity = 1.0 - distance
    print(f"  {rank}. [{similarity:.4f}] {doc}")
