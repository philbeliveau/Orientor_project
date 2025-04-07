type MessageType = 'user' | 'ai';

interface ChatMessageProps {
  message: string;
  type: MessageType;
}

export default function ChatMessage({ message, type }: ChatMessageProps) {
  return (
    <div className={`flex ${type === 'user' ? 'justify-end' : 'justify-start'}`}>
      <div className={`max-w-[80%] rounded-lg px-4 py-2 ${
        type === 'user' 
          ? 'bg-blue-600 text-white' 
          : 'bg-gray-700 text-gray-100'
      }`}>
        {message}
      </div>
    </div>
  );
}