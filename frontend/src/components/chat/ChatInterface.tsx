'use client';
import { useState } from 'react';
import ChatMessage from './ChatMessage';

interface Message {
  text: string;
  type: 'user' | 'ai';
}

export default function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState('');

  const handleSend = () => {
    if (!inputText.trim()) return;
    
    // Add user message
    const newMessage: Message = {
      text: inputText,
      type: 'user'
    };
    
    setMessages(prev => [...prev, newMessage]);
    setInputText('');

    // Simulate AI response (we'll replace this with real AI later)
    setTimeout(() => {
      const aiResponse: Message = {
        text: "I'm here to help guide your learning journey. What would you like to learn about?",
        type: 'ai'
      };
      setMessages(prev => [...prev, aiResponse]);
    }, 1000);
  };

  return (
    <div className="bg-white rounded-lg shadow-md border border-gray-200 p-6">
      <div className="space-y-4">
        {/* Messages container */}
        <div className="space-y-4 h-[400px] overflow-y-auto mb-4">
          {messages.map((message, index) => (
            <ChatMessage 
              key={index}
              message={message.text}
              type={message.type}
            />
          ))}
        </div>

        {/* Input area */}
        <div className="flex items-center space-x-2">
          <input
            type="text"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSend()}
            placeholder="Type your message..."
            className="flex-1 p-2 rounded-lg bg-gray-50 border border-gray-300 text-gray-900 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
          <button 
            onClick={handleSend}
            className="bg-blue-600 hover:bg-blue-500 text-white px-4 py-2 rounded-lg transition-colors duration-200"
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
}