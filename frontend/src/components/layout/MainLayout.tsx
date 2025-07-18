'use client';
import { useEffect, useState, useRef } from 'react';
import Link from 'next/link';
import { useRouter, usePathname } from 'next/navigation';
import XPProgress from '../ui/XPProgress';
import DarkModeToggle from '../ui/DarkModeToggle';
import ThemeToggle from '../ui/ThemeToggle';
import styles from '@/styles/patterns.module.css';
import LoadingScreen from '@/components/ui/LoadingScreen';
import NewSidebar from './NewSidebar';
import { useAuth } from '@/hooks/useAuth';
import { useAuthCheck } from '@/hooks/useAuthCheck';
import { logger } from '@/utils/logger';

// Composants pour les menus déroulants
const ProfileDropdown = ({ pathname }: { pathname: string | null }) => {
    const [profileMenuOpen, setProfileMenuOpen] = useState(false);
    const profileMenuRef = useRef<HTMLDivElement>(null);

    // Fermer le menu lorsqu'on clique en dehors
    useEffect(() => {
        function handleClickOutside(event: MouseEvent) {
            if (profileMenuRef.current && !profileMenuRef.current.contains(event.target as Node)) {
                setProfileMenuOpen(false);
            }
        }
        
        document.addEventListener("mousedown", handleClickOutside);
        return () => {
            document.removeEventListener("mousedown", handleClickOutside);
        };
    }, []);

    return (
        <div className="relative inline-block text-left" ref={profileMenuRef}>
            <button
                onClick={() => setProfileMenuOpen(!profileMenuOpen)}
                className={`px-4 py-2 text-sm font-medium rounded-md transition-colors duration-150 ease-in-out flex items-center
                    ${pathname === '/profile' || pathname?.startsWith('/profile/')
                        ? 'text-blue-700 bg-blue-50 dark:text-blue-400 dark:bg-gray-800'
                        : 'text-gray-700 hover:text-blue-600 hover:bg-gray-50 dark:text-gray-300 dark:hover:text-gray-100 dark:hover:bg-gray-800'
                    }`}
            >
                Profile
                <svg
                    className={`ml-1 h-4 w-4 transition-transform duration-200 ${profileMenuOpen ? 'rotate-180' : ''}`}
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
            </button>
            
            {profileMenuOpen && (
                <div className="absolute right-0 mt-2 w-48 rounded-md shadow-lg bg-light-background dark:bg-dark-background ring-1 ring-black ring-opacity-5 z-40">
                    <div className="py-1" role="menu" aria-orientation="vertical">
                        <Link
                            href="/profile"
                            onClick={() => setProfileMenuOpen(false)}
                            className={`block px-4 py-2 text-sm ${pathname === '/profile' ? 'bg-blue-50 text-blue-700 dark:bg-gray-800 dark:text-blue-400' : 'text-gray-700 hover:bg-gray-50 hover:text-blue-600 dark:text-gray-300 dark:hover:bg-gray-800 dark:hover:text-gray-100'}`}
                            role="menuitem"
                        >
                            Informations générales
                        </Link>
                        <Link
                            href="/profile/holland-results"
                            onClick={() => setProfileMenuOpen(false)}
                            className={`block px-4 py-2 text-sm ${pathname === '/profile/holland-results' ? 'bg-blue-50 text-blue-700 dark:bg-gray-800 dark:text-blue-400' : 'text-gray-700 hover:bg-gray-50 hover:text-blue-600 dark:text-gray-300 dark:hover:bg-gray-800 dark:hover:text-gray-100'}`}
                            role="menuitem"
                        >
                            Résultats RIASEC
                        </Link>
                    </div>
                </div>
            )}
        </div>
    );
};

