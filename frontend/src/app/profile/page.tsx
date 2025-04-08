'use client';
import { useState, useEffect } from 'react';
import MainLayout from '@/components/layout/MainLayout';
import axios from 'axios';

interface ApiError {
    response?: {
        data?: {
            detail?: string;
        };
    };
}

interface Profile {
    favorite_movie: string;
    favorite_book: string;
    favorite_celebrities: string;
    learning_style: string;
    interests: string;
}

export default function ProfilePage() {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [profile, setProfile] = useState<Profile>({
        favorite_movie: '',
        favorite_book: '',
        favorite_celebrities: '',
        learning_style: '',
        interests: ''
    });
    const [error, setError] = useState<string | null>(null);
    const [message, setMessage] = useState<string | null>(null);

    // Fetch existing profile data when component mounts
    useEffect(() => {
        const fetchProfile = async () => {
            try {
                const token = localStorage.getItem('access_token');
                const response = await axios.get('http://localhost:8000/profiles/me', {
                    headers: {
                        Authorization: `Bearer ${token}`
                    }
                });
                setProfile(response.data);
            } catch (err) {
                console.log('No existing profile found');
            }
        };
        fetchProfile();
    }, []);

    const handleUpdate = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            const token = localStorage.getItem('access_token');
            // Update user info
            if (email || password) {
                await axios.put(
                    'http://localhost:8000/users/update',
                    { email, password },
                    {
                        headers: {
                            Authorization: `Bearer ${token}`,
                            'Content-Type': 'application/json',
                        },
                    }
                );
            }

            // Update profile info
            await axios.put(
                'http://localhost:8000/profiles/update',
                profile,
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

    const handleProfileChange = (field: keyof Profile) => (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
        setProfile(prev => ({
            ...prev,
            [field]: e.target.value
        }));
    };

    return (
        <MainLayout>
            <div className="space-y-6">
                <h2 className="text-2xl font-bold text-white">User Profile</h2>
                <div className="bg-white rounded-lg shadow-md border border-gray-200 p-6">
                    <form onSubmit={handleUpdate} className="space-y-4">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            {/* Account Settings Section */}
                            <div className="space-y-4">
                                <h3 className="text-lg font-semibold text-gray-700">Account Settings</h3>
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
                                    <label className="block text-gray-700 mb-2">New Password (optional)</label>
                                    <input
                                        type="password"
                                        value={password}
                                        onChange={(e) => setPassword(e.target.value)}
                                        className="flex-1 w-full p-2 rounded-lg bg-gray-50 border border-gray-300 text-gray-900 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                        placeholder="Leave blank to keep current password"
                                    />
                                </div>
                            </div>

                            {/* Personal Preferences Section */}
                            <div className="space-y-4">
                                <h3 className="text-lg font-semibold text-gray-700">Personal Preferences</h3>
                                <div>
                                    <label className="block text-gray-700 mb-2">Favorite Movie</label>
                                    <input
                                        type="text"
                                        value={profile.favorite_movie}
                                        onChange={handleProfileChange('favorite_movie')}
                                        className="flex-1 w-full p-2 rounded-lg bg-gray-50 border border-gray-300 text-gray-900 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                        placeholder="What's your favorite movie?"
                                    />
                                </div>
                                <div>
                                    <label className="block text-gray-700 mb-2">Favorite Book</label>
                                    <input
                                        type="text"
                                        value={profile.favorite_book}
                                        onChange={handleProfileChange('favorite_book')}
                                        className="flex-1 w-full p-2 rounded-lg bg-gray-50 border border-gray-300 text-gray-900 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                        placeholder="What's your favorite book?"
                                    />
                                </div>
                                <div>
                                    <label className="block text-gray-700 mb-2">Favorite Celebrities</label>
                                    <input
                                        type="text"
                                        value={profile.favorite_celebrities}
                                        onChange={handleProfileChange('favorite_celebrities')}
                                        className="flex-1 w-full p-2 rounded-lg bg-gray-50 border border-gray-300 text-gray-900 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                        placeholder="Who inspires you? (comma-separated)"
                                    />
                                </div>
                                <div>
                                    <label className="block text-gray-700 mb-2">Learning Style</label>
                                    <select
                                        value={profile.learning_style}
                                        onChange={handleProfileChange('learning_style')}
                                        className="flex-1 w-full p-2 rounded-lg bg-gray-50 border border-gray-300 text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                    >
                                        <option value="">Select your learning style</option>
                                        <option value="Visual">Visual</option>
                                        <option value="Auditory">Auditory</option>
                                        <option value="Reading/Writing">Reading/Writing</option>
                                        <option value="Kinesthetic">Kinesthetic</option>
                                    </select>
                                </div>
                                <div>
                                    <label className="block text-gray-700 mb-2">Interests</label>
                                    <textarea
                                        value={profile.interests}
                                        onChange={handleProfileChange('interests')}
                                        className="flex-1 w-full p-2 rounded-lg bg-gray-50 border border-gray-300 text-gray-900 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                        placeholder="What are your interests? (comma-separated)"
                                        rows={3}
                                    />
                                </div>
                            </div>
                        </div>

                        <button
                            type="submit"
                            className="w-full bg-blue-600 hover:bg-blue-500 text-white px-4 py-2 rounded-lg transition-colors duration-200"
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
