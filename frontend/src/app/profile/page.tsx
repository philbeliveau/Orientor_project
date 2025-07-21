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
    user_id: number;
    name: string | null;
    age: number | null;
    sex: string | null;
    major: string | null;
    year: number | null;
    gpa: number | null;
    hobbies: string | null;
    country: string | null;
    state_province: string | null;
    unique_quality: string | null;
    story: string | null;
    favorite_movie: string | null;
    favorite_book: string | null;
    favorite_celebrities: string | null;
    learning_style: string | null;
    interests: string[] | null;
    // Career fields
    job_title: string | null;
    industry: string | null;
    years_experience: number | null;
    education_level: string | null;
    career_goals: string | null;
    skills: string[] | null;
    // Skill scores
    creativity: number | null;
    leadership: number | null;
    digital_literacy: number | null;
    critical_thinking: number | null;
    problem_solving: number | null;
    // Cognitive traits
    analytical_thinking: number | null;
    attention_to_detail: number | null;
    collaboration: number | null;
    adaptability: number | null;
    independence: number | null;
    evaluation: number | null;
    decision_making: number | null;
    stress_tolerance: number | null;
}

export default function ProfilePage() {
    const [activeTab, setActiveTab] = useState('basic');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState<string | null>(null);
    const [message, setMessage] = useState<string | null>(null);
    const [profile, setProfile] = useState<Profile>({
        user_id: 0,
        name: null,
        age: null,
        sex: null,
        major: null,
        year: null,
        gpa: null,
        hobbies: null,
        country: null,
        state_province: null,
        unique_quality: null,
        story: null,
        favorite_movie: null,
        favorite_book: null,
        favorite_celebrities: null,
        learning_style: null,
        interests: null,
        job_title: null,
        industry: null,
        years_experience: null,
        education_level: null,
        career_goals: null,
        skills: null,
        creativity: null,
        leadership: null,
        digital_literacy: null,
        critical_thinking: null,
        problem_solving: null,
        analytical_thinking: null,
        attention_to_detail: null,
        collaboration: null,
        adaptability: null,
        independence: null,
        evaluation: null,
        decision_making: null,
        stress_tolerance: null
    });
    const [rawInputs, setRawInputs] = useState({
        skills: '',
        interests: ''
    });

    // Fetch existing profile data when component mounts
    useEffect(() => {
        const fetchProfile = async () => {
            try {
                const token = localStorage.getItem('access_token');
                if (!token) {
                    console.error('No access token found');
                    return;
                }
                
                const response = await axios.get<Profile>(`${cleanApiUrl}/api/v1/profiles/me`, {
                    headers: {
                        Authorization: `Bearer ${token}`
                    }
                });
                console.log('Profile data received:', response.data);
                
                // First set the profile data
                setProfile(response.data);
                
                // Then properly format and set the raw inputs
                const formattedSkills = Array.isArray(response.data.skills) 
                    ? response.data.skills.join(', ')
                    : '';
                    
                const formattedinterests = Array.isArray(response.data.interests)
                    ? response.data.interests.join(', ')
                    : '';
                
                setRawInputs({
                    skills: formattedSkills,
                    interests: formattedinterests
                });
                setProfile(prev => ({
                    ...prev,
                    skills: response.data.skills || [],
                    interests: response.data.interests || []
                }));
            } catch (err) {
                const error = err as ApiError;
                console.error('Error fetching profile:', error.response?.data || error.message);
                setError(error.response?.data?.detail || 'Failed to fetch profile');
            }
        };
        fetchProfile();
    }, []);

    const handleProfileChange = (field: keyof Profile) => (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
        let value: string | number | string[] | null = e.target.value;
        
        // Convert numeric fields
        if (['age', 'year', 'years_experience'].includes(field) && value !== '') {
            value = parseInt(value) || null;
        } else if (field === 'gpa' && value !== '') {
            value = parseFloat(value) || null;
        } else if (value === '') {
            value = null;
        }
        
        setProfile(prev => ({
            ...prev,
            [field]: value
        }));
    };

    const handleArrayChange = (field: 'interests' | 'skills') => (e: React.ChangeEvent<HTMLInputElement>) => {
        e.stopPropagation();
        const value = e.target.value;
        setRawInputs(prev => ({
            ...prev,
            [field]: value
        }));
    };

    const handleArrayBlur = (field: 'interests' | 'skills') => () => {
        const value = rawInputs[field];
        // Split by comma, trim each item, and filter out empty strings
        const array = value
            .split(',')
            .map(item => item.trim())
            .filter(item => item !== '');
        
        // Update the profile with the processed array
        setProfile(prev => ({
            ...prev,
            [field]: array
        }));
    };

    const handleUpdate = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            const token = localStorage.getItem('access_token');
            
            // Process arrays and skill scores before sending
            const processedProfile = {
                ...profile,
                skills: rawInputs.skills
                    .split(',')
                    .map(item => item.trim())
                    .filter(item => item !== ''),
                interests: rawInputs.interests
                    .split(',')
                    .map(item => item.trim())
                    .filter(item => item !== ''),
                // Convert skill scores to numbers or null
                creativity: profile.creativity === null || profile.creativity === undefined ? null : Number(profile.creativity),
                leadership: profile.leadership === null || profile.leadership === undefined ? null : Number(profile.leadership),
                digital_literacy: profile.digital_literacy === null || profile.digital_literacy === undefined ? null : Number(profile.digital_literacy),
                critical_thinking: profile.critical_thinking === null || profile.critical_thinking === undefined ? null : Number(profile.critical_thinking),
                problem_solving: profile.problem_solving === null || profile.problem_solving === undefined ? null : Number(profile.problem_solving),
                // Convert cognitive traits to numbers
                analytical_thinking: profile.analytical_thinking === null || profile.analytical_thinking === undefined ? null : Number(profile.analytical_thinking),
                attention_to_detail: profile.attention_to_detail === null || profile.attention_to_detail === undefined ? null : Number(profile.attention_to_detail),
                collaboration: profile.collaboration === null || profile.collaboration === undefined ? null : Number(profile.collaboration),
                adaptability: profile.adaptability === null || profile.adaptability === undefined ? null : Number(profile.adaptability),
                independence: profile.independence === null || profile.independence === undefined ? null : Number(profile.independence),
                evaluation: profile.evaluation === null || profile.evaluation === undefined ? null : Number(profile.evaluation),
                decision_making: profile.decision_making === null || profile.decision_making === undefined ? null : Number(profile.decision_making),
                stress_tolerance: profile.stress_tolerance === null || profile.stress_tolerance === undefined ? null : Number(profile.stress_tolerance)
            };

            // Create a clean profile object with all fields
            const cleanProfile = {
                user_id: processedProfile.user_id,
                // Basic Info
                name: processedProfile.name || null,
                age: processedProfile.age || null,
                sex: processedProfile.sex || null,
                country: processedProfile.country || null,
                state_province: processedProfile.state_province || null,
                
                // Academic Info
                major: processedProfile.major || null,
                year: processedProfile.year || null,
                gpa: processedProfile.gpa || null,
                learning_style: processedProfile.learning_style || null,
                
                // Personal Info
                hobbies: processedProfile.hobbies || null,
                unique_quality: processedProfile.unique_quality || null,
                story: processedProfile.story || null,
                favorite_movie: processedProfile.favorite_movie || null,
                favorite_book: processedProfile.favorite_book || null,
                favorite_celebrities: processedProfile.favorite_celebrities || null,
                
                // Career Info
                job_title: processedProfile.job_title || null,
                industry: processedProfile.industry || null,
                years_experience: processedProfile.years_experience || null,
                education_level: processedProfile.education_level || null,
                career_goals: processedProfile.career_goals || null,
                skills: processedProfile.skills,
                interests: processedProfile.interests,
                
                // Skill scores
                creativity: processedProfile.creativity,
                leadership: processedProfile.leadership,
                digital_literacy: processedProfile.digital_literacy,
                critical_thinking: processedProfile.critical_thinking,
                problem_solving: processedProfile.problem_solving,
                
                // Cognitive traits
                analytical_thinking: processedProfile.analytical_thinking,
                attention_to_detail: processedProfile.attention_to_detail,
                collaboration: processedProfile.collaboration,
                adaptability: processedProfile.adaptability,
                independence: processedProfile.independence,
                evaluation: processedProfile.evaluation,
                decision_making: processedProfile.decision_making,
                stress_tolerance: processedProfile.stress_tolerance
            };

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
            const response = await axios.put(
                `${cleanApiUrl}/api/v1/profiles/update`,
                cleanProfile,
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
            console.error('Profile update error:', error.response?.data);
            setError(error.response?.data?.detail || 'Update failed');
            setMessage(null);
        }
    };

    return (
        <MainLayout>
            <div className="relative flex size-full min-h-screen flex-col bg-[#f8fcf9] group/design-root overflow-x-hidden" style={{fontFamily: '"Space Grotesk", "Noto Sans", sans-serif'}}>
                <div className="layout-container flex h-full grow flex-col">
                    <div className="px-4 md:px-10 flex flex-1 justify-center py-5">
                        <div className="layout-content-container flex flex-col max-w-[960px] flex-1">
                            <div className="flex flex-wrap justify-between gap-3 p-4">
                                <div className="flex min-w-72 flex-col gap-3">
                                    <p className="text-[#0d1b13] tracking-light text-[32px] font-bold leading-tight">Profile Builder</p>
                                    <p className="text-[#4c9a6a] text-sm font-normal leading-normal">Complete your profile to unlock personalized career recommendations and skill-building resources.</p>
                                </div>
                            </div>
                            <div className="flex flex-col gap-3 p-4">
                                <div className="flex gap-6 justify-between">
                                    <p className="text-[#0d1b13] text-base font-medium leading-normal">Profile Completion</p>
                                    <p className="text-[#0d1b13] text-sm font-normal leading-normal">25%</p>
                                </div>
                                <div className="rounded bg-[#cfe7d8]"><div className="h-2 rounded bg-[#10cf59]" style={{width: '25%'}}></div></div>
                            </div>
                            
                            <form onSubmit={handleUpdate} className="space-y-6">
                                {/* Tabs */}
                                <div className="pb-3">
                                    <div className="flex border-b border-[#cfe7d8] px-4 gap-8">
                                        <a
                                            className={`flex flex-col items-center justify-center border-b-[3px] ${activeTab === 'basic' ? 'border-b-[#10cf59] text-[#0d1b13]' : 'border-b-transparent text-[#4c9a6a]'} pb-[13px] pt-4`}
                                            href="#"
                                            onClick={(e) => { e.preventDefault(); setActiveTab('basic'); }}
                                        >
                                            <p className={`${activeTab === 'basic' ? 'text-[#0d1b13]' : 'text-[#4c9a6a]'} text-sm font-bold leading-normal tracking-[0.015em]`}>Basic Information</p>
                                        </a>
                                        <a
                                            className={`flex flex-col items-center justify-center border-b-[3px] ${activeTab === 'academic' ? 'border-b-[#10cf59] text-[#0d1b13]' : 'border-b-transparent text-[#4c9a6a]'} pb-[13px] pt-4`}
                                            href="#"
                                            onClick={(e) => { e.preventDefault(); setActiveTab('academic'); }}
                                        >
                                            <p className={`${activeTab === 'academic' ? 'text-[#0d1b13]' : 'text-[#4c9a6a]'} text-sm font-bold leading-normal tracking-[0.015em]`}>Academic Background</p>
                                        </a>
                                        <a
                                            className={`flex flex-col items-center justify-center border-b-[3px] ${activeTab === 'career' ? 'border-b-[#10cf59] text-[#0d1b13]' : 'border-b-transparent text-[#4c9a6a]'} pb-[13px] pt-4`}
                                            href="#"
                                            onClick={(e) => { e.preventDefault(); setActiveTab('career'); }}
                                        >
                                            <p className={`${activeTab === 'career' ? 'text-[#0d1b13]' : 'text-[#4c9a6a]'} text-sm font-bold leading-normal tracking-[0.015em]`}>Career Goals</p>
                                        </a>
                                        <a
                                            className={`flex flex-col items-center justify-center border-b-[3px] ${activeTab === 'skills' ? 'border-b-[#10cf59] text-[#0d1b13]' : 'border-b-transparent text-[#4c9a6a]'} pb-[13px] pt-4`}
                                            href="#"
                                            onClick={(e) => { e.preventDefault(); setActiveTab('skills'); }}
                                        >
                                            <p className={`${activeTab === 'skills' ? 'text-[#0d1b13]' : 'text-[#4c9a6a]'} text-sm font-bold leading-normal tracking-[0.015em]`}>Skills &amp; Interests</p>
                                        </a>
                                    </div>
                                </div>

                                {/* Tab Content */}
                                <div className="mt-6">
                                    {activeTab === 'basic' && (
                                        <div className="space-y-6">
                                            <div className="flex max-w-[480px] flex-wrap items-end gap-4 px-4 py-3">
                                                <label className="flex flex-col min-w-40 flex-1">
                                                    <p className="text-[#0d1b13] text-base font-medium leading-normal pb-2">Full Name</p>
                                                    <input
                                                        placeholder="Enter your full name"
                                                        className="form-input flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-xl text-[#0d1b13] focus:outline-0 focus:ring-0 border-none bg-[#e7f3ec] focus:border-none h-14 placeholder:text-[#4c9a6a] p-4 text-base font-normal leading-normal"
                                                        type="text"
                                                        value={profile.name || ''}
                                                        onChange={handleProfileChange('name')}
                                                    />
                                                </label>
                                            </div>
                                            <div className="flex max-w-[480px] flex-wrap items-end gap-4 px-4 py-3">
                                                <label className="flex flex-col min-w-40 flex-1">
                                                    <p className="text-[#0d1b13] text-base font-medium leading-normal pb-2">Age</p>
                                                    <select
                                                        className="form-input flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-xl text-[#0d1b13] focus:outline-0 focus:ring-0 border-none bg-[#e7f3ec] focus:border-none h-14 bg-[image:--select-button-svg] placeholder:text-[#4c9a6a] p-4 text-base font-normal leading-normal"
                                                        value={profile.age || ''}
                                                        onChange={handleProfileChange('age')}
                                                    >
                                                        <option value="">Select your age</option>
                                                        <option value="18">18</option>
                                                        <option value="19">19</option>
                                                        <option value="20">20</option>
                                                        <option value="21">21</option>
                                                        <option value="22">22</option>
                                                        <option value="23">23</option>
                                                        <option value="24">24</option>
                                                        <option value="25">25+</option>
                                                    </select>
                                                </label>
                                            </div>
                                            <div className="flex max-w-[480px] flex-wrap items-end gap-4 px-4 py-3">
                                                <label className="flex flex-col min-w-40 flex-1">
                                                    <p className="text-[#0d1b13] text-base font-medium leading-normal pb-2">Sex</p>
                                                    <select
                                                        className="form-input flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-xl text-[#0d1b13] focus:outline-0 focus:ring-0 border-none bg-[#e7f3ec] focus:border-none h-14 bg-[image:--select-button-svg] placeholder:text-[#4c9a6a] p-4 text-base font-normal leading-normal"
                                                        value={profile.sex || ''}
                                                        onChange={handleProfileChange('sex')}
                                                    >
                                                        <option value="">Select your sex</option>
                                                        <option value="Male">Male</option>
                                                        <option value="Female">Female</option>
                                                        <option value="Other">Other</option>
                                                        <option value="Prefer not to say">Prefer not to say</option>
                                                    </select>
                                                </label>
                                            </div>
                                            <div className="flex max-w-[480px] flex-wrap items-end gap-4 px-4 py-3">
                                                <label className="flex flex-col min-w-40 flex-1">
                                                    <p className="text-[#0d1b13] text-base font-medium leading-normal pb-2">Country</p>
                                                    <input
                                                        placeholder="Enter your country"
                                                        className="form-input flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-xl text-[#0d1b13] focus:outline-0 focus:ring-0 border-none bg-[#e7f3ec] focus:border-none h-14 placeholder:text-[#4c9a6a] p-4 text-base font-normal leading-normal"
                                                        type="text"
                                                        value={profile.country || ''}
                                                        onChange={handleProfileChange('country')}
                                                    />
                                                </label>
                                            </div>
                                            <div className="flex max-w-[480px] flex-wrap items-end gap-4 px-4 py-3">
                                                <label className="flex flex-col min-w-40 flex-1">
                                                    <p className="text-[#0d1b13] text-base font-medium leading-normal pb-2">State/Province</p>
                                                    <input
                                                        placeholder="Enter your state or province"
                                                        className="form-input flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-xl text-[#0d1b13] focus:outline-0 focus:ring-0 border-none bg-[#e7f3ec] focus:border-none h-14 placeholder:text-[#4c9a6a] p-4 text-base font-normal leading-normal"
                                                        type="text"
                                                        value={profile.state_province || ''}
                                                        onChange={handleProfileChange('state_province')}
                                                    />
                                                </label>
                                            </div>
                                        </div>
                                    )}
                                    {activeTab === 'academic' && (
                                        <div className="space-y-6">
                                            <div className="flex max-w-[480px] flex-wrap items-end gap-4 px-4 py-3">
                                                <label className="flex flex-col min-w-40 flex-1">
                                                    <p className="text-[#0d1b13] text-base font-medium leading-normal pb-2">Major</p>
                                                    <select
                                                        className="form-input flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-xl text-[#0d1b13] focus:outline-0 focus:ring-0 border-none bg-[#e7f3ec] focus:border-none h-14 bg-[image:--select-button-svg] placeholder:text-[#4c9a6a] p-4 text-base font-normal leading-normal"
                                                        value={profile.major || ''}
                                                        onChange={handleProfileChange('major')}
                                                    >
                                                        <option value="">Select your major</option>
                                                        <option value="Computer Science">Computer Science</option>
                                                        <option value="Engineering">Engineering</option>
                                                        <option value="Business">Business</option>
                                                        <option value="Arts">Arts</option>
                                                        <option value="Sciences">Sciences</option>
                                                        <option value="Health">Health</option>
                                                        <option value="Law">Law</option>
                                                        <option value="Medicine">Medicine</option>
                                                        <option value="Education">Education</option>
                                                        <option value="Social Sciences">Social Sciences</option>
                                                        <option value="Humanities">Humanities</option>
                                                        <option value="Mathematics">Mathematics</option>
                                                        <option value="Music">Music</option>
                                                        <option value="Psychology">Psychology</option>
                                                        <option value="Economics">Economics</option>
                                                        <option value="Architecture">Architecture</option>
                                                        <option value="Design">Design</option>
                                                        <option value="Fashion">Fashion</option>
                                                        <option value="Film">Film</option>
                                                        <option value="Journalism">Journalism</option>
                                                        <option value="Marketing">Marketing</option>
                                                        <option value="Public Relations">Public Relations</option>
                                                        <option value="Social Work">Social Work</option>
                                                        <option value="Automotive Technology">Automotive Technology</option>
                                                        <option value="Construction and Building Technology">Construction and Building Technology</option>
                                                        <option value="Electrical Technology">Electrical Technology</option>
                                                        <option value="HVAC & Refrigeration">HVAC & Refrigeration</option>
                                                        <option value="Welding Technology">Welding Technology</option>
                                                        <option value="Plumbing and Heating">Plumbing and Heating</option>
                                                        <option value="Heavy Equipment Operation">Heavy Equipment Operation</option>
                                                        <option value="Industrial Mechanics">Industrial Mechanics</option>
                                                        <option value="Forestry Operations">Forestry Operations</option>
                                                        <option value="Landscape and Horticulture">Landscape and Horticulture</option>
                                                        <option value="Carpentry">Carpentry</option>
                                                        <option value="Appliance Repair and Maintenance">Appliance Repair and Maintenance</option>
                                                        <option value="Fire Protection Technology">Fire Protection Technology</option>
                                                        <option value="Renewable Energy Systems">Renewable Energy Systems</option>
                                                        <option value="High School">High School</option>
                                                        <option value="High School Diploma">High School Diploma</option>
                                                        <option value="High School Diploma with Honors">High School Diploma with Honors</option>
                                                        <option value="High School Diploma with Distinction">High School Diploma with Distinction</option>
                                                        <option value="High School Diploma with Honors and Distinction">High School Diploma with Honors and Distinction</option>
                                                        <option value="High School Diploma with Honors and Distinction">High School Diploma with Honors and Distinction</option>
                                                        <option value="Other">Other</option>
                                                    </select>
                                                </label>
                                            </div>
                                            <div className="flex max-w-[480px] flex-wrap items-end gap-4 px-4 py-3">
                                                <label className="flex flex-col min-w-40 flex-1">
                                                    <p className="text-[#0d1b13] text-base font-medium leading-normal pb-2">Year</p>
                                                    <select
                                                        className="form-input flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-xl text-[#0d1b13] focus:outline-0 focus:ring-0 border-none bg-[#e7f3ec] focus:border-none h-14 bg-[image:--select-button-svg] placeholder:text-[#4c9a6a] p-4 text-base font-normal leading-normal"
                                                        value={profile.year || ''}
                                                        onChange={handleProfileChange('year')}
                                                    >
                                                        <option value="">Select your year</option>
                                                        <option value="1">First Year</option>
                                                        <option value="2">Second Year</option>
                                                        <option value="3">Third Year</option>
                                                        <option value="4">Fourth Year</option>
                                                        <option value="5">Fifth Year or Beyond</option>
                                                    </select>
                                                </label>
                                            </div>
                                            <div className="flex max-w-[480px] flex-wrap items-end gap-4 px-4 py-3">
                                                <label className="flex flex-col min-w-40 flex-1">
                                                    <p className="text-[#0d1b13] text-base font-medium leading-normal pb-2">GPA</p>
                                                    <input
                                                        placeholder="Your GPA"
                                                        className="form-input flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-xl text-[#0d1b13] focus:outline-0 focus:ring-0 border-none bg-[#e7f3ec] focus:border-none h-14 placeholder:text-[#4c9a6a] p-4 text-base font-normal leading-normal"
                                                        type="number"
                                                        value={profile.gpa || ''}
                                                        onChange={handleProfileChange('gpa')}
                                                        step="0.01"
                                                        min="0"
                                                        max="4"
                                                    />
                                                </label>
                                            </div>
                                            <div className="flex max-w-[480px] flex-wrap items-end gap-4 px-4 py-3">
                                                <label className="flex flex-col min-w-40 flex-1">
                                                    <p className="text-[#0d1b13] text-base font-medium leading-normal pb-2">Learning Style</p>
                                                    <select
                                                        className="form-input flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-xl text-[#0d1b13] focus:outline-0 focus:ring-0 border-none bg-[#e7f3ec] focus:border-none h-14 bg-[image:--select-button-svg] placeholder:text-[#4c9a6a] p-4 text-base font-normal leading-normal"
                                                        value={profile.learning_style || ''}
                                                        onChange={handleProfileChange('learning_style')}
                                                    >
                                                        <option value="">Select your learning style</option>
                                                        <option value="Visual">Visual</option>
                                                        <option value="Auditory">Auditory</option>
                                                        <option value="Reading/Writing">Reading/Writing</option>
                                                        <option value="Kinesthetic">Kinesthetic</option>
                                                    </select>
                                                </label>
                                            </div>
                                        </div>
                                    )}
                                    {activeTab === 'career' && (
                                        <div className="space-y-6">
                                            <div className="flex max-w-[480px] flex-wrap items-end gap-4 px-4 py-3">
                                                <label className="flex flex-col min-w-40 flex-1">
                                                    <p className="text-[#0d1b13] text-base font-medium leading-normal pb-2">Job Title</p>
                                                    <input
                                                        placeholder="Your current or desired job title"
                                                        className="form-input flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-xl text-[#0d1b13] focus:outline-0 focus:ring-0 border-none bg-[#e7f3ec] focus:border-none h-14 placeholder:text-[#4c9a6a] p-4 text-base font-normal leading-normal"
                                                        type="text"
                                                        value={profile.job_title || ''}
                                                        onChange={handleProfileChange('job_title')}
                                                    />
                                                </label>
                                            </div>
                                            <div className="flex max-w-[480px] flex-wrap items-end gap-4 px-4 py-3">
                                                <label className="flex flex-col min-w-40 flex-1">
                                                    <p className="text-[#0d1b13] text-base font-medium leading-normal pb-2">Industry</p>
                                                    <input
                                                        placeholder="Your industry"
                                                        className="form-input flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-xl text-[#0d1b13] focus:outline-0 focus:ring-0 border-none bg-[#e7f3ec] focus:border-none h-14 placeholder:text-[#4c9a6a] p-4 text-base font-normal leading-normal"
                                                        type="text"
                                                        value={profile.industry || ''}
                                                        onChange={handleProfileChange('industry')}
                                                    />
                                                </label>
                                            </div>
                                            <div className="flex max-w-[480px] flex-wrap items-end gap-4 px-4 py-3">
                                                <label className="flex flex-col min-w-40 flex-1">
                                                    <p className="text-[#0d1b13] text-base font-medium leading-normal pb-2">Years of Experience</p>
                                                    <input
                                                        placeholder="Years of experience"
                                                        className="form-input flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-xl text-[#0d1b13] focus:outline-0 focus:ring-0 border-none bg-[#e7f3ec] focus:border-none h-14 placeholder:text-[#4c9a6a] p-4 text-base font-normal leading-normal"
                                                        type="number"
                                                        value={profile.years_experience || ''}
                                                        onChange={handleProfileChange('years_experience')}
                                                        min="0"
                                                    />
                                                </label>
                                            </div>
                                            <div className="flex max-w-[480px] flex-wrap items-end gap-4 px-4 py-3">
                                                <label className="flex flex-col min-w-40 flex-1">
                                                    <p className="text-[#0d1b13] text-base font-medium leading-normal pb-2">Education Level</p>
                                                    <select
                                                        className="form-input flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-xl text-[#0d1b13] focus:outline-0 focus:ring-0 border-none bg-[#e7f3ec] focus:border-none h-14 bg-[image:--select-button-svg] placeholder:text-[#4c9a6a] p-4 text-base font-normal leading-normal"
                                                        value={profile.education_level || ''}
                                                        onChange={handleProfileChange('education_level')}
                                                    >
                                                        <option value="">Select your education level</option>
                                                        <option value="High School">High School</option>
                                                        <option value="Associate's Degree">Associate's Degree</option>
                                                        <option value="Bachelor's Degree">Bachelor's Degree</option>
                                                        <option value="Master's Degree">Master's Degree</option>
                                                        <option value="Doctorate">Doctorate</option>
                                                    </select>
                                                </label>
                                            </div>
                                            <div className="flex max-w-[480px] flex-wrap items-end gap-4 px-4 py-3">
                                                <label className="flex flex-col min-w-40 flex-1">
                                                    <p className="text-[#0d1b13] text-base font-medium leading-normal pb-2">Career Goals</p>
                                                    <textarea
                                                        placeholder="Describe your career goals"
                                                        className="form-input flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-xl text-[#0d1b13] focus:outline-0 focus:ring-0 border-none bg-[#e7f3ec] focus:border-none min-h-36 placeholder:text-[#4c9a6a] p-4 text-base font-normal leading-normal"
                                                        value={profile.career_goals || ''}
                                                        onChange={handleProfileChange('career_goals')}
                                                    ></textarea>
                                                </label>
                                            </div>
                                        </div>
                                    )}
                                    {activeTab === 'skills' && (
                                        <div className="space-y-6">
                                            <div className="flex max-w-[480px] flex-wrap items-end gap-4 px-4 py-3">
                                                <label className="flex flex-col min-w-40 flex-1">
                                                    <p className="text-[#0d1b13] text-base font-medium leading-normal pb-2">Skills</p>
                                                    <input
                                                        placeholder="Enter your skills, separated by commas"
                                                        className="form-input flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-xl text-[#0d1b13] focus:outline-0 focus:ring-0 border-none bg-[#e7f3ec] focus:border-none h-14 placeholder:text-[#4c9a6a] p-4 text-base font-normal leading-normal"
                                                        type="text"
                                                        value={rawInputs.skills}
                                                        onChange={handleArrayChange('skills')}
                                                        onBlur={handleArrayBlur('skills')}
                                                    />
                                                </label>
                                            </div>
                                            <div className="flex max-w-[480px] flex-wrap items-end gap-4 px-4 py-3">
                                                <label className="flex flex-col min-w-40 flex-1">
                                                    <p className="text-[#0d1b13] text-base font-medium leading-normal pb-2">Interests</p>
                                                    <input
                                                        placeholder="Enter your interests, separated by commas"
                                                        className="form-input flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-xl text-[#0d1b13] focus:outline-0 focus:ring-0 border-none bg-[#e7f3ec] focus:border-none h-14 placeholder:text-[#4c9a6a] p-4 text-base font-normal leading-normal"
                                                        type="text"
                                                        value={rawInputs.interests}
                                                        onChange={handleArrayChange('interests')}
                                                        onBlur={handleArrayBlur('interests')}
                                                    />
                                                </label>
                                            </div>
                                            <div className="flex max-w-[480px] flex-wrap items-end gap-4 px-4 py-3">
                                                <label className="flex flex-col min-w-40 flex-1">
                                                    <p className="text-[#0d1b13] text-base font-medium leading-normal pb-2">Hobbies</p>
                                                    <textarea
                                                        placeholder="What are your hobbies?"
                                                        className="form-input flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-xl text-[#0d1b13] focus:outline-0 focus:ring-0 border-none bg-[#e7f3ec] focus:border-none min-h-36 placeholder:text-[#4c9a6a] p-4 text-base font-normal leading-normal"
                                                        value={profile.hobbies || ''}
                                                        onChange={handleProfileChange('hobbies')}
                                                    ></textarea>
                                                </label>
                                            </div>
                                            <div className="flex max-w-[480px] flex-wrap items-end gap-4 px-4 py-3">
                                                <label className="flex flex-col min-w-40 flex-1">
                                                    <p className="text-[#0d1b13] text-base font-medium leading-normal pb-2">Learning Style</p>
                                                    <select
                                                        className="form-input flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-xl text-[#0d1b13] focus:outline-0 focus:ring-0 border-none bg-[#e7f3ec] focus:border-none h-14 bg-[image:--select-button-svg] placeholder:text-[#4c9a6a] p-4 text-base font-normal leading-normal"
                                                        value={profile.learning_style || ''}
                                                        onChange={handleProfileChange('learning_style')}
                                                    >
                                                        <option value="">Select your learning style</option>
                                                        <option value="Visual">Visual</option>
                                                        <option value="Auditory">Auditory</option>
                                                        <option value="Reading/Writing">Reading/Writing</option>
                                                        <option value="Kinesthetic">Kinesthetic</option>
                                                    </select>
                                                </label>
                                            </div>
                                            <div className="flex max-w-[480px] flex-wrap items-end gap-4 px-4 py-3">
                                                <label className="flex flex-col min-w-40 flex-1">
                                                    <p className="text-[#0d1b13] text-base font-medium leading-normal pb-2">Unique Quality</p>
                                                    <textarea
                                                        placeholder="What makes you unique?"
                                                        className="form-input flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-xl text-[#0d1b13] focus:outline-0 focus:ring-0 border-none bg-[#e7f3ec] focus:border-none min-h-36 placeholder:text-[#4c9a6a] p-4 text-base font-normal leading-normal"
                                                        value={profile.unique_quality || ''}
                                                        onChange={handleProfileChange('unique_quality')}
                                                    ></textarea>
                                                </label>
                                            </div>
                                            <div className="flex max-w-[480px] flex-wrap items-end gap-4 px-4 py-3">
                                                <label className="flex flex-col min-w-40 flex-1">
                                                    <p className="text-[#0d1b13] text-base font-medium leading-normal pb-2">Your Story</p>
                                                    <textarea
                                                        placeholder="Tell us your story"
                                                        className="form-input flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-xl text-[#0d1b13] focus:outline-0 focus:ring-0 border-none bg-[#e7f3ec] focus:border-none min-h-36 placeholder:text-[#4c9a6a] p-4 text-base font-normal leading-normal"
                                                        value={profile.story || ''}
                                                        onChange={handleProfileChange('story')}
                                                    ></textarea>
                                                </label>
                                            </div>
                                            <div className="flex max-w-[480px] flex-wrap items-end gap-4 px-4 py-3">
                                                <label className="flex flex-col min-w-40 flex-1">
                                                    <p className="text-[#0d1b13] text-base font-medium leading-normal pb-2">Favorite Movie</p>
                                                    <input
                                                        placeholder="What's your favorite movie?"
                                                        className="form-input flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-xl text-[#0d1b13] focus:outline-0 focus:ring-0 border-none bg-[#e7f3ec] focus:border-none h-14 placeholder:text-[#4c9a6a] p-4 text-base font-normal leading-normal"
                                                        type="text"
                                                        value={profile.favorite_movie || ''}
                                                        onChange={handleProfileChange('favorite_movie')}
                                                    />
                                                </label>
                                            </div>
                                            <div className="flex max-w-[480px] flex-wrap items-end gap-4 px-4 py-3">
                                                <label className="flex flex-col min-w-40 flex-1">
                                                    <p className="text-[#0d1b13] text-base font-medium leading-normal pb-2">Favorite Book</p>
                                                    <input
                                                        placeholder="What's your favorite book?"
                                                        className="form-input flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-xl text-[#0d1b13] focus:outline-0 focus:ring-0 border-none bg-[#e7f3ec] focus:border-none h-14 placeholder:text-[#4c9a6a] p-4 text-base font-normal leading-normal"
                                                        type="text"
                                                        value={profile.favorite_book || ''}
                                                        onChange={handleProfileChange('favorite_book')}
                                                    />
                                                </label>
                                            </div>
                                            <div className="flex max-w-[480px] flex-wrap items-end gap-4 px-4 py-3">
                                                <label className="flex flex-col min-w-40 flex-1">
                                                    <p className="text-[#0d1b13] text-base font-medium leading-normal pb-2">Favorite Celebrities</p>
                                                    <input
                                                        placeholder="Your role model or favorite celebrity"
                                                        className="form-input flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-xl text-[#0d1b13] focus:outline-0 focus:ring-0 border-none bg-[#e7f3ec] focus:border-none h-14 placeholder:text-[#4c9a6a] p-4 text-base font-normal leading-normal"
                                                        type="text"
                                                        value={profile.favorite_celebrities || ''}
                                                        onChange={handleProfileChange('favorite_celebrities')}
                                                    />
                                                </label>
                                            </div>
                                            <div className="md:col-span-2">
                                                <h3 className="text-lg font-medium text-neutral-lightgray mb-4">Skill Scores</h3>
                                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                                    <div>
                                                        <label className="block text-sm font-medium text-neutral-lightgray mb-1">
                                                            Creativity: {profile.creativity || 0}
                                                        </label>
                                                        <input
                                                            type="range"
                                                            value={profile.creativity || 0}
                                                            onChange={handleProfileChange('creativity')}
                                                            className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                                                            min="0"
                                                            max="5"
                                                            step="0.5"
                                                        />
                                                    </div>
                                                    <div>
                                                        <label className="block text-sm font-medium text-neutral-lightgray mb-1">
                                                            Leadership: {profile.leadership || 0}
                                                        </label>
                                                        <input
                                                            type="range"
                                                            value={profile.leadership || 0}
                                                            onChange={handleProfileChange('leadership')}
                                                            className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                                                            min="0"
                                                            max="5"
                                                            step="0.5"
                                                        />
                                                    </div>
                                                    <div>
                                                        <label className="block text-sm font-medium text-neutral-lightgray mb-1">
                                                            Digital Literacy: {profile.digital_literacy || 0}
                                                        </label>
                                                        <input
                                                            type="range"
                                                            value={profile.digital_literacy || 0}
                                                            onChange={handleProfileChange('digital_literacy')}
                                                            className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                                                            min="0"
                                                            max="5"
                                                            step="0.5"
                                                        />
                                                    </div>
                                                    <div>
                                                        <label className="block text-sm font-medium text-neutral-lightgray mb-1">
                                                            Critical Thinking: {profile.critical_thinking || 0}
                                                        </label>
                                                        <input
                                                            type="range"
                                                            value={profile.critical_thinking || 0}
                                                            onChange={handleProfileChange('critical_thinking')}
                                                            className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                                                            min="0"
                                                            max="5"
                                                            step="0.5"
                                                        />
                                                    </div>
                                                    <div>
                                                        <label className="block text-sm font-medium text-neutral-lightgray mb-1">
                                                            Problem Solving: {profile.problem_solving || 0}
                                                        </label>
                                                        <input
                                                            type="range"
                                                            value={profile.problem_solving || 0}
                                                            onChange={handleProfileChange('problem_solving')}
                                                            className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                                                            min="0"
                                                            max="5"
                                                            step="0.5"
                                                        />
                                                    </div>
                                                </div>
                                            </div>
                                            <div className="md:col-span-2">
                                                <h3 className="text-lg font-medium text-neutral-lightgray mb-4">Cognitive Traits</h3>
                                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                                    <div>
                                                        <label className="block text-sm font-medium text-neutral-lightgray mb-1">
                                                            Analytical Thinking: {profile.analytical_thinking || 0}
                                                        </label>
                                                        <input
                                                            type="range"
                                                            value={profile.analytical_thinking || 0}
                                                            onChange={handleProfileChange('analytical_thinking')}
                                                            className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                                                            min="0"
                                                            max="5"
                                                            step="0.5"
                                                        />
                                                    </div>
                                                    <div>
                                                        <label className="block text-sm font-medium text-neutral-lightgray mb-1">
                                                            Attention to Detail: {profile.attention_to_detail || 0}
                                                        </label>
                                                        <input
                                                            type="range"
                                                            value={profile.attention_to_detail || 0}
                                                            onChange={handleProfileChange('attention_to_detail')}
                                                            className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                                                            min="0"
                                                            max="5"
                                                            step="0.5"
                                                        />
                                                    </div>
                                                    <div>
                                                        <label className="block text-sm font-medium text-neutral-lightgray mb-1">
                                                            Collaboration: {profile.collaboration || 0}
                                                        </label>
                                                        <input
                                                            type="range"
                                                            value={profile.collaboration || 0}
                                                            onChange={handleProfileChange('collaboration')}
                                                            className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                                                            min="0"
                                                            max="5"
                                                            step="0.5"
                                                        />
                                                    </div>
                                                    <div>
                                                        <label className="block text-sm font-medium text-neutral-lightgray mb-1">
                                                            Adaptability: {profile.adaptability || 0}
                                                        </label>
                                                        <input
                                                            type="range"
                                                            value={profile.adaptability || 0}
                                                            onChange={handleProfileChange('adaptability')}
                                                            className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                                                            min="0"
                                                            max="5"
                                                            step="0.5"
                                                        />
                                                    </div>
                                                    <div>
                                                        <label className="block text-sm font-medium text-neutral-lightgray mb-1">
                                                            Independence: {profile.independence || 0}
                                                        </label>
                                                        <input
                                                            type="range"
                                                            value={profile.independence || 0}
                                                            onChange={handleProfileChange('independence')}
                                                            className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                                                            min="0"
                                                            max="5"
                                                            step="0.5"
                                                        />
                                                    </div>
                                                    <div>
                                                        <label className="block text-sm font-medium text-neutral-lightgray mb-1">
                                                            Evaluation: {profile.evaluation || 0}
                                                        </label>
                                                        <input
                                                            type="range"
                                                            value={profile.evaluation || 0}
                                                            onChange={handleProfileChange('evaluation')}
                                                            className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                                                            min="0"
                                                            max="5"
                                                            step="0.5"
                                                        />
                                                    </div>
                                                    <div>
                                                        <label className="block text-sm font-medium text-neutral-lightgray mb-1">
                                                            Decision Making: {profile.decision_making || 0}
                                                        </label>
                                                        <input
                                                            type="range"
                                                            value={profile.decision_making || 0}
                                                            onChange={handleProfileChange('decision_making')}
                                                            className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                                                            min="0"
                                                            max="5"
                                                            step="0.5"
                                                        />
                                                    </div>
                                                    <div>
                                                        <label className="block text-sm font-medium text-neutral-lightgray mb-1">
                                                            Stress Tolerance: {profile.stress_tolerance || 0}
                                                        </label>
                                                        <input
                                                            type="range"
                                                            value={profile.stress_tolerance || 0}
                                                            onChange={handleProfileChange('stress_tolerance')}
                                                            className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                                                            min="0"
                                                            max="5"
                                                            step="0.5"
                                                        />
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    )}
                                </div>

                                {/* Error and Success Messages */}
                                {error && (
                                    <div className="text-red-500 text-sm mt-4 p-3 bg-red-900/20 border border-red-500 rounded-lg">
                                        {typeof error === 'string' ? error : 'An error occurred'}
                                    </div>
                                )}
                                {message && (
                                    <div className="text-green-500 text-sm mt-4 p-3 bg-green-900/20 border border-green-500 rounded-lg">
                                        {message}
                                    </div>
                                )}

                                {/* Submit Button */}
                                <div className="flex px-4 py-3 justify-end">
                                    <button
                                        type="submit"
                                        className="flex min-w-[84px] max-w-[480px] cursor-pointer items-center justify-center overflow-hidden rounded-full h-10 px-4 bg-[#10cf59] text-[#0d1b13] text-sm font-bold leading-normal tracking-[0.015em]"
                                    >
                                        <span className="truncate">Save &amp; Continue</span>
                                    </button>
                                </div>
                            </form>
                        </div>
                    </div>
                </div>
            </div>
        </MainLayout>
    );
}
