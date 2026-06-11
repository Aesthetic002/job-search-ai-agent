"use client";

import { useState, useEffect } from "react";
import { Sidebar, type NavPage } from "@/components/Sidebar";
import { DashboardPage } from "@/components/DashboardPage";
import { JobsFeedPage } from "@/components/JobsFeedPage";
import { ResumePage } from "@/components/ResumePage";
import { KanbanPage } from "@/components/KanbanPage";
import { InterviewPage } from "@/components/InterviewPage";
import { ResumeDemoPage } from "@/components/ResumeDemoPage";
import { AboutPage } from "@/components/AboutPage";
import { OnboardingPage } from "@/components/OnboardingPage";

const ONBOARDING_KEY = "job_search_ai_onboarded";

export default function App() {
  const [onboarded, setOnboarded] = useState<boolean | null>(null);
  const [activePage, setActivePage] = useState<NavPage>("dashboard");
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  // Read localStorage on mount (avoids SSR mismatch)
  useEffect(() => {
    const done = localStorage.getItem(ONBOARDING_KEY) === "true";
    setOnboarded(done);
  }, []);

  const handleOnboardingComplete = (_fileName: string) => {
    localStorage.setItem(ONBOARDING_KEY, "true");
    setOnboarded(true);
  };

  const handleOnboardingSkip = () => {
    localStorage.setItem(ONBOARDING_KEY, "true");
    setOnboarded(true);
  };

  const navigate = (page: string) => setActivePage(page as NavPage);

  // SSR hydration: render nothing until we've read localStorage
  if (onboarded === null) return null;

  // First-time visitor → show full-screen onboarding
  if (!onboarded) {
    return (
      <OnboardingPage
        onComplete={handleOnboardingComplete}
        onSkip={handleOnboardingSkip}
      />
    );
  }

  const renderPage = () => {
    switch (activePage) {
      case "dashboard":
        return <DashboardPage />;
      case "jobs":
        return <JobsFeedPage />;
      case "resume":
        return <ResumePage />;
      case "kanban":
        return <KanbanPage />;
      case "interview":
        return <InterviewPage />;
      case "demo":
        return <ResumeDemoPage onNavigate={navigate} />;
      case "about":
        return <AboutPage onNavigate={navigate} />;
      default:
        return <DashboardPage />;
    }
  };

  return (
    <div
      style={{
        display: "flex",
        minHeight: "100vh",
        fontFamily: "'Instrument Sans', 'Inter', -apple-system, BlinkMacSystemFont, sans-serif",
        background: "#F8FAFC",
        color: "#0F172A",
        fontSize: 14,
      }}
    >
      <Sidebar
        active={activePage}
        setActive={setActivePage}
        collapsed={sidebarCollapsed}
        onToggle={() => setSidebarCollapsed((c) => !c)}
      />
      <main
        style={{
          flex: 1,
          overflow: "auto",
          minWidth: 0,
          transition: "padding 0.2s ease",
        }}
      >
        {renderPage()}
      </main>
    </div>
  );
}
