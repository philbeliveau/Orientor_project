'use client';

import React, { useState, useEffect } from 'react';

interface StreamingMessageProps {
  content: string;
  isTyping?: boolean;
  onComplete?: () => void;
  className?: string;
}

export const StreamingMessage: React.FC<StreamingMessageProps> = ({
  content,
  isTyping = false,
  onComplete,
  className = ''
}) => {
  const [displayedText, setDisplayedText] = useState('');
  const [currentIndex, setCurrentIndex] = useState(0);

  useEffect(() => {
    if (isTyping && currentIndex < content.length) {
      const timer = setTimeout(() => {
        setDisplayedText(content.slice(0, currentIndex + 1));
        setCurrentIndex(prev => prev + 1);
      }, 15); // Faster typing speed for better UX

      return () => clearTimeout(timer);
    } else if (currentIndex >= content.length && onComplete) {
      onComplete();
    }
  }, [content, currentIndex, isTyping, onComplete]);

  useEffect(() => {
    // Reset when content changes
    setDisplayedText('');
    setCurrentIndex(0);
  }, [content]);

  useEffect(() => {
    if (!isTyping) {
      // Show all text immediately if not typing
      setDisplayedText(content);
      setCurrentIndex(content.length);
    }
  }, [isTyping, content]);

  return (
    <span className={className}>
      {displayedText}
      {isTyping && currentIndex < content.length && (
        <span className="animate-pulse">▋</span>
      )}
    </span>
  );
};

export default StreamingMessage;