// Composant pour le menu déroulant du profil mobile
const MobileProfileMenu = ({
    pathname,
    setMoreMenuOpen,
    setCareerMenuOpen,
    setWorkspaceMenuOpen
}: {
    pathname: string | null;
    setMoreMenuOpen: (open: boolean) => void;
    setCareerMenuOpen: (open: boolean) => void;
    setWorkspaceMenuOpen: (open: boolean) => void;
}) => {
    const [profileMobileMenuOpen, setProfileMobileMenuOpen] = useState(false);
    const profileMobileMenuRef = useRef<HTMLDivElement>(null);
    const router = useRouter();
    
    // Fermer le menu lorsqu'on clique en dehors
    useEffect(() => {
        function handleClickOutside(event: MouseEvent) {
            if (profileMobileMenuRef.current && !profileMobileMenuRef.current.contains(event.target as Node)) {
                setProfileMobileMenuOpen(false);
            }
        }
        
        document.addEventListener("mousedown", handleClickOutside);
        return () => {
            document.removeEventListener("mousedown", handleClickOutside);
        };
    }, []);
    
    return (
        <div className="relative" ref={profileMobileMenuRef}>
            <button
                className={`flex flex-col items-center text-xs w-full ${pathname === '/profile' || pathname?.startsWith('/profile/') ? 'text-blue-600 dark:text-blue-400' : 'text-gray-600 dark:text-gray-400'}`}
                onClick={() => {
                    setMoreMenuOpen(false);
                    setCareerMenuOpen(false);
                    setWorkspaceMenuOpen(false);
                    setProfileMobileMenuOpen(!profileMobileMenuOpen);
                }}
            >
                <span className="material-icons-outlined">person</span>
                <span>Profile</span>
            </button>
            
            {/* Menu du profil pour mobile */}
            {profileMobileMenuOpen && (
                <div className="absolute bottom-full right-0 mb-2 w-48 bg-light-background dark:bg-dark-background rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 overflow-hidden">
                    <div className="py-1">
                        <Link
                            href="/profile"
                            onClick={() => setProfileMobileMenuOpen(false)}
                            className={`flex items-center px-4 py-3 text-sm ${pathname === '/profile' ? 'bg-blue-50 text-blue-600 dark:bg-gray-800 dark:text-blue-400' : 'text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800'}`}
                        >
                            <span className="material-icons-outlined mr-2 text-gray-500 dark:text-gray-400">account_circle</span>
                            Informations générales
                        </Link>
                        <Link
                            href="/profile/holland-results"
                            onClick={() => setProfileMobileMenuOpen(false)}
                            className={`flex items-center px-4 py-3 text-sm ${pathname === '/profile/holland-results' ? 'bg-blue-50 text-blue-600 dark:bg-gray-800 dark:text-blue-400' : 'text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800'}`}
                        >
                            <span className="material-icons-outlined mr-2 text-gray-500 dark:text-gray-400">psychology</span>
                            Résultats RIASEC
                        </Link>
                    </div>
                </div>
            )}
        </div>
    );
};

