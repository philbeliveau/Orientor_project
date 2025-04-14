'use client';
import { useState, useEffect } from 'react';
import MainLayout from '@/components/layout/MainLayout';
import axios from 'axios';

// Define API URL with fallback and trim any trailing spaces
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const cleanApiUrl = API_URL ? API_URL.trim() : '';

interface ApiError {
    response?: {
        data?: {
            detail?: string;
        };
        status?: number;
    };
    message?: string;
}

interface Profile {
    name: string;
    age: number | '';
    sex: string;
    major: string;
    year: number | '';
    gpa: number | '';
    hobbies: string;
    country: string;
    state_province: string;
    unique_quality: string;
    story: string;
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
        name: '',
        age: '',
        sex: '',
        major: '',
        year: '',
        gpa: '',
        hobbies: '',
        country: '',
        state_province: '',
        unique_quality: '',
        story: '',
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
                const response = await axios.get<Profile>(`${cleanApiUrl}/profiles/me`, {
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
                    `${cleanApiUrl}/users/update`,
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
                `${cleanApiUrl}/profiles/update`,
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
        let value: string | number = e.target.value;
        
        // Convert numeric fields
        if (['age', 'year'].includes(field) && value !== '') {
            value = parseInt(value);
        } else if (field === 'gpa' && value !== '') {
            value = parseFloat(value);
        }
        
        setProfile(prev => ({
            ...prev,
            [field]: value
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

                            {/* Basic Information Section */}
                            <div className="space-y-4">
                                <h3 className="text-xl font-semibold text-secondary-purple mb-4">Basic Information</h3>
                                <div>
                                    <label className="block text-sm font-medium text-neutral-lightgray mb-1">
                                        Full Name
                                    </label>
                                    <input
                                        type="text"
                                        value={profile.name}
                                        onChange={handleProfileChange('name')}
                                        className="input"
                                        placeholder="Your full name"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-neutral-lightgray mb-1">
                                        Age
                                    </label>
                                    <input
                                        type="number"
                                        value={profile.age}
                                        onChange={handleProfileChange('age')}
                                        className="input"
                                        placeholder="Your age"
                                        min="0"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-neutral-lightgray mb-1">
                                        Sex
                                    </label>
                                    <select
                                        value={profile.sex}
                                        onChange={handleProfileChange('sex')}
                                        className="input bg-gray-800"
                                    >
                                        <option value="">Select your sex</option>
                                        <option value="Male">Male</option>
                                        <option value="Female">Female</option>
                                        <option value="Other">Other</option>
                                        <option value="Prefer not to say">Prefer not to say</option>
                                    </select>
                                </div>
                            </div>

                            {/* Academic Information Section */}
                            <div className="space-y-4">
                                <h3 className="text-xl font-semibold text-secondary-teal mb-4">Academic Information</h3>
                                <div>
                                    <label className="block text-sm font-medium text-neutral-lightgray mb-1">
                                        Major
                                    </label>
                                    <input
                                        type="text"
                                        value={profile.major}
                                        onChange={handleProfileChange('major')}
                                        className="input"
                                        placeholder="Your field of study"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-neutral-lightgray mb-1">
                                        Year
                                    </label>
                                    <input
                                        type="number"
                                        value={profile.year}
                                        onChange={handleProfileChange('year')}
                                        className="input"
                                        placeholder="Current year of study"
                                        min="1"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-neutral-lightgray mb-1">
                                        GPA
                                    </label>
                                    <input
                                        type="number"
                                        value={profile.gpa}
                                        onChange={handleProfileChange('gpa')}
                                        className="input"
                                        placeholder="Your GPA"
                                        step="0.01"
                                        min="0"
                                        max="4.0"
                                    />
                                </div>
                            </div>

                            {/* Location Section */}
                            <div className="space-y-4">
                                <h3 className="text-xl font-semibold text-secondary-purple mb-4">Location</h3>
                                <div>
                                    <label className="block text-sm font-medium text-neutral-lightgray mb-1">
                                        Country
                                    </label>
                                    <input
                                        type="text"
                                        value={profile.country}
                                        onChange={handleProfileChange('country')}
                                        className="input"
                                        placeholder="Your country"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-neutral-lightgray mb-1">
                                        State/Province
                                    </label>
                                    <input
                                        type="text"
                                        value={profile.state_province}
                                        onChange={handleProfileChange('state_province')}
                                        className="input"
                                        placeholder="Your state or province"
                                    />
                                </div>
                            </div>

                            {/* Personal Details Section */}
                            <div className="space-y-4">
                                <h3 className="text-xl font-semibold text-secondary-teal mb-4">Personal Details</h3>
                                <div>
                                    <label className="block text-sm font-medium text-neutral-lightgray mb-1">
                                        Hobbies
                                    </label>
                                    <textarea
                                        value={profile.hobbies}
                                        onChange={handleProfileChange('hobbies')}
                                        className="input"
                                        placeholder="What are your hobbies? (comma-separated)"
                                        rows={3}
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-neutral-lightgray mb-1">
                                        Unique Quality
                                    </label>
                                    <textarea
                                        value={profile.unique_quality}
                                        onChange={handleProfileChange('unique_quality')}
                                        className="input"
                                        placeholder="What makes you unique?"
                                        rows={3}
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-neutral-lightgray mb-1">
                                        Your Story
                                    </label>
                                    <textarea
                                        value={profile.story}
                                        onChange={handleProfileChange('story')}
                                        className="input"
                                        placeholder="Tell us your story"
                                        rows={4}
                                    />
                                </div>
                            </div>

                            {/* Preferences Section */}
                            <div className="space-y-4">
                                <h3 className="text-xl font-semibold text-secondary-purple mb-4">Preferences</h3>
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
                                        Interests
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
