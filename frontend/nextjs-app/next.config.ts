import type { NextConfig } from "next";

/**
 * Next.js API Route Rewrites
 *
 * All /api/* calls from the browser are proxied to the appropriate FastAPI
 * microservice. This avoids CORS issues in the browser and keeps service URLs
 * out of the client bundle.
 *
 * Service ports (local dev):
 *   Auth Service        → :8001
 *   Jobs Service        → :8002
 *   Resume Service      → :8003
 *   Interview Service   → :8004
 *   Analytics Service   → :8005
 *
 * In production, set NEXT_PUBLIC_AUTH_URL, NEXT_PUBLIC_JOBS_URL, etc.
 * via environment variables to point to deployed service URLs.
 */

const AUTH_URL      = process.env.AUTH_SERVICE_URL      ?? "http://localhost:8001";
const JOBS_URL      = process.env.JOBS_SERVICE_URL      ?? "http://localhost:8002";
const RESUME_URL    = process.env.RESUME_SERVICE_URL    ?? "http://localhost:8003";
const INTERVIEW_URL = process.env.INTERVIEW_SERVICE_URL ?? "http://localhost:8004";
const ANALYTICS_URL = process.env.ANALYTICS_SERVICE_URL ?? "http://localhost:8005";

const nextConfig: NextConfig = {
  async rewrites() {
    return [
      // Auth Service (Port 8001)
      {
        source: "/api/auth/:path*",
        destination: `${AUTH_URL}/auth/:path*`,
      },

      // Jobs Service (Port 8002)
      {
        source: "/api/jobs/:path*",
        destination: `${JOBS_URL}/jobs/:path*`,
      },

      // Applications are stored via the Auth/User Service
      {
        source: "/api/applications/:path*",
        destination: `${AUTH_URL}/applications/:path*`,
      },

      // Resume Service (Port 8003)
      {
        source: "/api/resumes/:path*",
        destination: `${RESUME_URL}/resumes/:path*`,
      },

      // Interview Service (Port 8004)
      {
        source: "/api/interview/:path*",
        destination: `${INTERVIEW_URL}/interview/:path*`,
      },

      // Analytics Service (Port 8005)
      {
        source: "/api/analytics/:path*",
        destination: `${ANALYTICS_URL}/:path*`,
      },

      // Connected Sources (via Auth Service)
      {
        source: "/api/sources/:path*",
        destination: `${AUTH_URL}/sources/:path*`,
      },
    ];
  },
};

export default nextConfig;
