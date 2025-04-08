'use client';
import { useState, useEffect } from 'react';
import axios from 'axios';
import { useRouter } from 'next/navigation';
import Link from 'next/link';

interface LoginResponse {
    access_token: string;
    token_type: string;
}

export default function LoginPage() {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const router = useRouter();

    useEffect(() => {
        // Check if user is already logged in
        const token = localStorage.getItem('access_token');
        if (token) {
            router.push('/chat');
        }
    }, [router]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            const response = await axios.post<LoginResponse>('http://localhost:8000/users/login', {
                email,
                password
            });
            
            // Store the token in localStorage
            localStorage.setItem('access_token', response.data.access_token);
            
            // Redirect to chat page after successful login
            router.push('/chat');
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Login failed');
        }
    };

    return (
        <div className="min-h-screen bg-primary-charcoal flex items-center justify-center px-4">
            <div className="w-full max-w-md card space-y-6">
                <div className="text-center">
                    <h1 className="text-4xl font-bold text-secondary-teal mb-2">
                        Orientor
                    </h1>
                    <h2 className="text-2xl font-bold text-neutral-lightgray mb-2">
                        Sign In
                    </h2>
                    <p className="text-neutral-lightgray opacity-70">
                        Your personal mentor for self-discovery
                    </p>
                </div>
                
                <form className="space-y-5" onSubmit={handleSubmit}>
                    <div className="space-y-4">
                        <div>
                            <label htmlFor="email" className="block text-sm font-medium text-neutral-lightgray mb-1">
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
                        
                        <div>
                            <label htmlFor="password" className="block text-sm font-medium text-neutral-lightgray mb-1">
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
                            <a href="#" className="text-sm text-secondary-teal hover:text-secondary-purple transition-colors">
                                Forgot password?
                            </a>
                        </div>
                    </div>

                    {error && (
                        <div className="text-secondary-coral text-sm text-center py-2 bg-red-900/20 rounded-md">
                            {error}
                        </div>
                    )}

                    <div>
                        <button
                            type="submit"
                            className="btn btn-primary w-full"
                        >
                            Sign In
                        </button>
                    </div>
                </form>
                
                <div className="text-center text-sm text-neutral-lightgray">
                    Don't have an account?{' '}
                    <Link href="/register" className="text-secondary-teal hover:text-secondary-purple transition-colors">
                        Register here
                    </Link>
                </div>
            </div>
        </div>
    );
}