'use client';

import React from 'react';

export type ChatMode = 'default' | 'socratic' | 'claude';

interface ChatModeSelectorProps {
  chatMode: ChatMode;
  setChatMode: (mode: ChatMode) => void;
  showModeSelector: boolean;
  setShowModeSelector: (show: boolean) => void;
  enableOrientator?: boolean;
}

export default function ChatModeSelector({
  chatMode,
  setChatMode,
  showModeSelector,
  setShowModeSelector,
  enableOrientator = false
}: ChatModeSelectorProps) {
  const getModeColor = (mode: ChatMode) => {
    switch (mode) {
      case 'claude': return 'bg-purple-100 text-purple-700';
      case 'socratic': return 'bg-blue-100 text-blue-700';
      default: return 'bg-blue-100 text-blue-700';
    }
  };

  const getModeLabel = (mode: ChatMode) => {
    switch (mode) {
      case 'default': return 'Default';
      case 'socratic': return 'Socratic';
      case 'claude': return 'Claude';
    }
  };

  const getModeDescription = (mode: ChatMode) => {
    switch (mode) {
      case 'default': return 'Helpful assistant';
      case 'socratic': return 'Discover through questions';
      case 'claude': return 'Bold challenges';
    }
  };

  return (
    <div className="relative">
      {/* Orientator Mode Indicator */}
      {enableOrientator && (
        <div className="px-2 py-1 bg-green-100 text-green-700 text-xs font-medium rounded-full border border-green-200 mr-2 inline-block">
          🤖 Orientator AI
        </div>
      )}
      
      {/* Mode Selector Button */}
      <button
        onClick={() => setShowModeSelector(!showModeSelector)}
        className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-all ${getModeColor(chatMode)} hover:opacity-80`}
        aria-label={`Current mode: ${getModeLabel(chatMode)}. Click to change mode.`}
      >
        {getModeLabel(chatMode)}
      </button>
      
      {/* Mode Dropdown */}
      {showModeSelector && (
        <>
          {/* Backdrop */}
          <div 
            className="fixed inset-0 z-10" 
            onClick={() => setShowModeSelector(false)}
          />
          
          {/* Dropdown Menu */}
          <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-200 z-20">
            <div className="py-1">
              {(['default', 'socratic', 'claude'] as ChatMode[]).map((mode) => (
                <button
                  key={mode}
                  onClick={() => { 
                    setChatMode(mode); 
                    setShowModeSelector(false); 
                  }}
                  className={`w-full text-left px-4 py-2 hover:bg-gray-100 transition-colors ${
                    mode === 'default' ? 'rounded-t-lg' : 
                    mode === 'claude' ? 'rounded-b-lg' : ''
                  } ${chatMode === mode ? 'bg-gray-50' : ''}`}
                >
                  <div className="font-medium">{getModeLabel(mode)}</div>
                  <div className="text-xs text-gray-600">{getModeDescription(mode)}</div>
                </button>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  );
}