from __future__ import annotations

import math
import os
import re
import shutil
from pathlib import Path

import lancedb

SENTENCES = [
    "The cat sat on the mat.",
    "A dog barked at the mailman.",
    "Birds fly south for the winter.",
    "The kitten purred contentedly.",
    "Migratory species follow seasonal patterns.",
]

QUERY = "Where do animals go when seasons change?"

# Tiny hand-built concept vectors keep the POC to a single third-party package.
LEXICON = {
    "animals": [0.1, 0.1, 0.1, 0.2, 0.0, 0.0, 0.0, 0.0, 1.0],
    "barked": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.1, 0.8, 0.1],
    "bird": [0.0, 0.0, 1.0, 0.4, 0.0, 0.5, 0.0, 0.0, 1.0],
    "birds": [0.0, 0.0, 1.0, 0.4, 0.0, 0.5, 0.0, 0.0, 1.0],
    "cat": [1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.8, 0.0, 1.0],
    "change": [0.0, 0.0, 0.0, 0.6, 0.8, 0.0, 0.0, 0.0, 0.0],
    "contentedly": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.1, 0.6, 0.0],
    "dog": [0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.8, 0.0, 1.0],
    "fly": [0.0, 0.0, 0.2, 0.5, 0.0, 1.0, 0.0, 0.0, 0.0],
    "follow": [0.0, 0.0, 0.0, 0.3, 0.0, 0.2, 0.0, 0.0, 0.0],
    "go": [0.0, 0.0, 0.0, 0.6, 0.0, 1.0, 0.0, 0.0, 0.0],
    "kitten": [1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.8, 0.4, 1.0],
    "migratory": [0.0, 0.0, 0.5, 1.0, 0.7, 0.5, 0.0, 0.0, 1.0],
    "patterns": [0.0, 0.0, 0.0, 0.5, 0.5, 0.0, 0.0, 0.0, 0.0],
    "purred": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.2, 1.0, 0.2],
    "seasonal": [0.0, 0.0, 0.0, 0.8, 1.0, 0.0, 0.0, 0.0, 0.0],
    "seasons": [0.0, 0.0, 0.0, 0.7, 1.0, 0.0, 0.0, 0.0, 0.0],
    "south": [0.0, 0.0, 0.0, 0.8, 0.0, 0.8, 0.0, 0.0, 0.0],
    "species": [0.0, 0.0, 0.0, 0.2, 0.0, 0.0, 0.0, 0.0, 1.0],
    "winter": [0.0, 0.0, 0.0, 0.6, 1.0, 0.0, 0.0, 0.0, 0.0],
}


def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z']+", text.lower())


def embed_text(text: str) -> list[float]:
    vector = [0.0] * len(next(iter(LEXICON.values())))
    hits = 0

    for token in tokenize(text):
        if token not in LEXICON:
            continue
        hits += 1
        for index, value in enumerate(LEXICON[token]):
            vector[index] += value

    if hits == 0:
        raise ValueError(f"No embedding terms found for: {text!r}")

    norm = math.sqrt(sum(value * value for value in vector))
    return [value / norm for value in vector]


def build_rows() -> list[dict[str, object]]:
    return [
        {"id": index, "text": sentence, "vector": embed_text(sentence)}
        for index, sentence in enumerate(SENTENCES, start=1)
    ]


def similarity_from_cosine_distance(distance: float) -> float:
    return 1.0 - distance


class SuppressStderr:
    def __enter__(self) -> None:
        self.saved_stderr_fd = os.dup(2)
        self.devnull_fd = os.open(os.devnull, os.O_WRONLY)
        os.dup2(self.devnull_fd, 2)

    def __exit__(self, exc_type, exc, tb) -> None:
        os.dup2(self.saved_stderr_fd, 2)
        os.close(self.saved_stderr_fd)
        os.close(self.devnull_fd)


def main() -> None:
    db_path = Path(__file__).with_name(".poc_lancedb")
    if db_path.exists():
        shutil.rmtree(db_path)

    db = lancedb.connect(str(db_path))
    with SuppressStderr():
        table = db.create_table("sentences", data=build_rows(), mode="overwrite")

    results = (
        table.search(embed_text(QUERY))
        .distance_type("cosine")
        .limit(3)
        .to_list()
    )

    print(f"Query: {QUERY}")
    print("Top 3 most similar sentences:")
    for rank, row in enumerate(results, start=1):
        similarity = similarity_from_cosine_distance(float(row["_distance"]))
        print(f"{rank}. {similarity:.4f} | {row['text']}")


if __name__ == "__main__":
    main()
