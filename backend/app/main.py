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
    return {"status": "healthy"}

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
    try:
        vectorstore = get_vectorstore()
        qa_chain = get_qa_chain(vectorstore)
        
        # Execute chain
        result = qa_chain(
            {"question": request.query, "chat_history": request.chat_history}
        )
        
        # Format response
        response = {
            "answer": result["answer"],
            "sources": result.get("source_documents", [])
        }
        
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error querying: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)