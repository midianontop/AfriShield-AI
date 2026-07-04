import json
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# =========================
# Load data
# =========================

with open(r"documents\chunks.json", "r", encoding="utf-8") as f:
    chunks = json.load(f)

print(f"\nLoaded {len(chunks)} chunks.")

# =========================
# Load model
# =========================

print("Loading embedding model...")
model = SentenceTransformer("all-MiniLM-L6-v2")

# =========================
# Generate chunk embeddings
# =========================

print("Generating embeddings...")
chunk_embeddings = model.encode(chunks)

print("Ready.\n")

# =========================
# Search loop
# =========================

while True:

    query = input("Ask a question (or type 'exit'): ").strip()

    if query.lower() == "exit":
        print("Goodbye.")
        break

    # Create query embedding
    query_embedding = model.encode([query])

    # Compare with all chunks
    scores = cosine_similarity(
        query_embedding,
        chunk_embeddings
    )[0]

    # Top 3 results
    top_k = 3
    top_indices = scores.argsort()[-top_k:][::-1]

    print("\n" + "=" * 70)
    print("TOP MATCHES")
    print("=" * 70)

    for rank, idx in enumerate(top_indices, start=1):

        chunk = chunks[idx]

        # Limit displayed text
        preview = chunk[:800]

        print(f"\nResult #{rank}")
        print(f"Similarity Score: {scores[idx]:.4f}")
        print("-" * 70)
        print(preview)

        if len(chunk) > 800:
            print("...")

    print("\n" + "=" * 70 + "\n")