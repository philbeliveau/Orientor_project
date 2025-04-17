'use client';
import { useState, useRef, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import axios from 'axios';
import type { AxiosError, isAxiosError } from 'axios';
import MainLayout from '@/components/layout/MainLayout';

interface Message {
    id: number;
    text: string;
    sender: 'user' | 'ai';
    timestamp: Date;
}

interface MessageFeedback {
    messageId: number;
    feedback: 'helpful' | 'not_helpful';
}

interface ChatResponse {
    response: string;
}

// Define API URL with fallback and trim any trailing spaces
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const cleanApiUrl = API_URL ? API_URL.trim() : '';

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
            text: "Hello! I'm your Socratic mentor. What would you like to explore today about your career path or personal interests?",
            sender: 'ai',
            timestamp: new Date(),
        };
        setMessages([welcomeMessage]);
    }, [router]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!inputMessage.trim() || isTyping) return;

        const userMessage: Message = {
            id: Date.now(),
            text: inputMessage,
            sender: 'user',
            timestamp: new Date(),
        };

        setMessages(prev => [...prev, userMessage]);
        setInputMessage('');
        setIsTyping(true);

        try {
            const token = localStorage.getItem('access_token');
            if (!token) {
                router.push('/login');
                return;
            }

            const response = await axios.post<ChatResponse>(
                `${cleanApiUrl}/chat`,
                { message: inputMessage },
                {
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/json',
                    },
                }
            );

            const aiMessage: Message = {
                id: Date.now() + 1,
                text: response.data.response,
                sender: 'ai',
                timestamp: new Date(),
            };

            setMessages(prev => [...prev, aiMessage]);
        } catch (error: unknown) {
            console.error('Error sending message:', error);
            if (error && typeof error === 'object' && 'response' in error && 
                typeof error.response === 'object' && error.response && 
                'status' in error.response && error.response.status === 401) {
                setAuthError('Your session has expired. Please log in again.');
                setTimeout(() => router.push('/login'), 2000);
            } else {
                setAuthError('An error occurred while sending your message. Please try again.');
            }
        } finally {
            setIsTyping(false);
        }
    };

    const handleClearChat = async () => {
        if (isClearingChat || messages.length === 0) return;
        setIsClearingChat(true);

        try {
            const token = localStorage.getItem('access_token');
            if (!token) {
                router.push('/login');
                return;
            }

            await axios.post(
                `${cleanApiUrl}/chat/clear`,
                {},
                {
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/json',
                    },
                }
            );

            setMessages([]);
            const welcomeMessage: Message = {
                id: Date.now(),
                text: "Hello! I'm your Socratic mentor. What would you like to explore today about your career path or personal interests?",
                sender: 'ai',
                timestamp: new Date(),
            };
            setMessages([welcomeMessage]);
        } catch (error: unknown) {
            console.error('Error clearing chat:', error);
            if (error && typeof error === 'object' && 'response' in error && 
                typeof error.response === 'object' && error.response && 
                'status' in error.response && error.response.status === 401) {
                setAuthError('Your session has expired. Please log in again.');
                setTimeout(() => router.push('/login'), 2000);
            } else {
                setAuthError('An error occurred while clearing the chat. Please try again.');
            }
        } finally {
            setIsClearingChat(false);
        }
    };

    const handleFeedback = (messageId: number, feedbackType: 'helpful' | 'not_helpful') => {
        setFeedback(prev => [...prev, { messageId, feedback: feedbackType }]);
    };

    return (
        <MainLayout>
            <div className="flex flex-col h-[calc(100vh-12rem)] max-w-4xl mx-auto">
                <div className="flex justify-between items-center mb-4">
                    <div>
                        <p className="text-sm text-neutral-lightgray opacity-70">Your Socratic mentor for self-discovery</p>
                    </div>
                    <button
                        onClick={handleClearChat}
                        disabled={isClearingChat || messages.length === 0}
                        className="btn btn-secondary text-sm"
                    >
                        Clear Chat
                    </button>
                </div>
                
                {authError && (
                    <div className="bg-red-900/20 border border-secondary-coral text-secondary-coral px-4 py-3 rounded-lg mb-4">
                        {authError}
                    </div>
                )}
                
                <div className="flex-1 overflow-y-auto bg-white/30 backdrop-blur-sm rounded-lg p-4 mb-4">
                    {messages.map((message) => (
                        <div
                            key={message.id}
                            className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'} mb-4`}
                        >
                            <div className={message.sender === 'user' ? 'message-user' : 'message-system'}>
                                <div className="whitespace-pre-wrap">{message.text}</div>
                                {message.sender === 'ai' && !feedback.find(f => f.messageId === message.id) && (
                                    <div className="flex items-center justify-end mt-2 space-x-2 text-xs">
                                        <button
                                            onClick={() => handleFeedback(message.id, 'helpful')}
                                            className="text-neutral-lightgray hover:text-secondary-teal transition-colors"
                                        >
                                        </button>
                                        <button
                                            onClick={() => handleFeedback(message.id, 'not_helpful')}
                                            className="text-neutral-lightgray hover:text-secondary-coral transition-colors"
                                        >
                                        </button>
                                    </div>
                                )}
                            </div>
                        </div>
                    ))}
                    {isTyping && (
                        <div className="flex justify-start mb-4">
                            <div className="message-system flex items-center space-x-2">
                                <div className="flex space-x-1">
                                    <div className="h-2 w-2 bg-primary-blue rounded-full animate-bounce [animation-delay:-0.3s]"></div>
                                    <div className="h-2 w-2 bg-primary-blue rounded-full animate-bounce [animation-delay:-0.15s]"></div>
                                    <div className="h-2 w-2 bg-primary-blue rounded-full animate-bounce"></div>
                                </div>
                                <span className="text-sm">Thinking...</span>
                            </div>
                        </div>
                    )}
                    <div ref={messagesEndRef} />
                </div>

                <form onSubmit={handleSubmit} className="relative">
                    <input
                        type="text"
                        value={inputMessage}
                        onChange={(e) => setInputMessage(e.target.value)}
                        placeholder="Ask anything about your career path, interests, or goals..."
                        className="input pr-20 py-3"
                        disabled={isTyping}
                    />
                    <button
                        type="submit"
                        disabled={!inputMessage.trim() || isTyping}
                        className="absolute right-2 top-1/2 -translate-y-1/2 btn btn-primary py-1 px-4"
                    >
                        Send
                    </button>
                </form>
            </div>
        </MainLayout>
    );
} 