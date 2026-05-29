"use client";

import React, { useState } from "react";
import { COLORS, Icon, Card, Badge } from "./ui";

// ─── This page is intentional DEMO / showcase content ─────────────────────
// It illustrates what Job Search AI's ATS analysis produces, using a curated example
// resume and job description. This is NOT real user data.

const EXAMPLE_JD = `We are seeking a Staff Frontend Engineer to lead architecture decisions for our payments dashboard. You will work closely with product and design teams to deliver world-class user experiences at scale.

Requirements:
• 7+ years of frontend engineering experience
• Deep expertise in React, TypeScript, and GraphQL
• Experience with design systems and component libraries
• Strong understanding of performance profiling and optimization
• Familiarity with Kubernetes and platform engineering is a plus`;

const EXAMPLE_RESUME_SKILLS = [
  "React", "TypeScript", "Next.js", "GraphQL", "Node.js",
  "PostgreSQL", "Redis", "Docker", "AWS", "Webpack", "Jest", "Storybook",
];

const EXAMPLE_MATCHED = [
  "React", "TypeScript", "GraphQL", "Next.js",
  "Component Library", "Performance Optimization", "System Design",
];

const EXAMPLE_MISSING = [
  "Kubernetes", "Terraform", "Go", "gRPC",
  "Platform Engineering", "SRE experience",
];

const EXAMPLE_EXPERIENCE = [
  {
    role: "Senior Frontend Engineer",
    company: "Flipkart",
    period: "Jan 2022 – Present",
    bullets: [
      "Led migration of legacy jQuery codebase to React 18 + TypeScript, reducing bundle size by 43%",
      "Architected micro-frontend system serving 12 product teams with zero cross-team deployment conflicts",
      "Implemented real-time inventory updates using WebSocket + Redis, improving UX for 2M daily users",
    ],
  },
  {
    role: "Frontend Engineer II",
    company: "InMobi",
    period: "Jul 2019 – Dec 2021",
    bullets: [
      "Built campaign analytics dashboard using D3.js and React, processing 500M+ daily ad events",
      "Reduced p95 LCP from 4.2s to 1.8s through code-splitting, lazy loading, and CDN optimization",
    ],
  },
];

const STEPS = [
  {
    icon: "upload",
    title: "Upload Your Resume",
    desc: "Drop your PDF or DOCX. Our parser extracts skills, experience, and education in seconds.",
  },
  {
    icon: "file-text",
    title: "Paste the Job Description",
    desc: "Copy the full JD from LinkedIn, Naukri, or any job board and paste it directly.",
  },
  {
    icon: "zap",
    title: "Run ATS Analysis",
    desc: "Our AI compares your resume against the JD to score keyword coverage and identify gaps.",
  },
  {
    icon: "lightbulb",
    title: "Get Actionable Suggestions",
    desc: "See exactly which keywords to add and receive AI-rewritten bullet points to boost your score.",
  },
];

type ResumeTab = "experience" | "skills";

