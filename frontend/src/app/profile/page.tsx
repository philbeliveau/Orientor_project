'use client';
import { useState } from 'react';
import MainLayout from '@/components/layout/MainLayout';
import axios from 'axios';

interface ApiError {
    response?: {
        data?: {
            detail?: string;
        };
    };
}

export default function ProfilePage() {
    const [username, setUsername] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState<string | null>(null);
    const [message, setMessage] = useState<string | null>(null);

    const handleUpdate = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            const token = localStorage.getItem('access_token');
            await axios.put(
                'http://localhost:8000/users/update',
                { username, email, password },
                {
                    headers: {
                        Authorization: `Bearer ${token}`,
                        'Content-Type': 'application/json',
                    },
                }
            );
            setMessage('Profile updated successfully!');
            setError(null);
        } catch (err) {
            const error = err as ApiError;
            setError(error.response?.data?.detail || 'Update failed');
            setMessage(null);
        }
    };

    return (
        <MainLayout>
            <div className="space-y-6">
                <h2 className="text-2xl font-bold text-white">User Profile</h2>
                <div className="bg-white rounded-lg shadow-md border border-gray-200 p-6">
                    <form onSubmit={handleUpdate} className="space-y-4">
                        <div>
                            <label className="block text-gray-700 mb-2">Username</label>
                            <input
                                type="text"
                                value={username}
                                onChange={(e) => setUsername(e.target.value)}
                                className="flex-1 w-full p-2 rounded-lg bg-gray-50 border border-gray-300 text-gray-900 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                            />
                        </div>
                        <div>
                            <label className="block text-gray-700 mb-2">Email</label>
                            <input
                                type="email"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                className="flex-1 w-full p-2 rounded-lg bg-gray-50 border border-gray-300 text-gray-900 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                            />
                        </div>
                        <div>
                            <label className="block text-gray-700 mb-2">Password</label>
                            <input
                                type="password"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                className="flex-1 w-full p-2 rounded-lg bg-gray-50 border border-gray-300 text-gray-900 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                            />
                        </div>
                        <button
                            type="submit"
                            className="bg-blue-600 hover:bg-blue-500 text-white px-4 py-2 rounded-lg transition-colors duration-200"
                        >
                            Update Profile
                        </button>
                    </form>
                    {error && (
                        <div className="mt-4 p-2 bg-red-100 text-red-700 rounded-lg">
                            {error}
                        </div>
                    )}
                    {message && (
                        <div className="mt-4 p-2 bg-green-100 text-green-700 rounded-lg">
                            {message}
                        </div>
                    )}
                </div>
            </div>
        </MainLayout>
    );
}
