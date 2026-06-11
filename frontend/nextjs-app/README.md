# Job Search AI Agent — Frontend

> **Next.js 14 (App Router)** — Custom CSS design system · No external UI libraries

---

## Overview

This is the full-stack frontend for the Job Search AI Agent platform. It communicates with 5 separate FastAPI microservices via Next.js API rewrites (so no CORS issues and service URLs stay out of the browser bundle).

---

## Features

| Page | Route | Description |
|---|---|---|
| **Onboarding** | (first visit) | Resume upload gate — parsed immediately on upload |
| **Dashboard** | `/` → `dashboard` | Stats summary + recommended job feed |
| **Jobs Feed** | `jobs` | Search Naukri/Indeed/LinkedIn with Indian filters + AI insights |
| **Resume** | `resume` | Upload + AI parsing + ATS score against any JD |
| **Kanban** | `kanban` | Drag-and-drop tracker (Applied → Screening → Offer) |
| **Interview** | `interview` | AI question generator + answer evaluator + negotiation chatbot |

---

## Tech Stack

- **Framework**: Next.js 14 with App Router
- **Styling**: Vanilla CSS-in-JS (inline styles with the shared `COLORS` token system in `ui.tsx`)
- **Type Safety**: TypeScript throughout
- **State**: React `useState` / `useCallback` — no Redux or Zustand
- **API Layer**: `src/lib/api.ts` — typed async functions for all 5 services

---

## Project Structure

```
src/
├── app/
│   ├── page.tsx            # App shell — routes between pages; Onboarding gate ✨
│   ├── layout.tsx          # Root layout + Google Fonts
│   └── globals.css         # CSS reset
├── components/
│   ├── ui.tsx              # Shared design system (COLORS, Icon, Card, Badge…)
│   ├── Sidebar.tsx         # Collapsible navigation sidebar
│   ├── OnboardingPage.tsx  # First-visit resume upload flow
│   ├── DashboardPage.tsx   # Home dashboard with stats + job feed
│   ├── JobsFeedPage.tsx    # Search + filters + AI insights panel
│   ├── ResumePage.tsx      # Resume upload + ATS analysis
│   ├── KanbanPage.tsx      # Application tracking board
│   ├── InterviewPage.tsx   # Mock interview + salary negotiation
│   ├── ResumeDemoPage.tsx  # Demo/walkthrough page
│   └── AboutPage.tsx       # About page
└── lib/
    ├── api.ts              # Typed API client (all 5 microservices)
    └── types.ts            # Shared TypeScript interfaces
```

---

## Running Locally

```bash
npm install
npm run dev     # starts on http://localhost:3000
```

The backend services must also be running on their respective ports (8001–8005). See the root `README.md` for the full startup guide.

---

## API Wiring

All `/api/*` calls are proxied via `next.config.ts`:

| Frontend path | Backend service |
|---|---|
| `/api/auth/*` | Auth Service `:8001` |
| `/api/jobs/*` | Jobs Service `:8002` |
| `/api/resumes/*` | Resume Service `:8003` |
| `/api/interview/*` | Interview Service `:8004` |
| `/api/analytics/*` | Analytics Service `:8005` |
| `/api/applications/*` | Auth Service `:8001` |

---

## Environment Variables

The frontend itself needs no secrets. All service URLs default to `localhost:800x` but can be overridden for production:

```env
AUTH_SERVICE_URL=https://auth.yourapp.com
JOBS_SERVICE_URL=https://jobs.yourapp.com
RESUME_SERVICE_URL=https://resume.yourapp.com
INTERVIEW_SERVICE_URL=https://interview.yourapp.com
ANALYTICS_SERVICE_URL=https://analytics.yourapp.com
```

---

## Building for Production

```bash
npm run build   # TypeScript check + static page generation
npm start       # Serve the production build
```

---

## Design System

All styling uses the `COLORS` token object from `src/components/ui.tsx`:

```typescript
COLORS.bg         // Page background (#F8FAFC)
COLORS.card       // Card surfaces (#FFFFFF)
COLORS.brand      // Primary blue (#3B82F6)
COLORS.brandLight // Light blue tint (#EFF6FF)
COLORS.text       // Primary text (#0F172A)
COLORS.textMuted  // Secondary text (#64748B)
COLORS.border     // Card borders (#E2E8F0)
```

Common components: `Card`, `Badge`, `Icon`, `EmptyState`, `StatCard`, `Skeleton`