export const ResumeDemoPage = ({ onNavigate }: { onNavigate?: (page: string) => void }) => {
  const [activeTab, setActiveTab] = useState<ResumeTab>("experience");

  return (
    <div style={{ flex: 1, display: "flex", flexDirection: "column", background: COLORS.bg, minHeight: "100vh" }}>
      {/* Hero */}
      <div style={{ padding: "32px 28px 0" }}>
        <div style={{ display: "inline-flex", alignItems: "center", gap: 6, padding: "4px 10px", borderRadius: 20, background: COLORS.brandLight, border: `1px solid #C7D2FE`, marginBottom: 14 }}>
          <Icon name="sparkles" size={12} color={COLORS.brand} />
          <span style={{ fontSize: 12, fontWeight: 600, color: COLORS.brand, letterSpacing: "0.01em" }}>Live Demo</span>
        </div>
        <h1 style={{ fontSize: 24, fontWeight: 700, color: COLORS.text, margin: "0 0 10px", letterSpacing: "-0.4px" }}>
          See Job Search AI's ATS Analysis in Action
        </h1>
        <p style={{ fontSize: 14, color: COLORS.textMuted, margin: "0 0 28px", maxWidth: 580, lineHeight: 1.7 }}>
          This walkthrough shows a real example of how Job Search AI compares a resume against a job description, identifies keyword gaps, and generates targeted improvement suggestions.
        </p>
      </div>

      {/* How it works */}
      <div style={{ padding: "0 28px 24px" }}>
        <div style={{ fontSize: 13, fontWeight: 600, color: COLORS.textMuted, letterSpacing: "0.04em", textTransform: "uppercase", marginBottom: 14 }}>
          How it works
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 12 }}>
          {STEPS.map((step, i) => (
            <Card key={i} style={{ padding: 16 }}>
              <div style={{ display: "flex", alignItems: "flex-start", gap: 12 }}>
                <div style={{ width: 32, height: 32, borderRadius: 8, background: COLORS.brandLight, display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
                  <Icon name={step.icon} size={15} color={COLORS.brand} />
                </div>
                <div>
                  <div style={{ display: "flex", alignItems: "center", gap: 7, marginBottom: 5 }}>
                    <span style={{ fontSize: 10, fontWeight: 700, color: COLORS.brand, background: COLORS.brandLight, padding: "1px 6px", borderRadius: 10 }}>{i + 1}</span>
                    <span style={{ fontSize: 13, fontWeight: 600, color: COLORS.text }}>{step.title}</span>
                  </div>
                  <p style={{ fontSize: 12, color: COLORS.textMuted, margin: 0, lineHeight: 1.6 }}>{step.desc}</p>
                </div>
              </div>
            </Card>
          ))}
        </div>
      </div>

      {/* Example banner */}
      <div style={{ margin: "0 28px 16px", padding: "8px 14px", borderRadius: 6, background: COLORS.warningBg, border: `1px solid #FDE68A`, display: "flex", alignItems: "center", gap: 8 }}>
        <Icon name="alert-triangle" size={13} color={COLORS.warning} />
        <span style={{ fontSize: 12, color: COLORS.warning, fontWeight: 500 }}>
          The resume and job description below are illustrative examples only — not real user data.
        </span>
      </div>

      {/* Example analysis */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12, padding: "0 28px 0" }}>
        {/* Resume */}
        <Card style={{ overflow: "hidden", display: "flex", flexDirection: "column" }}>
          <div style={{ padding: "12px 16px", borderBottom: `1px solid ${COLORS.borderLight}`, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <span style={{ fontSize: 13.5, fontWeight: 600, color: COLORS.text }}>Example Resume</span>
            <div style={{ display: "flex", gap: 0, borderRadius: 6, overflow: "hidden", border: `1px solid ${COLORS.border}` }}>
              {(["experience", "skills"] as ResumeTab[]).map((tab) => (
                <button
                  key={tab}
                  onClick={() => setActiveTab(tab)}
                  style={{
                    padding: "5px 12px",
                    border: "none",
                    fontSize: 12,
                    cursor: "pointer",
                    fontWeight: 500,
                    textTransform: "capitalize",
                    background: activeTab === tab ? COLORS.brand : COLORS.card,
                    color: activeTab === tab ? "#fff" : COLORS.textMuted,
                    borderRight: tab === "experience" ? `1px solid ${COLORS.border}` : "none",
                  }}
                >
                  {tab}
                </button>
              ))}
            </div>
          </div>
          <div style={{ padding: 16, overflowY: "auto", maxHeight: 320 }}>
            {activeTab === "experience" &&
              EXAMPLE_EXPERIENCE.map((exp, i) => (
                <div key={i} style={{ marginBottom: 20 }}>
                  <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 2 }}>
                    <span style={{ fontSize: 13.5, fontWeight: 600, color: COLORS.text }}>{exp.role}</span>
                    <span style={{ fontSize: 11, color: COLORS.textLight }}>{exp.period}</span>
                  </div>
                  <div style={{ fontSize: 12, color: COLORS.textMuted, marginBottom: 8 }}>{exp.company}</div>
                  {exp.bullets.map((b, bi) => (
                    <div key={bi} style={{ display: "flex", gap: 8, marginBottom: 5 }}>
                      <span style={{ color: COLORS.brand, flexShrink: 0 }}>•</span>
                      <span style={{ fontSize: 12.5, color: COLORS.text, lineHeight: 1.6 }}>{b}</span>
                    </div>
                  ))}
                </div>
              ))}
            {activeTab === "skills" && (
              <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
                {EXAMPLE_RESUME_SKILLS.map((s, i) => (
                  <span key={i} style={{ padding: "4px 10px", borderRadius: 4, background: COLORS.brandLight, color: COLORS.brand, fontSize: 12, fontWeight: 500, border: "1px solid #C7D2FE" }}>{s}</span>
                ))}
              </div>
            )}
          </div>
        </Card>

        {/* JD */}
        <Card style={{ overflow: "hidden", display: "flex", flexDirection: "column" }}>
          <div style={{ padding: "12px 16px", borderBottom: `1px solid ${COLORS.borderLight}`, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <span style={{ fontSize: 13.5, fontWeight: 600, color: COLORS.text }}>Target Job Description</span>
            <div style={{ display: "flex", alignItems: "center", gap: 8, padding: "5px 12px", borderRadius: 6, background: COLORS.successBg, border: "1px solid #A7F3D0" }}>
              <span style={{ fontSize: 20, fontWeight: 700, color: COLORS.success }}>78</span>
              <div>
                <div style={{ fontSize: 10, color: COLORS.success, fontWeight: 600 }}>ATS SCORE</div>
                <div style={{ fontSize: 10, color: COLORS.successMid }}>out of 100</div>
              </div>
            </div>
          </div>
          <div style={{ padding: 16, overflowY: "auto", maxHeight: 320 }}>
            <div style={{ marginBottom: 10 }}>
              <div style={{ fontSize: 13.5, fontWeight: 600, color: COLORS.text }}>Staff Frontend Engineer</div>
              <div style={{ fontSize: 12, color: COLORS.textMuted, marginTop: 2 }}>
                Razorpay · Bengaluru · ₹40–55 LPA
                <Badge variant="linkedin" size="xs" style={{ marginLeft: 6 } as React.CSSProperties}>LinkedIn</Badge>
              </div>
            </div>
            <div style={{ fontSize: 12.5, color: COLORS.text, lineHeight: 1.8 }}>
              We are seeking a <strong style={{ background: "#D1FAE5", padding: "1px 3px", borderRadius: 2 }}>Staff Frontend Engineer</strong> to lead architecture decisions. Build scalable systems using <strong style={{ background: "#D1FAE5", padding: "1px 3px", borderRadius: 2 }}>React</strong>, <strong style={{ background: "#D1FAE5", padding: "1px 3px", borderRadius: 2 }}>TypeScript</strong>, and <strong style={{ background: "#D1FAE5", padding: "1px 3px", borderRadius: 2 }}>GraphQL</strong>. Experience with <strong style={{ background: "#FEF3C7", padding: "1px 3px", borderRadius: 2 }}>Kubernetes</strong> and platform engineering is a plus. You should have built <strong style={{ background: "#D1FAE5", padding: "1px 3px", borderRadius: 2 }}>component libraries</strong> and driven <strong style={{ background: "#D1FAE5", padding: "1px 3px", borderRadius: 2 }}>performance optimization</strong> initiatives.
            </div>
            <div style={{ marginTop: 12, padding: 10, borderRadius: 6, background: COLORS.warningBg, border: "1px solid #FDE68A" }}>
              <div style={{ fontSize: 12, color: COLORS.warning, fontWeight: 500, display: "flex", alignItems: "center", gap: 5 }}>
                <Icon name="lightbulb" size={12} color={COLORS.warning} /> Adding Kubernetes and Go experience could push this score to 91+
              </div>
            </div>
          </div>
        </Card>
      </div>

      {/* Gap analysis */}
      <div style={{ padding: "12px 28px 28px" }}>
        <Card>
          <div style={{ padding: "14px 16px", borderBottom: `1px solid ${COLORS.borderLight}` }}>
            <span style={{ fontSize: 13.5, fontWeight: 600, color: COLORS.text }}>Keyword Gap Analysis</span>
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 0 }}>
            <div style={{ padding: 16, borderRight: `1px solid ${COLORS.borderLight}` }}>
              <div style={{ fontSize: 12, fontWeight: 600, color: COLORS.success, marginBottom: 10, display: "flex", alignItems: "center", gap: 5 }}>
                <Icon name="check" size={12} color={COLORS.success} /> Matched Keywords ({EXAMPLE_MATCHED.length})
              </div>
              <div style={{ display: "flex", flexWrap: "wrap", gap: 5 }}>
                {EXAMPLE_MATCHED.map((k, i) => (
                  <span key={i} style={{ fontSize: 12, padding: "3px 8px", borderRadius: 4, background: COLORS.successBg, color: COLORS.success, border: "1px solid #A7F3D0" }}>{k}</span>
                ))}
              </div>
            </div>
            <div style={{ padding: 16 }}>
              <div style={{ fontSize: 12, fontWeight: 600, color: COLORS.warning, marginBottom: 10, display: "flex", alignItems: "center", gap: 5 }}>
                <Icon name="alert-triangle" size={12} color={COLORS.warning} /> Missing Keywords ({EXAMPLE_MISSING.length})
              </div>
              <div style={{ display: "flex", flexWrap: "wrap", gap: 5, marginBottom: 12 }}>
                {EXAMPLE_MISSING.map((k, i) => (
                  <span key={i} style={{ fontSize: 12, padding: "3px 8px", borderRadius: 4, background: COLORS.warningBg, color: COLORS.warning, border: "1px solid #FDE68A" }}>{k}</span>
                ))}
              </div>
              <div style={{ padding: 10, borderRadius: 6, background: COLORS.bg, border: `1px solid ${COLORS.border}` }}>
                <div style={{ fontSize: 12, fontWeight: 600, color: COLORS.text, marginBottom: 4 }}>Suggested rewrite:</div>
                <div style={{ fontSize: 12, color: COLORS.textMuted, lineHeight: 1.7 }}>
                  <span style={{ color: COLORS.dangerMid, textDecoration: "line-through" }}>Led migration of legacy codebase…</span>{" "}
                  <span style={{ color: COLORS.success }}>→ "Architected platform-level frontend systems deployed on Kubernetes, coordinating with Go microservices via gRPC…"</span>
                </div>
              </div>
            </div>
          </div>
        </Card>
      </div>

      {/* CTA */}
      <div style={{ margin: "0 28px 32px", padding: "24px 28px", borderRadius: 12, background: `linear-gradient(135deg, ${COLORS.brandLight} 0%, #EDE9FE 100%)`, border: `1px solid #C7D2FE`, display: "flex", alignItems: "center", justifyContent: "space-between", gap: 24 }}>
        <div>
          <div style={{ fontSize: 16, fontWeight: 700, color: COLORS.text, marginBottom: 6 }}>Ready to analyze your own resume?</div>
          <div style={{ fontSize: 13, color: COLORS.textMuted }}>Upload your resume and a job description to get your personalized ATS score in seconds.</div>
        </div>
        <button
          onClick={() => onNavigate?.("resume")}
          style={{ padding: "10px 24px", borderRadius: 8, border: "none", background: COLORS.brand, color: "#fff", fontSize: 14, fontWeight: 600, cursor: "pointer", whiteSpace: "nowrap", display: "flex", alignItems: "center", gap: 8, flexShrink: 0 }}
        >
          <Icon name="upload" size={15} color="#fff" /> Upload My Resume
        </button>
      </div>
    </div>
  );
};
