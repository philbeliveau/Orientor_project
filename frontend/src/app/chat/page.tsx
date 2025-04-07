'use client';
import { useState, useRef, useEffect } from 'react';

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
    const [messages, setMessages] = useState<Message[]>([]);
    const [inputMessage, setInputMessage] = useState('');
    const [isTyping, setIsTyping] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);
    const [feedback, setFeedback] = useState<MessageFeedback[]>([]);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!inputMessage.trim() || isTyping) return;

        const newMessage: Message = {
            id: Date.now(),
            text: inputMessage,
            sender: 'user',
            timestamp: new Date(),
        };

        setMessages(prev => [...prev, newMessage]);
        setInputMessage('');
        setIsTyping(true);

        // Simulate AI response
        setTimeout(() => {
            const aiMessage: Message = {
                id: Date.now(),
                text: "I'm here to help you with your career path. What specific aspects would you like to discuss?",
                sender: 'ai',
                timestamp: new Date(),
            };
            setMessages(prev => [...prev, aiMessage]);
            setIsTyping(false);
        }, 1000);
    };

    const handleFeedback = (messageId: number, type: 'helpful' | 'not_helpful') => {
        setFeedback(prev => [...prev, { messageId, type }]);
    };

    return (
        <div className="chat-container">
            <div className="chat-box">
                <div className="chat-header">
                    <h1 className="text-xl font-semibold">Career Advisor</h1>
                    <div className="text-sm text-gray-400">AI Assistant</div>
                </div>
                
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
    );
} 