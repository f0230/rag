from typing import List, Any, Dict
import requests
import json
import logging
from langchain.schema import BaseRetriever
from langchain.chains.base import Chain

class KhojRetriever(BaseRetriever):
    """Retriever que combina Khoj API con el vectorstore local"""
    
    def __init__(self, vectorstore, khoj_url: str):
        self.vectorstore = vectorstore
        self.khoj_url = khoj_url
    
    def get_relevant_documents(self, query: str) -> List[Dict]:
        # Primero obtenemos documentos relevantes del vectorstore
        docs = self.vectorstore.similarity_search(query, k=5)
        
        # Convertimos a formato compatible con Khoj si es necesario
        return [{"content": doc.page_content, "metadata": doc.metadata} for doc in docs]

class KhojQAChain(Chain):
    """Cadena personalizada para integrar Khoj con el vectorstore"""
    
    def __init__(self, retriever: KhojRetriever):
        super().__init__()
        self.retriever = retriever
    
    @property
    def input_keys(self) -> List[str]:
        return ["question"]
    
    @property
    def output_keys(self) -> List[str]:
        return ["answer", "source_documents"]
    
    def _call(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        question = inputs["question"]
        
        try:
            # Obtenemos documentos relevantes
            docs = self.retriever.get_relevant_documents(question)
            
            # Llamamos a la API de Khoj
            response = requests.post(
                f"{self.retriever.khoj_url}/api/chat",
                headers={"Content-Type": "application/json"},
                data=json.dumps({
                    "message": question,
                    "use_context": True,
                    "context": docs[:3]  # Enviamos los 3 documentos más relevantes
                }),
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            
            return {
                "answer": result.get("response", "No response from Khoj"),
                "source_documents": docs
            }
            
        except Exception as e:
            logging.error(f"Error in KhojQAChain: {e}")
            return {
                "answer": f"Error processing your question: {str(e)}",
                "source_documents": []
            }

def get_qa_chain(vectorstore, khoj_url: str = "http://khoj:4000"):
    """
    Crea y retorna una cadena de QA que integra Khoj con el vectorstore
    
    Args:
        vectorstore: Instancia del vectorstore
        khoj_url: URL del servicio Khoj
        
    Returns:
        KhojQAChain: Cadena configurada para hacer QA
    """
    retriever = KhojRetriever(vectorstore, khoj_url)
    return KhojQAChain(retriever)