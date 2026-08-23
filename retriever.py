"""
===============================================================================
AfriShield AI
Offline Cybersecurity Intelligence Platform

Semantic Document Retriever
Version: 4.1.0
===============================================================================
"""

from __future__ import annotations

import logging
import os
from typing import List

import streamlit as st


# =============================================================================
# CONFIGURATION
# =============================================================================

VECTOR_DB_PATH = "vector_db"
COLLECTION_NAME = "cyber_docs"

# Local Hugging Face model
EMBEDDING_MODEL = os.path.expanduser(
    r"~\.cache\huggingface\hub\models--sentence-transformers--all-MiniLM-L6-v2"
    r"\snapshots\1110a243fdf4706b3f48f1d95db1a4f5529b4d41"
)


# =============================================================================
# LOGGING
# =============================================================================

logger = logging.getLogger("afrishield.retriever")


# =============================================================================
# LOAD RETRIEVER
# =============================================================================

@st.cache_resource
def _load_retriever():
    """
    Load the embedding model and ChromaDB collection once.

    Streamlit keeps these resources in memory so they are reused
    between user questions.
    """

    import chromadb
    from sentence_transformers import SentenceTransformer

    logger.info("Loading local embedding model...")

    model = SentenceTransformer(
        EMBEDDING_MODEL,
        device="cpu",
        local_files_only=True,
    )

    logger.info(
        "Embedding model loaded successfully."
    )

    logger.info("Connecting to ChromaDB...")

    client = chromadb.PersistentClient(
        path=VECTOR_DB_PATH
    )

    collection = client.get_collection(
        COLLECTION_NAME
    )

    logger.info(
        "Retriever initialized successfully."
    )

    return model, collection


# =============================================================================
# SEARCH
# =============================================================================

def search_documents(
    query: str,
    top_k: int = 3,
) -> List[str]:
    """
    Search the cybersecurity knowledge base.

    Parameters
    ----------
    query : str
        User question.

    top_k : int
        Number of document chunks to retrieve.

    Returns
    -------
    List[str]
        Matching document chunks.
    """

    if not query or not query.strip():
        return []

    try:

        model, collection = _load_retriever()

        # ---------------------------------------------------------------
        # Generate query embedding
        # ---------------------------------------------------------------

        embedding = model.encode(
            query.strip(),
            normalize_embeddings=True,
            show_progress_bar=False,
        ).tolist()

        # ---------------------------------------------------------------
        # Search ChromaDB
        # ---------------------------------------------------------------

        results = collection.query(
            query_embeddings=[embedding],
            n_results=top_k,
        )

        documents = results.get(
            "documents",
            []
        )

        if not documents:
            logger.warning(
                "No documents returned."
            )
            return []

        if not documents[0]:
            logger.warning(
                "Document list was empty."
            )
            return []

        logger.info(
            "Retrieved %d document(s).",
            len(documents[0]),
        )

        return documents[0]

    except Exception:

        logger.exception(
            "Document retrieval failed."
        )

        return []


# =============================================================================
# HEALTH CHECK
# =============================================================================

def retriever_ready() -> bool:
    """
    Check whether the retriever can initialize.
    """

    try:

        _load_retriever()

        return True

    except Exception:

        logger.exception(
            "Retriever health check failed."
        )

        return False


# =============================================================================
# SIMPLE TEST
# =============================================================================

if __name__ == "__main__":

    print("=" * 70)
    print("AfriShield Retriever Test")
    print("=" * 70)

    print("\nInitializing retriever...")

    if not retriever_ready():

        print(
            "Retriever failed to initialize."
        )

        raise SystemExit(1)

    print(
        "Retriever initialized successfully."
    )

    while True:

        question = input(
            "\nQuestion: "
        ).strip()

        if question.lower() in {
            "exit",
            "quit",
        }:
            break

        docs = search_documents(
            question
        )

        print()

        if not docs:

            print(
                "No matching documents found."
            )

            continue

        for i, doc in enumerate(
            docs,
            start=1
        ):

            print(
                f"[{i}]"
            )

            print(doc)

            print(
                "-" * 70
            )