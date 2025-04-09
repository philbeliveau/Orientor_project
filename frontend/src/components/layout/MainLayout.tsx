'use client';
import { useEffect, useState } from 'react';
import Link from 'next/link';
import { useRouter, usePathname } from 'next/navigation';

export default function MainLayout({ children }: { children: React.ReactNode }) {
    const [isLoggedIn, setIsLoggedIn] = useState(false);
    const router = useRouter();
    const pathname = usePathname();

    // Public routes that don't require authentication
    const publicRoutes = ['/login', '/register'];
    const isPublicRoute = publicRoutes.includes(pathname);

    useEffect(() => {
        // Check if user is logged in
        const token = localStorage.getItem('access_token');
        if (!token && !isPublicRoute) {
            router.push('/login');
            return;
        }
        setIsLoggedIn(!!token);
    }, [router, isPublicRoute]);

    // For public routes, render immediately without checking auth
    if (isPublicRoute) {
        return (
            <div className="min-h-screen bg-primary-charcoal flex flex-col">
                <main className="flex-1 w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
                    {children}
                </main>
            </div>
        );
    }

    // For protected routes, wait for auth check
    if (!isLoggedIn) {
        return null;
    }

    const handleLogout = () => {
        localStorage.removeItem('access_token');
        setIsLoggedIn(false);
        router.push('/login');
    };

    const navLinks = [
        { href: '/chat', label: 'Chat', requiresAuth: true },
        { href: '/profile', label: 'Profile', requiresAuth: true },
    ];

    return (
        <div className="min-h-screen bg-primary-charcoal flex flex-col">
            {/* Header/Navigation */}
            <header className="bg-primary-indigo shadow-md">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex justify-between h-16">
                        <div className="flex items-center">
                            <Link href="/" className="text-2xl font-semibold text-secondary-teal hover:text-secondary-purple transition-colors duration-200">
                                Navigo
                            </Link>
                        </div>
                        <nav className="flex items-center space-x-4">
                            {navLinks
                                .filter(link => !link.requiresAuth || isLoggedIn)
                                .map(link => (
                                    <Link 
                                        key={link.href} 
                                        href={link.href}
                                        className={`nav-link ${pathname === link.href ? 'nav-link-active' : ''}`}
                                    >
                                        {link.label}
                                    </Link>
                                ))
                            }
                            <button
                                onClick={handleLogout}
                                className="nav-link"
                            >
                                Logout
                            </button>
                        </nav>
                    </div>
                </div>
            </header>

            {/* Main Content */}
            <main className="flex-1 w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
                {children}
            </main>
        </div>
    );
}