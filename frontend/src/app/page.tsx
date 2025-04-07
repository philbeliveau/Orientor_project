import ChatInterface from '@/components/chat/ChatInterface';
import MainLayout from '@/components/layout/MainLayout';

export default function Home() {
  return (
    <MainLayout>
      <div className="space-y-6">
        <h2 className="text-2xl font-bold text-gray-100">Welcome to Orientor</h2>
        <ChatInterface />
      </div>
    </MainLayout>
  );
}