'use client';

import { useEffect } from 'react';
import Link from 'next/link';

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    // Log the error to an error reporting service
    console.error(error);
  }, [error]);

  return (
    <div className="min-h-screen flex flex-col items-center justify-center">
      <div className="card backdrop-blur-md max-w-lg p-8 text-center">
        <h1 className="text-4xl font-bold font-display gradient-text mb-4">Something went wrong!</h1>
        <p className="text-neutral-300 mb-8">
          Sorry, an unexpected error has occurred.
        </p>
        <div className="space-x-4">
          <button onClick={reset} className="btn btn-primary">
            Try again
          </button>
          <Link href="/" className="btn btn-outline">
            Return Home
          </Link>
        </div>
      </div>
    </div>
  );
} 