import { Inter } from "next/font/google";
import "./globals.css";
import NavTabs from "@/components/layout/NavTabs";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
});

// Root layout as a server component
export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${inter.variable} min-h-screen bg-white text-gray-900`}>
        <div className="min-h-screen p-4 flex flex-col">
          <nav className="bg-gray-100 rounded-xl border border-gray-200 p-4 mb-6 shadow-lg">
            <NavTabs />
          </nav>
          <main className="flex-1">
            {children}
          </main>
        </div>
      </body>
    </html>
  );
}