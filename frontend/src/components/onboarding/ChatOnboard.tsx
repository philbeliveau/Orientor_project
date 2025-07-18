'use client';

import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, RefreshCw, Check } from 'lucide-react';
import { useOnboardingStore } from '../../stores/onboardingStore';
import { ChatMessage as ChatMessageType } from '../../types/onboarding';
import TypingIndicator from './TypingIndicator';
import PsychProfile from './PsychProfile';

interface ChatOnboardProps {
  onComplete?: (responses: any[]) => void;
  className?: string;
}

const ChatOnboard: React.FC<ChatOnboardProps> = ({ onComplete, className = '' }) => {
  const [inputValue, setInputValue] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  // Add custom styles to override global focus styles
  React.useEffect(() => {
    const style = document.createElement('style');
    style.textContent = `
      .onboarding-textarea:focus {
        outline: none !important;
        border: none !important;
        box-shadow: none !important;
        ring: none !important;
      }
    `;
    document.head.appendChild(style);
    
    return () => {
      if (document.head.contains(style)) {
        document.head.removeChild(style);
      }
    };
  }, []);
  
  const {
    messages,
    responses,
    currentQuestionIndex,
    isTyping,
    isComplete,
    psychProfile,
    addMessage,
    addResponse,
    nextQuestion,
    setTyping,
    reset,
    getCurrentQuestion,
    getProgress,
    startOnboarding,
    saveResponseToAPI,
    completeOnboarding,
    loadOnboardingStatus
  } = useOnboardingStore();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const focusInput = () => {
    if (inputRef.current && !isTyping && !isComplete) {
      inputRef.current.focus();
    }
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Auto-focus the input when component mounts or after typing stops
  useEffect(() => {
    const timer = setTimeout(() => {
      focusInput();
    }, 100);
    return () => clearTimeout(timer);
  }, [isTyping, isComplete]);

  // Paper-like interaction: focus input when clicking on page
  useEffect(() => {
    const handleClick = (e: MouseEvent) => {
      // Only re-focus if clicking in the main content area (not on buttons/header)
      const target = e.target as HTMLElement;
      if (!target.closest('button, a, input, textarea, .sticky') && 
          !isComplete && !isTyping) {
        setTimeout(focusInput, 50);
      }
    };

    const handleKeyDown = (e: KeyboardEvent) => {
      // Paper-like behavior: start typing anywhere on the page
      if (!isComplete && !isTyping && e.target !== inputRef.current) {
        // Don't interfere with form controls or special keys
        if (!e.ctrlKey && !e.metaKey && !e.altKey && 
            e.key !== 'Tab' && e.key !== 'F5' && !e.key.startsWith('F') &&
            e.key !== 'Escape' && e.key !== 'Backspace' && e.key !== 'Delete') {
          
          // Only capture printable characters
          if (e.key.length === 1) {
            e.preventDefault();
            focusInput();
            // Add the typed character to input
            if (inputRef.current) {
              const input = inputRef.current;
              const newValue = inputValue + e.key;
              setInputValue(newValue);
              // Set cursor to end
              setTimeout(() => {
                input.setSelectionRange(newValue.length, newValue.length);
              }, 0);
            }
          }
        }
      }
    };

    document.addEventListener('click', handleClick);
    document.addEventListener('keydown', handleKeyDown);

    return () => {
      document.removeEventListener('click', handleClick);
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [inputValue, isComplete, isTyping]);

  useEffect(() => {
    const initializeOnboarding = async () => {
      // Load existing onboarding status first
      await loadOnboardingStatus();
      
      // Start onboarding session if not complete
      await startOnboarding();
      
      if (currentQuestionIndex === 0) {
        // Show first question after welcome message
        setTimeout(() => {
          const firstQuestion = getCurrentQuestion();
          if (firstQuestion) {
            setTyping(true);
            setTimeout(() => {
              addMessage({
                type: 'system',
                content: firstQuestion.text
              });
              setTyping(false);
            }, 1500);
          }
        }, 1000);
      }
    };

    initializeOnboarding();
  }, []);

  useEffect(() => {
    if (isComplete && psychProfile) {
      console.log('ChatOnboard: Onboarding complete, calling onComplete callback');
      onComplete?.(responses);
    }
  }, [isComplete, psychProfile, responses, onComplete]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim()) return;

    const currentQuestion = getCurrentQuestion();
    if (!currentQuestion) return;

    // Add user message
    addMessage({
      type: 'user',
      content: inputValue.trim()
    });

    // Create response object
    const responseData = {
      questionId: currentQuestion.id,
      question: currentQuestion.text,
      response: inputValue.trim(),
      timestamp: new Date()
    };

    // Add response to store
    addResponse(responseData);

    // Save response to API
    await saveResponseToAPI(responseData);

    setInputValue('');

    // Show typing indicator
    setTyping(true);

    // Keep focus on input after submission
    setTimeout(focusInput, 50);

    // Simulate processing time
    setTimeout(() => {
      nextQuestion();
      
      const nextQ = getCurrentQuestion();
      if (nextQ) {
        // Add next question
        addMessage({
          type: 'system',
          content: nextQ.text
        });
      } else {
        // Generate psychological profile
        generatePsychProfile();
      }
      
      setTyping(false);
      // Re-focus input after typing stops
      setTimeout(focusInput, 100);
    }, 1500);
  };

  const generatePsychProfile = async () => {
    // Simple profile generation based on responses
    // In a real implementation, this would use ML models
    const profile = {
      hexaco: {
        extraversion: Math.random() * 100,
        openness: Math.random() * 100,
        conscientiousness: Math.random() * 100,
        emotionality: Math.random() * 100,
        agreeableness: Math.random() * 100,
        honesty: Math.random() * 100
      },
      riasec: {
        realistic: Math.random() * 100,
        investigative: Math.random() * 100,
        artistic: Math.random() * 100,
        social: Math.random() * 100,
        enterprising: Math.random() * 100,
        conventional: Math.random() * 100
      },
      topTraits: ['Creative', 'Analytical', 'Collaborative'],
      description: 'You have a unique blend of creativity and analytical thinking, with strong collaborative instincts.'
    };

    console.log('Generated psychological profile:', profile);
    useOnboardingStore.getState().setPsychProfile(profile);
    
    // Complete onboarding on the backend
    console.log('Calling completeOnboarding...');
    await completeOnboarding();
    console.log('Onboarding completion API call finished');
    
    addMessage({
      type: 'system',
      content: "Great! I've analyzed your responses and created your psychological profile. Let me show you some career recommendations based on your personality."
    });
  };

  const handleRefresh = () => {
    if (window.confirm('Are you sure you want to start over? This will clear all your responses.')) {
      reset();
    }
  };


  return (
    <div className={`min-h-screen bg-white flex flex-col ${className}`}>
      {/* Header */}
      <div className="sticky top-0 bg-white/95 backdrop-blur-sm border-b border-gray-100 p-6">
        <div className="flex items-center justify-between max-w-4xl mx-auto">
          <div className="flex-1">
            <div className="h-1 bg-gray-100 rounded-full overflow-hidden">
              <motion.div 
                className="h-full bg-blue-500"
                initial={{ width: 0 }}
                animate={{ width: `${getProgress()}%` }}
                transition={{ duration: 0.5 }}
              />
            </div>
          </div>
          <button
            onClick={handleRefresh}
            className="ml-6 p-2 text-gray-400 hover:text-blue-500 transition-colors rounded-full hover:bg-blue-50"
            title="Refresh and start over"
          >
            <RefreshCw size={18} />
          </button>
        </div>
      </div>

      {/* Paper-like Chat Interface */}
      <div className="flex-1 overflow-y-auto px-8 py-12">
        <div className="max-w-4xl mx-auto">
          <div className="space-y-8">
            <AnimatePresence mode="wait">
              {messages.map((message, index) => (
                <PaperMessage 
                  key={message.id} 
                  message={message} 
                  isLast={index === messages.length - 1}
                  onResponse={!isComplete && index === messages.length - 1 && message.type === 'system'}
                  inputRef={inputRef}
                  inputValue={inputValue}
                  setInputValue={setInputValue}
                  onSubmit={handleSubmit}
                  isTyping={isTyping}
                  focusInput={focusInput}
                />
              ))}
            </AnimatePresence>
            
            {isTyping && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                transition={{ duration: 0.6, ease: "easeOut" }}
                className="border-l-3 border-blue-500 pl-8 py-2"
              >
                <TypingIndicator />
              </motion.div>
            )}

            {isComplete && psychProfile && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.5 }}
              >
                <PsychProfile profile={psychProfile} />
              </motion.div>
            )}
            
            <div ref={messagesEndRef} />
          </div>
        </div>
      </div>

      {/* Finish Button */}
      {isComplete && (
        <div className="sticky bottom-0 bg-white/95 backdrop-blur-sm border-t border-gray-200 p-4">
          <div className="max-w-4xl mx-auto">
            <button
              onClick={() => onComplete?.(responses)}
              className="w-full bg-blue-500 text-white py-3 px-6 rounded-2xl 
                hover:bg-blue-600 transition-colors flex items-center justify-center space-x-2"
            >
              <Check size={20} />
              <span>Complete Onboarding</span>
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

// Paper Message Component - mimics writing on paper
interface PaperMessageProps {
  message: ChatMessageType;
  isLast: boolean;
  onResponse: boolean;
  inputRef: React.RefObject<HTMLTextAreaElement>;
  inputValue: string;
  setInputValue: (value: string) => void;
  onSubmit: (e: React.FormEvent) => void;
  isTyping: boolean;
  focusInput: () => void;
}

const PaperMessage: React.FC<PaperMessageProps> = ({ 
  message, 
  isLast, 
  onResponse, 
  inputRef, 
  inputValue, 
  setInputValue, 
  onSubmit, 
  isTyping,
  focusInput 
}) => {
  const isSystem = message.type === 'system';
  
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, ease: "easeOut" }}
      className="space-y-8"
    >
      {/* System message with elegant blue accent */}
      {isSystem && (
        <motion.div 
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.8, delay: 0.2, ease: "easeOut" }}
          className="border-l-3 border-blue-500 pl-8 py-2"
        >
          <p className="text-xl leading-relaxed text-blue-600 font-light tracking-wide">
            {message.content}
          </p>
        </motion.div>
      )}
      
      {/* User message as elegant plain text */}
      {!isSystem && (
        <motion.div 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5 }}
          className="pl-4 py-1"
        >
          <p className="text-xl leading-relaxed text-gray-800 font-light tracking-wide">
            {message.content}
          </p>
        </motion.div>
      )}
      
      {/* Elegant inline input for current question */}
      {onResponse && isSystem && (
        <motion.div 
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.4 }}
          className="pl-4 py-2"
        >
          <form onSubmit={onSubmit} className="w-full">
            <textarea
              ref={inputRef}
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder="Write here.."
              className="onboarding-textarea w-full text-xl leading-relaxed text-gray-800 placeholder-gray-400 
                bg-transparent border-none outline-none resize-none font-light tracking-wide
                focus:text-gray-900 transition-all duration-300 min-h-[2.5rem]
                focus:placeholder-gray-300"
              rows={1}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  onSubmit(e);
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
              onBlur={(e) => {
                // Prevent loss of focus unless clicking on interactive elements
                const relatedTarget = e.relatedTarget as HTMLElement;
                if (!relatedTarget || !relatedTarget.closest('button, a, input, textarea')) {
                  setTimeout(focusInput, 50);
                }
              }}
              disabled={isTyping}
              autoFocus
              style={{ minHeight: '2.5rem' }}
            />
          </form>
        </motion.div>
      )}
    </motion.div>
  );
};

export default ChatOnboard;