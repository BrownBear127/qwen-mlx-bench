"""
Minimal proof-of-concept: ChromaDB vector similarity search.

Ingests 5 sentences, then queries for the top-3 most similar to a
given query sentence.  Runs entirely in-memory on macOS Apple Silicon.
"""

import chromadb


def main() -> None:
    # 1. Create an in-memory Chroma client (no server needed)
    client = chromadb.Client()

    # 2. Create (or get) a collection
    collection = client.get_or_create_collection(name="sentences")

    # 3. Sentences to ingest
    sentences = [
        "The cat sat on the mat.",
        "A dog barked at the mailman.",
        "Birds fly south for the winter.",
        "The kitten purred contentedly.",
        "Migratory species follow seasonal patterns.",
    ]
    ids = [f"id{i}" for i in range(1, len(sentences) + 1)]

    # 4. Add documents — Chroma auto-embeds them
    collection.upsert(documents=sentences, ids=ids)

    # 5. Query
    query = "Where do animals go when seasons change?"
    results = collection.query(query_texts=[query], n_results=3)

    # 6. Print top-3 results with similarity scores
    print(f"Query: \"{query}\"\n")
    print("Top-3 most similar sentences:\n")

    docs = results["documents"][0]
    distances = results["distances"][0]

    for rank, (doc, dist) in enumerate(zip(docs, distances), start=1):
        # Chroma returns cosine distance; convert to similarity (1 - distance)
        similarity = 1.0 - dist
        print(f"  {rank}. [{similarity:.4f}] {doc}")


if __name__ == "__main__":
    main()
