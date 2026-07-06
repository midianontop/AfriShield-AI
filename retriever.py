import chromadb
from sentence_transformers import SentenceTransformer


# Load embedding model once
model = SentenceTransformer("all-MiniLM-L6-v2")

# Connect to ChromaDB once
client = chromadb.PersistentClient(path="vector_db")

collection = client.get_collection("cyber_docs")


def search_documents(query, top_k=3):
    """
    Search documents using semantic similarity.

    Args:
        query (str): User question
        top_k (int): Number of results to return

    Returns:
        list: Matching document chunks
    """

    # Convert question into embedding
    query_embedding = model.encode(query).tolist()

    # Search ChromaDB
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )

    # Return matching chunks
    return results["documents"][0]