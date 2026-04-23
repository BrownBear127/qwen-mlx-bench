"""
Proof-of-Concept: ChromaDB vector similarity search on macOS Apple Silicon.

Ingests 5 sentences, then runs a similarity query and returns the top-3
most similar results with their scores.

Run with:
    uv run --with chromadb python poc.py
"""

import chromadb


def main():
    # 1. Create an in-memory Chroma client (no server needed)
    client = chromadb.Client()

    # 2. Create (or get) a collection
    collection = client.get_or_create_collection(name="sentences")

    # 3. Define the sentences to ingest
    sentences = [
        "The cat sat on the mat.",
        "A dog barked at the mailman.",
        "Birds fly south for the winter.",
        "The kitten purred contentedly.",
        "Migratory species follow seasonal patterns.",
    ]
    ids = [f"doc_{i}" for i in range(len(sentences))]

    # 4. Add documents — Chroma auto-embeds them
    collection.add(documents=sentences, ids=ids)

    # 5. Query
    query = "Where do animals go when seasons change?"
    results = collection.query(query_texts=[query], n_results=3)

    # 6. Print top-3 results with similarity scores
    print(f"Query: \"{query}\"\n")
    print("Top-3 most similar sentences:\n")

    ids_list = results["ids"][0]
    docs_list = results["documents"][0]
    dists_list = results["distances"][0]

    for rank, (doc_id, doc, distance) in enumerate(
        zip(ids_list, docs_list, dists_list), start=1
    ):
        # Chroma returns cosine distance; convert to similarity (1 - distance)
        similarity = round(1.0 - distance, 4)
        print(f"  {rank}. [{similarity:.4f}] {doc}")


if __name__ == "__main__":
    main()