export default function MainLayout({ 
    children, 
    showNav = true 
}: { 
    children: React.ReactNode, 
    showNav?: boolean 
}) {
    const { isLoggedIn, isLoading, isPublicRoute } = useAuthCheck(showNav);
    const [moreMenuOpen, setMoreMenuOpen] = useState(false);
    const [careerMenuOpen, setCareerMenuOpen] = useState(false);
    const [workspaceMenuOpen, setWorkspaceMenuOpen] = useState(false);
    const moreMenuRef = useRef<HTMLDivElement>(null);
    const careerMenuRef = useRef<HTMLDivElement>(null);
    const workspaceMenuRef = useRef<HTMLDivElement>(null);
    const router = useRouter();
    const pathname = usePathname();
    const { logout } = useAuth();

    // Navigation items for the sidebar
    const navItems = [
        { name: 'Dashboard', icon: 'Dashboard', path: '/dashboard' },
        { name: 'Education', icon: 'Education', path: '/education' },
        { name: 'Chat', icon: 'Chat', path: '/chat' },
        { name: 'Swipe', icon: 'Swipe', path: '/find-your-way' },
        { name: 'Saved', icon: 'Bookmark', path: '/space' },
        { name: 'Challenges', icon: 'Trophy', path: '/challenges' },
        { name: 'Notes', icon: 'Note', path: '/notes' },
        { name: 'Case Study', icon: 'Case Study', path: '/case-study-journey' },
        { name: 'Competence Tree', icon: 'Tree', path: '/competence-tree' },
    ];

    // Authentication logic moved to useAuthCheck hook

    // Close menus when clicking outside
    useEffect(() => {
        function handleClickOutside(event: MouseEvent) {
            if (moreMenuRef.current && !moreMenuRef.current.contains(event.target as Node)) {
                setMoreMenuOpen(false);
            }
            if (careerMenuRef.current && !careerMenuRef.current.contains(event.target as Node)) {
                setCareerMenuOpen(false);
            }
            if (workspaceMenuRef.current && !workspaceMenuRef.current.contains(event.target as Node)) {
                setWorkspaceMenuOpen(false);
            }
        }
        
        document.addEventListener("mousedown", handleClickOutside);
        return () => {
            document.removeEventListener("mousedown", handleClickOutside);
        };
    }, []);

    // Close mobile menus when route changes
    useEffect(() => {
        logger.debug('Route changed to:', pathname);
        setMoreMenuOpen(false);
        setCareerMenuOpen(false);
        setWorkspaceMenuOpen(false);
    }, [pathname]);

    const handleLogout = () => {
        logger.debug('Logging out user');
        logout();
    };

    const toggleCareerDropdown = () => {
        logger.debug('Toggling career dropdown');
        setCareerMenuOpen(!careerMenuOpen);
        if (workspaceMenuOpen) setWorkspaceMenuOpen(false);
    };

    const toggleWorkspaceDropdown = () => {
        logger.debug('Toggling workspace dropdown, current state:', workspaceMenuOpen);
        setWorkspaceMenuOpen(!workspaceMenuOpen);
        if (careerMenuOpen) setCareerMenuOpen(false);
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

    // Show loading state while checking authentication
    if (isLoading) {
        return <LoadingScreen message="Loading..." />;
    }

    // Check if current path is in career path section
    const isCareerPath = ['/vector-search', '/find-your-way', '/cv', '/tree'].includes(pathname || '');

    logger.debug('Rendering layout with isLoggedIn:', isLoggedIn);

    return (
        <div className="min-h-screen flex flex-col" style={{ backgroundColor: '#ffffff' }}>
            {/* Desktop Navigation Bar - Only visible on larger screens */}
            {isLoggedIn && (
            //             <div className="min-h-screen bg-light-background dark:bg-dark-background">
            // {showNav && (
                <header className="fixed top-0 left-0 right-0 w-full z-50 px-4 py-3 hidden md:block font-departure header" style={{ backgroundColor: '#ffffff' }}>
                    <div className="w-full px-4">
                        <div className="flex justify-between items-center w-full">
                            {/* Left Side - Logo positioned at far left */}
                            <div className="flex items-center">
                                {/* Logo */}
                                <Link href="/dashboard" className="flex-shrink-0 flex items-center">
                                    <span className="text-xl font-bold tracking-tight text-stitch-accent font-departure">
                                        Navigo
                                    </span>
                                </Link>
                            </div>

                            {/* Right Side - XP Progress, Dark Mode Toggle */}
                            <div className="flex items-center space-x-4">
                                {/* XP Progress Bar */}
                                <div className="relative group">
                                    <XPProgress className="mr-2" />
                                    <div className="absolute inset-0 bg-stitch-accent/10 blur-sm opacity-0 group-hover:opacity-100 transition-opacity duration-300 rounded-full"></div>
                                </div>
                                
                                {/* Theme Toggle */}
                                <ThemeToggle />
                                
                                {/* Logout Button */}
                                <button
                                    onClick={handleLogout}
                                    className="p-2 text-sm font-bold rounded-md text-stitch-sage hover:text-red-500 hover:bg-stitch-primary/30 transition-colors duration-150 ease-in-out"
                                >
                                    <span className="material-icons-outlined">logout</span>
                                </button>
                            </div>
                        </div>
                    </div>
                </header>
            )}

            {/* Main content area with sidebar */}
            <div className="flex w-full h-full grow relative z-10">
                {/* Sidebar - hidden on chat page, shows on hover */}
                {isLoggedIn && showNav && (
                    <>
                        {pathname === '/chat' ? (
                            <div className="hidden md:block group">
                                {/* Invisible hover trigger area for chat page */}
                                <div className="fixed left-0 top-20 w-12 h-[calc(100vh-5rem)] z-40 bg-transparent" />
                                {/* Sidebar wrapper that slides in from left */}
                                <div className="fixed left-0 top-20 h-[calc(100vh-5rem)] z-50 transform -translate-x-full group-hover:translate-x-0 transition-transform duration-300 ease-in-out">
                                    <div className="w-20 h-full bg-white border-r border-gray-200 shadow-lg flex flex-col items-center py-4">
                                        <div className="flex flex-col gap-6 w-full px-2 flex-1">
                                            {navItems.map((item, index) => (
                                                <Link href={item.path} key={index} className="relative flex justify-center items-center w-full p-3 rounded-lg transition-all duration-300 ease-in-out text-gray-600 hover:bg-gray-100 hover:transform hover:-translate-y-0.5 group/item">
                                                    <div className="flex justify-center items-center w-full h-full">
                                                        {item.icon === 'Dashboard' && (
                                                            <svg xmlns="http://www.w3.org/2000/svg" width="24px" height="24px" fill="currentColor" viewBox="0 0 256 256">
                                                                <path d="M218.83,103.77l-80-75.48a1.14,1.14,0,0,1-.11-.11a16,16,0,0,0-21.53,0l-.11.11L37.17,103.77A8,8,0,0,0,32,110.62V208a16,16,0,0,0,16,16H208a16,16,0,0,0,16-16V110.62A8,8,0,0,0,218.83,103.77ZM208,208H160V160a8,8,0,0,0-8-8H104a8,8,0,0,0-8,8v48H48V115.55l80-75.48,80,75.48Z"></path>
                                                            </svg>
                                                        )}
                                                        {item.icon === 'Classes' && (
                                                            <svg xmlns="http://www.w3.org/2000/svg" width="24px" height="24px" fill="currentColor" viewBox="0 0 256 256">
                                                                <path d="M225.86,102.82c-.03-.07-.07-.13-.11-.2L208,80.51V56a8,8,0,0,0-8-8H56a8,8,0,0,0-8,8V80.51L30.25,102.62c0,.07-.08.13-.11.2A8,8,0,0,0,32,112v96a8,8,0,0,0,8,8H64a8,8,0,0,0,8-8V176h48v32a8,8,0,0,0,8,8h24a8,8,0,0,0,8-8V176h48v32a8,8,0,0,0,8,8h24a8,8,0,0,0,8-8V112A8,8,0,0,0,225.86,102.82ZM64,64H192V158.3l-16-16V104a8,8,0,0,0-8-8H88a8,8,0,0,0-8,8v38.3l-16,16Zm32,48h64v38.3l-32-32Z"></path>
                                                            </svg>
                                                        )}
                                                        {item.icon === 'Education' && (
                                                            <svg xmlns="http://www.w3.org/2000/svg" width="24px" height="24px" fill="currentColor" viewBox="0 0 256 256">
                                                                <path d="M208,24H72A32,32,0,0,0,40,56V224a8,8,0,0,0,8,8H192a8,8,0,0,0,0-16H56a16,16,0,0,1,16-16H208a8,8,0,0,0,8-8V32A8,8,0,0,0,208,24Zm-8,160H72a31.82,31.82,0,0,0-16,4.29V56A16,16,0,0,1,72,40H200Z"></path>
                                                            </svg>
                                                        )}
                                                        {item.icon === 'Chat' && (
                                                            <svg xmlns="http://www.w3.org/2000/svg" width="24px" height="24px" fill="currentColor" viewBox="0 0 256 256">
                                                                <path d="M216,48H40A16,16,0,0,0,24,64V224a15.84,15.84,0,0,0,9.25,14.5A16.05,16.05,0,0,0,40,240a15.89,15.89,0,0,0,10.25-3.78.69.69,0,0,0,.13-.11L82.5,208H216a16,16,0,0,0,16-16V64A16,16,0,0,0,216,48ZM40,224V64H216V192H82.5a16,16,0,0,0-10.25,3.78L40,224Z"></path>
                                                            </svg>
                                                        )}
                                                        {item.icon === 'Swipe' && (
                                                            <svg xmlns="http://www.w3.org/2000/svg" width="24px" height="24px" fill="currentColor" viewBox="0 0 256 256">
                                                                <path d="M216,64H176V56a16,16,0,0,0-16-16H136V24a8,8,0,0,0-16,0V40H96A16,16,0,0,0,80,56v8H40A16,16,0,0,0,24,80V200a16,16,0,0,0,16,16H216a16,16,0,0,0,16-16V80A16,16,0,0,0,216,64ZM96,56h64v8H96ZM216,200H40V80H216V200ZM128,96a12,12,0,1,0,12,12A12,12,0,0,0,128,96Zm0,48a12,12,0,1,0,12,12A12,12,0,0,0,128,144Zm40-24a12,12,0,1,0,12,12A12,12,0,0,0,168,120ZM88,120a12,12,0,1,0,12,12A12,12,0,0,0,88,120Z"></path>
                                                            </svg>
                                                        )}
                                                        {item.icon === 'Bookmark' && (
                                                            <svg xmlns="http://www.w3.org/2000/svg" width="24px" height="24px" fill="currentColor" viewBox="0 0 256 256">
                                                                <path d="M184,32H72A16,16,0,0,0,56,48V224a8,8,0,0,0,12.24,6.78L128,193.43l59.77,37.35A8,8,0,0,0,200,224V48A16,16,0,0,0,184,32Zm0,177.57-51.77-32.35a8,8,0,0,0-8.48,0L72,209.57V48H184Z"></path>
                                                            </svg>
                                                        )}
                                                        {item.icon === 'Trophy' && (
                                                            <svg xmlns="http://www.w3.org/2000/svg" width="24px" height="24px" fill="currentColor" viewBox="0 0 256 256">
                                                                <path d="M232,64H208V56a16,16,0,0,0-16-16H64A16,16,0,0,0,48,56v8H24A16,16,0,0,0,8,80V96a40,40,0,0,0,40,40h3.65A80.13,80.13,0,0,0,120,191.61V216H96a8,8,0,0,0,0,16h64a8,8,0,0,0,0-16H136V191.58c31.94-3.23,58.44-25.64,68.08-55.58H208a40,40,0,0,0,40-40V80A16,16,0,0,0,232,64ZM48,120A24,24,0,0,1,24,96V80H48v32q0,4,.39,8Zm144-8.9c0,35.52-28.49,64.64-63.51,64.9H128a64,64,0,0,1-64-64V56H192ZM232,96a24,24,0,0,1-24,24h-.5a81.81,81.81,0,0,0,.5-8.9V80h24Z"></path>
                                                            </svg>
                                                        )}
                                                        {item.icon === 'Note' && (
                                                            <svg xmlns="http://www.w3.org/2000/svg" width="24px" height="24px" fill="currentColor" viewBox="0 0 256 256">
                                                                <path d="M216,40H40A16,16,0,0,0,24,56V200a16,16,0,0,0,16,16H216a16,16,0,0,0,16-16V56A16,16,0,0,0,216,40ZM40,56H216v96H176a16,16,0,0,0-16,16v48H40Zm152,144V168h24v32Z"></path>
                                                            </svg>
                                                        )}
                                                        {item.icon === 'Case Study' && (
                                                            <svg xmlns="http://www.w3.org/2000/svg" width="24px" height="24px" fill="currentColor" viewBox="0 0 256 256">
                                                                <path d="M128,16A112,112,0,1,0,240,128,112.13,112.13,0,0,0,128,16Zm0,208a96,96,0,1,1,96-96A96.11,96.11,0,0,1,128,224Z"></path>
                                                            </svg>
                                                        )}
                                                        {item.icon === 'Tree' && (
                                                            <svg xmlns="http://www.w3.org/2000/svg" width="24px" height="24px" fill="currentColor" viewBox="0 0 256 256">
                                                                <path d="M198.1,62.6a76,76,0,0,0-140.2,0A72.27,72.27,0,0,0,16,127.8C15.89,166.62,47.36,199,86.14,200A71.68,71.68,0,0,0,120,192.49V232a8,8,0,0,0,16,0V192.49A71.45,71.45,0,0,0,168,200l1.86,0c38.78-1,70.25-33.36,70.14-72.18A72.26,72.26,0,0,0,198.1,62.6ZM169.45,184a55.61,55.61,0,0,1-32.52-9.4q-.47-.3-.93-.57V132.94l43.58-21.78a8,8,0,1,0-7.16-14.32L136,115.06V88a8,8,0,0,0-16,0v51.06L83.58,120.84a8,8,0,1,0-7.16,14.32L120,156.94V174q-.47.27-.93.57A55.7,55.7,0,0,1,86.55,184a56,56,0,0,1-22-106.86,15.9,15.9,0,0,0,8.05-8.33,60,60,0,0,1,110.7,0,15.9,15.9,0,0,0,8.05,8.33,56,56,0,0,1-22,106.86Z"></path>
                                                            </svg>
                                                        )}
                                                    </div>
                                                    <span className="absolute left-full top-1/2 transform -translate-y-1/2 translate-x-2 bg-gray-900 text-white px-2 py-1 rounded text-sm whitespace-nowrap opacity-0 group-hover/item:opacity-100 transition-opacity duration-200 pointer-events-none ml-2 z-50">
                                                        {item.name}
                                                    </span>
                                                </Link>
                                            ))}
                                        </div>
                                        {/* Profile Icon at Bottom */}
                                        <Link href="/profile" className="relative flex justify-center items-center w-full p-3 rounded-lg transition-all duration-300 ease-in-out text-gray-600 hover:bg-gray-100 hover:transform hover:-translate-y-0.5 group/item">
                                            <div className="flex justify-center items-center w-full h-full">
                                                <svg xmlns="http://www.w3.org/2000/svg" width="24px" height="24px" fill="currentColor" viewBox="0 0 256 256">
                                                    <path d="M128,24A104,104,0,1,0,232,128,104.11,104.11,0,0,0,128,24ZM74.08,197.5a64,64,0,0,1,107.84,0,87.83,87.83,0,0,1-107.84,0ZM96,120a32,32,0,1,1,32,32A32,32,0,0,1,96,120Zm97.76,66.41a79.66,79.66,0,0,0-36.06-28.75,48,48,0,1,0-59.4,0,79.66,79.66,0,0,0-36.06,28.75,88,88,0,1,1,131.52,0Z"></path>
                                                </svg>
                                            </div>
                                            <span className="absolute left-full top-1/2 transform -translate-y-1/2 translate-x-2 bg-gray-900 text-white px-2 py-1 rounded text-sm whitespace-nowrap opacity-0 group-hover/item:opacity-100 transition-opacity duration-200 pointer-events-none ml-2 z-50">
                                                Profile
                                            </span>
                                        </Link>
                                    </div>
                                </div>
                            </div>
                        ) : (
                            <div className="hidden md:block">
                                <NewSidebar navItems={navItems} />
                            </div>
                        )}
                    </>
                )}
                
                {/* Main content */}
                <main className={`flex-1 w-full ${isLoggedIn && showNav && pathname !== '/chat' ? 'md:ml-20' : ''} ${isLoggedIn ? 'pt-0 md:pt-20 pb-50 md:pb-20' : 'py-20'}`} style={{ backgroundColor: '#ffffff' }}>
                    <div className="w-full">
                        {children}
                    </div>
                </main>
            </div>

            {/* Mobile Bottom Navigation (only visible on smaller screens) */}
            {isLoggedIn && (
                <div className="fixed bottom-0 left-0 right-0 w-full bg-white border-t border-gray-200 md:hidden z-50 font-departure shadow-lg">
                    <div className="grid grid-cols-4 py-1 px-2 safe-area-inset-bottom">
                        <Link 
                            href="/chat" 
                            className={`flex flex-col items-center justify-center text-xs font-departure py-2 px-1 rounded-lg transition-all duration-200 active:scale-95 ${pathname === '/chat' ? 'text-blue-600 bg-blue-50' : 'text-gray-600 hover:text-blue-600 hover:bg-gray-50'}`}
                            style={{ minHeight: '60px', touchAction: 'manipulation', WebkitTapHighlightColor: 'transparent' }}
                        >
                            <span className="material-icons-outlined text-lg">chat</span>
                            <span className="mt-1">Chat</span>
                        </Link>
                        <Link 
                            href="/peers" 
                            className={`flex flex-col items-center justify-center text-xs font-departure py-2 px-1 rounded-lg transition-all duration-200 active:scale-95 ${pathname === '/peers' ? 'text-blue-600 bg-blue-50' : 'text-gray-600 hover:text-blue-600 hover:bg-gray-50'}`}
                            style={{ minHeight: '60px', touchAction: 'manipulation', WebkitTapHighlightColor: 'transparent' }}
                        >
                            <span className="material-icons-outlined text-lg">people</span>
                            <span className="mt-1">Peers</span>
                        </Link>
                        
                        {/* More menu button */}
                        <div className="relative">
                            <button 
                                className={`flex flex-col items-center justify-center w-full text-xs font-departure py-2 px-1 rounded-lg transition-all duration-200 active:scale-95 ${moreMenuOpen ? 'text-blue-600 bg-blue-50' : 'text-gray-600 hover:text-blue-600 hover:bg-gray-50'}`}
                                onClick={() => setMoreMenuOpen(!moreMenuOpen)}
                                aria-label="More options"
                                style={{ minHeight: '60px', touchAction: 'manipulation', WebkitTapHighlightColor: 'transparent' }}
                            >
                                <span className="material-icons-outlined text-lg">more_horiz</span>
                                <span className="mt-1">More</span>
                            </button>
                            
                            {/* More dropdown menu */}
                            {moreMenuOpen && (
                                <div 
                                    ref={moreMenuRef}
                                    className="absolute bottom-full left-1/2 transform -translate-x-1/2 w-64 mb-3 bg-white rounded-2xl shadow-xl border border-gray-200 overflow-hidden"
                                >
                                    <div className="py-1">
                                        {/* Dropdown menu items with dark mode styles */}
                                        <Link 
                                            href="/vector-search" 
                                            className={`flex items-center px-4 py-4 text-sm font-medium transition-all duration-200 active:scale-95 ${pathname === '/vector-search' ? 'bg-blue-50 text-blue-600' : 'text-gray-700 hover:bg-gray-50 hover:text-blue-600'}`}
                                            style={{ minHeight: '56px', touchAction: 'manipulation', WebkitTapHighlightColor: 'transparent' }}
                                        >
                                            <span className="material-icons-outlined mr-3 text-current">trending_up</span>
                                            Career Recommendation
                                        </Link>
                                        <Link 
                                            href="/find-your-way" 
                                            className={`flex items-center px-4 py-3 text-sm ${pathname === '/find-your-way' ? 'bg-stitch-primary/50 text-stitch-accent' : 'text-stitch-sage hover:bg-stitch-primary/30 hover:text-stitch-accent'}`}
                                        >
                                            <span className="material-icons-outlined mr-2 text-stitch-sage">explore</span>
                                            Pathway Explorer
                                        </Link>
                                        <Link 
                                            href="/career" 
                                            className={`flex items-center px-4 py-3 text-sm ${pathname === '/career' ? 'bg-stitch-primary/50 text-stitch-accent' : 'text-stitch-sage hover:bg-stitch-primary/30 hover:text-stitch-accent'}`}
                                        >
                                            <span className="material-icons-outlined mr-2 text-stitch-sage">business</span>
                                            Career Explorer
                                        </Link>
                                        <Link 
                                            href="/enhanced-skills" 
                                            className={`flex items-center px-4 py-3 text-sm ${
                                                pathname === '/enhanced-skills'
                                                    ? 'bg-stitch-primary/50 text-stitch-accent font-bold'
                                                    : 'text-stitch-sage hover:bg-stitch-primary/30 hover:text-stitch-accent'
                                            }`}
                                        >
                                            <span className="material-icons-outlined mr-2 text-stitch-sage">school</span>
                                            Enhanced Skills Path
                                        </Link>
                                        <Link
                                            href="/holland-test"
                                            className={`flex items-center px-4 py-3 text-sm ${
                                                pathname === '/holland-test'
                                                    ? 'bg-stitch-primary/50 text-stitch-accent font-bold'
                                                    : 'text-stitch-sage hover:bg-stitch-primary/30 hover:text-stitch-accent'
                                            }`}
                                        >
                                            <span className="material-icons-outlined mr-2 text-stitch-sage">psychology</span>
                                            Test Holland (RIASEC)
                                        </Link>
                                        <Link
                                            href="/education"
                                            className={`flex items-center px-4 py-3 text-sm ${
                                                pathname === '/education'
                                                    ? 'bg-stitch-primary/50 text-stitch-accent font-bold'
                                                    : 'text-stitch-sage hover:bg-stitch-primary/30 hover:text-stitch-accent'
                                            }`}
                                        >
                                            <span className="material-icons-outlined mr-2 text-stitch-sage">school</span>
                                            Education Programs
                                            <span className="ml-2 px-2 py-1 text-xs bg-stitch-accent text-white rounded-full">New</span>
                                        </Link>
                                        <div className="border-t border-stitch-border mt-1"></div>
                                        
                                        {/* Theme Toggle in mobile menu */}
                                        <div className="flex items-center px-4 py-3">
                                            <span className="material-icons-outlined mr-2 text-stitch-sage">palette</span>
                                            <span className="text-sm text-stitch-sage mr-auto">Thème</span>
                                            <ThemeToggle />
                                        </div>
                                        
                                        <button 
                                            onClick={handleLogout}
                                            className="flex items-center w-full px-4 py-3 text-sm text-red-500 hover:bg-stitch-primary/30"
                                        >
                                            <span className="material-icons-outlined mr-2">logout</span>
                                            Logout
                                        </button>
                                    </div>
                                </div>
                            )}
                        </div>
                        
                        <div className="relative">
                            <button
                                className={`flex flex-col items-center justify-center w-full text-xs font-departure py-2 px-1 rounded-lg transition-all duration-200 active:scale-95 ${
                                    pathname === '/space' || pathname === '/tree-path' || workspaceMenuOpen
                                        ? 'text-blue-600 bg-blue-50'
                                        : 'text-gray-600 hover:text-blue-600 hover:bg-gray-50'
                                }`}
                                onClick={() => setWorkspaceMenuOpen(!workspaceMenuOpen)}
                                style={{ minHeight: '60px', touchAction: 'manipulation', WebkitTapHighlightColor: 'transparent' }}
                            >
                                <span className="material-icons-outlined text-lg">folder</span>
                                <span className="mt-1">Workspace</span>
                            </button>
                            
                        {/* Mobile Workspace Dropdown Menu */}
                        {workspaceMenuOpen && (
                            <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 w-48 mb-3 bg-white rounded-2xl shadow-xl border border-gray-200 overflow-hidden">
                                <div className="py-1">
                                    <Link 
                                        href="/space"
                                        onClick={() => setWorkspaceMenuOpen(false)}
                                        className={`flex items-center px-4 py-4 text-sm font-medium transition-all duration-200 active:scale-95
                                            ${pathname === '/space'
                                                ? 'text-blue-600 bg-blue-50'
                                                : 'text-gray-700 hover:bg-gray-50 hover:text-blue-600'
                                            }`}
                                        style={{ minHeight: '56px', touchAction: 'manipulation', WebkitTapHighlightColor: 'transparent' }}
                                    >
                                        <span className="material-icons-outlined mr-3 text-current">space_dashboard</span>
                                        Space
                                    </Link>
                                    <Link 
                                        href="/tree-path"
                                        onClick={() => setWorkspaceMenuOpen(false)}
                                        className={`block px-4 py-2 text-sm rounded-md transition-colors duration-150 ease-in-out
                                            ${pathname === '/tree-path'
                                                ? 'text-stitch-accent bg-stitch-primary/50'
                                                : 'text-stitch-sage hover:text-stitch-accent hover:bg-stitch-primary/30'
                                            }`}
                                    >
                                        <span className="material-icons-outlined mr-2 text-stitch-sage">account_tree</span>
                                        Tree Path
                                    </Link>
                                </div>
                            </div>
                        )}
                        </div>
                        <MobileProfileMenu
                            pathname={pathname}
                            setMoreMenuOpen={setMoreMenuOpen}
                            setCareerMenuOpen={setCareerMenuOpen}
                            setWorkspaceMenuOpen={setWorkspaceMenuOpen}
                        />
                    </div>
                </div>
            )}
        </div>
    );
}