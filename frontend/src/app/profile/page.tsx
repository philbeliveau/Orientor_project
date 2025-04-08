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
            <div className="max-w-4xl mx-auto space-y-6">
                <div className="flex items-center justify-between">
                    <h2 className="text-2xl font-bold text-neutral-lightgray">Your Profile</h2>
                    <div className="text-sm text-neutral-lightgray opacity-70">
                        Help us personalize your experience
                    </div>
                </div>
                
                <div className="card">
                    <form onSubmit={handleUpdate} className="space-y-6">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            {/* Account Settings Section */}
                            <div className="space-y-4">
                                <h3 className="text-xl font-semibold text-secondary-teal mb-4">Account Settings</h3>
                                <div>
                                    <label className="block text-sm font-medium text-neutral-lightgray mb-1">
                                        Email Address
                                    </label>
                                    <input
                                        type="email"
                                        value={email}
                                        onChange={(e) => setEmail(e.target.value)}
                                        className="input"
                                        placeholder="your@email.com"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-neutral-lightgray mb-1">
                                        New Password
                                    </label>
                                    <input
                                        type="password"
                                        value={password}
                                        onChange={(e) => setPassword(e.target.value)}
                                        className="input"
                                        placeholder="Leave blank to keep current password"
                                    />
                                </div>
                            </div>

                            {/* Personal Preferences Section */}
                            <div className="space-y-4">
                                <h3 className="text-xl font-semibold text-secondary-purple mb-4">Personal Preferences</h3>
                                <div>
                                    <label className="block text-sm font-medium text-neutral-lightgray mb-1">
                                        Favorite Movie
                                    </label>
                                    <input
                                        type="text"
                                        value={profile.favorite_movie}
                                        onChange={handleProfileChange('favorite_movie')}
                                        className="input"
                                        placeholder="What's your favorite movie?"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-neutral-lightgray mb-1">
                                        Favorite Book
                                    </label>
                                    <input
                                        type="text"
                                        value={profile.favorite_book}
                                        onChange={handleProfileChange('favorite_book')}
                                        className="input"
                                        placeholder="What's your favorite book?"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-neutral-lightgray mb-1">
                                        Role Models
                                    </label>
                                    <input
                                        type="text"
                                        value={profile.favorite_celebrities}
                                        onChange={handleProfileChange('favorite_celebrities')}
                                        className="input"
                                        placeholder="Who inspires you? (comma-separated)"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-neutral-lightgray mb-1">
                                        Learning Style
                                    </label>
                                    <select
                                        value={profile.learning_style}
                                        onChange={handleProfileChange('learning_style')}
                                        className="input bg-gray-800"
                                    >
                                        <option value="">Select your learning style</option>
                                        <option value="Visual">Visual</option>
                                        <option value="Auditory">Auditory</option>
                                        <option value="Reading/Writing">Reading/Writing</option>
                                        <option value="Kinesthetic">Kinesthetic</option>
                                    </select>
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-neutral-lightgray mb-1">
                                        Interests & Hobbies
                                    </label>
                                    <textarea
                                        value={profile.interests}
                                        onChange={handleProfileChange('interests')}
                                        className="input"
                                        placeholder="What are your interests? (comma-separated)"
                                        rows={3}
                                    />
                                </div>
                            </div>
                        </div>

                        <div className="pt-4">
                            <button
                                type="submit"
                                className="btn btn-primary w-full md:w-auto"
                            >
                                Save Changes
                            </button>
                        </div>
                    </form>

                    {error && (
                        <div className="mt-4 p-3 bg-red-900/20 border border-secondary-coral text-secondary-coral rounded-lg">
                            {error}
                        </div>
                    )}
                    {message && (
                        <div className="mt-4 p-3 bg-green-900/20 border border-secondary-teal text-secondary-teal rounded-lg">
                            {message}
                        </div>
                    )}
                </div>
            </div>
        </MainLayout>
    );
}
