import { Inter, Montserrat } from "next/font/google";
import { Analytics } from '@vercel/analytics/react';
import { SpeedInsights } from '@vercel/speed-insights/next';
import "./globals.css";

// Load fonts
const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
  weight: ["400", "500", "600", "700"],
});

const montserrat = Montserrat({
  subsets: ["latin"],
  variable: "--font-montserrat",
  display: "swap",
  weight: ["500", "600", "700"],
});

// Root layout as a server component
export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="scroll-smooth">
      <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <meta name="description" content="Navigo - Your personal guidance for growth and self-discovery" />
      </head>
      <body className={`${inter.variable} ${montserrat.variable} min-h-screen bg-gradient-dark text-neutral-50 antialiased`}>
        {/* Background gradient elements */}
        <div className="fixed inset-0 -z-10 bg-[radial-gradient(circle_at_top_right,rgba(125,91,166,0.15),transparent_40%)]"></div>
        <div className="fixed inset-0 -z-10 bg-[radial-gradient(circle_at_bottom_left,rgba(89,194,201,0.15),transparent_40%)]"></div>
        
        <div className="min-h-screen flex flex-col">
          <main className="flex-1 max-w-7xl mx-auto w-full p-4 md:p-6">
            {children}
          </main>
        </div>
        <Analytics />
        <SpeedInsights />
      </body>
    </html>
  );
}