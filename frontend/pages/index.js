import { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { FiSend, FiUpload, FiInfo } from 'react-icons/fi';
import ReactMarkdown from 'react-markdown';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function Home() {
    const [query, setQuery] = useState('');
    const [messages, setMessages] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    const [file, setFile] = useState(null);
    const [uploadStatus, setUploadStatus] = useState('');
    const [chatHistory, setChatHistory] = useState([]);

    const messagesEndRef = useRef(null);

    // Scroll to bottom on new messages
    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const handleSendMessage = async (e) => {
        e.preventDefault();

        if (!query.trim()) return;

        // Add user message to chat
        const userMessage = { role: 'user', content: query };
        setMessages(prev => [...prev, userMessage]);

        // Reset input
        setQuery('');
        setIsLoading(true);

        try {
            // Prepare chat history for API
            const apiChatHistory = chatHistory.map(msg => ({
                role: msg.role,
                content: msg.content
            }));

            // Send query to API
            const response = await axios.post(`${API_URL}/query`, {
                query: query,
                chat_history: apiChatHistory
            });

            // Add bot response to chat
            const botMessage = {
                role: 'assistant',
                content: response.data.answer,
                sources: response.data.sources
            };

            setMessages(prev => [...prev, botMessage]);

            // Update chat history
            setChatHistory([...chatHistory, userMessage, {
                role: 'assistant',
                content: response.data.answer
            }]);

        } catch (error) {
            console.error('Error fetching response:', error);

            // Add error message
            setMessages(prev => [...prev, {
                role: 'assistant',
                content: 'Sorry, I encountered an error. Please try again.'
            }]);
        }

        setIsLoading(false);
    };

    const handleFileChange = (e) => {
        setFile(e.target.files[0]);
    };

    const handleFileUpload = async () => {
        if (!file) return;

        setUploadStatus('Uploading...');

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await axios.post(`${API_URL}/upload`, formData, {
                headers: {
                    'Content-Type': 'multipart/form-data'
                }
            });

            setUploadStatus(`File uploaded and processed: ${file.name}`);
            setFile(null);

            // Add system notification
            setMessages(prev => [...prev, {
                role: 'system',
                content: `Document "${file.name}" processed successfully.`
            }]);

        } catch (error) {
            console.error('Error uploading file:', error);
            setUploadStatus('Error uploading file');
        }
    };

    return (
        <div className="flex flex-col h-screen bg-gray-100">
            {/* Header */}
            <header className="bg-white shadow p-4">
                <h1 className="text-xl font-bold text-gray-800">RAG System with LangChain & Khoj</h1>
            </header>

            {/* Main content */}
            <div className="flex flex-1 overflow-hidden">
                {/* Sidebar */}
                <div className="w-1/4 bg-white shadow-md p-4 flex flex-col">
                    <h2 className="text-lg font-semibold mb-4">Upload Documents</h2>

                    <div className="mb-4">
                        <input
                            type="file"
                            id="file-upload"
                            className="hidden"
                            onChange={handleFileChange}
                        />
                        <label
                            htmlFor="file-upload"
                            className="flex items-center justify-center p-2 border-2 border-dashed border-gray-300 rounded-md cursor-pointer hover:border-blue-500 transition-colors"
                        >
                            <FiUpload className="mr-2" />
                            {file ? file.name : 'Select File'}
                        </label>
                    </div>

                    {file && (
                        <button
                            className="bg-blue-500 hover:bg-blue-600 text-white rounded-md p-2 mb-4 transition-colors"
                            onClick={handleFileUpload}
                        >
                            Upload Document
                        </button>
                    )}

                    {uploadStatus && (
                        <p className="text-sm text-gray-600 mb-4">{uploadStatus}</p>
                    )}

                    <div className="mt-auto">
                        <div className="bg-blue-50 p-3 rounded-md flex items-start">
                            <FiInfo className="text-blue-500 mt-1 mr-2 flex-shrink-0" />
                            <p className="text-sm text-gray-700">
                                Upload documents to build your knowledge base. The system supports PDF, DOCX, TXT, CSV, and HTML files.
                            </p>
                        </div>
                    </div>
                </div>

                {/* Chat area */}
                <div className="flex-1 flex flex-col">
                    {/* Message history */}
                    <div className="flex-1 p-4 overflow-y-auto">
                        {messages.length === 0 ? (
                            <div className="h-full flex flex-col items-center justify-center text-gray-400">
                                <p className="text-lg mb-2">Start a conversation</p>
                                <p className="text-sm">Ask questions about your uploaded documents</p>
                            </div>
                        ) : (
                            messages.map((message, index) => (
                                <div
                                    key={index}
                                    className={`mb-4 ${message.role === 'user'
                                            ? 'flex justify-end'
                                            : 'flex justify-start'
                                        }`}
                                >
                                    <div
                                        className={`max-w-3/4 rounded-lg p-3 ${message.role === 'user'
                                                ? 'bg-blue-500 text-white'
                                                : message.role === 'system'
                                                    ? 'bg-gray-200 text-gray-800'
                                                    : 'bg-white shadow text-gray-800'
                                            }`}
                                    >
                                        <ReactMarkdown className="prose">
                                            {message.content}
                                        </ReactMarkdown>

                                        {message.sources && message.sources.length > 0 && (
                                            <div className="mt-2 pt-2 border-t border-gray-200 text-xs text-gray-500">
                                                <p className="font-semibold">Sources:</p>
                                                <ul className="list-disc pl-4">
                                                    {message.sources.map((source, idx) => (
                                                        <li key={idx}>
                                                            {source.metadata?.source || 'Unknown source'}
                                                        </li>
                                                    ))}
                                                </ul>
                                            </div>
                                        )}
                                    </div>
                                </div>
                            ))
                        )}
                        <div ref={messagesEndRef} />
                    </div>

                    {/* Input area */}
                    <div className="p-4 bg-white shadow-md">
                        <form onSubmit={handleSendMessage} className="flex">
                            <input
                                type="text"
                                value={query}
                                onChange={(e) => setQuery(e.target.value)}
                                placeholder="Ask a question about your documents..."
                                className="flex-1 p-2 border border-gray-300 rounded-l-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                disabled={isLoading}
                            />
                            <button
                                type="submit"
                                className="bg-blue-500 hover:bg-blue-600 text-white p-2 rounded-r-md transition-colors flex items-center justify-center"
                                disabled={isLoading}
                            >
                                {isLoading ? (
                                    <div className="w-6 h-6 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                                ) : (
                                    <FiSend />
                                )}
                            </button>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    );
}