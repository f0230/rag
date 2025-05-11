import os
from typing import List
from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document

# Configuration
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
CHROMA_PERSIST_DIRECTORY = "chroma_db"
CHROMA_HOST = os.environ.get("CHROMA_HOST", "localhost")
CHROMA_PORT = os.environ.get("CHROMA_PORT", "8000")  

# Singleton pattern for the vector store
_vectorstore_instance = None

def get_embedding_function():
    """
    Get the embedding function using HuggingFace models
    """
    return HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)

def get_vectorstore():
    """
    Get a singleton instance of the Chroma vector store
    """
    global _vectorstore_instance
    
    if _vectorstore_instance is None:
        embedding_function = get_embedding_function()
        
        # For Docker setup, use the client mode
        _vectorstore_instance = Chroma(
            persist_directory=CHROMA_PERSIST_DIRECTORY,
            embedding_function=embedding_function,
            client_settings={"host": CHROMA_HOST, "port": CHROMA_PORT}
        )
    
    return _vectorstore_instance

def search_vectorstore(query: str, k: int = 5):
    """
    Search the vector store for similar documents
    
    Args:
        query: The search query
        k: Number of results to return
        
    Returns:
        List of documents
    """
    vectorstore = get_vectorstore()
    docs = vectorstore.similarity_search(query, k=k)
    return docs

def add_documents_to_vectorstore(documents: List[Document]):
    """
    Add documents to the vector store
    
    Args:
        documents: List of Documents to add
    """
    vectorstore = get_vectorstore()
    vectorstore.add_documents(documents)