// frontend/src/components/layout/NavTabs.tsx

'use client';

import { usePathname } from 'next/navigation';
import Link from 'next/link';

export default function NavTabs() {
  const pathname = usePathname();
  
  const tabs = [
    { href: '/', label: 'Home' },
    { href: '/register', label: 'Login' },
    { href: '/profile', label: 'Profile' },
  ];

  return (
    <div className="flex space-x-2 p-1 bg-gray-600 rounded-xl">
      {tabs.map((tab) => (
        <Link
          key={tab.href}
          href={tab.href}
          className={`px-4 py-2 rounded-lg transition-all duration-200 ${
            pathname === tab.href 
              ? 'tab-gradient font-medium' 
              : 'text-gray-200 hover:tab-hover'
          }`}
        >
          {tab.label}
        </Link>
      ))}
    </div>
  );
}