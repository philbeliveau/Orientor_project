'use client';
import { useState } from 'react';
import axios from 'axios';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import MainLayout from '@/components/layout/MainLayout';

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
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const router = useRouter();
    
    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setError('');
        
        try {
            console.log('Attempting to register with:', { email, password });
            const response = await axios.post<RegisterResponse>(
                'http://localhost:8000/users/register', 
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
        <MainLayout>
            <div className="flex min-h-[80vh] items-center justify-center">
                <div className="w-full max-w-md space-y-8 bg-gray-800 p-8 rounded-lg shadow-lg">
                    <div>
                        <h2 className="text-center text-3xl font-bold text-gray-100">
                            Sign up for Orientor
                        </h2>
                    </div>
                    <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
                        <div className="space-y-4 rounded-md shadow-sm">
                            <div>
                                <label htmlFor="email" className="sr-only">
                                    Email address
                                </label>
                                <input
                                    id="email"
                                    name="email"
                                    type="email"
                                    required
                                    className="relative block w-full rounded-md border-0 p-2 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-blue-600"
                                    placeholder="Email address"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    disabled={loading}
                                />
                            </div>
                            <div>
                                <label htmlFor="password" className="sr-only">
                                    Password
                                </label>
                                <input
                                    id="password"
                                    name="password"
                                    type="password"
                                    required
                                    className="relative block w-full rounded-md border-0 p-2 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-blue-600"
                                    placeholder="Password"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    disabled={loading}
                                />
                            </div>
                        </div>

                        {error && (
                            <div className="text-red-500 text-sm p-2 bg-red-500/10 rounded-md text-center">
                                {error}
                            </div>
                        )}

                        <div>
                            <button
                                type="submit"
                                className="group relative flex w-full justify-center rounded-md bg-blue-600 px-3 py-2 text-sm font-semibold text-white hover:bg-blue-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600"
                                disabled={loading}
                            >
                                {loading ? 'Signing up...' : 'Sign up'}
                            </button>
                        </div>
                    </form>
                    <div className="text-center text-sm text-gray-400">
                        Already have an account?{' '}
                        <Link href="/login" className="text-blue-400 hover:text-blue-300">
                            Sign in
                        </Link>
                    </div>
                </div>
            </div>
        </MainLayout>
    );
} 