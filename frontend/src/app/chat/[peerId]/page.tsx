'use client';
import { useState, useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';
import MainLayout from '@/components/layout/MainLayout';
import MessageList from '@/components/chat/MessageList';
import MessageInput from '@/components/chat/MessageInput';
import axios from 'axios';

// Define API URL with fallback and trim any trailing spaces
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const cleanApiUrl = API_URL ? API_URL.trim() : '';

interface Message {
    message_id: number;
    sender_id: number;
    recipient_id: number;
    body: string;
    timestamp: string;
}

interface PeerProfile {
    user_id: number;
    name: string | null;
    major: string | null;
    year: number | null;
}

export default function PeerChatPage() {
    const router = useRouter();
    const params = useParams();
    const peerId = params?.peerId as string;
    
    const [messages, setMessages] = useState<Message[]>([]);
    const [peer, setPeer] = useState<PeerProfile | null>(null);
    const [currentUserId, setCurrentUserId] = useState<number | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    // Function to fetch conversation history
    const fetchMessages = async () => {
        try {
            const token = localStorage.getItem('access_token');
            if (!token) {
                router.push('/login');
                return;
            }

            const response = await axios.get<Message[]>(
                `${cleanApiUrl}/messages/conversation/${peerId}`,
                {
                    headers: { Authorization: `Bearer ${token}` }
                }
            );

            setMessages(response.data);
        } catch (err: any) {
            console.error('Error fetching messages:', err);
            setError(err.response?.data?.detail || 'Failed to load messages');
        }
    };

    // Function to fetch peer profile
    const fetchPeerProfile = async () => {
        try {
            const token = localStorage.getItem('access_token');
            if (!token) {
                router.push('/login');
                return;
            }

            const response = await axios.get<PeerProfile>(
                `${cleanApiUrl}/users/${peerId}/profile`,
                {
                    headers: { Authorization: `Bearer ${token}` }
                }
            );

            setPeer(response.data);
        } catch (err: any) {
            console.error('Error fetching peer profile:', err);
            setError(err.response?.data?.detail || 'Failed to load peer profile');
        }
    };

    // Function to get current user ID
    const fetchCurrentUserId = async () => {
        try {
            const token = localStorage.getItem('access_token');
            if (!token) {
                router.push('/login');
                return;
            }

            const response = await axios.get<{id: number}>(
                `${cleanApiUrl}/users/me`,
                {
                    headers: { Authorization: `Bearer ${token}` }
                }
            );

            setCurrentUserId(response.data.id);
        } catch (err: any) {
            console.error('Error fetching current user:', err);
            setError(err.response?.data?.detail || 'Failed to load user information');
        }
    };

    // Function to send a message
    const handleSendMessage = async (messageText: string) => {
        try {
            const token = localStorage.getItem('access_token');
            if (!token) {
                router.push('/login');
                return;
            }

            await axios.post(
                `${cleanApiUrl}/messages`,
                {
                    recipient_id: parseInt(peerId),
                    body: messageText
                },
                {
                    headers: { Authorization: `Bearer ${token}` }
                }
            );

            // Refresh messages after sending
            fetchMessages();
        } catch (err: any) {
            console.error('Error sending message:', err);
            setError(err.response?.data?.detail || 'Failed to send message');
        }
    };

    // Initial data fetch
    useEffect(() => {
        const initializeChat = async () => {
            setLoading(true);
            setError(null);
            
            try {
                await Promise.all([
                    fetchCurrentUserId(),
                    fetchPeerProfile(),
                    fetchMessages()
                ]);
            } catch (err) {
                console.error('Error initializing chat:', err);
            } finally {
                setLoading(false);
            }
        };

        if (peerId) {
            initializeChat();
        }
    }, [peerId]);

    // Set up polling for new messages
    useEffect(() => {
        if (!peerId) return;

        const pollInterval = setInterval(fetchMessages, 5000); // Poll every 5 seconds

        return () => clearInterval(pollInterval);
    }, [peerId]);

    if (!peerId) {
        return (
            <MainLayout>
                <div className="flex h-full items-center justify-center">
                    <p className="text-neutral-gray">No peer selected</p>
                </div>
            </MainLayout>
        );
    }

    return (
        <MainLayout>
            <div className="flex h-full flex-col">
                {/* Chat header */}
                <div className="border-b border-neutral-lightest p-4">
                    <h2 className="text-xl font-semibold text-neutral-darkest">
                        {peer?.name || `User ${peerId}`}
                    </h2>
                    {peer?.major && (
                        <p className="text-sm text-neutral-gray">
                            {peer.major}{peer.year ? `, Year ${peer.year}` : ''}
                        </p>
                    )}
                </div>

                {/* Chat content */}
                <div className="flex-1 overflow-y-auto">
                    {loading ? (
                        <div className="flex h-full items-center justify-center">
                            <div className="h-8 w-8 animate-spin rounded-full border-2 border-secondary-purple border-t-transparent"></div>
                        </div>
                    ) : error ? (
                        <div className="flex h-full items-center justify-center">
                            <p className="text-red-500">{error}</p>
                        </div>
                    ) : messages.length === 0 ? (
                        <div className="flex h-full items-center justify-center">
                            <p className="text-neutral-gray">No messages yet. Start the conversation!</p>
                        </div>
                    ) : (
                        currentUserId && (
                            <MessageList
                                messages={messages}
                                currentUserId={currentUserId}
                                className="min-h-0"
                            />
                        )
                    )}
                </div>
                {/* Message input */}
                <div className="border-t border-neutral-lightest">
                    <MessageInput
                        onSendMessage={handleSendMessage}
                        placeholder="Type your message..."
                        className="text-gray-900" // Added class for better visibility
                    />
                </div>
            </div>
        </MainLayout>
    );
} 