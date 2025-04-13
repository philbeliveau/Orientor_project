'use client';
import { useState, useEffect } from 'react';
import axios from 'axios';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { endpoint, logApiDetails } from '@/utils/api';

interface LoginResponse {
    access_token: string;
    token_type: string;
}

export default function LoginPage() {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const router = useRouter();

    useEffect(() => {
        // Check if user is already logged in
        const token = localStorage.getItem('access_token');
        if (token) {
            router.push('/chat');
        }
        
        // Log API details for debugging
        logApiDetails();
    }, [router]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);
        setError('');
        
        try {
            console.log('Attempting to login with:', { email });
            
            const loginUrl = endpoint('/users/login');
            console.log('Full login URL:', loginUrl);
            
            const response = await axios.post<LoginResponse>(loginUrl, {
                email,
                password
            });
            
            // Store the token in localStorage
            localStorage.setItem('access_token', response.data.access_token);
            
            // Redirect to chat page after successful login
            router.push('/chat');
        } catch (err: any) {
            console.error('Login error:', err);
            setError(err.response?.data?.detail || 'Login failed');
            setIsLoading(false);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center px-4 py-12">
            <div className="w-full max-w-md">
                <div className="text-center mb-8">
                    <h1 className="text-4xl font-bold font-display gradient-text mb-2">
                        Navigo
                    </h1>
                    <h2 className="text-2xl font-bold text-neutral-100 mb-2">
                        Welcome Back
                    </h2>
                    <p className="text-neutral-300">
                        Your personal guide for growth and self-discovery
                    </p>
                </div>
                
                <div className="card backdrop-blur-md">
                    <form className="space-y-6" onSubmit={handleSubmit}>
                        <div className="space-y-4">
                            <div className="input-group">
                                <label htmlFor="email" className="label">
                                    Email address
                                </label>
                                <input
                                    id="email"
                                    name="email"
                                    type="email"
                                    required
                                    className="input"
                                    placeholder="you@example.com"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                />
                            </div>
                            
                            <div className="input-group">
                                <label htmlFor="password" className="label">
                                    Password
                                </label>
                                <input
                                    id="password"
                                    name="password"
                                    type="password"
                                    required
                                    className="input"
                                    placeholder="••••••••"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                />
                            </div>
                            
                            <div className="text-right">
                                <a href="#" className="text-sm text-primary-teal hover:text-primary-lilac transition-colors duration-300">
                                    Forgot password?
                                </a>
                            </div>
                        </div>

                        {error && (
                            <div className="text-accent-coral text-sm text-center py-3 px-4 bg-accent-coral/10 border border-accent-coral/20 rounded-lg">
                                {error}
                            </div>
                        )}

                        <div>
                            <button
                                type="submit"
                                disabled={isLoading}
                                className="btn btn-primary w-full"
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
                        </div>
                    
                        <div className="text-center text-sm text-neutral-300 pt-4">
                            Don't have an account?{' '}
                            <Link href="/register" className="text-primary-teal hover:text-primary-lilac transition-colors duration-300 font-medium">
                                Register here
                            </Link>
                        </div>
                    </form>
                </div>
                
                <div className="mt-8 text-center text-xs text-neutral-400">
                    By signing in, you agree to our
                    <a href="#" className="text-primary-teal hover:text-primary-lilac mx-1">Terms of Service</a>
                    and
                    <a href="#" className="text-primary-teal hover:text-primary-lilac mx-1">Privacy Policy</a>
                </div>
            </div>
        </div>
    );
}