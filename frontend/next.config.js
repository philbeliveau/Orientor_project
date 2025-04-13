// import type { NextConfig } from "next";

// const nextConfig: NextConfig = {
//   /* config options here */
// };

// export default nextConfig;

/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  images: {
    domains: ['orientor-backend-production.up.railway.app'], // Add your image domains here
    unoptimized: true, // This helps with static exports if needed
  },
  // Vercel specific settings
  swcMinify: true,
  compiler: {
    removeConsole: process.env.NODE_ENV === 'production',
  },
  // Handle environment variables
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'https://orientor-backend-production.up.railway.app',
  },
  // Configure build output
  output: 'standalone',
  poweredByHeader: false,
  // Performance optimizations
  experimental: {
    optimizeCss: true,
    scrollRestoration: true,
  },
  // Error handling and performance
  onDemandEntries: {
    maxInactiveAge: 60 * 60 * 1000,
    pagesBufferLength: 5,
  },
  // Remove static export settings
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'https://orientor-backend-production.up.railway.app/api/:path*',
      },
    ];
  },
  // Custom error handling
  async headers() {
    return [
      {
        source: '/:path*',
        headers: [
          {
            key: 'X-DNS-Prefetch-Control',
            value: 'on',
          },
          {
            key: 'Strict-Transport-Security',
            value: 'max-age=63072000; includeSubDomains; preload',
          },
        ],
      },
    ];
  },
};

module.exports = nextConfig;