import { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { FiSend, FiUpload, FiInfo } from 'react-icons/fi';
import ReactMarkdown from 'react-markdown';

export default function Home() {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [uploadStatus, setUploadStatus] = useState('');
    const fileInputRef = useRef(null);
    const messagesEndRef = useRef(null);

    // Scroll to bottom when messages change
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    // Function to handle sending a query
    const sendQuery = async (e) => {
        e.preventDefault();
        if (!input.trim()) return;

        const userMessage = { role: 'user', content: input };
        setMessages([...messages, userMessage]);
        setInput('');
        setIsLoading(true);

        try {
            const response = await axios.post('http://localhost:8000/query', {
                query: input,
                chat_history: messages.map(msg => ({
                    role: msg.role,
                    content: msg.content
                }))
            });

            const aiMessage = {
                role: 'assistant',
                content: response.data.answer,
                sources: response.data.sources || []
            };

            setMessages(prev => [...prev, aiMessage]);
        } catch (error) {
            console.error('Error sending query:', error);
            setMessages(prev => [
                ...prev,
                {
                    role: 'assistant',
                    content: 'Lo siento, ha ocurrido un error al procesar tu consulta.'
                }
            ]);
        } finally {
            setIsLoading(false);
        }
    };

    // Function to handle file upload
    const handleFileUpload = async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        const formData = new FormData();
        formData.append('file', file);
        setUploadStatus(`Subiendo ${file.name}...`);

        try {
            await axios.post('http://localhost:8000/upload', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data'
                }
            });

            setUploadStatus(`¡Archivo ${file.name} procesado con éxito!`);
            setTimeout(() => setUploadStatus(''), 3000);
        } catch (error) {
            console.error('Error uploading file:', error);
            setUploadStatus(`Error al procesar ${file.name}.`);
        }
    };

    // Format source references
    const formatSources = (sources) => {
        if (!sources || sources.length === 0) return null;

        return (
            <div className="sources">
                <h4>Fuentes:</h4>
                <ul>
                    {sources.map((source, index) => (
                        <li key={index}>
                            {source.metadata?.source || 'Fuente desconocida'}
                        </li>
                    ))}
                </ul>
            </div>
        );
    };

    return (
        <div className="app-container">
            <header>
                <h1>Sistema RAG con LangChain, ChromaDB y Khoj</h1>
            </header>

            <main>
                <div className="sidebar">
                    <div className="upload-section">
                        <h3>Subir Documentos</h3>
                        <button
                            className="upload-button"
                            onClick={() => fileInputRef.current.click()}
                        >
                            <FiUpload /> Seleccionar Archivo
                        </button>
                        <input
                            type="file"
                            ref={fileInputRef}
                            onChange={handleFileUpload}
                            style={{ display: 'none' }}
                        />
                        {uploadStatus && <p className="upload-status">{uploadStatus}</p>}
                    </div>

                    <div className="info-section">
                        <h3>Información</h3>
                        <p>
                            <FiInfo /> Este sistema permite realizar consultas sobre documentos
                            subidos utilizando técnicas de RAG (Retrieval-Augmented Generation).
                        </p>
                    </div>
                </div>

                <div className="chat-container">
                    <div className="messages">
                        {messages.length === 0 ? (
                            <div className="welcome-message">
                                <h2>¡Bienvenido al Sistema RAG!</h2>
                                <p>Sube documentos y haz preguntas sobre ellos.</p>
                            </div>
                        ) : (
                            messages.map((msg, index) => (
                                <div
                                    key={index}
                                    className={`message ${msg.role === 'user' ? 'user' : 'assistant'}`}
                                >
                                    <div className="content">
                                        <ReactMarkdown>{msg.content}</ReactMarkdown>
                                        {msg.sources && formatSources(msg.sources)}
                                    </div>
                                </div>
                            ))
                        )}
                        <div ref={messagesEndRef} />
                    </div>

                    <form className="input-form" onSubmit={sendQuery}>
                        <input
                            type="text"
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            placeholder="Escribe tu pregunta..."
                            disabled={isLoading}
                        />
                        <button type="submit" disabled={isLoading || !input.trim()}>
                            <FiSend />
                        </button>
                    </form>
                </div>
            </main>

            <style jsx global>{`
        * {
          box-sizing: border-box;
          margin: 0;
          padding: 0;
          font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        
        html, body {
          height: 100%;
          background-color: #f5f7fa;
        }
        
        .app-container {
          display: flex;
          flex-direction: column;
          height: 100vh;
        }
        
        header {
          padding: 1rem;
          background-color: #333;
          color: white;
          text-align: center;
        }
        
        main {
          display: flex;
          flex: 1;
          overflow: hidden;
        }
        
        .sidebar {
          width: 300px;
          padding: 1rem;
          background-color: #e9ecef;
          border-right: 1px solid #dee2e6;
          overflow-y: auto;
        }
        
        .chat-container {
          flex: 1;
          display: flex;
          flex-direction: column;
          height: 100%;
        }
        
        .messages {
          flex: 1;
          padding: 1rem;
          overflow-y: auto;
          display: flex;
          flex-direction: column;
        }
        
        .welcome-message {
          margin: auto;
          text-align: center;
          color: #6c757d;
          padding: 2rem;
        }
        
        .message {
          margin-bottom: 1rem;
          max-width: 85%;
          padding: 0.8rem;
          border-radius: 0.5rem;
        }
        
        .user {
          background-color: #007bff;
          color: white;
          align-self: flex-end;
        }
        
        .assistant {
          background-color: #f8f9fa;
          border: 1px solid #dee2e6;
          align-self: flex-start;
        }
        
        .sources {
          margin-top: 0.5rem;
          font-size: 0.8rem;
          color: #6c757d;
        }
        
        .sources ul {
          margin-left: 1rem;
        }
        
        .input-form {
          display: flex;
          padding: 1rem;
          border-top: 1px solid #dee2e6;
          background-color: white;
        }
        
        input {
          flex: 1;
          padding: 0.5rem;
          border: 1px solid #ced4da;
          border-radius: 0.25rem;
          font-size: 1rem;
        }
        
        button {
          margin-left: 0.5rem;
          padding: 0.5rem 1rem;
          background-color: #007bff;
          color: white;
          border: none;
          border-radius: 0.25rem;
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
        }
        
        button:disabled {
          background-color: #6c757d;
          cursor: not-allowed;
        }
        
        .upload-button {
          width: 100%;
          margin-bottom: 1rem;
          padding: 0.75rem;
          background-color: #28a745;
        }
        
        .upload-status {
          font-size: 0.85rem;
          color: #28a745;
          margin-bottom: 1rem;
        }
        
        h3 {
          margin-bottom: 1rem;
        }
        
        .info-section {
          margin-top: 2rem;
        }
      `}</style>
        </div>
    );
}