// import React from 'react';

// type MessageType = 'user' | 'ai';

// interface ChatMessageProps {
//   message: string;
//   type: MessageType;
// }

// export default function ChatMessage({ message, type }: ChatMessageProps) {
//   return (
//     <div className={`flex ${type === 'user' ? 'justify-end' : 'justify-start'}`}>
//       <div className={`max-w-[80%] rounded-lg px-4 py-2 ${
//         type === 'user' 
//           ? 'bg-blue-600 text-white' 
//           : 'bg-gray-700 text-gray-100'
//       }`}>
//         {message}
//       </div>
//     </div>
//   );
// }

// frontend/src/components/chat/ChatMessage.tsx

// frontend/src/components/chat/ChatMessage.tsx

import React from 'react';

type MessageType = 'user' | 'ai';

interface ChatMessageProps {
  message: string;
  type: MessageType;
  userColor?: string; // Optional prop for user message color
  aiColor?: string;   // Optional prop for AI message color
}

export default function ChatMessage({ message, type, userColor = 'bg-gray-800', aiColor = 'bg-gray-600' }: ChatMessageProps) {
  return (
    <div className={`flex ${type === 'user' ? 'justify-end' : 'justify-start'}`}>
      <div className={`max-w-[80%] rounded-lg px-4 py-2 ${type === 'user' ? userColor : aiColor} text-white`}>
        {message}
      </div>
    </div>
  );
}