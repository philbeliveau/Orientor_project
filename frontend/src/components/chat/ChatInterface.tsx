'use client';// frontend/src/components/chat/ChatInterface.tsx
// frontend/src/components/chat/ChatInterface.tsx

import { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';
import axios from 'axios';
import ChatMessage from './ChatMessage';

interface Message {
  text: string;
  type: 'user' | 'ai';
  id: number;
  timestamp: Date;
}

interface ChatResponse {
  text: string;
}

export default function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const router = useRouter();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Check authentication and show welcome message
  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      router.push('/login');
      return;
    }

    // Display welcome message when component mounts
    const welcomeMessage: Message = {
      id: Date.now(),
      text: "Hello! I'm your Career Advisor. How can I help you today?",
      type: 'ai',
      timestamp: new Date(),
    };
    setMessages([welcomeMessage]);
  }, [router]);

  const handleSend = async () => {
    if (!inputText.trim() || isTyping) return;

    const token = localStorage.getItem('access_token');
    if (!token) {
      router.push('/login');
      return;
    }

    const newMessage: Message = {
      id: Date.now(),
      text: inputText,
      type: 'user',
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, newMessage]);
    setInputText('');
    setIsTyping(true);

    try {
      const response = await axios.post<ChatResponse>(
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
        type: 'ai',
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
        type: 'ai',
        timestamp: new Date(),
      };
      
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setIsTyping(false);
    }
  };

  return (
    <div className="bg-gray-900 rounded-lg shadow-md border border-gray-700 p-6">
      <div className="space-y-4">
        <div className="space-y-4 h-[400px] overflow-y-auto mb-4">
          {messages.map((message) => (
            <ChatMessage 
              key={message.id}
              message={message.text}
              type={message.type}
              userColor="bg-blue-600"
              aiColor="bg-gray-700"
            />
          ))}
          {isTyping && (
            <ChatMessage 
              message="Typing..."
              type="ai"
              userColor="bg-blue-600"
              aiColor="bg-gray-700"
            />
          )}
          <div ref={messagesEndRef} />
        </div>

        <div className="flex items-center space-x-2">
          <input
            type="text"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && !isTyping && handleSend()}
            placeholder="Type your message..."
            className="flex-1 p-2 rounded-lg bg-gray-700 border border-gray-600 text-gray-900 placeholder-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            disabled={isTyping}
          />
          <button 
            onClick={handleSend}
            disabled={!inputText.trim() || isTyping}
            className="bg-blue-600 hover:bg-blue-500 text-gray-900 px-4 py-2 rounded-lg transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
}