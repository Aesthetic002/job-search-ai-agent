"use client";

import React from "react";
import { COLORS, Icon, Card } from "./ui";

const FEATURES = [
  {
    icon: "briefcase",
    title: "AI Job Matching",
    desc: "Connect LinkedIn, Naukri, and Indeed. Our AI ranks every listing against your resume, skills, and target role — so you see the best matches first.",
  },
  {
    icon: "target",
    title: "ATS Score Engine",
    desc: "Paste any job description and get an instant keyword match score. Our AI identifies exactly what's missing and rewrites your bullet points to pass ATS filters.",
  },
  {
    icon: "layout",
    title: "Application Kanban",
    desc: "Track every application across stages — Applied, Screening, Interviewing, Offer. Never lose track of a deadline or follow-up again.",
  },
  {
    icon: "mic",
    title: "Mock Interview Coach",
    desc: "Practice role-specific questions — behavioral, technical, system design. Get AI feedback, scoring, and suggested rewrites for every answer.",
  },
  {
    icon: "bar-chart",
    title: "Job Search Analytics",
    desc: "Visualize your application pipeline, offer rate, response rate by source, and ATS score trends over time.",
  },
  {
    icon: "zap",
    title: "Smart Automation",
    desc: "Auto-sync jobs from connected sources, auto-fill application forms, and get notified when a high-match job is posted.",
  },
];

const TECH = [
  { label: "Frontend", stack: ["Next.js 16", "TypeScript", "React 19"] },
  { label: "Backend", stack: ["Python", "FastAPI", "LangGraph"] },
  { label: "AI / ML", stack: ["Gemini 2.0", "LangChain", "Vertex AI"] },
  { label: "Database", stack: ["Firestore", "Redis", "Cloud SQL"] },
  { label: "Infrastructure", stack: ["Google Cloud", "Firebase", "Docker"] },
  { label: "Job Sources", stack: ["LinkedIn API", "Naukri API", "Indeed API"] },
];

