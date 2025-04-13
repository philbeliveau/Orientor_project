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
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
  },
  // Add configuration for handling client-side rendering
  experimental: {
    appDir: true,
  },
  // Ensure proper handling of dynamic routes
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'https://orientor-backend-production.up.railway.app/api/:path*',
      },
    ];
  },
};

module.exports = nextConfig;