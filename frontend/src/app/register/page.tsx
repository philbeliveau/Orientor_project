'use client';
import { useState, useEffect } from 'react';
import axios from 'axios';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { endpoint, logApiDetails } from '@/utils/api';

interface RegisterResponse {
    access_token: string;
}

interface ApiError {
    response?: {
        data?: {
            detail?: string;
        };
        status?: number;
    };
    message?: string;
}

export default function RegisterPage() {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const router = useRouter();
    
    // Log API details when component mounts
    useEffect(() => {
        logApiDetails();
    }, []);
    
    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        
        if (password !== confirmPassword) {
            setError('Passwords do not match');
            return;
        }
        
        setLoading(true);
        setError('');
        
        try {
            console.log('Attempting to register with:', { email, password });
            
            const registerUrl = endpoint('/users/register');
            console.log('Full request URL:', registerUrl);
            
            const response = await axios.post<RegisterResponse>(
                registerUrl, 
                { email, password },
                { 
                    headers: { 'Content-Type': 'application/json' },
                    timeout: 10000 // 10 second timeout
                }
            );
            
            console.log('Registration successful:', response.data);
            
            // Redirect to login page after successful registration
            router.push('/login');
        } catch (err) {
            const error = err as ApiError;
            console.error('Registration error:', error);
            
            if (error.message === 'Network Error') {
                setError('Cannot connect to the server. Please check if the backend server is running.');
            } else if (error.response?.status === 400) {
                setError(error.response.data?.detail || 'Email already registered or invalid format.');
            } else {
                setError(error.response?.data?.detail || error.message || 'Registration failed. Please try again.');
            }
        } finally {
            setLoading(false);
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
                        Create Your Account
                    </h2>
                    <p className="text-neutral-300">
                        Join our community and start your journey
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
                                    disabled={loading}
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
                                    placeholder="Create a strong password"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    disabled={loading}
                                />
                            </div>
                            
                            <div className="input-group">
                                <label htmlFor="confirmPassword" className="label">
                                    Confirm Password
                                </label>
                                <input
                                    id="confirmPassword"
                                    name="confirmPassword"
                                    type="password"
                                    required
                                    className="input"
                                    placeholder="Confirm your password"
                                    value={confirmPassword}
                                    onChange={(e) => setConfirmPassword(e.target.value)}
                                    disabled={loading}
                                />
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
                                className="btn btn-primary w-full"
                                disabled={loading}
                            >
                                {loading ? (
                                    <span className="flex items-center justify-center">
                                        <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                        </svg>
                                        Creating account...
                                    </span>
                                ) : 'Create Account'}
                            </button>
                        </div>
                        
                        <div className="text-center text-sm text-neutral-300 pt-4">
                            Already have an account?{' '}
                            <Link href="/login" className="text-primary-teal hover:text-primary-lilac transition-colors duration-300 font-medium">
                                Sign in
                            </Link>
                        </div>
                    </form>
                </div>
                
                <div className="mt-8 text-center text-xs text-neutral-400">
                    By signing up, you agree to our
                    <a href="#" className="text-primary-teal hover:text-primary-lilac mx-1">Terms of Service</a>
                    and
                    <a href="#" className="text-primary-teal hover:text-primary-lilac mx-1">Privacy Policy</a>
                </div>
            </div>
        </div>
    );
} 