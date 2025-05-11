import os
from pathlib import Path
from typing import List, Dict, Any
import uuid

from langchain.document_loaders import (
    PyPDFLoader,
    UnstructuredWordDocumentLoader,
    TextLoader,
    CSVLoader,
    UnstructuredEmailLoader,
    BSHTMLLoader
)
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

from app.vectorstore import get_vectorstore

# File type handlers
FILE_LOADERS = {
    ".pdf": PyPDFLoader,
    ".docx": UnstructuredWordDocumentLoader,
    ".doc": UnstructuredWordDocumentLoader,
    ".txt": TextLoader,
    ".csv": CSVLoader,
    ".eml": UnstructuredEmailLoader,
    ".html": BSHTMLLoader,
    ".htm": BSHTMLLoader
}

# Process a document
async def process_document(file_path: str) -> str:
    """
    Process a document for ingestion into the vector store
    
    Args:
        file_path: Path to the document
        
    Returns:
        str: Document ID
    """
    try:
        # Generate a document ID
        doc_id = str(uuid.uuid4())
        
        # Get the file extension
        file_extension = Path(file_path).suffix.lower()
        
        # Check if we have a loader for this file type
        if file_extension not in FILE_LOADERS:
            raise ValueError(f"Unsupported file type: {file_extension}")
        
        # Load the document
        loader_class = FILE_LOADERS[file_extension]
        loader = loader_class(file_path)
        documents = loader.load()
        
        # Add metadata
        for doc in documents:
            doc.metadata["source"] = file_path
            doc.metadata["doc_id"] = doc_id
        
        # Split the documents
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        docs = text_splitter.split_documents(documents)
        
        # Add to vector store
        vectorstore = get_vectorstore()
        vectorstore.add_documents(docs)
        
        print(f"Processed {file_path} - Added {len(docs)} chunks to vector store")
        return doc_id
        
    except Exception as e:
        print(f"Error processing document {file_path}: {str(e)}")
        raise

# Function to handle web scraping
async def process_url(url: str) -> str:
    """
    Process a URL for ingestion into the vector store
    
    Args:
        url: URL to scrape
        
    Returns:
        str: Document ID
    """
    # This would use a web scraper like playwright or requests + BeautifulSoup
    # Implementation left for future development
    pass

# Function to handle database connections
async def process_database(connection_string: str, query: str) -> str:
    """
    Process a database query for ingestion into the vector store
    
    Args:
        connection_string: Database connection string
        query: SQL query to execute
        
    Returns:
        str: Document ID
    """
    # This would use SQLAlchemy or similar to connect to databases
    # Implementation left for future development
    pass