import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "../styles/globals.css";
import Link from 'next/link';

// Inside your component
<Link href="/profile">Profile</Link>

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Orientor - Your AI Assistant",
  description: "AI-powered chat and assistance platform",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${inter.variable} antialiased`}>
        <div className="grok-container">
          <nav className="grok-card p-4 mb-6">
            <div className="grok-tabs">
              <Link href="/login" className="grok-tab grok-tab-active">
                Sign In
              </Link>
              <Link href="/register" className="grok-tab">
                Register
              </Link>
              <Link href="/chat" className="grok-tab">
                Chat
              </Link>
            </div>
          </nav>
          <main className="flex-1">
            {children}
          </main>
        </div>
      </body>
    </html>
  );
} 