'use client';

import React from 'react';
import { Plus, MessageSquare } from 'lucide-react';
import ChatModeSelector, { ChatMode } from './ChatModeSelector';

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

interface ChatHeaderProps {
  currentConversation: Conversation | null;
  isEditingTitle: boolean;
  editingTitleValue: string;
  setEditingTitleValue: (value: string) => void;
  handleTitleEdit: () => void;
  handleTitleSave: () => void;
  setIsEditingTitle: (editing: boolean) => void;
  setShowConversations: (show: boolean) => void;
  handleCreateNewConversation: () => void;
  chatMode: ChatMode;
  setChatMode: (mode: ChatMode) => void;
  showModeSelector: boolean;
  setShowModeSelector: (show: boolean) => void;
  enableOrientator?: boolean;
}

export default function ChatHeader({
  currentConversation,
  isEditingTitle,
  editingTitleValue,
  setEditingTitleValue,
  handleTitleEdit,
  handleTitleSave,
  setIsEditingTitle,
  setShowConversations,
  handleCreateNewConversation,
  chatMode,
  setChatMode,
  showModeSelector,
  setShowModeSelector,
  enableOrientator = false
}: ChatHeaderProps) {
  return (
    <div className="sticky top-0 bg-white/95 backdrop-blur-sm border-b border-gray-100 p-6">
      <div className="flex items-center justify-between max-w-4xl mx-auto">
        <div className="flex-1">
          {isEditingTitle ? (
            <input
              type="text"
              value={editingTitleValue}
              onChange={(e) => setEditingTitleValue(e.target.value)}
              onBlur={handleTitleSave}
              onKeyDown={(e) => {
                if (e.key === 'Enter') {
                  handleTitleSave();
                } else if (e.key === 'Escape') {
                  setIsEditingTitle(false);
                  setEditingTitleValue('');
                }
              }}
              className="text-2xl font-light text-gray-800 tracking-wide bg-transparent border-none outline-none focus:outline-none focus:ring-0 focus:border-none w-full"
              autoFocus
              aria-label="Edit conversation title"
            />
          ) : (
            <h1 
              className="text-2xl font-light text-gray-800 tracking-wide cursor-pointer hover:text-blue-600 hover:bg-blue-50 px-2 py-1 rounded transition-all duration-200"
              onClick={handleTitleEdit}
              title="Click to edit conversation name"
              role="button"
              tabIndex={0}
              onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                  handleTitleEdit();
                }
              }}
            >
              {currentConversation?.title || 'Chat'}
              <span className="ml-2 text-gray-400 opacity-0 hover:opacity-100 transition-opacity text-sm">✏️</span>
            </h1>
          )}
        </div>
        
        <div className="flex items-center gap-2">
          <ChatModeSelector
            chatMode={chatMode}
            setChatMode={setChatMode}
            showModeSelector={showModeSelector}
            setShowModeSelector={setShowModeSelector}
            enableOrientator={enableOrientator}
          />
          
          <button
            onClick={() => setShowConversations(true)}
            className="p-2 text-gray-400 hover:text-blue-500 transition-colors rounded-full hover:bg-blue-50"
            title="View conversation history"
            aria-label="View conversation history"
          >
            <MessageSquare className="w-5 h-5" />
          </button>
          
          <button
            onClick={handleCreateNewConversation}
            className="p-2 text-gray-400 hover:text-blue-500 transition-colors rounded-full hover:bg-blue-50"
            title="New conversation"
            aria-label="Start new conversation"
          >
            <Plus className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  );
}