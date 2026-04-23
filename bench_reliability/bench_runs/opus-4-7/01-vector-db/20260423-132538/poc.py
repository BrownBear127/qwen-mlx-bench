"""Minimal vector-database proof-of-concept using ChromaDB."""

import chromadb

# --- Ingest ---
client = chromadb.Client()
collection = client.create_collection(
    name="sentences",
    metadata={"hnsw:space": "cosine"},  # cosine distance
)

sentences = [
    "The cat sat on the mat.",
    "A dog barked at the mailman.",
    "Birds fly south for the winter.",
    "The kitten purred contentedly.",
    "Migratory species follow seasonal patterns.",
]

collection.add(
    documents=sentences,
    ids=[f"s{i}" for i in range(len(sentences))],
)

# --- Query ---
query = "Where do animals go when seasons change?"
results = collection.query(query_texts=[query], n_results=3)

print(f"Query: {query!r}\n")
print("Top-3 most similar sentences:")
for rank, (doc, dist) in enumerate(
    zip(results["documents"][0], results["distances"][0]), start=1
):
    similarity = 1 - dist  # ChromaDB returns cosine *distance*; similarity = 1 - distance
    print(f"  {rank}. (similarity={similarity:.4f}) {doc}")
