'use client';
import { Analytics } from '@vercel/analytics/react';
import { SpeedInsights } from '@vercel/speed-insights/react';
import { Providers } from './providers';
import MainLayout from '@/components/layout/MainLayout';
import './globals.css';
import localFont from 'next/font/local';

// Load custom fonts using correct paths for Next.js
const departureMono = localFont({
  src: './fonts/DepartureMono-1.422/DepartureMono-Regular.woff2',
  variable: '--font-departure',
  weight: '400',
  style: 'normal',
  display: 'swap',
});

const technor = localFont({
  src: [
    {
      path: './fonts/Technor_Complete/Fonts/WEB/fonts/Technor-Regular.woff2',
      weight: '400',
      style: 'normal',
    },
    {
      path: './fonts/Technor_Complete/Fonts/WEB/fonts/Technor-Medium.woff',
      weight: '500',
      style: 'normal',
    },
    {
      path: './fonts/Technor_Complete/Fonts/WEB/fonts/Technor-Semibold.woff2',
      weight: '600',
      style: 'normal',
    },
    {
      path: './fonts/Technor_Complete/Fonts/WEB/fonts/Technor-Bold.woff2',
      weight: '700',
      style: 'normal',
    },
  ],
  variable: '--font-technor',
  display: 'swap',
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
    <html lang="en" className={`scroll-smooth ${departureMono.variable} ${technor.variable}`}>
      <head>
        <link href="https://fonts.googleapis.com/icon?family=Material+Icons+Outlined" rel="stylesheet" />
      </head>
      <Providers>
        <body className="min-h-screen antialiased">
          {children}
          <Analytics />
          <SpeedInsights />
        </body>
      </Providers>
    </html>
  );
}