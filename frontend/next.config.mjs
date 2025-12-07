/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  images: {
    domains: ['localhost'],
  },
  // Optimize untuk fast load
  compiler: {
    removeConsole: process.env.NODE_ENV === 'production',
  },
  // Enable experimental features untuk performa
  experimental: {
    optimizeCss: true,
  },
};

export default nextConfig;
