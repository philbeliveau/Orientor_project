'use client';
import { useRouter } from 'next/navigation';
import Image from 'next/image';
import { Player } from '@lottiefiles/react-lottie-player'; // npm install @lottiefiles/react-lottie-player
import { motion } from 'framer-motion'; // npm install framer-motion
import Link from 'next/link';

export default function LandingPage() {
  const router = useRouter();

  return (
    <div className="max-w-7xl mx-auto">
      {/* Hero Section */}
      <section className="section">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-12 items-center">
          <motion.div
            className="space-y-8"
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
          >
            <h1 className="text-4xl md:text-6xl font-bold gradient-text">
              Welcome to Navigo
            </h1>
            <p className="text-xl text-neutral-200 leading-relaxed">
              Discover who you are, and who you could become. Navigo helps you reflect, explore, and track your growth with personalized, intelligent guidance.
            </p>
            <div className="flex flex-col sm:flex-row gap-4">
              <Link href="/login" className="btn btn-primary">Log In</Link>
              <Link href="/register" className="btn btn-outline">Sign Up</Link>
            </div>
          </motion.div>

          <motion.div
            className="relative h-80 md:h-96 rounded-lg overflow-hidden"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.3, duration: 0.8 }}
          >
            <Player
              autoplay
              loop
              src="https://assets9.lottiefiles.com/packages/lf20_uegxllzu.json" // Replace with your Lottie file URL
              className="w-full h-full"
            />
          </motion.div>
        </div>
      </section>

      {/* Mission Section */}
      <section className="section">
        <div className="card container-narrow">
          <div className="text-center space-y-8">
            <h2 className="text-3xl md:text-4xl font-bold gradient-text-secondary">Our Mission</h2>
            <p className="text-xl text-neutral-200 leading-relaxed">
              Navigo empowers young minds to understand their strengths, track their growth, and explore career paths they may have never imagined. Our platform gives students tools to reflect, challenge themselves, and set meaningful direction.
            </p>
            <p className="text-xl text-neutral-200 leading-relaxed">
              Through interactive guidance, skill-based mapping, and daily recommendations, we help students craft their future one thoughtful step at a time.
            </p>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="section">
        <h2 className="text-3xl md:text-4xl font-bold text-center mb-12 gradient-text">How Navigo Helps</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">

          {/* Feature 1: Career Guidance */}
          <div className="card hover-lift">
            <div className="mb-6 p-3 bg-primary-purple/20 rounded-full w-14 h-14 flex items-center justify-center">
              <svg className="w-8 h-8 text-primary-teal" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
              </svg>
            </div>
            <h3 className="text-xl font-bold text-primary-teal mb-4">Skill-Based Career Mapping</h3>
            <p className="text-neutral-300">
              We go beyond job titles. Navigo builds a graph of your skills to suggest personalized next steps—based on what you know, what you’re building, and where you want to go.
            </p>
          </div>

          {/* Feature 2: Personal Growth */}
          <div className="card hover-lift">
            <div className="mb-6 p-3 bg-accent-amber/20 rounded-full w-14 h-14 flex items-center justify-center">
              <svg className="w-8 h-8 text-accent-amber" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <h3 className="text-xl font-bold text-accent-amber mb-4">Space: Your Personal Mission Hub</h3>
            <p className="text-neutral-300">
              Track your chosen career goals, compare your current skills with what’s needed, reflect on daily progress, and receive micro-recommendations on how to advance.
            </p>
          </div>

          {/* Feature 3: Future Path Prediction */}
          <div className="card hover-lift">
            <div className="mb-6 p-3 bg-primary-teal/20 rounded-full w-14 h-14 flex items-center justify-center">
              <svg className="w-8 h-8 text-primary-purple" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 14l9-5-9-5-9 5 9 5zm0 0v7" />
              </svg>
            </div>
            <h3 className="text-xl font-bold text-primary-lilac mb-4">See Your Possible Futures</h3>
            <p className="text-neutral-300">
              Navigo predicts skill-based branches of what you could become. Think of it as a constellation of futures—mapped out based on your growth patterns and intentions.
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
                Join Navigo and let your curiosity, discipline, and imagination build the future you're meant to explore.
              </p>
              <div className="flex flex-col sm:flex-row justify-center gap-4">
                <Link href="/register" className="btn btn-primary">Create Account</Link>
                <Link href="/login" className="btn btn-outline">Log In</Link>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
