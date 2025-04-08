'use client';
import { useState, useRef, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import axios from 'axios';
import MainLayout from '@/components/layout/MainLayout';

interface Message {
    id: number;
    text: string;
    sender: 'user' | 'ai';
    timestamp: Date;
}

interface MessageFeedback {
    messageId: number;
    type: 'helpful' | 'not_helpful';
}

export default function ChatPage() {
    const router = useRouter();
    const [messages, setMessages] = useState<Message[]>([]);
    const [inputMessage, setInputMessage] = useState('');
    const [isTyping, setIsTyping] = useState(false);
    const [isClearingChat, setIsClearingChat] = useState(false);
    const [authError, setAuthError] = useState<string | null>(null);
    const messagesEndRef = useRef<HTMLDivElement>(null);
    const [feedback, setFeedback] = useState<MessageFeedback[]>([]);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    // Check authentication on mount
    useEffect(() => {
        const token = localStorage.getItem('access_token');
        if (!token) {
            router.push('/login');
            return;
        }

        // Display welcome message when component mounts and user is authenticated
        const welcomeMessage: Message = {
            id: Date.now(),
            text: "Hello! I'm your Career Advisor. How can I help you today?",
            sender: 'ai',
            timestamp: new Date(),
        };
        setMessages([welcomeMessage]);
    }, [router]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!inputMessage.trim() || isTyping) return;

        const token = localStorage.getItem('access_token');
        if (!token) {
            router.push('/login');
            return;
        }

        const newMessage: Message = {
            id: Date.now(),
            text: inputMessage,
            sender: 'user',
            timestamp: new Date(),
        };

        setMessages(prev => [...prev, newMessage]);
        setInputMessage('');
        setIsTyping(true);
        setAuthError(null);

        try {
            const response = await axios.post(
                'http://localhost:8000/chat/send',
                { text: newMessage.text },
                {
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/json'
                    }
                }
            );
            
            const aiMessage: Message = {
                id: Date.now(),
                text: response.data.text,
                sender: 'ai',
                timestamp: new Date(),
            };
            
            setMessages(prev => [...prev, aiMessage]);
        } catch (error: any) {
            console.error('Failed to get AI response:', error);
            
            let errorMessage = "Sorry, I'm having trouble connecting to my brain right now. Please try again later.";
            
            if (error.response?.status === 401) {
                router.push('/login');
                return;
            } else if (error.response?.data?.detail) {
                errorMessage = error.response.data.detail;
            }
            
            const errorMsg: Message = {
                id: Date.now(),
                text: errorMessage,
                sender: 'ai',
                timestamp: new Date(),
            };
            
            setMessages(prev => [...prev, errorMsg]);
        } finally {
            setIsTyping(false);
        }
    };

    const handleFeedback = (messageId: number, type: 'helpful' | 'not_helpful') => {
        setFeedback(prev => [...prev, { messageId, type }]);
    };

    const handleClearChat = async () => {
        try {
            setIsClearingChat(true);
            const token = localStorage.getItem('access_token');
            
            if (!token) {
                router.push('/login');
                return;
            }
            
            await axios.post(
                'http://localhost:8000/chat/clear',
                {},
                {
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/json'
                    }
                }
            );
            
            // Clear local messages
            setMessages([]);
            setFeedback([]);
            
            // Add welcome message
            const welcomeMessage: Message = {
                id: Date.now(),
                text: "Hello! I'm your Career Advisor. How can I help you today?",
                sender: 'ai',
                timestamp: new Date(),
            };
            
            setMessages([welcomeMessage]);
        } catch (error: any) {
            console.error('Failed to clear chat:', error);
            if (error.response?.status === 401) {
                router.push('/login');
                return;
            }
        } finally {
            setIsClearingChat(false);
        }
    };

    return (
        <MainLayout>
            <div className="chat-container">
                <div className="chat-box">
                    <div className="chat-header">
                        <div className="flex justify-between items-center w-full">
                            <div>
                                <h1 className="text-xl font-semibold text-white">Career Advisor</h1>
                                <div className="text-sm text-gray-400">AI Assistant</div>
                            </div>
                            <button
                                onClick={handleClearChat}
                                disabled={isClearingChat || messages.length === 0}
                                className="px-3 py-1 bg-gray-600 text-white text-sm rounded hover:bg-gray-500 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                                Clear Chat
                            </button>
                        </div>
                    </div>
                    
                    {authError && (
                        <div className="bg-red-500/10 border border-red-500/50 text-red-500 px-4 py-2 rounded-lg m-4">
                            {authError}
                        </div>
                    )}
                    
                    <div className="chat-messages">
                        {messages.map((message) => (
                            <div
                                key={message.id}
                                className={`chat-message ${
                                    message.sender === 'user' ? 'justify-end' : 'justify-start'
                                }`}
                            >
                                <div
                                    className={`chat-message-content ${
                                        message.sender === 'user' ? 'chat-message-user' : 'chat-message-bot'
                                    }`}
                                >
                                    <div className="message-text">{message.text}</div>
                                    {message.sender === 'ai' && !feedback.find(f => f.messageId === message.id) && (
                                        <div className="feedback-container">
                                            <button
                                                onClick={() => handleFeedback(message.id, 'helpful')}
                                                className="feedback-button"
                                            >
                                                👍 Helpful
                                            </button>
                                            <button
                                                onClick={() => handleFeedback(message.id, 'not_helpful')}
                                                className="feedback-button"
                                            >
                                                👎 Not helpful
                                            </button>
                                        </div>
                                    )}
                                </div>
                            </div>
                        ))}
                        {isTyping && (
                            <div className="chat-message justify-start">
                                <div className="chat-message-content chat-message-bot">
                                    <div className="typing-indicator">Typing...</div>
                                </div>
                            </div>
                        )}
                        <div ref={messagesEndRef} />
                    </div>

                    <div className="chat-input-container">
                        <form onSubmit={handleSubmit} className="chat-input-wrapper">
                            <input
                                type="text"
                                value={inputMessage}
                                onChange={(e) => setInputMessage(e.target.value)}
                                placeholder="Ask about your career path..."
                                className="chat-input"
                                disabled={isTyping}
                            />
                            <button
                                type="submit"
                                className="chat-send-button"
                                disabled={!inputMessage.trim() || isTyping}
                            >
                                Send
                            </button>
                        </form>
                    </div>
                </div>
            </div>
        </MainLayout>
    );
} 