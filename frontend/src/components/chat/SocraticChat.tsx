/**
 * Socratic Chat Component - Dual-mode chat interface
 * 
 * Provides two distinct conversational experiences:
 * 1. Socratic Mode - Guided discovery through thoughtful questioning
 * 2. Claude Mode - Bold, direct challenges to push thinking further
 */

'use client';

import React, { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Brain, Zap, Send } from 'lucide-react';
import axios from 'axios';
import LoadingSpinner from '@/components/ui/LoadingSpinner';

type ChatMode = 'socratic' | 'claude';

interface Message {
  id: number;
  text: string;
  isUser: boolean;
  timestamp: Date;
  mode?: ChatMode;
}

interface ModeInfo {
  id: ChatMode;
  name: string;
  description: string;
  extended_description: string;
  best_for: string[];
  style: string;
  powered_by: string;
  color: string;
  icon: React.ReactNode;
}

const SocraticChat: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [conversationId, setConversationId] = useState<number | null>(null);
  const [selectedMode, setSelectedMode] = useState<ChatMode | null>(null);
  const [showModeSelection, setShowModeSelection] = useState(true);
  const [modeInfo, setModeInfo] = useState<Record<ChatMode, ModeInfo> | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    // Load available modes info
    loadModesInfo();
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const loadModesInfo = async () => {
    try {
      const response = await axios.get('/api/v1/socratic-chat/modes');
      const modes = response.data.modes;
      
      // Add UI-specific properties
      const enhancedModes = {
        socratic: {
          ...modes.socratic,
          color: 'blue',
          icon: <Brain className="w-5 h-5" />
        },
        claude: {
          ...modes.claude,
          color: 'purple',
          icon: <Zap className="w-5 h-5" />
        }
      };
      
      setModeInfo(enhancedModes as Record<ChatMode, ModeInfo>);
    } catch (error) {
      console.error('Failed to load modes info:', error);
    }
  };

  const selectMode = async (mode: ChatMode) => {
    setSelectedMode(mode);
    setShowModeSelection(false);
    
    // Get introduction message for the selected mode
    try {
      const response = await axios.post(
        '/api/v1/socratic-chat/introduction',
        { mode },
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
          }
        }
      );
      
      const introMessage: Message = {
        id: 0,
        text: response.data.introduction,
        isUser: false,
        timestamp: new Date(),
        mode
      };
      
      setMessages([introMessage]);
      
      // Focus input after mode selection
      setTimeout(() => inputRef.current?.focus(), 100);
    } catch (error) {
      console.error('Failed to get introduction:', error);
    }
  };

  const sendMessage = async () => {
    if (!inputText.trim() || isLoading || !selectedMode) return;

    const userMessage: Message = {
      id: messages.length + 1,
      text: inputText,
      isUser: true,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputText('');
    setIsLoading(true);

    try {
      const response = await axios.post(
        '/api/v1/socratic-chat/send',
        {
          text: inputText,
          mode: selectedMode,
          conversation_id: conversationId
        },
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
          }
        }
      );

      if (!conversationId) {
        setConversationId(response.data.conversation_id);
      }

      const aiMessage: Message = {
        id: response.data.message_id,
        text: response.data.response,
        isUser: false,
        timestamp: new Date(),
        mode: selectedMode
      };

      setMessages(prev => [...prev, aiMessage]);

    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage: Message = {
        id: messages.length + 2,
        text: "I apologize, but I'm having trouble connecting. Please try again.",
        isUser: false,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
      // Refocus input after sending
      setTimeout(() => inputRef.current?.focus(), 100);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const resetChat = () => {
    setMessages([]);
    setConversationId(null);
    setSelectedMode(null);
    setShowModeSelection(true);
  };

  // Mode Selection Screen
  if (showModeSelection && modeInfo) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 flex items-center justify-center p-4">
        <div className="max-w-4xl w-full">
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold text-gray-800 mb-4">
              Choose Your Thinking Partner
            </h1>
            <p className="text-lg text-gray-600">
              Select the conversational style that best fits your current needs
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-6">
            {/* Socratic Mode Card */}
            <Card 
              className="cursor-pointer transition-all hover:shadow-xl hover:scale-102 border-2 hover:border-blue-300"
              onClick={() => selectMode('socratic')}
            >
              <CardHeader className="text-center pb-4">
                <div className="mx-auto mb-4 w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center">
                  <Brain className="w-8 h-8 text-blue-600" />
                </div>
                <CardTitle className="text-2xl text-blue-600">
                  {modeInfo.socratic.name}
                </CardTitle>
                <p className="text-gray-600 mt-2">
                  {modeInfo.socratic.description}
                </p>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-gray-700 mb-4">
                  {modeInfo.socratic.extended_description}
                </p>
                <div className="mb-4">
                  <p className="font-semibold text-sm mb-2">Best for:</p>
                  <div className="flex flex-wrap gap-2">
                    {modeInfo.socratic.best_for.map((item, idx) => (
                      <Badge key={idx} variant="secondary" className="text-xs">
                        {item}
                      </Badge>
                    ))}
                  </div>
                </div>
                <div className="flex items-center justify-between text-sm text-gray-600">
                  <span>Style: {modeInfo.socratic.style}</span>
                  <span className="text-xs">Powered by {modeInfo.socratic.powered_by}</span>
                </div>
              </CardContent>
            </Card>

            {/* Claude Mode Card */}
            <Card 
              className="cursor-pointer transition-all hover:shadow-xl hover:scale-102 border-2 hover:border-purple-300"
              onClick={() => selectMode('claude')}
            >
              <CardHeader className="text-center pb-4">
                <div className="mx-auto mb-4 w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center">
                  <Zap className="w-8 h-8 text-purple-600" />
                </div>
                <CardTitle className="text-2xl text-purple-600">
                  {modeInfo.claude.name}
                </CardTitle>
                <p className="text-gray-600 mt-2">
                  {modeInfo.claude.description}
                </p>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-gray-700 mb-4">
                  {modeInfo.claude.extended_description}
                </p>
                <div className="mb-4">
                  <p className="font-semibold text-sm mb-2">Best for:</p>
                  <div className="flex flex-wrap gap-2">
                    {modeInfo.claude.best_for.map((item, idx) => (
                      <Badge key={idx} variant="secondary" className="text-xs">
                        {item}
                      </Badge>
                    ))}
                  </div>
                </div>
                <div className="flex items-center justify-between text-sm text-gray-600">
                  <span>Style: {modeInfo.claude.style}</span>
                  <span className="text-xs">Powered by {modeInfo.claude.powered_by}</span>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    );
  }

  // Chat Interface
  const currentModeInfo = selectedMode && modeInfo ? modeInfo[selectedMode] : null;
  const modeColor = selectedMode === 'socratic' ? 'blue' : 'purple';

  return (
    <div className="flex h-screen bg-gray-50">
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="bg-white border-b p-4 shadow-sm">
          <div className="flex items-center justify-between max-w-4xl mx-auto">
            <div className="flex items-center space-x-4">
              <div className={`w-10 h-10 bg-${modeColor}-100 rounded-full flex items-center justify-center`}>
                {currentModeInfo?.icon}
              </div>
              <div>
                <h1 className="text-xl font-semibold text-gray-800">
                  {currentModeInfo?.name}
                </h1>
                <p className="text-sm text-gray-600">
                  {currentModeInfo?.style}
                </p>
              </div>
            </div>
            <Button 
              variant="outline" 
              size="sm"
              onClick={resetChat}
            >
              Change Mode
            </Button>
          </div>
        </div>

        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto p-4">
          <div className="max-w-4xl mx-auto space-y-4">
            {messages.map((message) => (
              <div 
                key={message.id} 
                className={`flex ${message.isUser ? 'justify-end' : 'justify-start'}`}
              >
                <div className={`max-w-2xl p-4 rounded-lg ${
                  message.isUser 
                    ? 'bg-gray-800 text-white' 
                    : `bg-white border shadow-sm ${
                        message.mode === 'socratic' 
                          ? 'border-l-4 border-blue-500' 
                          : 'border-l-4 border-purple-500'
                      }`
                }`}>
                  <div className="whitespace-pre-wrap">
                    {message.text}
                  </div>
                  <div className={`text-xs mt-2 ${
                    message.isUser ? 'text-gray-400' : 'text-gray-500'
                  }`}>
                    {message.timestamp.toLocaleTimeString()}
                  </div>
                </div>
              </div>
            ))}
            
            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-white border rounded-lg p-4 shadow-sm">
                  <div className="flex items-center space-x-2">
                    <LoadingSpinner size="sm" />
                    <span className="text-sm text-gray-600">
                      {selectedMode === 'socratic' ? 'Thinking deeply...' : 'Preparing challenge...'}
                    </span>
                  </div>
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* Input Area */}
        <div className="border-t bg-white p-4">
          <div className="max-w-4xl mx-auto">
            <div className="flex space-x-2">
              <textarea
                ref={inputRef}
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder={
                  selectedMode === 'socratic' 
                    ? "Share your thoughts..." 
                    : "What's on your mind?"
                }
                className="flex-1 p-3 border rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-blue-500"
                rows={1}
                style={{ minHeight: '50px', maxHeight: '200px' }}
                disabled={isLoading}
              />
              <Button 
                onClick={sendMessage} 
                disabled={isLoading || !inputText.trim()}
                className={`px-6 ${
                  selectedMode === 'socratic' 
                    ? 'bg-blue-600 hover:bg-blue-700' 
                    : 'bg-purple-600 hover:bg-purple-700'
                }`}
              >
                <Send className="w-4 h-4" />
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SocraticChat;