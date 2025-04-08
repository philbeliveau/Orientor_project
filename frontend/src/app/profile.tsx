// src/app/profile/page.tsx
import {useState } from 'react';
import axios from 'axios';
// import { AxiosError } from 'axios';

const ProfilePage = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [message, setMessage] = useState('');

    const handleUpdate = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            const token = localStorage.getItem('access_token'); // Assuming you store the token in local storage
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
            setMessage('Profile updated successfully!');
        } catch (error) {
            const axiosError = error as { response?: { data?: { detail?: string } } };
            setMessage('Error updating profile: ' + (axiosError.response?.data?.detail || 'Unknown error'));
        }
    };

    return (
        <div className="container mx-auto p-4">
            <h1 className="text-2xl font-bold mb-6">User Profile</h1>
            <form onSubmit={handleUpdate} className="max-w-md space-y-4">
                <div className="space-y-2">
                    <label className="block text-sm font-medium">Email:</label>
                    <input
                        type="email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        className="w-full p-2 border rounded-md"
                    />
                </div>
                <div className="space-y-2">
                    <label className="block text-sm font-medium">New Password (optional):</label>
                    <input
                        type="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        className="w-full p-2 border rounded-md"
                        placeholder="Leave blank to keep current password"
                    />
                </div>
                <button 
                    type="submit" 
                    className="w-full bg-blue-500 text-white py-2 px-4 rounded-md hover:bg-blue-600 transition-colors"
                >
                    Update Profile
                </button>
            </form>
            {message && (
                <p className={`mt-4 p-3 rounded ${
                    message.includes('Error') ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'
                }`}>
                    {message}
                </p>
            )}
        </div>
    );
};

export default ProfilePage;