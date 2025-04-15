import { Inter, Montserrat } from 'next/font/google';
import { Analytics } from '@vercel/analytics/react';
import { SpeedInsights } from '@vercel/speed-insights/next';
import './globals.css';

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-inter',
  display: 'swap',
  weight: ['400', '500', '600', '700'],
});

const montserrat = Montserrat({
  subsets: ['latin'],
  variable: '--font-montserrat',
  display: 'swap',
  weight: ['500', '600', '700'],
});

export const metadata = {
  title: 'Navigo - Your Personal Guide',
  description: 'Your personal guidance for growth and self-discovery',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={`${inter.variable} ${montserrat.variable} scroll-smooth`}>
      <body className="min-h-screen bg-gradient-dark text-neutral-50 antialiased">
        {/* Background gradient elements */}
        <div className="fixed inset-0 -z-10 bg-[radial-gradient(circle_at_top_right,rgba(125,91,166,0.15),transparent_40%)]"></div>
        <div className="fixed inset-0 -z-10 bg-[radial-gradient(circle_at_bottom_left,rgba(89,194,201,0.15),transparent_40%)]"></div>
        {children}
        <Analytics />
        <SpeedInsights />
      </body>
    </html>
  );
}