import os
from typing import Dict, Any, List

from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.chat_models.base import BaseChatModel
from langchain.vectorstores.base import VectorStore
from langchain.callbacks.manager import CallbackManagerForLLMRun
from langchain.llms.base import LLM
from langchain.schema.output import Generation

# Custom Khoj LLM class to interface with Khoj
class KhojLLM(LLM):
    """Custom LLM wrapper for Khoj API."""
    
    khoj_url: str = "http://khoj:4000"  # Docker service name
    
    @property
    def _llm_type(self) -> str:
        return "Khoj"
    
    def _call(
        self, 
        prompt: str, 
        stop: List[str] = None, 
        run_manager: CallbackManagerForLLMRun = None,
        **kwargs: Any,
    ) -> str:
        """Call the Khoj API and return the response."""
        import requests
        import json
        
        try:
            response = requests.post(
                f"{self.khoj_url}/api/chat",
                headers={"Content-Type": "application/json"},
                data=json.dumps({
                    "message": prompt,
                    "use_context": True,  # Enable retrieval
                })
            )
            response.raise_for_status()
            result = response.json()
            return result.get("response", "No response from Khoj")
        except Exception as e:
            print(f"Error calling Khoj API: {e}")
            return f"Error: Could not get response from Khoj. {str(e)}"

# Function to get the LLM instance
def get_llm():
    """Get an instance of the LLM."""
    return KhojLLM()

# Function to create a conversational retrieval chain
def get_qa_chain(vectorstore: VectorStore):
    """
    Creates a ConversationalRetrievalChain for question answering
    
    Args:
        vectorstore: The vector store to use for retrieval
        
    Returns:
        A ConversationalRetrievalChain
    """
    llm = get_llm()
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True
    )
    
    chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 5}
        ),
        memory=memory,
        return_source_documents=True,
        verbose=True
    )
    
    return chain