"""
Minimal proof-of-concept: ingest 5 sentences into Qdrant and run a similarity query.
"""

import uuid
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams
from sentence_transformers import SentenceTransformer

# --- Configuration ---
COLLECTION_NAME = "sentence_poc"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # 384-dim, fast, good quality

# --- Data ---
sentences = [
    "The cat sat on the mat.",
    "A dog barked at the mailman.",
    "Birds fly south for the winter.",
    "The kitten purred contentedly.",
    "Migratory species follow seasonal patterns.",
]
query = "Where do animals go when seasons change?"


def main():
    # 1. Load embedding model
    model = SentenceTransformer(EMBEDDING_MODEL)

    # 2. Start an in-memory Qdrant client (no server needed)
    client = QdrantClient(":memory:")

    # 3. Create collection with cosine distance
    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=384, distance=Distance.COSINE),
    )

    # 4. Embed and upsert sentences
    embeddings = model.encode(sentences)
    points = [
        PointStruct(
            id=idx,
            vector=emb.tolist(),
            payload={"text": text},
        )
        for idx, (text, emb) in enumerate(zip(sentences, embeddings))
    ]
    client.upsert(collection_name=COLLECTION_NAME, points=points)

    # 5. Embed query and search
    query_vec = model.encode([query])[0].tolist()
    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vec,
        limit=3,
    )

    # 6. Print top-3 results
    print(f"Query: \"{query}\"\n")
    print("Top-3 most similar sentences:\n")
    for rank, point in enumerate(results.points, 1):
        print(f"  {rank}. Score: {point.score:.4f}  |  \"{point.payload['text']}\"")


if __name__ == "__main__":
    main()