export const AboutPage = ({ onNavigate }: { onNavigate?: (page: string) => void }) => {
  return (
    <div style={{ flex: 1, display: "flex", flexDirection: "column", background: COLORS.bg, minHeight: "100vh" }}>
      {/* Hero */}
      <div style={{ padding: "36px 28px 0", maxWidth: 680 }}>
        <div style={{ display: "inline-flex", alignItems: "center", gap: 8, padding: "5px 12px", borderRadius: 20, background: COLORS.brandLight, border: `1px solid #C7D2FE`, marginBottom: 16 }}>
          <div style={{ width: 20, height: 20, borderRadius: 5, background: COLORS.brand, display: "flex", alignItems: "center", justifyContent: "center" }}>
            <Icon name="cpu" size={11} color="#fff" />
          </div>
          <span style={{ fontSize: 13, fontWeight: 600, color: COLORS.brand }}>Job Search AI</span>
        </div>
        <h1 style={{ fontSize: 28, fontWeight: 800, color: COLORS.text, margin: "0 0 14px", letterSpacing: "-0.5px", lineHeight: 1.25 }}>
          Your intelligent AI-powered<br />job search assistant
        </h1>
        <p style={{ fontSize: 14, color: COLORS.textMuted, margin: "0 0 32px", lineHeight: 1.8 }}>
          Job Search AI brings together AI job matching, ATS resume optimization, application tracking,
          and mock interview coaching into a single workspace — so every hour you spend on your
          job search is focused, effective, and measurably better.
        </p>
        <div style={{ display: "flex", gap: 10 }}>
          <button
            onClick={() => onNavigate?.("dashboard")}
            style={{ padding: "10px 22px", borderRadius: 8, border: "none", background: COLORS.brand, color: "#fff", fontSize: 14, fontWeight: 600, cursor: "pointer", display: "flex", alignItems: "center", gap: 7 }}
          >
            <Icon name="grid" size={14} color="#fff" /> Go to Dashboard
          </button>
          <button
            onClick={() => onNavigate?.("demo")}
            style={{ padding: "10px 22px", borderRadius: 8, border: `1px solid ${COLORS.border}`, background: COLORS.card, color: COLORS.text, fontSize: 14, fontWeight: 500, cursor: "pointer", display: "flex", alignItems: "center", gap: 7 }}
          >
            <Icon name="play" size={14} color={COLORS.textMuted} /> See a Demo
          </button>
        </div>
      </div>

      {/* Features */}
      <div style={{ padding: "36px 28px 0" }}>
        <div style={{ fontSize: 11, fontWeight: 700, color: COLORS.textLight, letterSpacing: "0.07em", textTransform: "uppercase", marginBottom: 16 }}>
          Core Features
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 12 }}>
          {FEATURES.map((f, i) => (
            <Card key={i} style={{ padding: 20 }}>
              <div style={{ width: 36, height: 36, borderRadius: 9, background: COLORS.brandLight, display: "flex", alignItems: "center", justifyContent: "center", marginBottom: 14 }}>
                <Icon name={f.icon} size={17} color={COLORS.brand} />
              </div>
              <div style={{ fontSize: 14, fontWeight: 700, color: COLORS.text, marginBottom: 7 }}>{f.title}</div>
              <p style={{ fontSize: 12.5, color: COLORS.textMuted, margin: 0, lineHeight: 1.7 }}>{f.desc}</p>
            </Card>
          ))}
        </div>
      </div>

      {/* Tech stack */}
      <div style={{ padding: "28px 28px 0" }}>
        <div style={{ fontSize: 11, fontWeight: 700, color: COLORS.textLight, letterSpacing: "0.07em", textTransform: "uppercase", marginBottom: 16 }}>
          Technology Stack
        </div>
        <Card>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 0 }}>
            {TECH.map((t, i) => (
              <div
                key={i}
                style={{
                  padding: 18,
                  borderRight: i % 3 < 2 ? `1px solid ${COLORS.borderLight}` : "none",
                  borderBottom: i < 3 ? `1px solid ${COLORS.borderLight}` : "none",
                }}
              >
                <div style={{ fontSize: 11, fontWeight: 700, color: COLORS.brand, letterSpacing: "0.06em", textTransform: "uppercase", marginBottom: 10 }}>
                  {t.label}
                </div>
                <div style={{ display: "flex", flexWrap: "wrap", gap: 5 }}>
                  {t.stack.map((s, si) => (
                    <span key={si} style={{ fontSize: 12, padding: "3px 8px", borderRadius: 4, background: COLORS.borderLight, color: COLORS.textMuted, fontWeight: 500 }}>{s}</span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </Card>
      </div>

      {/* Mission */}
      <div style={{ padding: "24px 28px 0" }}>
        <Card style={{ padding: 24, background: `linear-gradient(135deg, #FAFAFF 0%, #F5F3FF 100%)`, border: `1px solid #DDD6FE` }}>
          <div style={{ display: "flex", gap: 20, alignItems: "flex-start" }}>
            <div style={{ width: 40, height: 40, borderRadius: 10, background: COLORS.brand, display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
              <Icon name="target" size={18} color="#fff" />
            </div>
            <div>
              <div style={{ fontSize: 15, fontWeight: 700, color: COLORS.text, marginBottom: 8 }}>Our Mission</div>
              <p style={{ fontSize: 13, color: COLORS.textMuted, margin: 0, lineHeight: 1.8, maxWidth: 600 }}>
                Job searching is broken. Candidates spend 80% of their time on low-signal tasks — browsing random listings, rewriting resumes without knowing what hiring algorithms want, and rehearsing answers alone. Job Search AI fixes this by making every part of the job search process intelligent, measurable, and dramatically faster.
              </p>
            </div>
          </div>
        </Card>
      </div>

      {/* Status */}
      <div style={{ padding: "20px 28px 0" }}>
        <div style={{ fontSize: 11, fontWeight: 700, color: COLORS.textLight, letterSpacing: "0.07em", textTransform: "uppercase", marginBottom: 12 }}>
          Build Status
        </div>
        <Card>
          <div style={{ padding: 0 }}>
            {[
              { feature: "Dashboard & Stats", status: "ready", label: "Ready" },
              { feature: "Jobs Feed & Search", status: "ready", label: "Ready — awaiting job source API keys" },
              { feature: "Resume Upload", status: "ready", label: "UI ready — backend parsing in progress" },
              { feature: "ATS Analysis Engine", status: "progress", label: "In Progress — LangGraph workflow in dev" },
              { feature: "Application Kanban", status: "ready", label: "Ready — awaiting backend connection" },
              { feature: "Mock Interview Coach", status: "progress", label: "In Progress — question bank + evaluator in dev" },
              { feature: "Analytics Dashboard", status: "planned", label: "Planned" },
            ].map((row, i, arr) => (
              <div
                key={i}
                style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  padding: "13px 18px",
                  borderBottom: i < arr.length - 1 ? `1px solid ${COLORS.borderLight}` : "none",
                }}
              >
                <span style={{ fontSize: 13, color: COLORS.text, fontWeight: 500 }}>{row.feature}</span>
                <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                  <span style={{ fontSize: 12, color: COLORS.textMuted }}>{row.label}</span>
                  <div
                    style={{
                      width: 8,
                      height: 8,
                      borderRadius: "50%",
                      background:
                        row.status === "ready"
                          ? COLORS.successMid
                          : row.status === "progress"
                          ? COLORS.warningMid
                          : COLORS.textLight,
                    }}
                  />
                </div>
              </div>
            ))}
          </div>
        </Card>
      </div>

      {/* Links */}
      <div style={{ padding: "20px 28px 40px", display: "flex", gap: 10, flexWrap: "wrap" }}>
        <a
          href="https://github.com"
          target="_blank"
          rel="noopener noreferrer"
          style={{
            display: "flex",
            alignItems: "center",
            gap: 6,
            padding: "8px 16px",
            borderRadius: 6,
            border: `1px solid ${COLORS.border}`,
            background: COLORS.card,
            fontSize: 13,
            color: COLORS.textMuted,
            fontWeight: 500,
            textDecoration: "none",
          }}
        >
          <Icon name="link" size={13} color={COLORS.textMuted} /> GitHub Repository
        </a>
        <a
          href="mailto:team@capabl.ai"
          style={{
            display: "flex",
            alignItems: "center",
            gap: 6,
            padding: "8px 16px",
            borderRadius: 6,
            border: `1px solid ${COLORS.border}`,
            background: COLORS.card,
            fontSize: 13,
            color: COLORS.textMuted,
            fontWeight: 500,
            textDecoration: "none",
          }}
        >
          <Icon name="send" size={13} color={COLORS.textMuted} /> Contact Team
        </a>
      </div>
    </div>
  );
};
