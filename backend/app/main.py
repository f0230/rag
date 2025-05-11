from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import os
import shutil
from pydantic import BaseModel

from app.ingest import process_document
from app.chains import get_qa_chain
from app.vectorstore import get_vectorstore

app = FastAPI(title="LangChain RAG API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development - restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    import requests
    
    services_status = {
        "backend": "healthy",
        "chroma": "unknown",
        "khoj": "unknown"
    }
    
    # Check ChromaDB
    try:
        vectorstore = get_vectorstore()
        # If we got here without errors, ChromaDB is working
        services_status["chroma"] = "healthy"
    except Exception as e:
        services_status["chroma"] = f"unhealthy: {str(e)}"
    
    # Check Khoj
    try:
        response = requests.get("http://khoj:4000/api/health", timeout=2)
        if response.status_code == 200:
            services_status["khoj"] = "healthy"
        else:
            services_status["khoj"] = f"unhealthy: status code {response.status_code}"
    except Exception as e:
        services_status["khoj"] = f"unhealthy: {str(e)}"
    
    return {
        "status": "healthy",
        "services": services_status
    }

# Models
class QueryRequest(BaseModel):
    query: str
    chat_history: Optional[List[dict]] = []

class QueryResponse(BaseModel):
    answer: str
    sources: List[dict] = []

# Upload endpoint
@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    # Create data directory if it doesn't exist
    os.makedirs("data", exist_ok=True)
    
    # Save the file
    file_path = f"data/{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Process the document
    try:
        doc_id = await process_document(file_path)
        return {"message": "Document processed successfully", "document_id": doc_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")

# Query endpoint
@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    import logging
    
    logging.info(f"Received query: {request.query}")
    
    try:
        # Check if we have documents in the vectorstore
        vectorstore = get_vectorstore()
        
        # Get document count - if 0, return a helpful message
        try:
            collection = vectorstore._collection
            count = collection.count()
            if count == 0:
                return {
                    "answer": "No hay documentos para consultar. Por favor, sube algún documento primero.",
                    "sources": []
                }
        except Exception as e:
            logging.error(f"Error checking document count: {e}")
            # Continue with query anyway
        
        # Create QA chain
        qa_chain = get_qa_chain(vectorstore)
        
        # Execute chain
        logging.info("Executing QA chain...")
        result = qa_chain(
            {"question": request.query, "chat_history": request.chat_history}
        )
        logging.info("QA chain executed successfully")
        
        # Format response
        response = {
            "answer": result["answer"],
            "sources": result.get("source_documents", [])
        }
        
        return response
    except Exception as e:
        logging.exception(f"Error in query endpoint: {e}")
        
        # Return a more user-friendly error
        if "khoj" in str(e).lower():
            raise HTTPException(
                status_code=503, 
                detail="El servicio Khoj no está disponible. Por favor, espere un momento e intente de nuevo."
            )
        elif "chroma" in str(e).lower():
            raise HTTPException(
                status_code=503, 
                detail="Error al conectar con la base de datos vectorial. Por favor, espere un momento e intente de nuevo."
            )
        else:
            raise HTTPException(status_code=500, detail=f"Error al procesar su consulta: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)