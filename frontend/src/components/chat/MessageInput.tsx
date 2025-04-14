'use client';
import { useState, FormEvent, KeyboardEvent } from 'react';

interface MessageInputProps {
    onSendMessage: (message: string) => void;
    placeholder?: string;
    className?: string;
}

export default function MessageInput({ 
    onSendMessage, 
    placeholder = 'Type a message...', 
    className = '' 
}: MessageInputProps) {
    const [message, setMessage] = useState('');

    const handleSubmit = (e: FormEvent) => {
        e.preventDefault();
        if (message.trim()) {
            onSendMessage(message.trim());
            setMessage('');
        }
    };

    const handleKeyPress = (e: KeyboardEvent<HTMLTextAreaElement>) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSubmit(e);
        }
    };

    return (
        <form onSubmit={handleSubmit} className={`flex items-end space-x-2 p-4 ${className}`}>
            <textarea
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder={placeholder}
                className="flex-1 resize-none rounded-lg border border-neutral-lightest p-3 focus:border-secondary-purple focus:outline-none"
                rows={1}
                style={{ minHeight: '44px', maxHeight: '120px' }}
            />
            <button
                type="submit"
                disabled={!message.trim()}
                className="rounded-lg bg-secondary-purple px-4 py-2 text-white transition-colors hover:bg-secondary-purple/90 disabled:opacity-50"
            >
                Send
            </button>
        </form>
    );
} 