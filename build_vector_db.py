import json
from sentence_transformers import SentenceTransformer
import chromadb

# =========================
# Load chunks
# =========================

with open("documents/chunks.json", "r", encoding="utf-8") as f:
    chunks = json.load(f)

print(f"Loaded {len(chunks)} chunks")

# =========================
# Load embedding model
# =========================

model = SentenceTransformer("all-MiniLM-L6-v2")

print("Embedding chunks...")

# =========================
# Create Chroma client
# =========================

client = chromadb.PersistentClient(path="vector_db")

collection = client.get_or_create_collection(
    name="cyber_docs"
)

# =========================
# Store chunks
# =========================

for i, chunk in enumerate(chunks):

    embedding = model.encode(chunk).tolist()

    collection.add(
    ids=[str(i)],
    embeddings=[embedding],
    documents=[chunk],
    metadatas=[{"source": "profile"}]
)
    

print("Database created successfully!")