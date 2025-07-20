'use client';
import { useState, useEffect } from 'react';
import MainLayout from '@/components/layout/MainLayout';
import Link from 'next/link';
import axios from 'axios';
import { useRouter } from 'next/navigation';
import { format } from 'date-fns';
import LoadingScreen from '@/components/ui/LoadingScreen';

// Define API URL with fallback and trim any trailing spaces
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const cleanApiUrl = API_URL ? API_URL.trim() : '';

interface ConversationPreview {
    peer_id: number;
    peer_name: string | null;
    last_message: string;
    timestamp: string;
    unread_count: number;
}

export default function MessagesPage() {
    const router = useRouter();
    const [conversations, setConversations] = useState<ConversationPreview[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchConversations = async () => {
            try {
                setLoading(true);
                setError(null);
                
                const token = localStorage.getItem('access_token');
                if (!token) {
                    router.push('/login');
                    return;
                }
                
                try {
                    // First try to get actual conversations
                    const response = await axios.get<ConversationPreview[]>(`${cleanApiUrl}/messages/conversations`, {
                        headers: {
                            Authorization: `Bearer ${token}`
                        }
                    });
                    
                    setConversations(response.data);
                } catch (err) {
                    console.error('Error fetching conversations, falling back to suggested peers:', err);
                    
                    // Fallback to suggested peers if no conversations exist yet
                    const peersResponse = await axios.get<any[]>(`${cleanApiUrl}/peers/suggested`, {
                        headers: {
                            Authorization: `Bearer ${token}`
                        }
                    });
                    
                    // Transform peers data into conversation previews
                    const conversationPreviews = peersResponse.data.map(peer => ({
                        peer_id: peer.user_id,
                        peer_name: peer.name || `User ${peer.user_id}`,
                        last_message: 'No messages yet',
                        timestamp: new Date().toISOString(),
                        unread_count: 0
                    }));
                    
                    setConversations(conversationPreviews);
                }
            } catch (err: any) {
                console.error('Error fetching conversations:', err);
                setError(err.response?.data?.detail || 'Failed to load conversations');
            } finally {
                setLoading(false);
            }
        };
        
        fetchConversations();
    }, [router]);

    return (
        <MainLayout>
            <div className="max-w-2xl mx-auto space-y-6">
                <div className="flex items-center justify-between">
                    <h2 className="text-2xl font-bold text-neutral-darkest">Messages</h2>
                </div>
                
                {loading ? (
                    <LoadingScreen message="Loading messages..." />
                ) : error ? (
                    <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
                        {error}
                    </div>
                ) : conversations.length === 0 ? (
                    <div className="text-center py-10">
                        <p className="text-neutral-gray">No conversations yet.</p>
                        <p className="mt-2 text-sm text-neutral-gray">
                            Start chatting with your suggested peers to begin a conversation.
                        </p>
                        <Link 
                            href="/peers" 
                            className="mt-4 inline-block px-4 py-2 bg-secondary-purple text-white rounded hover:bg-secondary-purple/90 transition-colors"
                        >
                            Find Peers
                        </Link>
                    </div>
                ) : (
                    <div className="divide-y divide-neutral-lightest">
                        {conversations.map((conversation) => (
                            <Link 
                                key={conversation.peer_id}
                                href={`/chat/${conversation.peer_id}`}
                                className="block hover:bg-neutral-lightest/50 transition-colors"
                            >
                                <div className="py-4 px-2 flex items-center space-x-4">
                                    <div className="w-12 h-12 bg-secondary-purple/20 rounded-full flex items-center justify-center text-secondary-purple font-semibold">
                                        {conversation.peer_name && conversation.peer_name.charAt(0) ? conversation.peer_name.charAt(0).toUpperCase() : '?'}
                                    </div>
                                    <div className="flex-1 min-w-0">
                                        <div className="flex items-baseline justify-between">
                                            <h3 className="text-lg font-medium text-neutral-darkest truncate">
                                                {conversation.peer_name}
                                            </h3>
                                            <span className="text-xs text-neutral-gray">
                                                {format(new Date(conversation.timestamp), 'MMM d, h:mm a')}
                                            </span>
                                        </div>
                                        <p className="text-sm text-neutral-gray truncate">
                                            {conversation.last_message}
                                        </p>
                                    </div>
                                    {conversation.unread_count > 0 && (
                                        <div className="w-5 h-5 bg-secondary-teal rounded-full flex items-center justify-center text-white text-xs">
                                            {conversation.unread_count}
                                        </div>
                                    )}
                                </div>
                            </Link>
                        ))}
                    </div>
                )}
            </div>
        </MainLayout>
    );
} 