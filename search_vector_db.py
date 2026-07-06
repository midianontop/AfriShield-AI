import chromadb
from sentence_transformers import SentenceTransformer

# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Connect to database
client = chromadb.PersistentClient(path="vector_db")

collection = client.get_collection("cyber_docs")

# Ask a question
query = "What is SQL Injection?"

# Convert question to embedding
query_embedding = model.encode(query).tolist()

# Search database
results = collection.query(
    query_embeddings=[query_embedding],
    n_results=3
)

print("\nQUESTION:")
print(query)

print("\nTOP RESULTS:\n")

for i, doc in enumerate(results["documents"][0], start=1):
    print(f"Result {i}")
    print("-" * 50)
    print(doc[:500])  # show first 500 chars
    print()