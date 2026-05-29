# Job Search AI — Next.js Frontend Dashboard

This directory houses the premium React dashboard for the Job Search AI Agent portal, built on Next.js 16 (App Router) with custom TypeScript definitions and custom Vanilla CSS.

---

## 🎨 Design Philosophy & UI Guidelines

The dashboard is designed to feel highly premium, state-of-the-art, and professional. It aligns with the following product design rules:
*   **Strict Light Mode:** Curated HSL-tailored colors (`bg`, `card`, `border`, `brand`, `success`, `warning`, `danger`) define the theme—completely avoiding plain browser defaults or dark mode styling.
*   **No Placeholders or Generic Layouts:** Every page is populated with custom mock interfaces, interactive statuses, and detailed metric structures.
*   **Zero Emojis:** Standardized, clean vector icons (via SVG paths mapped in `ui.tsx`) are used exclusively for clean aesthetic presentation.
*   **Collapsible Sidebar:** Navigation collapses down to a compact 60px icon-only layout with hardware-accelerated CSS transition curves.
*   **Loading States:** Built-in `<Skeleton />` loaders with a custom CSS shimmer keyframe ensure smooth content transitions.

---

## 📁 Key Dashboard Features

1.  **Resume Onboarding Gate (`OnboardingPage`):**
    *   Guards the application on initial visit. A full-screen drag-and-drop zone forces resume upload.
    *   Saves the onboarded status inside the browser's `localStorage` to bypass future onboarding steps.
2.  **Dashboard Hub (`DashboardPage`):**
    *   Displays macro statistics (Application Counts, Scheduled Interviews, ATS Averages, and Success Rates).
    *   Shows a visual SVG sparkline trend graph and a summary table of active application files.
3.  **Job Recommendations & Search (`JobsFeedPage`):**
    *   Browse matching positions in a dual-column layout (Listings on the left, full Job Details + description on the right).
    *   Supports text search queries, source filters (LinkedIn, Naukri, Indeed), and instant application submissions.
4.  **Drag-and-Drop Kanban Board (`KanbanPage`):**
    *   A status tracker featuring five stages: *Wishlist*, *Applied*, *Interviewing*, *Offer*, and *Rejected*.
    *   Implemented via local React state handlers, permitting card dragging, sorting, and stage transitions.
5.  **Resume Analysis & ATS Gap Check (`ResumePage` & `ResumeDemoPage`):**
    *   Paste job descriptions side-by-side with resumes to view keyword overlap scores out of 100.
    *   Color-coded matched and missing skill badges with improvement warnings.
6.  **AI Interview Practice simulator (`InterviewPage`):**
    *   Select round types (Technical, HR, Behavioral) and target roles to trigger mock interview questions.
    *   Track answer lengths, response logs, and evaluation metrics dynamically.

---

## 🛠️ Folder Structure

```
src/
├── app/
│   ├── globals.css      # Core CSS tokens, styles, and @keyframes (shimmer, spin)
│   ├── layout.tsx       # Global HTML5 wrappers and SEO metadata
│   └── page.tsx         # App shell coordinating Onboarding states and active routes
├── components/
│   ├── ui.tsx           # Shared components (Card, Badge, EmptyState, Skeleton, StatCard, Icon)
│   ├── Sidebar.tsx      # Collapsible side navigation layout
│   ├── OnboardingPage.tsx # Onboarding drag-and-drop wizard
│   ├── DashboardPage.tsx # Summary statistics and lists
│   ├── KanbanPage.tsx    # Drag-and-drop board
│   ├── JobsFeedPage.tsx  # Dual-column job search client
│   ├── ResumePage.tsx    # Resume uploads and ATS analysis
│   ├── ResumeDemoPage.tsx # Step-by-step ATS checklist demo
│   ├── InterviewPage.tsx # Interactive Q&A mock round simulator
│   └── AboutPage.tsx     # Mission statements and tech-stack tables
└── lib/
    ├── api.ts           # Central fetch client (API stubs to real backend routes)
    └── types.ts         # Global TypeScript interface specifications (Job, Application, User, etc.)
```

---

## 💻 Development & Build Scripts

First, install dependencies:
```bash
npm install
```

Run the local development server:
```bash
npm run dev
```
Open [http://localhost:3000](http://localhost:3000) with your browser.

Build the application for production deployment (runs compiler type checks and static pages generation):
```bash
npm run build
```

Run production build locally:
```bash
npm run start
```
