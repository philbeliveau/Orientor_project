'use client';
import { useState, useEffect } from 'react';
import axios from 'axios';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { endpoint, logApiDetails } from '@/utils/api';
import { useAuth } from '@/hooks/useAuth';

interface LoginResponse {
    access_token: string;
    token_type: string;
    user_id: number;
}

export default function LoginPage() {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const router = useRouter();
    
    // Use auth hook to handle redirects for already authenticated users
    const { login, isLoading: authLoading } = useAuth({ 
        redirectTo: '/dashboard', 
        redirectIfFound: true 
    });

    useEffect(() => {
        // Log API details for debugging
        logApiDetails();
    }, []);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);
        setError('');
        
        try {
            console.log('Attempting to login with:', { email });
            
            const loginUrl = endpoint('/auth/login');
            console.log('Full login URL:', loginUrl);
            
            const response = await axios.post<LoginResponse>(
                loginUrl,
                { email, password },
                {
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    timeout: 10000
                }
            );
            
            console.log('Login successful, token received');
            
            // Manually set auth info to avoid triggering useAuth redirect
            localStorage.setItem('access_token', response.data.access_token);
            localStorage.setItem('user_id', response.data.user_id.toString());
            
            // Check if user needs onboarding
            try {
                const { onboardingService } = await import('../../services/onboardingService');
                console.log('🔍 About to check onboarding status...');
                
                const status = await onboardingService.getStatus();
                console.log('✅ Onboarding status received:', status);
                
                if (status.isComplete) {
                    console.log('✅ User onboarding complete, redirecting to dashboard');
                    router.push('/dashboard');
                } else {
                    console.log('❌ User needs onboarding, redirecting to onboarding page');
                    router.push('/onboarding');
                }
            } catch (onboardingError: any) {
                console.error('💥 Error checking onboarding status:', onboardingError);
                console.error('Error details:', {
                    message: onboardingError.message,
                    status: onboardingError.response?.status,
                    data: onboardingError.response?.data
                });
                console.log('🔄 Could not check onboarding status, assuming new user - redirecting to onboarding');
                router.push('/onboarding');
            }
        } catch (err: any) {
            console.error('Login error details:', {
                message: err.message,
                status: err.response?.status,
                statusText: err.response?.statusText,
                data: err.response?.data
            });
            
            // Handle different error cases
            if (err.code === 'ECONNABORTED') {
                setError('Connection timeout. The server took too long to respond.');
            } else if (err.message.includes('Network Error')) {
                setError('Network error. Please check your connection or the server might be down.');
            } else if (err.response?.status === 401) {
                setError('Invalid email or password');
            } else if (err.response?.status === 403) {
                setError('Access forbidden. You may not have permission to log in.');
            } else if (err.response?.status === 404) {
                setError('Login endpoint not found. Please contact support.');
            } else if (err.response?.status === 500) {
                setError('Server error. Please try again later.');
            } else {
                setError(err.response?.data?.detail || 'Login failed. Please try again.');
            }
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 flex items-center justify-center px-4 py-12">
            <div className="w-full max-w-md">
                {/* Header */}
                <div className="text-center mb-8">
                    <div className="flex items-center justify-center mb-4">
                        <div className="w-12 h-12 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-xl flex items-center justify-center">
                            <span className="text-white font-bold text-xl font-departure">N</span>
                        </div>
                    </div>
                    <h1 className="text-3xl font-bold text-gray-900 mb-2 font-departure">
                        Welcome back
                    </h1>
                    <p className="text-gray-600">
                        Sign in to your Navigo account
                    </p>
                </div>
                
                {/* Login Form */}
                <div className="bg-white/80 backdrop-blur-lg shadow-xl rounded-2xl p-8 border border-white/20">
                    <form className="space-y-6" onSubmit={handleSubmit}>
                        <div className="space-y-5">
                            <div>
                                <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                                    Email address
                                </label>
                                <input
                                    id="email"
                                    name="email"
                                    type="email"
                                    required
                                    className="w-full px-4 py-3 border border-gray-200 rounded-xl 
                                        focus:ring-2 focus:ring-blue-500 focus:border-transparent 
                                        transition-all duration-200 bg-white/50 
                                        placeholder-gray-400 text-gray-900
                                        hover:border-gray-300 disabled:bg-gray-50 disabled:cursor-not-allowed"
                                    placeholder="Enter your email"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    disabled={isLoading}
                                />
                            </div>
                            
                            <div>
                                <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
                                    Password
                                </label>
                                <input
                                    id="password"
                                    name="password"
                                    type="password"
                                    required
                                    className="w-full px-4 py-3 border border-gray-200 rounded-xl 
                                        focus:ring-2 focus:ring-blue-500 focus:border-transparent 
                                        transition-all duration-200 bg-white/50 
                                        placeholder-gray-400 text-gray-900
                                        hover:border-gray-300 disabled:bg-gray-50 disabled:cursor-not-allowed"
                                    placeholder="Enter your password"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    disabled={isLoading}
                                />
                            </div>
                        </div>

                        {error && (
                            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-xl text-sm">
                                {error}
                            </div>
                        )}

                        <button
                            type="submit"
                            className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 
                                text-white font-semibold py-3 px-4 rounded-xl 
                                hover:from-blue-700 hover:to-indigo-700 
                                focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 
                                transition-all duration-200 
                                disabled:opacity-50 disabled:cursor-not-allowed 
                                shadow-lg hover:shadow-xl"
                            disabled={isLoading}
                        >
                            {isLoading ? (
                                <span className="flex items-center justify-center">
                                    <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                    </svg>
                                    Signing in...
                                </span>
                            ) : 'Sign In'}
                        </button>
                        
                        <div className="text-center pt-4">
                            <p className="text-sm text-gray-600">
                                Don't have an account?{' '}
                                <Link href="/register" className="text-blue-600 hover:text-blue-700 font-semibold transition-colors duration-200">
                                    Sign up
                                </Link>
                            </p>
                        </div>
                    </form>
                </div>
                
                {/* Footer */}
                <div className="mt-6 text-center">
                    <p className="text-xs text-gray-500">
                        By signing in, you agree to our{' '}
                        <a href="#" className="text-blue-600 hover:text-blue-700 transition-colors">Terms of Service</a>
                        {' '}and{' '}
                        <a href="#" className="text-blue-600 hover:text-blue-700 transition-colors">Privacy Policy</a>
                    </p>
                </div>
            </div>
        </div>
    );
}