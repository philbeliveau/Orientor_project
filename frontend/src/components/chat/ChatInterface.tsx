'use client';

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import axios from 'axios';
import ChatMessage from './ChatMessage';
import ConversationList from './ConversationList';
import ConversationManager from './ConversationManager';
import SearchInterface from './SearchInterface';
import CategoryManager from './CategoryManager';
import AnalyticsDashboard from './AnalyticsDashboard';
import { Menu, Search, Folder, BarChart3, Plus } from 'lucide-react';
import styles from './ChatBot.module.css';
import { MessageComponentRenderer, MessageComponent, ComponentAction, MessageComponentType } from './MessageComponent';

interface Message {
  id: number;
  role: 'user' | 'assistant' | 'system';
  content: string;
  created_at: string;
  tokens_used?: number;
  components?: MessageComponent[];
  metadata?: {
    tools_invoked?: string[];
    processing_time_ms?: number;
    confidence_score?: number;
  };
}

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

interface Category {
  id: number;
  name: string;
  description: string | null;
  color: string | null;
  conversation_count: number;
  created_at: string;
}

interface ChatInterfaceProps {
  currentUserId: number;
  enableOrientator?: boolean;
}

// Paper Chat Message Component - mimics writing on paper
interface PaperChatMessageProps {
  message: Message;
  isLast: boolean;
  chatMode: ChatMode;
  onComponentAction?: (action: ComponentAction, componentId: string) => void;
}

const PaperChatMessage: React.FC<PaperChatMessageProps> = ({ message, isLast, chatMode, onComponentAction }) => {
  const isUser = message.role === 'user';
  
  // Debug logging for message rendering
  if (!isUser && message.components && message.components.length > 0) {
    console.log('🎨 Rendering message with', message.components.length, 'components');
    console.log('🧩 Component types:', message.components.map(c => c.type));
  }
  
  return (
    <div className="space-y-4">
      {/* AI/System message with mode-specific accent */}
      {!isUser && (
        <div>
          <div className={`border-l-3 pl-8 py-2 ${
            chatMode === 'claude' 
              ? 'border-purple-500' 
              : 'border-blue-500'
          }`}>
            <p className={`text-xl leading-relaxed font-light tracking-wide ${
              chatMode === 'claude' 
                ? 'text-purple-600' 
                : 'text-blue-600'
            }`}>
              {message.content}
            </p>
          </div>
          {/* Render message components if present */}
          {message.components && message.components.length > 0 && (
            <div className="mt-4 space-y-3 pl-8">
              {message.components.map((component, index) => (
                <MessageComponentRenderer
                  key={component.id || index}
                  component={component}
                  onAction={onComponentAction || (() => {})}
                />
              ))}
            </div>
          )}
        </div>
      )}
      
      {/* User message as elegant plain text */}
      {isUser && (
        <div className="pl-4 py-1">
          <p className="text-xl leading-relaxed text-gray-800 font-light tracking-wide">
            {message.content}
          </p>
        </div>
      )}
    </div>
  );
};

type ChatMode = 'default' | 'socratic' | 'claude';

