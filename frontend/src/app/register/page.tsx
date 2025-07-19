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
    const [name, setName] = useState('');
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
            
            const registerUrl = endpoint('/auth/register');
            console.log('Full request URL:', registerUrl);
            
            const response = await axios.post<RegisterResponse>(
                registerUrl, 
                { email, password, name },
                { 
                    headers: { 'Content-Type': 'application/json' },
                    timeout: 10000 // 10 second timeout
                }
            );
            
            console.log('Registration successful:', response.data);
            
            // Now login the user automatically
            try {
                const loginResponse = await axios.post(
                    endpoint('/auth/login'),
                    { email, password },
                    { 
                        headers: { 'Content-Type': 'application/json' },
                        timeout: 10000 
                    }
                );
                
                // Store the token and user ID in localStorage
                localStorage.setItem('access_token', loginResponse.data.access_token);
                localStorage.setItem('user_id', loginResponse.data.user_id.toString());
                
                console.log('Auto-login successful after registration');
                
                // Redirect to onboarding for new users
                router.push('/onboarding');
            } catch (loginError) {
                console.error('Auto-login failed after registration:', loginError);
                // Still redirect to login if auto-login fails
                router.push('/login');
            }
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
        <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 flex items-center justify-center px-4 py-12">
            <div className="w-full max-w-md">
                {/* Header */}
                <div className="text-center mb-8">
                    <div className="flex items-center justify-center mb-4">
                        <div className="w-12 h-12 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-xl flex items-center justify-center">
                            <span className="text-white font-bold text-xl font-departure">N</span>
                        </div>
                    </div>
                    <h1 className="text-3xl font-bold text-gray-900 mb-2 font-departure">
                        Create your account
                    </h1>
                    <p className="text-gray-600">
                        Join Navigo and start your journey
                    </p>
                </div>
                
                {/* Registration Form */}
                <div className="bg-white/80 backdrop-blur-lg shadow-xl rounded-2xl p-8 border border-white/20">
                    <form className="space-y-6" onSubmit={handleSubmit}>
                        <div className="space-y-5">
                            <div>
                                <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-2">
                                    Full Name
                                </label>
                                <input
                                    id="name"
                                    name="name"
                                    type="text"
                                    required
                                    className="w-full px-4 py-3 border border-gray-200 rounded-xl 
                                        focus:ring-2 focus:ring-blue-500 focus:border-transparent 
                                        transition-all duration-200 bg-white/50 
                                        placeholder-gray-400 text-gray-900
                                        hover:border-gray-300 disabled:bg-gray-50 disabled:cursor-not-allowed"
                                    placeholder="Enter your full name"
                                    value={name}
                                    onChange={(e) => setName(e.target.value)}
                                    disabled={loading}
                                />
                            </div>
                            
                            <div>
                                <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                                    Email address
                                </label>
                                <input
                                    id="email"
                                    name="email"
                                    type="email"
                                    required
                                    className="w-full px-4 py-3 border border-gray-200 rounded-xl 
                                        focus:ring-2 focus:ring-blue-500 focus:border-transparent 
                                        transition-all duration-200 bg-white/50 
                                        placeholder-gray-400 text-gray-900
                                        hover:border-gray-300 disabled:bg-gray-50 disabled:cursor-not-allowed"
                                    placeholder="Enter your email"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    disabled={loading}
                                />
                            </div>
                            
                            <div>
                                <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
                                    Password
                                </label>
                                <input
                                    id="password"
                                    name="password"
                                    type="password"
                                    required
                                    className="w-full px-4 py-3 border border-gray-200 rounded-xl 
                                        focus:ring-2 focus:ring-blue-500 focus:border-transparent 
                                        transition-all duration-200 bg-white/50 
                                        placeholder-gray-400 text-gray-900
                                        hover:border-gray-300 disabled:bg-gray-50 disabled:cursor-not-allowed"
                                    placeholder="Create a strong password"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    disabled={loading}
                                />
                            </div>
                            
                            <div>
                                <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700 mb-2">
                                    Confirm Password
                                </label>
                                <input
                                    id="confirmPassword"
                                    name="confirmPassword"
                                    type="password"
                                    required
                                    className="w-full px-4 py-3 border border-gray-200 rounded-xl 
                                        focus:ring-2 focus:ring-blue-500 focus:border-transparent 
                                        transition-all duration-200 bg-white/50 
                                        placeholder-gray-400 text-gray-900
                                        hover:border-gray-300 disabled:bg-gray-50 disabled:cursor-not-allowed"
                                    placeholder="Confirm your password"
                                    value={confirmPassword}
                                    onChange={(e) => setConfirmPassword(e.target.value)}
                                    disabled={loading}
                                />
                            </div>
                        </div>

                        {error && (
                            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-xl text-sm">
                                {error}
                            </div>
                        )}

                        <button
                            type="submit"
                            className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 
                                text-white font-semibold py-3 px-4 rounded-xl 
                                hover:from-blue-700 hover:to-indigo-700 
                                focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 
                                transition-all duration-200 
                                disabled:opacity-50 disabled:cursor-not-allowed 
                                shadow-lg hover:shadow-xl"
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
                        
                        <div className="text-center pt-4">
                            <p className="text-sm text-gray-600">
                                Already have an account?{' '}
                                <Link href="/login" className="text-blue-600 hover:text-blue-700 font-semibold transition-colors duration-200">
                                    Sign in
                                </Link>
                            </p>
                        </div>
                    </form>
                </div>
                
                {/* Footer */}
                <div className="mt-6 text-center">
                    <p className="text-xs text-gray-500">
                        By signing up, you agree to our{' '}
                        <a href="#" className="text-blue-600 hover:text-blue-700 transition-colors">Terms of Service</a>
                        {' '}and{' '}
                        <a href="#" className="text-blue-600 hover:text-blue-700 transition-colors">Privacy Policy</a>
                    </p>
                </div>
            </div>
        </div>
    );
} 