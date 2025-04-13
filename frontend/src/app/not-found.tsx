'use client';

import Link from 'next/link';
import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function NotFound() {
  const router = useRouter();

  useEffect(() => {
    // Log the 404 error for monitoring
    console.error('404 error: Page not found');
  }, []);

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-dark">
      <div className="card backdrop-blur-md max-w-lg p-8 text-center relative overflow-hidden">
        {/* Decorative gradient elements */}
        <div className="absolute inset-0 -z-10 bg-[radial-gradient(circle_at_top_right,rgba(125,91,166,0.15),transparent_40%)]"></div>
        <div className="absolute inset-0 -z-10 bg-[radial-gradient(circle_at_bottom_left,rgba(89,194,201,0.15),transparent_40%)]"></div>
        
        <div className="mb-8">
          <h1 className="text-6xl font-bold font-display gradient-text mb-4">404</h1>
          <h2 className="text-2xl font-semibold text-neutral-100 mb-2">Page Not Found</h2>
          <p className="text-neutral-300">
            The page you're looking for doesn't exist or has been moved.
          </p>
        </div>

        <div className="space-y-4">
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button
              onClick={() => router.back()}
              className="btn btn-outline"
            >
              Go Back
            </button>
            <Link href="/" className="btn btn-primary">
              Return Home
            </Link>
          </div>
          
          <div className="text-sm text-neutral-400 mt-6">
            <p>Need help? Check out our</p>
            <Link href="/help" className="text-primary-teal hover:text-primary-lilac transition-colors duration-300">
              Help Center
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
} 