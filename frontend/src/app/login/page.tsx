'use client';
import { useState } from 'react';
import axios from 'axios';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import MainLayout from '@/components/layout/MainLayout';

interface LoginResponse {
    access_token: string;
}

interface ApiError {
    response?: {
        data?: {
            detail?: string;
        };
    };
}

export default function LoginPage() {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState<string | null>(null);
    const router = useRouter();

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            const response = await axios.post<LoginResponse>(
                'http://localhost:8000/users/login',
                { email, password }
            );
            localStorage.setItem('access_token', response.data.access_token);
            router.push('/profile');
        } catch (err) {
            const error = err as ApiError;
            setError(error.response?.data?.detail || 'Login failed');
        }
    };

    return (
        <MainLayout>
            <div className="flex min-h-[80vh] items-center justify-center">
                <div className="w-full max-w-md space-y-8 bg-gray-800 p-8 rounded-lg shadow-lg">
                    <div>
                        <h2 className="text-center text-3xl font-bold text-gray-100">
                            Sign in to your account
                        </h2>
                    </div>
                    <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
                        {/* Email Input */}
                        <input
                            type="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            placeholder="Email"
                            required
                        />
                        {/* Password Input */}
                        <input
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            placeholder="Password"
                            required
                        />
                        {error && (
                            <div className="text-red-500 text-sm text-center">
                                {error}
                            </div>
                        )}
                        <button
                            type="submit"
                            className="group relative flex w-full justify-center rounded-md bg-blue-600 px-3 py-2 text-sm font-semibold text-white hover:bg-blue-500"
                        >
                            Sign in
                        </button>
                    </form>
                    <div className="text-center text-sm text-gray-400">
                        Don&apos;t have an account?{' '}
                        <Link href="/register" className="text-blue-400 hover:text-blue-300">
                            Register here
                        </Link>
                    </div>
                </div>
            </div>
        </MainLayout>
    );
}