'use client';
import { useEffect, useRef } from 'react';
import { format } from 'date-fns';

interface Message {
    message_id: number;
    sender_id: number;
    recipient_id: number;
    body: string;
    timestamp: string;
}

interface MessageListProps {
    messages: Message[];
    currentUserId: number;
    className?: string;
}

export default function MessageList({ messages, currentUserId, className = '' }: MessageListProps) {
    const messagesEndRef = useRef<HTMLDivElement>(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    return (
        <div className={`flex flex-col space-y-4 p-4 ${className}`}>
            {messages.map((message) => {
                const isSender = message.sender_id === currentUserId;
                return (
                    <div
                        key={message.message_id}
                        className={`flex ${isSender ? 'justify-end' : 'justify-start'}`}
                    >
                        <div
                            className={`max-w-[70%] rounded-lg p-3 ${
                                isSender
                                    ? 'bg-secondary-purple text-white'
                                    : 'bg-neutral-lightest text-neutral-darkest'
                            }`}
                        >
                            <p className="text-sm">{message.body}</p>
                            <p className={`text-xs mt-1 ${isSender ? 'text-white/70' : 'text-neutral-gray'}`}>
                                {format(new Date(message.timestamp), 'MMM d, h:mm a')}
                            </p>
                        </div>
                    </div>
                );
            })}
            <div ref={messagesEndRef} />
        </div>
    );
} 