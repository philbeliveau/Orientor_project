'use client';

import { usePathname } from 'next/navigation';
import Link from 'next/link';

export default function NavTabs() {
  const pathname = usePathname();
  
  const tabs = [
    { href: '/login', label: 'Sign In' },
    { href: '/register', label: 'Register' },
    { href: '/chat', label: 'Chat' },
    { href: '/profile', label: 'Profile' },
  ];

  return (
    <div className="flex space-x-2 p-1 bg-gray-50 rounded-xl">
      {tabs.map((tab) => (
        <Link
          key={tab.href}
          href={tab.href}
          className={`px-4 py-2 rounded-lg transition-all duration-200 ${
            pathname === tab.href 
              ? 'bg-blue-100 text-blue-700 font-medium' 
              : 'text-gray-700 hover:text-gray-900 hover:bg-gray-200'
          }`}
        >
          {tab.label}
        </Link>
      ))}
    </div>
  );
} 