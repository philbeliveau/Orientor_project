'use client';
import { Inter, Playfair_Display } from 'next/font/google';
import { Analytics } from '@vercel/analytics/react';
import { SpeedInsights } from '@vercel/speed-insights/next';
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
  return (
    <html lang="en" className={`${inter.variable} ${playfair.variable} scroll-smooth`}>
      <body className="min-h-screen bg-white text-neutral-700 antialiased">
        {/* Background patterns */}
        <div 
          className="fixed inset-0 -z-10 bg-[url('/patterns/branch.svg')] bg-repeat opacity-900"
          style={{ backgroundSize: '200px 200px' }}
        ></div>
        <div 
          className="fixed inset-0 -z-10 bg-[url('/patterns/grid.svg')] bg-repeat opacity-900"
          style={{ backgroundSize: '200px 200px' }}
        ></div>
        
        {/* Main content */}
        <main>
          {children}
        </main>

        <Analytics />
        <SpeedInsights />
      </body>
    </html>
  );
}