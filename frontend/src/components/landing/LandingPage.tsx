'use client';
import { useRouter } from 'next/navigation';
import Image from 'next/image';
import Link from 'next/link';

export default function LandingPage() {
  const router = useRouter();

  return (
    <div className="max-w-7xl mx-auto">
      {/* Hero Section */}
      <section className="section">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-12 items-center">
          <div className="space-y-8">
            <h1 className="text-4xl md:text-6xl font-bold gradient-text">
              Welcome to Navigo
            </h1>
            <p className="text-xl text-neutral-200 leading-relaxed">
              Your personal guide for growth, reflection, and achieving your goals. Navigo provides a supportive environment for youth to navigate life's challenges.
            </p>
            <div className="flex flex-col sm:flex-row gap-4">
              <Link href="/login" className="btn btn-primary">
                Log In
              </Link>
              <Link href="/register" className="btn btn-outline">
                Sign Up
              </Link>
            </div>
          </div>
          <div className="relative h-80 md:h-96 rounded-lg overflow-hidden shadow-glow-purple">
            {/* Animated gradient background */}
            <div className="absolute inset-0 bg-gradient-primary opacity-20 animate-gradient-shift bg-[length:200%_200%]"></div>
            {/* Floating elements */}
            <div className="absolute top-1/4 left-1/4 w-16 h-16 rounded-full bg-primary-purple opacity-40 animate-float"></div>
            <div className="absolute bottom-1/4 right-1/4 w-12 h-12 rounded-full bg-primary-teal opacity-40 animate-float [animation-delay:1s]"></div>
            <div className="absolute top-1/2 right-1/3 w-8 h-8 rounded-full bg-accent-amber opacity-30 animate-float [animation-delay:2s]"></div>
            
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="text-5xl font-display font-bold gradient-text">Navigo</div>
            </div>
          </div>
        </div>
      </section>

      {/* Mission Section */}
      <section className="section">
        <div className="card container-narrow">
          <div className="text-center space-y-8">
            <h2 className="text-3xl md:text-4xl font-bold gradient-text-secondary">
              Our Mission
            </h2>
            <p className="text-xl text-neutral-200 leading-relaxed">
              Navigo's mission is to empower youth by providing them with a safe, supportive environment to reflect, plan, and engage with mentors or automated guidance.
            </p>
            <p className="text-xl text-neutral-200 leading-relaxed">
              We believe in helping young people develop self-awareness, discover their path, and achieve personal milestones through meaningful conversations and guidance.
            </p>
          </div>
        </div>
      </section>

      {/* Features/Challenges Section */}
      <section className="section">
        <h2 className="text-3xl md:text-4xl font-bold text-center mb-12 gradient-text">
          How Navigo Helps
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {/* Challenge 1 */}
          <div className="card hover-lift">
            <div className="mb-6 p-3 bg-primary-purple/20 rounded-full w-14 h-14 flex items-center justify-center">
              <svg className="w-8 h-8 text-primary-teal" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
              </svg>
            </div>
            <h3 className="text-xl font-bold text-primary-teal mb-4">Career Guidance</h3>
            <p className="text-neutral-300">
              Navigate career uncertainty with personalized conversations about your interests, strengths, and potential paths forward.
            </p>
          </div>
          
          {/* Challenge 2 */}
          <div className="card hover-lift">
            <div className="mb-6 p-3 bg-primary-teal/20 rounded-full w-14 h-14 flex items-center justify-center">
              <svg className="w-8 h-8 text-primary-purple" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
              </svg>
            </div>
            <h3 className="text-xl font-bold text-primary-lilac mb-4">Mental Well-being</h3>
            <p className="text-neutral-300">
              Find support for stress, anxiety, and other challenges through thoughtful reflection and evidence-based coping strategies.
            </p>
          </div>
          
          {/* Challenge 3 */}
          <div className="card hover-lift">
            <div className="mb-6 p-3 bg-accent-amber/20 rounded-full w-14 h-14 flex items-center justify-center">
              <svg className="w-8 h-8 text-accent-amber" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <h3 className="text-xl font-bold text-accent-amber mb-4">Personal Growth</h3>
            <p className="text-neutral-300">
              Set meaningful goals, track your progress, and develop the skills needed to achieve your personal milestones.
            </p>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="section">
        <div className="bg-gradient-primary p-[1px] rounded-lg shadow-glow-purple">
          <div className="bg-neutral-800/90 backdrop-blur-md rounded-[calc(0.5rem-1px)] p-8 md:p-12">
            <div className="max-w-3xl mx-auto space-y-8">
              <h2 className="text-3xl md:text-4xl font-bold text-center text-neutral-50">
                Start Your Journey Today
              </h2>
              <p className="text-xl text-center text-neutral-200">
                Join Navigo and take the first step toward a more focused, purposeful, and supported future.
              </p>
              <div className="flex flex-col sm:flex-row justify-center gap-4">
                <Link href="/register" className="btn btn-primary">
                  Create Account
                </Link>
                <Link href="/login" className="btn btn-outline">
                  Log In
                </Link>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
} 