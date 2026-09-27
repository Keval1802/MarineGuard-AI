/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  images: {
    unoptimized: true,
  },
  async rewrites() {
    return [
      {
        source: '/storage/evidence/:path*',
        destination: 'http://localhost:8000/storage/evidence/:path*',
      },
    ]
  },
}

module.exports = nextConfig
