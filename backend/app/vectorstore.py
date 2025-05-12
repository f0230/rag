import os
from typing import List
from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document
from chromadb.config import Settings

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
    global _vectorstore_instance
    
    if _vectorstore_instance is None:
        try:
            embedding_function = get_embedding_function()
            
            # Configuración corregida para Chroma
            client_settings = Settings(
                chroma_server_host=CHROMA_HOST,
                chroma_server_http_port=CHROMA_PORT,
            )
            
            _vectorstore_instance = Chroma(
                persist_directory=CHROMA_PERSIST_DIRECTORY,
                embedding_function=embedding_function,
                client_settings=client_settings
            )
            
            # Test connection
            try:
                collection = _vectorstore_instance._client.get_or_create_collection("test")
                collection.count()  # Simple operation to test connection
            except Exception as e:
                raise ConnectionError(f"Failed to connect to ChromaDB: {e}")
                
        except Exception as e:
            raise RuntimeError(f"Error initializing vector store: {e}")
    
    return _vectorstore_instance

# Resto de tus funciones (search_vectorstore, add_documents_to_vectorstore) permanecen igual

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