import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  images: {
    domains: [
      'randomuser.me',
      'static.licdn.com',
      'media.licdn.com',
      'platform-lookaside.fbsbx.com',
      'lh3.googleusercontent.com',
      'avatars.githubusercontent.com'
    ],
  },
};

export default nextConfig;
