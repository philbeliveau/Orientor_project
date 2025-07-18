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
import ChatHeader from './ChatHeader';
import InitialChatView from './InitialChatView';
import { ChatMode } from './ChatModeSelector';
import styles from './ChatBot.module.css';
import { MessageComponentRenderer, MessageComponent, ComponentAction, MessageComponentType } from './MessageComponent';
import LoadingSpinner from '@/components/ui/LoadingSpinner';
import StreamingMessage from './StreamingMessage';
import './ChatAnimations.css';

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
  isStreaming?: boolean;
  onStreamingComplete?: () => void;
}

const PaperChatMessage: React.FC<PaperChatMessageProps> = ({ 
  message, 
  isLast, 
  chatMode, 
  onComponentAction, 
  isStreaming = false, 
  onStreamingComplete 
}) => {
  const isUser = message.role === 'user';
  
  // Debug logging for message rendering
  if (!isUser && message.components && message.components.length > 0) {
    console.log('🎨 Rendering message with', message.components.length, 'components');
    console.log('🧩 Component types:', message.components.map(c => c.type));
  }
  
  return (
    <div className={`space-y-4 ${isUser ? 'user-message-enter' : 'assistant-message-enter'}`}>
      {/* AI/System message with mode-specific accent */}
      {!isUser && (
        <div>
          <div className={`border-l-3 pl-4 sm:pl-6 lg:pl-8 py-2 ${
            chatMode === 'claude' 
              ? 'border-purple-500' 
              : 'border-blue-500'
          }`}>
            <div className={`text-lg sm:text-xl leading-relaxed font-light tracking-wide ${
              chatMode === 'claude' 
                ? 'text-purple-600' 
                : 'text-blue-600'
            }`}>
              <StreamingMessage
                content={message.content}
                isTyping={isStreaming}
                onComplete={onStreamingComplete}
              />
            </div>
          </div>
          {/* Render message components if present */}
          {message.components && message.components.length > 0 && (
            <div className="mt-4 space-y-3 pl-4 sm:pl-6 lg:pl-8">
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
        <div className="pl-2 sm:pl-4 py-1">
          <p className="text-lg sm:text-xl leading-relaxed text-gray-800 font-light tracking-wide">
            {message.content}
          </p>
        </div>
      )}
    </div>
  );
};


export default function ChatInterface({ currentUserId, enableOrientator = false }: ChatInterfaceProps) {
  
  // Only log initialization once per component mount, not on every render
  const initRef = useRef(false);
  if (!initRef.current) {
    console.log('🔧 ChatInterface initialized with currentUserId:', currentUserId, 'enableOrientator:', enableOrientator);
    initRef.current = true;
  }
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
  const [streamingMessageId, setStreamingMessageId] = useState<number | null>(null);
  const [isSending, setIsSending] = useState(false);
  const [newlyCreatedConversationId, setNewlyCreatedConversationId] = useState<number | null>(null);
  const [justSentMessage, setJustSentMessage] = useState(false);
  
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

  const loadConversationMessages = useCallback(async () => {
    if (!currentConversation) {
      console.log('No current conversation to load messages for');
      return;
    }
    
    console.log('🔄 Loading messages for conversation:', currentConversation.id, 'isSending:', isSending);
    
    try {
      // Use Orientator endpoint only for default mode when enabled
      // Socratic/Claude modes should always use the regular chat endpoint
      const isDefaultMode = (chatMode as ChatMode) === 'default';
      const endpoint = (enableOrientator && isDefaultMode)
        ? `${process.env.NEXT_PUBLIC_API_URL}/orientator/conversations/${currentConversation.id}/messages`
        : `${process.env.NEXT_PUBLIC_API_URL}/chat/conversations/${currentConversation.id}/messages`;
        
      console.log('🔍 Loading messages from endpoint:', endpoint);
      console.log('🔍 Chat mode:', chatMode, '| Default mode:', isDefaultMode, '| Orientator enabled:', enableOrientator);
        
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
      
      // Sort messages by creation time to ensure proper order
      const sortedMessages = messagesData
        .filter((msg: any) => msg.role !== 'system') // Filter out system messages
        .sort((a: any, b: any) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime());
      
      console.log('📅 Sorted messages by creation time:', sortedMessages.length);
      if (sortedMessages.length > 0) {
        console.log('📅 First message:', sortedMessages[0].role, '-', sortedMessages[0].content?.substring(0, 50));
        console.log('📅 Last message:', sortedMessages[sortedMessages.length - 1].role, '-', sortedMessages[sortedMessages.length - 1].content?.substring(0, 50));
      }
      
      setMessages(sortedMessages);
    } catch (error) {
      console.error('Failed to load conversation messages:', error);
      // Fallback to regular chat endpoint if Orientator endpoint fails
      const isDefaultMode = (chatMode as ChatMode) === 'default';
      if (enableOrientator && isDefaultMode) {
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
  }, [currentConversation, chatMode, enableOrientator, isSending]);

  // Load conversation when selected (but not during send process or for newly created conversations)
  useEffect(() => {
    if (currentConversation && 
        !isSending && 
        currentConversation.id !== newlyCreatedConversationId &&
        !isTyping &&
        !justSentMessage) { // Don't reload after just sending a message
      console.log('🔄 Loading conversation messages for:', currentConversation.id);
      loadConversationMessages();
      setChatStarted(true); // Show full chat interface when conversation is loaded
    }
  }, [currentConversation?.id, isSending, newlyCreatedConversationId, isTyping, justSentMessage, loadConversationMessages]);

  const sendLockRef = useRef(false);
  
  const handleSend = async () => {
    if (!inputText.trim() || isTyping || isSending || sendLockRef.current) return;
    
    // Set send lock to prevent duplicate sends
    sendLockRef.current = true;
    setJustSentMessage(true);

    const token = localStorage.getItem('access_token');
    if (!token) {
      router.push('/login');
      return;
    }

    // Prevent duplicate sends
    setIsSending(true);
    
    const userMessage = inputText;
    setInputText('');
    
    // Immediately add user message to display for smooth UX
    const userMessageObj: Message = {
      id: Date.now(),
      role: 'user',
      content: userMessage,
      created_at: new Date().toISOString()
    };
    
    setMessages(prev => {
      // Check if this message already exists to prevent duplicates
      const existingMessage = prev.find(msg => msg.id === userMessageObj.id);
      if (existingMessage) {
        console.log('🚫 User message already exists, skipping duplicate');
        return prev;
      }
      
      console.log('📝 Adding user message to state. Current messages:', prev.length);
      const newMessages = [...prev, userMessageObj];
      // Sort to ensure proper ordering
      return newMessages.sort((a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime());
    });
    setIsTyping(true);
    
    console.log('🚀 handleSend called with message:', userMessage);

    try {
      // If no conversation exists, create one and wait for completion
      let conversationId = currentConversation?.id;
      let conversationToUse = currentConversation;
      
      console.log('handleSend - currentConversation:', currentConversation);
      console.log('handleSend - conversationId:', conversationId);
      
      const isDefaultMode = (chatMode as ChatMode) === 'default';
      
      // For non-default modes (Socratic/Claude), don't create conversation upfront
      // Let the service handle it for better performance
      if (!conversationId && isDefaultMode) {
        console.log('No conversation ID found, creating new conversation for default mode');
        try {
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
          
          // Update state but don't wait for it to propagate
          setCurrentConversation(conversationToUse);
          setNewlyCreatedConversationId(conversationId || null);
          setRefreshConversationList(prev => prev + 1);
          
          console.log('✅ Created conversation:', conversationId);
          console.log('🔄 Updated currentConversation state during send process');
        } catch (createError) {
          console.error('Failed to create conversation:', createError);
          // Continue anyway - the service might handle it
        }
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
      console.log('   enableOrientator && chatMode === "default":', enableOrientator && isDefaultMode);
      
      if (enableOrientator && isDefaultMode) {
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
          mode: chatMode
        };
        
        // Only include conversation_id if we have one (not undefined)
        if (conversationId) {
          requestBody.conversation_id = conversationId;
          console.log('🔗 Including existing conversation_id:', conversationId);
        } else {
          console.log('🆕 New conversation - letting service create it');
        }
        
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
      
      // Add only assistant message (user message already added above)
      let assistantMessage: Message | null = null;
      
      console.log('🔍 Checking response format:');
      console.log('   enableOrientator:', enableOrientator);
      console.log('   chatMode:', chatMode);
      console.log('   response.data.message_id:', response.data.message_id);
      console.log('   response.data.success:', response.data.success);
      
      if (enableOrientator && isDefaultMode && response.data.message_id) {
        // Orientator format with components - single message response
        console.log('✅ Using Orientator format!');
        assistantMessage = {
          id: response.data.message_id,
          role: response.data.role,
          content: response.data.content,
          created_at: response.data.created_at,
          components: response.data.components,
          metadata: response.data.metadata,
          tokens_used: response.data.tokens_used
        };
        
        console.log('✅ Created Orientator message');
        console.log('🎨 Assistant message components:', assistantMessage?.components?.length || 0);
        if (assistantMessage?.components && assistantMessage.components.length > 0) {
          assistantMessage.components.forEach((comp, i) => {
            console.log(`   ${i+1}. ${comp.type} component with ${comp.actions?.length || 0} actions`);
          });
        }
      } else if ((chatMode === 'socratic' || chatMode === 'claude') && response.data.success) {
        // Socratic Chat Service format - reload messages from database
        console.log('✅ Using Socratic Chat format!');
        
        // Update conversationId if it's a new conversation
        if (!conversationId && response.data.conversation_id) {
          // Update the conversation in state
          conversationToUse = { 
            ...conversationToUse,
            id: response.data.conversation_id,
            title: response.data.conversation_title || conversationToUse?.title || 'New Chat'
          } as Conversation;
          setCurrentConversation(conversationToUse);
          setNewlyCreatedConversationId(response.data.conversation_id);
          
          // Update local variable for current request
          conversationId = response.data.conversation_id;
          
          // Trigger conversation list refresh to show new conversation
          setRefreshConversationList(prev => prev + 1);
        }
        
        // For better performance, use the response data directly instead of reloading
        // This avoids the database roundtrip and prevents message flickering
        assistantMessage = {
          id: response.data.message_id || Date.now() + 1, // Ensure unique ID
          role: 'assistant',
          content: response.data.response || response.data.content,
          created_at: new Date(Date.now() + 1).toISOString(), // Ensure assistant message comes after user message
          tokens_used: response.data.tokens_used
        };
        
        console.log('✅ Created assistant message directly from response');
      } else {
        // Standard chat format (user message already added)
        console.log('✅ Using standard chat format!');
        assistantMessage = {
          id: response.data.assistant_message_id || response.data.message_id || Date.now() + 1,
          role: 'assistant',
          content: response.data.response,
          created_at: new Date(Date.now() + 1).toISOString(), // Ensure assistant message comes after user message
          tokens_used: response.data.tokens_used
        };
      }
      
      // Add assistant message if we have one
      if (assistantMessage) {
        setMessages(prev => {
          // Check if this message already exists to prevent duplicates
          const existingMessage = prev.find(msg => msg.id === assistantMessage!.id);
          if (existingMessage) {
            console.log('🚫 Assistant message already exists, skipping duplicate');
            return prev;
          }
          
          console.log('🤖 Adding assistant message to state. Current messages:', prev.length);
          const newMessages = [...prev, assistantMessage as Message];
          // Sort to ensure proper chronological ordering
          return newMessages.sort((a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime());
        });
        // Start streaming animation for the new message
        setStreamingMessageId(assistantMessage.id);
        console.log('✅ Assistant message added with streaming animation');
      }
      setChatStarted(true); // Transition to full chat interface after sending first message
    } catch (error: any) {
      console.error('Failed to send message:', error);
      
      if (error.response?.status === 401) {
        router.push('/login');
        return;
      }
      
      // Show error message (user message is already displayed, so just add error)
      const errorMsg: Message = {
        id: Date.now(),
        role: 'system',
        content: "Sorry, I'm having trouble connecting. Please try again.",
        created_at: new Date().toISOString()
      };
      
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setIsTyping(false);
      setIsSending(false);
      // Release send lock to allow next message
      sendLockRef.current = false;
      // Clear the just sent message flag after a delay to allow state to settle
      setTimeout(() => {
        setJustSentMessage(false);
      }, 500);
      // Clear the newly created conversation tracking after a delay
      setTimeout(() => {
        setNewlyCreatedConversationId(null);
      }, 1000);
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

  const handleStreamingComplete = useCallback((messageId: number) => {
    setStreamingMessageId(null);
  }, []);

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
    return (
      <InitialChatView
        inputText={inputText}
        setInputText={setInputText}
        handleSend={handleSend}
        isTyping={isTyping}
        chatMode={chatMode}
        setChatMode={setChatMode}
        showConversations={showConversations}
        setShowConversations={setShowConversations}
        handleSelectConversation={handleSelectConversation}
        handleCreateNewConversation={handleCreateNewConversation}
        currentConversation={currentConversation}
        refreshConversationList={refreshConversationList}
        inputRef={inputRef}
      />
    );
  }

  // Paper-like full chat interface
  return (
    <div className="min-h-screen bg-white flex flex-col">
      <ChatHeader
        currentConversation={currentConversation}
        isEditingTitle={isEditingTitle}
        editingTitleValue={editingTitleValue}
        setEditingTitleValue={setEditingTitleValue}
        handleTitleEdit={handleTitleEdit}
        handleTitleSave={handleTitleSave}
        setIsEditingTitle={setIsEditingTitle}
        setShowConversations={setShowConversations}
        handleCreateNewConversation={handleCreateNewConversation}
        chatMode={chatMode}
        setChatMode={setChatMode}
        showModeSelector={showModeSelector}
        setShowModeSelector={setShowModeSelector}
        enableOrientator={enableOrientator}
      />

      {/* Paper-like Messages Area */}
      <div className="flex-1 overflow-y-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8 lg:py-12">
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
                  isStreaming={streamingMessageId === message.id}
                  onStreamingComplete={() => handleStreamingComplete(message.id)}
                />
              ))}
            
            {isTyping && (
              <div className="border-l-3 border-blue-500 pl-4 sm:pl-6 lg:pl-8 py-2 animate-fade-in">
                <div className="flex items-center space-x-3">
                  <div className="flex space-x-1">
                    <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                    <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                    <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                  </div>
                  <span className="text-blue-500 text-sm font-light">Thinking...</span>
                </div>
              </div>
            )}

            {/* Inline input for continuing conversation */}
            <div className="pl-2 sm:pl-4 py-2">
              <form onSubmit={(e) => { 
                e.preventDefault(); 
                if (!isSending && !isTyping) {
                  handleSend(); 
                }
              }} className="w-full">
                <textarea
                  ref={inputRef}
                  value={inputText}
                  onChange={(e) => setInputText(e.target.value)}
                  placeholder="Continue writing.."
                  className="w-full text-lg sm:text-xl leading-relaxed text-gray-800 placeholder-gray-300 
                    bg-transparent border-none outline-none resize-none font-light tracking-wide
                    focus:text-gray-900 transition-all duration-300 min-h-[2.5rem]
                    focus:placeholder-gray-200 focus:outline-none focus:ring-0 focus:border-none
                    touch-manipulation transform transition-transform duration-200"
                  rows={1}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                      e.preventDefault();
                      if (!isSending && !isTyping) {
                        handleSend();
                      }
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
                  aria-label="Type your message to continue the conversation"
                  aria-describedby="chat-input-help"
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
            role="backdrop"
            aria-label="Close conversation history"
          />
          <div 
            className="fixed top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-96 max-w-90vw max-h-80vh bg-white rounded-lg shadow-xl z-50 overflow-hidden"
            role="dialog"
            aria-modal="true"
            aria-labelledby="conversation-history-title"
          >
            <div className="p-4 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <h3 
                  id="conversation-history-title"
                  className="text-lg font-medium text-gray-800"
                >
                  Conversation History
                </h3>
                <button
                  onClick={() => setShowConversations(false)}
                  className="p-1 text-gray-400 hover:text-gray-600 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
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