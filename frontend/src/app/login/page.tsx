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
        
        // Perform a health check to the backend
        const checkBackendHealth = async () => {
            try {
                const healthUrl = endpoint('/api/health');
                console.log('Checking backend health at:', healthUrl);
                const response = await axios.get(healthUrl, { 
                    timeout: 5000,
                    withCredentials: true 
                });
                console.log('Backend health check result:', response.data);
            } catch (err: any) {
                console.error('Backend health check failed:', {
                    message: err.message,
                    status: err.response?.status,
                    data: err.response?.data,
                    url: err.config?.url
                });
            }
        };
        
        checkBackendHealth();
    }, [router]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);
        setError('');
        
        try {
            console.log('Attempting to login with:', { email });
            
            const loginUrl = endpoint('/api/users/login');
            console.log('Full login URL:', loginUrl);
            
            const response = await axios.post<LoginResponse>(
                loginUrl,
                { email, password },
                {
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    timeout: 10000,
                    withCredentials: true
                }
            );
            
            console.log('Login successful, token received');
            
            // Store the token in localStorage
            localStorage.setItem('access_token', response.data.access_token);
            
            // Redirect to chat page after successful login
            router.push('/chat');
        } catch (err: any) {
            console.error('Login error details:', {
                message: err.message,
                status: err.response?.status,
                statusText: err.response?.statusText,
                data: err.response?.data,
                headers: err.response?.headers
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