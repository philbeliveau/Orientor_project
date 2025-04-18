'use client';
import { useEffect, useState } from 'react';
import Link from 'next/link';
import { useRouter, usePathname } from 'next/navigation';

export default function MainLayout({ 
    children, 
    showNav = true 
}: { 
    children: React.ReactNode, 
    showNav?: boolean 
}) {
    const [isLoggedIn, setIsLoggedIn] = useState(false);
    const router = useRouter();
    const pathname = usePathname();

    // Public routes that don't require authentication
    const publicRoutes = ['/login', '/register'];
    const isPublicRoute = publicRoutes.includes(pathname);

    useEffect(() => {
        // Check if user is logged in
        const token = localStorage.getItem('access_token');
        if (!token && !isPublicRoute && showNav) {
            router.push('/login');
            return;
        }
        setIsLoggedIn(!!token);
    }, [router, isPublicRoute, showNav]);

    const handleLogout = () => {
        localStorage.removeItem('access_token');
        router.push('/login');
    };

    // For public routes, render immediately without checking auth
    if (isPublicRoute) {
        return (
            <div className="min-h-screen flex flex-col">
                <main className="flex-1 w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
                    {children}
                </main>
            </div>
        );
    }

    // For protected routes, wait for auth check
    if (!isLoggedIn && showNav) {
        return null;
    }

    return (
        <div className="min-h-screen flex flex-col">
            {/* Navigation Bar - Only show when logged in */}
            {isLoggedIn && (
                <header className="fixed top-0 w-full z-50 bg-white/10 backdrop-blur-md border-b border-white/10">
                    <nav className="max-w-7xl mx-auto px-6 py-4 flex justify-between items-center">
                        <Link href="/" className="text-xl font-light tracking-wide text-neutral-800">
                            Navigo
                        </Link>
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
            )}

            {/* Main Content */}
            <main className={`flex-1 w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 ${isLoggedIn ? 'pt-20' : ''}`}>
                {children}
            </main>
        </div>
    );
}