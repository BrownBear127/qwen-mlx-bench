"""
Minimal proof-of-concept: ingest 5 sentences into ChromaDB and run a
similarity query, returning the top-3 most similar results.
"""

import chromadb
from chromadb.utils import embedding_functions

# ---------------------------------------------------------------------------
# 1. Set up an in-memory Chroma client with a built-in embedding function
# ---------------------------------------------------------------------------
client = chromadb.Client()

# SentenceTransformersEmbeddingFunction uses the all-MiniLM-L6-v2 model
# (small, fast, and works great on Apple Silicon via MPS/CPU).
embedding_func = embedding_functions.SentenceTransformersEmbeddingFunction(
    model_name="all-MiniLM-L6-v2",
)

# ---------------------------------------------------------------------------
# 2. Create a collection and ingest the 5 sentences
# ---------------------------------------------------------------------------
collection = client.create_collection(
    name="animal_sentences",
    embedding_function=embedding_func,
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
    ids=[f"doc_{i}" for i in range(len(sentences))],
)

# ---------------------------------------------------------------------------
# 3. Run a similarity query
# ---------------------------------------------------------------------------
query = "Where do animals go when seasons change?"

results = collection.query(
    query_texts=[query],
    n_results=3,
)

# ---------------------------------------------------------------------------
# 4. Print the top-3 results with their distance/similarity scores
# ---------------------------------------------------------------------------
print(f"Query: \"{query}\"\n")
print("Top-3 most similar sentences:\n")

for i, (doc, dist) in enumerate(zip(results["documents"][0], results["distances"][0]), 1):
    # Chroma returns *distance* (L2 / Euclidean by default).
    # Convert to a similarity score (1 / (1 + distance)) for readability.
    similarity = 1.0 / (1.0 + dist)
    print(f"  {i}. \"{doc}\"")
    print(f"     Distance: {dist:.4f}  |  Similarity score: {similarity:.4f}")
