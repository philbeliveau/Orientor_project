// import React from 'react';
// import MainLayout from '@/components/layout/MainLayout';
// import ChatInterface from '@/components/chat/ChatInterface';

// export default function Home() {
//   return (
//     <MainLayout>
//       <div className="space-y-6">
//         <h2 className="text-2xl font-bold text-gray-100">Welcome to Orientor</h2>
//         <h1 className="text-3xl font-bold text-blue-500">This is a test message!</h1> {/* Test message */}
//         <button className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-500">
//           Click Me
//         </button>
//         <ChatInterface />
//       </div>
//     </MainLayout>
//   );
// }

import ChatInterface from '@/components/chat/ChatInterface';
import MainLayout from '@/components/layout/MainLayout';

export default function Home() {
  return (
    <MainLayout>
      <div className="space-y-6">
        <ChatInterface />
      </div>
    </MainLayout>
  );
}