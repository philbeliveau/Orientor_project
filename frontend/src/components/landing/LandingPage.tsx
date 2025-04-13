'use client';
import { useRouter } from 'next/navigation';
import Image from 'next/image';
import Link from 'next/link';

export default function LandingPage() {
  const router = useRouter();

  return (
    <div className="max-w-7xl mx-auto">
      {/* Hero Section */}
      <section className="py-16 md:py-24">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-12 items-center">
          <div className="space-y-8">
            <h1 className="text-4xl md:text-5xl font-bold bg-clip-text text-transparent bg-gradient-metallic-purple">
              Welcome to Navigo
            </h1>
            <p className="text-xl text-surface-light/90 leading-relaxed">
              Your personal guide for growth, reflection, and achieving your goals. Navigo provides a supportive environment for youth to navigate life's challenges.
            </p>
            <div className="flex flex-col sm:flex-row gap-4">
              <Link href="/login" className="btn btn-primary text-center">
                Log In
              </Link>
              <Link href="/register" className="btn btn-outline text-center">
                Sign Up
              </Link>
            </div>
          </div>
          <div className="relative h-80 md:h-96 rounded-xl overflow-hidden shadow-glow-purple">
            {/* Placeholder for an illustration - you can replace this with an actual image */}
            <div className="absolute inset-0 bg-gradient-metallic-purple opacity-20"></div>
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="text-5xl font-bold text-surface-light">Navigo</div>
            </div>
          </div>
        </div>
      </section>

      {/* Mission Section */}
      <section className="py-16 bg-surface-dark backdrop-blur-sm rounded-xl p-8 shadow-lg border border-metallic-purple/20 my-12">
        <div className="max-w-4xl mx-auto text-center space-y-8">
          <h2 className="text-3xl md:text-4xl font-bold bg-clip-text text-transparent bg-gradient-metallic-gold">
            Our Mission
          </h2>
          <p className="text-xl text-surface-light/90 leading-relaxed">
            Navigo's mission is to empower youth by providing them with a safe, supportive environment to reflect, plan, and engage with mentors or automated guidance.
          </p>
          <p className="text-xl text-surface-light/90 leading-relaxed">
            We believe in helping young people develop self-awareness, discover their path, and achieve personal milestones through meaningful conversations and guidance.
          </p>
        </div>
      </section>

      {/* Features/Challenges Section */}
      <section className="py-16">
        <h2 className="text-3xl md:text-4xl font-bold text-center mb-12 bg-clip-text text-transparent bg-gradient-metallic-purple">
          How Navigo Helps
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {/* Challenge 1 */}
          <div className="card hover-glow transition-all duration-300 hover:translate-y-[-5px]">
            <h3 className="text-xl font-bold text-metallic-gold mb-4">Career Guidance</h3>
            <p className="text-surface-light/80">
              Navigate career uncertainty with personalized conversations about your interests, strengths, and potential paths forward.
            </p>
          </div>
          
          {/* Challenge 2 */}
          <div className="card hover-glow transition-all duration-300 hover:translate-y-[-5px]">
            <h3 className="text-xl font-bold text-metallic-gold mb-4">Mental Well-being</h3>
            <p className="text-surface-light/80">
              Find support for stress, anxiety, and other challenges through thoughtful reflection and evidence-based coping strategies.
            </p>
          </div>
          
          {/* Challenge 3 */}
          <div className="card hover-glow transition-all duration-300 hover:translate-y-[-5px]">
            <h3 className="text-xl font-bold text-metallic-gold mb-4">Personal Growth</h3>
            <p className="text-surface-light/80">
              Set meaningful goals, track your progress, and develop the skills needed to achieve your personal milestones.
            </p>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-16 text-center">
        <div className="bg-gradient-metallic-purple p-0.5 rounded-xl">
          <div className="bg-base-charcoal rounded-[calc(0.75rem-1px)] p-8 md:p-12">
            <div className="max-w-3xl mx-auto space-y-8">
              <h2 className="text-3xl md:text-4xl font-bold text-surface-light">
                Start Your Journey Today
              </h2>
              <p className="text-xl text-surface-light/90">
                Join Navigo and take the first step toward a more focused, purposeful, and supported future.
              </p>
              <div className="flex flex-col sm:flex-row justify-center gap-4">
                <Link href="/register" className="btn btn-primary text-center">
                  Create Account
                </Link>
                <Link href="/login" className="btn btn-outline text-center">
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