'use client';
import { Inter, Playfair_Display } from 'next/font/google';
import { Analytics } from '@vercel/analytics/react';
import { SpeedInsights } from '@vercel/speed-insights/next';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import './globals.css';

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-inter',
  display: 'swap',
  weight: ['400', '500', '600'],
});

const playfair = Playfair_Display({
  subsets: ['latin'],
  variable: '--font-playfair',
  display: 'swap',
  weight: ['400', '500', '600'],
});

// export const metadata = {
//   title: 'Navigo - Your Personal Guide',
//   description: 'Your personal guidance for growth and self-discovery',
// };

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    router.push('/login');
  };

  return (
    <html lang="en" className={`${inter.variable} ${playfair.variable} scroll-smooth`}>
      <body className="min-h-screen bg-white text-neutral-700 antialiased">
        {/* Background patterns */}
        <div className="fixed inset-0 -z-10 bg-branch opacity-5"></div>
        <div className="fixed inset-0 -z-10 bg-grid opacity-5"></div>
        
        {/* Navigation */}
        <header className="fixed top-0 w-full z-50 bg-white/10 backdrop-blur-md border-b border-white/10">
          <nav className="max-w-7xl mx-auto px-6 py-4 flex justify-between items-center">
            <span className="text-xl font-light tracking-wide text-neutral-800">
              Navigo
            </span>
            <div className="flex gap-8">
              <Link href="/chat" className="nav-link">Chat</Link>
              <Link href="/peers" className="nav-link">Suggested Peers</Link>
              <Link href="/vector-search" className="nav-link">Career recommendation</Link>
              <Link href="/space" className="nav-link">My Space</Link>
              <Link href="/profile" className="nav-link">Profile</Link>
              <button onClick={handleLogout} className="nav-link">Logout</button>
            </div>
          </nav>
        </header>

        {/* Main content */}
        <main className="pt-20">
          {children}
        </main>

        <Analytics />
        <SpeedInsights />
      </body>
    </html>
  );
}