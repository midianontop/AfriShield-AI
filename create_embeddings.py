import json
from sentence_transformers import SentenceTransformer

with open("chunks.json", "r", encoding="utf-8") as f:
    chunks = json.load(f)

model = SentenceTransformer("all-MiniLM-L6-v2")

embeddings = model.encode(chunks)

print("Chunks:", len(chunks))
print("Embeddings:", len(embeddings))
print("Dimensions:", len(embeddings[0]))