export default function ChatInterface({ currentUserId, enableOrientator = false }: ChatInterfaceProps) {
  
  console.log('🔧 ChatInterface initialized with:');
  console.log('   currentUserId:', currentUserId);
  console.log('   enableOrientator:', enableOrientator);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [currentConversation, setCurrentConversation] = useState<Conversation | null>(null);
  const [selectedCategory, setSelectedCategory] = useState<Category | null>(null);
  const [showSidebar, setShowSidebar] = useState(false);
  const [showSearch, setShowSearch] = useState(false);
  const [showCategories, setShowCategories] = useState(false);
  const [showAnalytics, setShowAnalytics] = useState(false);
  const [sidebarView, setSidebarView] = useState<'conversations' | 'categories' | 'analytics'>('conversations');
  const [refreshConversationList, setRefreshConversationList] = useState(0);
  const [chatStarted, setChatStarted] = useState(false);
  const [showConversations, setShowConversations] = useState(false);
  const [isEditingTitle, setIsEditingTitle] = useState(false);
  const [editingTitleValue, setEditingTitleValue] = useState('');
  const [chatMode, setChatMode] = useState<ChatMode>(() => {
    // Restore chat mode from localStorage
    if (typeof window !== 'undefined') {
      const savedMode = localStorage.getItem('chat_mode');
      return (savedMode as ChatMode) || 'default';
    }
    return 'default';
  });
  const [showModeSelector, setShowModeSelector] = useState(false);
  
  const router = useRouter();
  const searchParams = useSearchParams();
  const inputRef = useRef<HTMLTextAreaElement>(null);

  // Persist chat mode changes to localStorage
  useEffect(() => {
    if (typeof window !== 'undefined') {
      localStorage.setItem('chat_mode', chatMode);
    }
  }, [chatMode]);

  // Handle component actions from Orientator messages
  const handleComponentAction = useCallback(async (action: ComponentAction, componentId: string) => {
    console.log('Component action:', action, 'for component:', componentId);
    
    const token = localStorage.getItem('access_token');
    if (!token) {
      router.push('/login');
      return;
    }

    try {
      switch (action.type) {
        case 'save':
          const saveResponse = await axios.post(
            `${process.env.NEXT_PUBLIC_API_URL}/api/orientator/save-component`,
            {
              component_id: componentId,
              conversation_id: currentConversation?.id,
              ...action.params
            },
            {
              headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
              }
            }
          );
          
          // Add save confirmation message
          const confirmationMessage: Message = {
            id: Date.now(),
            role: 'system',
            content: '',
            created_at: new Date().toISOString(),
            components: [{
              id: `save-confirm-${Date.now()}`,
              type: MessageComponentType.SAVE_CONFIRMATION,
              data: saveResponse.data,
              actions: [],
              saved: true
            }]
          };
          
          setMessages(prev => [...prev, confirmationMessage]);
          break;
          
        case 'explore':
        case 'start':
          // Handle exploration or start actions
          if (action.endpoint) {
            const response = await axios.post(
              `${process.env.NEXT_PUBLIC_API_URL}${action.endpoint}`,
              action.params,
              {
                headers: {
                  'Authorization': `Bearer ${token}`,
                  'Content-Type': 'application/json'
                }
              }
            );
            // Handle response based on action type
          }
          break;
          
        default:
          console.log('Unhandled action type:', action.type);
      }
    } catch (error) {
      console.error('Failed to handle component action:', error);
    }
  }, [currentConversation, router]);

  // Load conversation when selected
  useEffect(() => {
    if (currentConversation) {
      loadConversationMessages();
      setChatStarted(true); // Show full chat interface when conversation is loaded
    }
  }, [currentConversation?.id]);

  // Check if chat should be started based on messages
  useEffect(() => {
    if (messages && messages.filter(m => m.role !== 'system').length > 0) {
      setChatStarted(true);
    }
  }, [messages]);

  // Handle initial message from URL parameters
  useEffect(() => {
    const initialMessage = searchParams?.get('initial_message');
    const messageType = searchParams?.get('type');
    
    if (initialMessage && !currentConversation && messages.length === 0) {
      // Decode the message and set it as the input text
      const decodedMessage = decodeURIComponent(initialMessage);
      setInputText(decodedMessage);
      setChatStarted(true);
      
      // Focus the input field
      setTimeout(() => {
        if (inputRef.current) {
          inputRef.current.focus();
        }
      }, 100);
    }
  }, [searchParams, currentConversation, messages.length]);

  const loadConversationMessages = async () => {
    if (!currentConversation) {
      console.log('No current conversation to load messages for');
      return;
    }
    
    console.log('Loading messages for conversation:', currentConversation.id);
    
    try {
      // Use Orientator endpoint if enabled to get messages with components
      const endpoint = enableOrientator 
        ? `${process.env.NEXT_PUBLIC_API_URL}/orientator/conversations/${currentConversation.id}/messages`
        : `${process.env.NEXT_PUBLIC_API_URL}/chat/conversations/${currentConversation.id}/messages`;
        
      const response = await axios.get(endpoint, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });

      console.log('Messages API response:', response.data);
      
      // Handle different response formats
      let messagesData;
      if (response.data.messages) {
        // Unified format with components support
        messagesData = response.data.messages.map((msg: any) => ({
          id: msg.id,
          role: msg.role,
          content: msg.content,
          created_at: msg.created_at,
          components: msg.components || [],
          metadata: msg.metadata,
          tokens_used: msg.tokens_used
        }));
        console.log('Using unified format - Number of messages loaded:', messagesData.length);
      } else if (Array.isArray(response.data)) {
        // Legacy format from chat_router (fallback)
        messagesData = response.data;
        console.log('Using legacy format - Number of messages loaded:', messagesData.length);
      } else {
        console.warn('Unexpected response format:', response.data);
        messagesData = [];
      }
      
      setMessages(messagesData);
    } catch (error) {
      console.error('Failed to load conversation messages:', error);
      // Fallback to regular chat endpoint if Orientator endpoint fails
      if (enableOrientator) {
        try {
          const fallbackResponse = await axios.get(
            `${process.env.NEXT_PUBLIC_API_URL}/chat/conversations/${currentConversation.id}/messages`,
            {
              headers: {
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`
              }
            }
          );
          
          const fallbackData = Array.isArray(fallbackResponse.data) 
            ? fallbackResponse.data 
            : fallbackResponse.data.messages || [];
          setMessages(fallbackData);
          console.log('Loaded messages using fallback endpoint');
        } catch (fallbackError) {
          console.error('Both Orientator and fallback endpoints failed:', fallbackError);
          setMessages([]);
        }
      } else {
        setMessages([]);
      }
    }
  };

  const handleSend = async () => {
    if (!inputText.trim() || isTyping) return;

    const token = localStorage.getItem('access_token');
    if (!token) {
      router.push('/login');
      return;
    }

    setIsTyping(true);
    const userMessage = inputText;
    setInputText('');

    try {
      // If no conversation exists, create one and wait for completion
      let conversationId = currentConversation?.id;
      let conversationToUse = currentConversation;
      
      console.log('handleSend - currentConversation:', currentConversation);
      console.log('handleSend - conversationId:', conversationId);
      
      if (!conversationId && (chatMode === 'default' || (enableOrientator && chatMode === 'default'))) {
        // Create conversation for default mode or when Orientator is enabled for default mode
        // For Socratic/Claude modes, conversation creation is handled by the service
        console.log('No conversation ID found, creating new conversation');
        const createResponse = await axios.post(
          `${process.env.NEXT_PUBLIC_API_URL}/chat/conversations`,
          {
            initial_message: userMessage,
            category_id: selectedCategory?.id
          },
          {
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json'
            }
          }
        );
        
        conversationId = createResponse.data.id;
        conversationToUse = createResponse.data;
        
        // Update state and wait for it to propagate  
        setCurrentConversation(conversationToUse);
        // Trigger conversation list refresh
        setRefreshConversationList(prev => prev + 1);
        
        // Small delay to ensure state has propagated
        await new Promise(resolve => setTimeout(resolve, 100));
      }

      // Send message to appropriate endpoint based on chat mode
      let endpoint: string;
      let requestBody: any;
      let headers: any;
      
      console.log('🔍 DEBUGGING ROUTING:');
      console.log('   enableOrientator:', enableOrientator);
      console.log('   chatMode:', chatMode);
      console.log('   chatMode === "socratic":', chatMode === 'socratic');
      console.log('   chatMode === "claude":', chatMode === 'claude');
      console.log('   enableOrientator && chatMode === "default":', enableOrientator && chatMode === 'default');
      
      if (enableOrientator && chatMode === 'default') {
        console.log('🟡 TAKING ORIENTATOR PATH (default mode)');
        // Use Orientator endpoint only for default mode when enabled
        endpoint = `${process.env.NEXT_PUBLIC_API_URL}/api/orientator/test-message`;
        requestBody = { message: userMessage };
        headers = { 'Content-Type': 'application/json' };
      } else if (chatMode === 'socratic' || chatMode === 'claude') {
        console.log('🟢 TAKING SOCRATIC CHAT PATH (socratic/claude mode)');
        // Use Socratic Chat Service for Socratic and Claude modes
        endpoint = `${process.env.NEXT_PUBLIC_API_URL}/api/v1/socratic-chat/send`;
        requestBody = {
          text: userMessage,
          mode: chatMode,
          conversation_id: conversationId
        };
        headers = {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        };
      } else {
        console.log('🔵 TAKING REGULAR CHAT PATH (fallback default mode)');
        // Use regular chat endpoint for default mode
        endpoint = `${process.env.NEXT_PUBLIC_API_URL}/chat/conversations/send/${conversationId}`;
        requestBody = {
          message: userMessage,
          mode: chatMode
        };
        headers = {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        };
      }
      
      console.log('🚀 Sending message to endpoint:', endpoint);
      console.log('🤖 Orientator enabled:', enableOrientator);
      console.log('💬 Chat mode:', chatMode);
      console.log('💬 Message payload:', requestBody);
        
      const response = await axios.post(endpoint, requestBody, { headers });
      
      console.log('📨 Response received:', response.data);
      console.log('🔍 Response has message_id:', !!response.data.message_id);
      console.log('🧩 Response has components:', !!response.data.components, response.data.components?.length || 0);
      
      // Add both user and assistant messages
      let newMessages: Message[] = [];
      
      console.log('🔍 Checking response format:');
      console.log('   enableOrientator:', enableOrientator);
      console.log('   chatMode:', chatMode);
      console.log('   response.data.message_id:', response.data.message_id);
      console.log('   response.data.success:', response.data.success);
      
      if (enableOrientator && chatMode === 'default' && response.data.message_id) {
        // Orientator format with components - single message response
        console.log('✅ Using Orientator format!');
        newMessages = [
          {
            id: Date.now(), // User message ID
            role: 'user',
            content: userMessage,
            created_at: new Date().toISOString()
          },
          {
            id: response.data.message_id,
            role: response.data.role,
            content: response.data.content,
            created_at: response.data.created_at,
            components: response.data.components,
            metadata: response.data.metadata,
            tokens_used: response.data.tokens_used
          }
        ];
        
        console.log('✅ Created Orientator messages:', newMessages.length);
        console.log('🎨 Assistant message components:', newMessages[1]?.components?.length || 0);
        if (newMessages[1]?.components && newMessages[1].components.length > 0) {
          newMessages[1].components.forEach((comp, i) => {
            console.log(`   ${i+1}. ${comp.type} component with ${comp.actions?.length || 0} actions`);
          });
        }
      } else if ((chatMode === 'socratic' || chatMode === 'claude') && response.data.success) {
        // Socratic Chat Service format
        console.log('✅ Using Socratic Chat format!');
        newMessages = [
          {
            id: Date.now(), // User message ID
            role: 'user',
            content: userMessage,
            created_at: new Date().toISOString()
          },
          {
            id: response.data.message_id,
            role: 'assistant',
            content: response.data.response,
            created_at: new Date().toISOString(),
            tokens_used: response.data.tokens_used
          }
        ];
        
        // Update conversationId if it's a new conversation
        if (!conversationId && response.data.conversation_id) {
          // Update the conversation in state
          conversationToUse = { 
            ...conversationToUse,
            id: response.data.conversation_id 
          } as Conversation;
          setCurrentConversation(conversationToUse);
        }
        
        console.log('✅ Created Socratic Chat messages:', newMessages.length);
      } else {
        // Standard chat format
        console.log('✅ Using standard chat format!');
        newMessages = [
          {
            id: response.data.user_message_id || Date.now(),
            role: 'user',
            content: userMessage,
            created_at: new Date().toISOString()
          },
          {
            id: response.data.assistant_message_id || response.data.message_id,
            role: 'assistant',
            content: response.data.response,
            created_at: new Date().toISOString(),
            tokens_used: response.data.tokens_used
          }
        ];
      }
      
      setMessages(prev => [...prev, ...newMessages]);
      setChatStarted(true); // Transition to full chat interface after sending first message
    } catch (error: any) {
      console.error('Failed to send message:', error);
      
      if (error.response?.status === 401) {
        router.push('/login');
        return;
      }
      
      // Show error message
      const errorMsg: Message = {
        id: Date.now(),
        role: 'system',
        content: "Sorry, I'm having trouble connecting. Please try again.",
        created_at: new Date().toISOString()
      };
      
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setIsTyping(false);
      // Keep focus on input after sending message
      setTimeout(() => {
        inputRef.current?.focus();
      }, 100);
    }
  };

  const handleSelectConversation = (conversation: Conversation) => {
    setCurrentConversation(conversation);
    setShowSidebar(false); // Always hide sidebar when selecting conversation
  };

  const handleCreateNewConversation = () => {
    setCurrentConversation(null);
    setMessages([]);
    setSelectedCategory(null);
    setChatStarted(false); // Reset to initial state
    setShowConversations(false);
    setShowSidebar(false); // Always hide sidebar when creating new conversation
    // Focus on input for new conversation
    setTimeout(() => {
      inputRef.current?.focus();
    }, 100);
  };

  const handleSearchResult = (conversationId: number, messageId: number) => {
    // Load the conversation and scroll to the message
    axios.get(
      `${process.env.NEXT_PUBLIC_API_URL}/chat/conversations/${conversationId}`,
      {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      }
    ).then(response => {
      setCurrentConversation(response.data);
      setShowSearch(false);
      
      // After messages load, scroll to the specific message
      setTimeout(() => {
        const messageElement = document.getElementById(`message-${messageId}`);
        if (messageElement) {
          messageElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
          messageElement.classList.add('bg-yellow-100', 'dark:bg-yellow-900/20');
          setTimeout(() => {
            messageElement.classList.remove('bg-yellow-100', 'dark:bg-yellow-900/20');
          }, 2000);
        }
      }, 500);
    });
  };

  const handleArchiveConversation = async () => {
    if (!currentConversation) return;
    
    try {
      await axios.post(
        `${process.env.NEXT_PUBLIC_API_URL}/chat/conversations/${currentConversation.id}/archive`,
        {},
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
          }
        }
      );
      
      // Refresh conversation list
      window.location.reload();
    } catch (error) {
      console.error('Failed to archive conversation:', error);
    }
  };

  const handleDeleteConversation = async () => {
    if (!currentConversation) return;
    
    try {
      await axios.delete(
        `${process.env.NEXT_PUBLIC_API_URL}/chat/conversations/${currentConversation.id}`,
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
          }
        }
      );
      
      setCurrentConversation(null);
      setMessages([]);
      window.location.reload();
    } catch (error) {
      console.error('Failed to delete conversation:', error);
    }
  };

  const handleTitleUpdate = (newTitle: string) => {
    if (currentConversation) {
      setCurrentConversation({ ...currentConversation, title: newTitle });
    }
  };

  const handleTitleEdit = () => {
    if (currentConversation) {
      setEditingTitleValue(currentConversation.title);
      setIsEditingTitle(true);
    }
  };

  const handleTitleSave = async () => {
    if (!currentConversation || !editingTitleValue.trim()) {
      setIsEditingTitle(false);
      setEditingTitleValue('');
      return;
    }

    const newTitle = editingTitleValue.trim();
    if (newTitle === currentConversation.title) {
      setIsEditingTitle(false);
      setEditingTitleValue('');
      return;
    }

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/chat/conversations/${currentConversation.id}`,
        {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
          },
          body: JSON.stringify({ title: newTitle })
        }
      );

      console.log('Title update response status:', response.status);
      
      if (response.ok) {
        const responseData = await response.json();
        console.log('Title update response data:', responseData);
        
        // Update local state
        setCurrentConversation({ ...currentConversation, title: newTitle });
        setIsEditingTitle(false);
        setEditingTitleValue('');
        
        // Trigger conversation list refresh to show updated title
        setRefreshConversationList(prev => prev + 1);
        
        console.log('Title successfully updated to:', newTitle);
      } else {
        const errorData = await response.text();
        console.error('Failed to update title. Status:', response.status, 'Response:', errorData);
        throw new Error(`HTTP ${response.status}: ${errorData}`);
      }
      
    } catch (error) {
      console.error('Failed to update conversation title:', error);
      
      // Revert to original title on error
      setIsEditingTitle(false);
      setEditingTitleValue('');
      
      // Show error message to user
      alert('Failed to update conversation title. Please try again.');
    }
  };

  if (!chatStarted && !currentConversation) {
    // Paper-like initial state
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
            >
              <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
                <path d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
              </svg>
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
                <div className="mt-6 flex gap-3">
                  <button
                    onClick={() => setChatMode('default')}
                    className={`px-4 py-2 rounded-lg transition-all ${
                      chatMode === 'default' 
                        ? 'bg-blue-100 text-blue-700 ring-2 ring-blue-300' 
                        : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                    }`}
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
                  />
                </form>
              </div>
            </div>
          </div>
        </div>

        {/* Conversations History Popup */}
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
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
              </div>
              <div className="p-4 max-h-96 overflow-y-auto">
                <ConversationList
                  selectedConversationId={(currentConversation as Conversation | null)?.id}
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

  // Paper-like full chat interface
  return (
    <div className="min-h-screen bg-white flex flex-col">
      {/* Header with conversations history icon */}
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
              />
            ) : (
              <h1 
                className="text-2xl font-light text-gray-800 tracking-wide cursor-pointer hover:text-blue-600 hover:bg-blue-50 px-2 py-1 rounded transition-all duration-200"
                onClick={handleTitleEdit}
                title="Click to edit conversation name"
              >
                {currentConversation?.title || 'Chat'}
                <span className="ml-2 text-gray-400 opacity-0 hover:opacity-100 transition-opacity text-sm">✏️</span>
              </h1>
            )}
          </div>
          <div className="flex items-center gap-2">
            {/* Orientator Mode Indicator */}
            {enableOrientator && (
              <div className="px-2 py-1 bg-green-100 text-green-700 text-xs font-medium rounded-full border border-green-200">
                🤖 Orientator AI
              </div>
            )}
            
            {/* Mode Indicator/Selector */}
            <div className="relative">
              <button
                onClick={() => setShowModeSelector(!showModeSelector)}
                className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-all ${
                  chatMode === 'claude' 
                    ? 'bg-purple-100 text-purple-700' 
                    : 'bg-blue-100 text-blue-700'
                }`}
              >
                {chatMode === 'default' && 'Default'}
                {chatMode === 'socratic' && 'Socratic'}
                {chatMode === 'claude' && 'Claude'}
              </button>
              
              {showModeSelector && (
                <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-200 z-10">
                  <button
                    onClick={() => { setChatMode('default'); setShowModeSelector(false); }}
                    className="w-full text-left px-4 py-2 hover:bg-gray-100 rounded-t-lg"
                  >
                    <div className="font-medium">Default</div>
                    <div className="text-xs text-gray-600">Helpful assistant</div>
                  </button>
                  <button
                    onClick={() => { setChatMode('socratic'); setShowModeSelector(false); }}
                    className="w-full text-left px-4 py-2 hover:bg-gray-100"
                  >
                    <div className="font-medium">Socratic</div>
                    <div className="text-xs text-gray-600">Discover through questions</div>
                  </button>
                  <button
                    onClick={() => { setChatMode('claude'); setShowModeSelector(false); }}
                    className="w-full text-left px-4 py-2 hover:bg-gray-100 rounded-b-lg"
                  >
                    <div className="font-medium">Claude</div>
                    <div className="text-xs text-gray-600">Bold challenges</div>
                  </button>
                </div>
              )}
            </div>
            
            <button
              onClick={() => setShowConversations(true)}
              className="p-2 text-gray-400 hover:text-blue-500 transition-colors rounded-full hover:bg-blue-50"
              title="View conversation history"
            >
              <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
                <path d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
              </svg>
            </button>
            <button
              onClick={handleCreateNewConversation}
              className="p-2 text-gray-400 hover:text-blue-500 transition-colors rounded-full hover:bg-blue-50"
              title="New conversation"
            >
              <Plus className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>

      {/* Paper-like Messages Area */}
      <div className="flex-1 overflow-y-auto px-8 py-12">
        <div className="max-w-4xl mx-auto">
          <div className="space-y-8">
            {(messages || [])
              .filter(message => message.role !== 'system' || (message.components && message.components.length > 0))
              .map((message, index) => (
                <PaperChatMessage 
                  key={message.id} 
                  message={message}
                  isLast={index === messages.length - 1}
                  chatMode={chatMode}
                  onComponentAction={enableOrientator ? handleComponentAction : undefined}
                />
              ))}
            
            {isTyping && (
              <div className="border-l-3 border-blue-500 pl-8 py-2">
                <div className="flex items-center space-x-2">
                  <div className="flex space-x-1">
                    <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                    <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                  </div>
                  <span className="text-blue-500 text-sm font-light">Thinking...</span>
                </div>
              </div>
            )}

            {/* Inline input for continuing conversation */}
            <div className="pl-4 py-2">
              <form onSubmit={(e) => { e.preventDefault(); handleSend(); }} className="w-full">
                <textarea
                  ref={inputRef}
                  value={inputText}
                  onChange={(e) => setInputText(e.target.value)}
                  placeholder="Continue writing.."
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
                  style={{ minHeight: '2.5rem' }}
                />
              </form>
            </div>
          </div>
        </div>
      </div>

      {/* Conversations History Popup */}
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