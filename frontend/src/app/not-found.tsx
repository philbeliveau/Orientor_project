'use client';

import Link from 'next/link';

export default function NotFound() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center">
      <div className="card backdrop-blur-md max-w-lg p-8 text-center">
        <h1 className="text-4xl font-bold font-display gradient-text mb-4">404 - Page Not Found</h1>
        <p className="text-neutral-300 mb-8">
          The page you're looking for doesn't exist or has been moved.
        </p>
        <div className="space-y-4">
          <Link href="/" className="btn btn-primary">
            Return Home
          </Link>
        </div>
      </div>
    </div>
  );
} 