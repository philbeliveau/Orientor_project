// src/app/profile/page.tsx
import {useState } from 'react';
import axios from 'axios';
// import { AxiosError } from 'axios';

const ProfilePage = () => {
    const [username, setUsername] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [message, setMessage] = useState('');
    const handleUpdate = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            const token = localStorage.getItem('access_token'); // Assuming you store the token in local storage
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
        // ... existing code ...
        } catch (error) {
            const axiosError = error as { response?: { data?: { detail?: string } } };
            setMessage('Error updating profile: ' + (axiosError.response?.data?.detail || 'Unknown error'));
        }
    };
    return (
        <div>
            <h1>User Profile</h1>
            <form onSubmit={handleUpdate}>
                <div>
                    <label>Username:</label>
                    <input
                        type="text"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                    />
                </div>
                <div>
                    <label>Email:</label>
                    <input
                        type="email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                    />
                </div>
                <div>
                    <label>Password:</label>
                    <input
                        type="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                    />
                </div>
                <button type="submit">Update Profile</button>
            </form>
            {message && <p>{message}</p>}
        </div>
    );
};

export default ProfilePage;