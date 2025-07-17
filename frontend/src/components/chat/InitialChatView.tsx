'use client';

import React from 'react';
import { MessageSquare } from 'lucide-react';
import ChatModeSelector, { ChatMode } from './ChatModeSelector';
import ConversationList from './ConversationList';

interface Conversation {
  id: number;
  title: string;
  auto_generated_title: boolean;
  category_id: number | null;
  is_favorite: boolean;
  is_archived: boolean;
  created_at: string;
  updated_at: string;
  last_message_at: string | null;
  message_count: number;
  total_tokens_used: number;
}

interface InitialChatViewProps {
  inputText: string;
  setInputText: (text: string) => void;
  handleSend: () => void;
  isTyping: boolean;
  chatMode: ChatMode;
  setChatMode: (mode: ChatMode) => void;
  showConversations: boolean;
  setShowConversations: (show: boolean) => void;
  handleSelectConversation: (conversation: Conversation) => void;
  handleCreateNewConversation: () => void;
  currentConversation: Conversation | null;
  refreshConversationList: number;
  inputRef: React.RefObject<HTMLTextAreaElement>;
}

export default function InitialChatView({
  inputText,
  setInputText,
  handleSend,
  isTyping,
  chatMode,
  setChatMode,
  showConversations,
  setShowConversations,
  handleSelectConversation,
  handleCreateNewConversation,
  currentConversation,
  refreshConversationList,
  inputRef
}: InitialChatViewProps) {
  return (
    <div className="min-h-screen bg-white flex flex-col">
      {/* Header with conversations history icon */}
      <div className="sticky top-0 bg-white/95 backdrop-blur-sm border-b border-gray-100 p-6">
        <div className="flex items-center justify-between max-w-4xl mx-auto">
          <div className="flex-1">
            <h1 className="text-2xl font-light text-gray-800 tracking-wide">Chat</h1>
          </div>
          <button
            onClick={() => setShowConversations(true)}
            className="p-2 text-gray-400 hover:text-blue-500 transition-colors rounded-full hover:bg-blue-50"
            title="View conversation history"
            aria-label="View conversation history"
          >
            <MessageSquare className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* Paper-like Chat Interface */}
      <div className="flex-1 overflow-y-auto px-8 py-12">
        <div className="max-w-4xl mx-auto">
          <div className="space-y-8">
            {/* Welcome prompt with mode selection */}
            <div className="border-l-3 border-blue-500 pl-8 py-2">
              <p className="text-xl leading-relaxed text-blue-600 font-light tracking-wide">
                What would you like to talk about today?
              </p>
              
              {/* Mode Selection */}
              <div className="mt-6 flex gap-3 flex-wrap">
                <button
                  onClick={() => setChatMode('default')}
                  className={`px-4 py-2 rounded-lg transition-all ${
                    chatMode === 'default' 
                      ? 'bg-blue-100 text-blue-700 ring-2 ring-blue-300' 
                      : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                  }`}
                  aria-pressed={chatMode === 'default'}
                >
                  <span className="font-medium">Default</span>
                  <span className="block text-xs mt-1">Helpful assistant</span>
                </button>
                
                <button
                  onClick={() => setChatMode('socratic')}
                  className={`px-4 py-2 rounded-lg transition-all ${
                    chatMode === 'socratic' 
                      ? 'bg-blue-100 text-blue-700 ring-2 ring-blue-300' 
                      : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                  }`}
                  aria-pressed={chatMode === 'socratic'}
                >
                  <span className="font-medium">Socratic</span>
                  <span className="block text-xs mt-1">Discover through questions</span>
                </button>
                
                <button
                  onClick={() => setChatMode('claude')}
                  className={`px-4 py-2 rounded-lg transition-all ${
                    chatMode === 'claude' 
                      ? 'bg-purple-100 text-purple-700 ring-2 ring-purple-300' 
                      : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                  }`}
                  aria-pressed={chatMode === 'claude'}
                >
                  <span className="font-medium">Claude</span>
                  <span className="block text-xs mt-1">Bold challenges</span>
                </button>
              </div>
            </div>
            
            {/* Paper-like input area */}
            <div className="pl-4 py-2">
              <form onSubmit={(e) => { e.preventDefault(); handleSend(); }} className="w-full">
                <textarea
                  ref={inputRef}
                  value={inputText}
                  onChange={(e) => setInputText(e.target.value)}
                  placeholder="Write here.."
                  className="w-full text-xl leading-relaxed text-gray-800 placeholder-gray-300 
                    bg-transparent border-none outline-none resize-none font-light tracking-wide
                    focus:text-gray-900 transition-all duration-300 min-h-[2.5rem]
                    focus:placeholder-gray-200 focus:outline-none focus:ring-0 focus:border-none"
                  rows={1}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                      e.preventDefault();
                      handleSend();
                    }
                    // Auto-resize textarea
                    const target = e.target as HTMLTextAreaElement;
                    target.style.height = 'auto';
                    target.style.height = `${target.scrollHeight}px`;
                  }}
                  onInput={(e) => {
                    // Auto-resize textarea
                    const target = e.target as HTMLTextAreaElement;
                    target.style.height = 'auto';
                    target.style.height = `${target.scrollHeight}px`;
                  }}
                  disabled={isTyping}
                  autoFocus
                  style={{ minHeight: '2.5rem' }}
                  aria-label="Type your message"
                />
              </form>
            </div>
          </div>
        </div>
      </div>

      {/* Conversations History Modal */}
      {showConversations && (
        <>
          <div 
            className="fixed inset-0 bg-black bg-opacity-50 z-40"
            onClick={() => setShowConversations(false)}
          />
          <div className="fixed top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-96 max-w-90vw max-h-80vh bg-white rounded-lg shadow-xl z-50 overflow-hidden">
            <div className="p-4 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-medium text-gray-800">Conversation History</h3>
                <button
                  onClick={() => setShowConversations(false)}
                  className="p-1 text-gray-400 hover:text-gray-600 rounded"
                  aria-label="Close conversation history"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>
            <div className="p-4 max-h-96 overflow-y-auto">
              <ConversationList
                selectedConversationId={currentConversation?.id}
                onSelectConversation={(conversation) => {
                  handleSelectConversation(conversation);
                  setShowConversations(false);
                }}
                onCreateNew={() => {
                  handleCreateNewConversation();
                  setShowConversations(false);
                }}
                refreshTrigger={refreshConversationList}
              />
            </div>
          </div>
        </>
      )}
    </div>
  );
}