"use client";

import React, { useState } from "react";
import { COLORS, Icon, Card, EmptyState } from "./ui";
import { fetchInterviewQuestions, evaluateAnswer } from "@/lib/api";
import type { RoundType, InterviewQuestion, InterviewEvaluation } from "@/lib/types";
import { NegotiationChat } from "./NegotiationChat";

const ROUND_TYPES: { value: RoundType; label: string; desc: string; icon: string }[] = [
  { value: "behavioral", label: "Behavioral", desc: "Situational & competency questions (STAR method)", icon: "user" },
  { value: "technical", label: "Technical", desc: "Coding, problem-solving, and system concepts", icon: "cpu" },
  { value: "system-design", label: "System Design", desc: "Architecture, scalability, and trade-offs", icon: "layers" },
  { value: "hr", label: "HR / Culture Fit", desc: "Salary, career goals, and company values", icon: "globe" },
  { value: "negotiation", label: "Salary Negotiation", desc: "Practice negotiating offers with an AI HR Recruiter", icon: "message-square" },
];

type SessionStage = "setup" | "loading" | "session" | "evaluated" | "complete";

export const InterviewPage = () => {
  // Setup
  const [jobTitle, setJobTitle] = useState("");
  const [company, setCompany] = useState("");
  const [roundType, setRoundType] = useState<RoundType>("behavioral");
  const [targetSalaryLpa, setTargetSalaryLpa] = useState<number>(25);

  // Session
  const [stage, setStage] = useState<SessionStage>("setup");
  const [questions, setQuestions] = useState<InterviewQuestion[]>([]);
  const [currentIdx, setCurrentIdx] = useState(0);
  const [answer, setAnswer] = useState("");
  const [evaluating, setEvaluating] = useState(false);
  const [evaluation, setEvaluation] = useState<InterviewEvaluation | null>(null);
  const [setupError, setSetupError] = useState<string | null>(null);

  const wordCount = answer.trim() ? answer.trim().split(/\s+/).length : 0;
  const currentQ = questions[currentIdx] ?? null;
  const isLastQ = currentIdx >= questions.length - 1;

  const handleStart = async () => {
    if (!jobTitle.trim()) { setSetupError("Please enter the job title."); return; }
    setSetupError(null);
    setStage("loading");
    
    if (roundType === "negotiation") {
      setStage("session");
      return;
    }

    try {
      const qs = await fetchInterviewQuestions(roundType, jobTitle.trim());
      setQuestions(qs);
      setCurrentIdx(0);
      setAnswer("");
      setEvaluation(null);
      setStage("session");
    } catch (e: unknown) {
      setSetupError(e instanceof Error ? e.message : "Failed to load questions.");
      setStage("setup");
    }
  };

  const handleEvaluate = async () => {
    if (!answer.trim() || !currentQ) return;
    setEvaluating(true);
    try {
      const ev = await evaluateAnswer(
        currentQ.id,
        answer,
        jobTitle,
        currentQ.text,                    // pass full question text to backend
        currentQ.category,                // pass category for STAR check
        currentQ.keyPoints,               // pass expected_topics for gap analysis
      );
      setEvaluation(ev);
      setStage("evaluated");
    } catch (e: unknown) {
      // Show a helpful message if the backend is down
      setEvaluation({
        questionId: currentQ.id,
        score: 0,
        strengths: [],
        improvements: ["Connect to the AI backend to get real evaluation."],
        suggestedAnswer:
          e instanceof Error && e.message.includes("503")
            ? "Interview Service is not running. Start it with: uvicorn backend.interview_service.main:app --port 8004"
            : "The AI evaluation endpoint is not yet reachable. Ensure all microservices are running.",
      });
      setStage("evaluated");
    } finally {
      setEvaluating(false);
    }
  };

  const handleNext = () => {
    if (isLastQ) {
      setStage("complete");
    } else {
      setCurrentIdx((i) => i + 1);
      setAnswer("");
      setEvaluation(null);
      setStage("session");
    }
  };

  const handleReset = () => {
    setStage("setup");
    setJobTitle("");
    setCompany("");
    setRoundType("behavioral");
    setQuestions([]);
    setCurrentIdx(0);
    setAnswer("");
    setEvaluation(null);
    setSetupError(null);
  };

  // ─── SETUP SCREEN ─────────────────────────────────────────────────────────
  if (stage === "setup") {
    return (
      <div style={{ flex: 1, display: "flex", flexDirection: "column", background: COLORS.bg, minHeight: "100vh" }}>
        <div style={{ padding: "20px 28px 0" }}>
          <h1 style={{ fontSize: 18, fontWeight: 600, color: COLORS.text, margin: 0 }}>Mock Interview</h1>
          <p style={{ fontSize: 13, color: COLORS.textMuted, margin: "4px 0 0" }}>
            Practice with AI-generated questions tailored to your target role
          </p>
        </div>
        <div style={{ flex: 1, display: "flex", alignItems: "center", justifyContent: "center", padding: "24px 28px 48px" }}>
          <Card style={{ width: "100%", maxWidth: 600, padding: 32 }}>
            <div style={{ fontSize: 16, fontWeight: 600, color: COLORS.text, marginBottom: 24 }}>
              Set up your session
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16, marginBottom: 20 }}>
              <div>
                <label style={{ fontSize: 12, fontWeight: 500, color: COLORS.textMuted, display: "block", marginBottom: 6 }}>
                  Target Role *
                </label>
                <input
                  value={jobTitle}
                  onChange={(e) => setJobTitle(e.target.value)}
                  placeholder="e.g. Staff Frontend Engineer"
                  style={{ width: "100%", padding: "9px 12px", borderRadius: 6, border: `1px solid ${COLORS.border}`, fontSize: 13, color: COLORS.text, outline: "none", boxSizing: "border-box" }}
                />
              </div>
              <div>
                <label style={{ fontSize: 12, fontWeight: 500, color: COLORS.textMuted, display: "block", marginBottom: 6 }}>
                  Company (optional)
                </label>
                <input
                  value={company}
                  onChange={(e) => setCompany(e.target.value)}
                  placeholder="e.g. Razorpay"
                  style={{ width: "100%", padding: "9px 12px", borderRadius: 6, border: `1px solid ${COLORS.border}`, fontSize: 13, color: COLORS.text, outline: "none", boxSizing: "border-box" }}
                />
              </div>
            </div>

            <div style={{ marginBottom: 24 }}>
              <label style={{ fontSize: 12, fontWeight: 500, color: COLORS.textMuted, display: "block", marginBottom: 8 }}>
                Round Type
              </label>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8 }}>
                {ROUND_TYPES.map((r) => (
                  <button
                    key={r.value}
                    onClick={() => setRoundType(r.value)}
                    style={{
                      padding: "12px 14px",
                      borderRadius: 8,
                      border: `1.5px solid ${roundType === r.value ? COLORS.brand : COLORS.border}`,
                      background: roundType === r.value ? COLORS.brandLight : COLORS.card,
                      cursor: "pointer",
                      textAlign: "left",
                      transition: "all 0.12s",
                    }}
                  >
                    <div style={{ display: "flex", alignItems: "center", gap: 7, marginBottom: 4 }}>
                      <Icon name={r.icon} size={14} color={roundType === r.value ? COLORS.brand : COLORS.textMuted} />
                      <span style={{ fontSize: 13, fontWeight: 600, color: roundType === r.value ? COLORS.brand : COLORS.text }}>{r.label}</span>
                    </div>
                    <div style={{ fontSize: 11.5, color: COLORS.textMuted, lineHeight: 1.4 }}>{r.desc}</div>
                  </button>
                ))}
              </div>
            </div>

            {roundType === "negotiation" && (
              <div style={{ marginBottom: 24 }}>
                <label style={{ fontSize: 12, fontWeight: 500, color: COLORS.textMuted, display: "block", marginBottom: 6 }}>
                  Target Salary (LPA) *
                </label>
                <input
                  type="number"
                  value={targetSalaryLpa}
                  onChange={(e) => setTargetSalaryLpa(parseFloat(e.target.value) || 0)}
                  placeholder="e.g. 25"
                  min={1}
                  style={{ width: "100%", padding: "9px 12px", borderRadius: 6, border: `1px solid ${COLORS.border}`, fontSize: 13, color: COLORS.text, outline: "none", boxSizing: "border-box" }}
                />
              </div>
            )}

            {setupError && (
              <div style={{ marginBottom: 16, padding: "8px 12px", borderRadius: 6, background: COLORS.dangerBg, border: `1px solid #FECACA`, fontSize: 12, color: COLORS.danger }}>
                {setupError}
              </div>
            )}

            <button
              onClick={handleStart}
              style={{ width: "100%", padding: "10px", borderRadius: 6, border: "none", background: COLORS.brand, color: "#fff", fontSize: 14, fontWeight: 600, cursor: "pointer", display: "flex", alignItems: "center", justifyContent: "center", gap: 8 }}
            >
              <Icon name="play" size={15} color="#fff" /> Start Session
            </button>
          </Card>
        </div>
      </div>
    );
  }

  // ─── LOADING ──────────────────────────────────────────────────────────────
  if (stage === "loading") {
    return (
      <div style={{ flex: 1, display: "flex", alignItems: "center", justifyContent: "center", background: COLORS.bg }}>
        <div style={{ textAlign: "center" }}>
          <Icon name="refresh-cw" size={28} color={COLORS.brand} style={{ animation: "spin 1s linear infinite", marginBottom: 16 }} />
          <div style={{ fontSize: 14, color: COLORS.textMuted }}>Preparing your interview...</div>
        </div>
        <style>{`@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }`}</style>
      </div>
    );
  }

  // ─── COMPLETE ─────────────────────────────────────────────────────────────
  if (stage === "complete") {
    return (
      <div style={{ flex: 1, display: "flex", alignItems: "center", justifyContent: "center", background: COLORS.bg }}>
        <Card style={{ maxWidth: 460, width: "100%", padding: 40, textAlign: "center" }}>
          <div style={{ width: 56, height: 56, borderRadius: "50%", background: COLORS.successBg, display: "flex", alignItems: "center", justifyContent: "center", margin: "0 auto 20px" }}>
            <Icon name="award" size={24} color={COLORS.successMid} />
          </div>
          <div style={{ fontSize: 18, fontWeight: 700, color: COLORS.text, marginBottom: 8 }}>Session Complete</div>
          <div style={{ fontSize: 13, color: COLORS.textMuted, marginBottom: 24, lineHeight: 1.7 }}>
            You completed the session for the {jobTitle} role.
          </div>
          <button onClick={handleReset} style={{ padding: "10px 24px", borderRadius: 6, border: "none", background: COLORS.brand, color: "#fff", fontSize: 13, fontWeight: 500, cursor: "pointer" }}>
            Start New Session
          </button>
        </Card>
      </div>
    );
  }

  // ─── SESSION: NEGOTIATION ─────────────────────────────────────────────────
  if (roundType === "negotiation") {
    return (
      <div style={{ flex: 1, display: "flex", flexDirection: "column", background: COLORS.bg, minHeight: "100vh" }}>
        <div style={{ padding: "20px 28px 14px", borderBottom: `1px solid ${COLORS.border}`, background: COLORS.card, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 3 }}>
              <div style={{ padding: "3px 8px", borderRadius: 4, background: COLORS.brandLight, border: "1px solid #C7D2FE" }}>
                <span style={{ fontSize: 11, fontWeight: 600, color: COLORS.brand, display: "flex", alignItems: "center", gap: 4 }}>
                  <span style={{ width: 6, height: 6, borderRadius: "50%", background: COLORS.brand, display: "inline-block", animation: "pulse 1.5s ease infinite" }} />
                  LIVE NEGOTIATION
                </span>
              </div>
              <span style={{ fontSize: 12, color: COLORS.textMuted }}>
                {jobTitle}{company ? ` @ ${company}` : ""}
              </span>
            </div>
            <h1 style={{ fontSize: 16, fontWeight: 600, color: COLORS.text, margin: 0 }}>
              Offer Negotiation
            </h1>
          </div>
          <button onClick={handleReset} style={{ padding: "7px 14px", borderRadius: 6, border: "none", background: COLORS.dangerBg, fontSize: 13, color: COLORS.danger, fontWeight: 500, cursor: "pointer" }}>
            End Session
          </button>
        </div>
        <div style={{ padding: "24px 28px", maxWidth: 800, margin: "0 auto", width: "100%" }}>
          <NegotiationChat jobTitle={jobTitle} targetSalaryLpa={targetSalaryLpa} />
        </div>
        <style>{`@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.4; } }`}</style>
      </div>
    );
  }

  // ─── SESSION: REGULAR (No questions available yet) ────────────────────────
  if (!currentQ) {
    return (
      <div style={{ flex: 1, display: "flex", alignItems: "center", justifyContent: "center", background: COLORS.bg }}>
        <Card style={{ maxWidth: 480, width: "100%", padding: 36 }}>
          <EmptyState
            icon="mic"
            title="No questions available"
            description="The AI question bank endpoint is not yet connected. Once the backend is wired up, questions tailored to your role will appear here."
            action={
              <button onClick={handleReset} style={{ padding: "8px 20px", borderRadius: 6, border: "none", background: COLORS.brand, color: "#fff", fontSize: 13, fontWeight: 500, cursor: "pointer" }}>
                Back to Setup
              </button>
            }
          />
        </Card>
      </div>
    );
  }

  // ─── LIVE SESSION ─────────────────────────────────────────────────────────
  return (
    <div style={{ flex: 1, display: "flex", flexDirection: "column", background: COLORS.bg, minHeight: "100vh" }}>
      {/* Session header */}
      <div style={{ padding: "20px 28px 14px", borderBottom: `1px solid ${COLORS.border}`, background: COLORS.card, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div>
          <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 3 }}>
            <div style={{ padding: "3px 8px", borderRadius: 4, background: COLORS.dangerBg, border: "1px solid #FECACA" }}>
              <span style={{ fontSize: 11, fontWeight: 600, color: COLORS.danger, display: "flex", alignItems: "center", gap: 4 }}>
                <span style={{ width: 6, height: 6, borderRadius: "50%", background: COLORS.dangerMid, display: "inline-block", animation: "pulse 1.5s ease infinite" }} />
                LIVE SESSION
              </span>
            </div>
            <span style={{ fontSize: 12, color: COLORS.textMuted }}>
              {jobTitle}{company ? ` @ ${company}` : ""} · {ROUND_TYPES.find((r) => r.value === roundType)?.label}
            </span>
          </div>
          <h1 style={{ fontSize: 16, fontWeight: 600, color: COLORS.text, margin: 0 }}>
            Mock Interview
          </h1>
        </div>
        <div style={{ display: "flex", gap: 8 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 5, padding: "6px 12px", borderRadius: 6, border: `1px solid ${COLORS.border}`, background: COLORS.card, fontSize: 12, color: COLORS.textMuted }}>
            <Icon name="clock" size={13} color={COLORS.textMuted} /> Q {currentIdx + 1} of {questions.length}
          </div>
          <button onClick={handleReset} style={{ padding: "7px 14px", borderRadius: 6, border: "none", background: COLORS.dangerBg, fontSize: 13, color: COLORS.danger, fontWeight: 500, cursor: "pointer" }}>
            End Session
          </button>
        </div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "360px 1fr", gap: 0, flex: 1 }}>
        {/* Left panel */}
        <div style={{ borderRight: `1px solid ${COLORS.border}`, background: COLORS.card, display: "flex", flexDirection: "column", padding: 24, gap: 20, overflowY: "auto" }}>
          <div>
            <div style={{ fontSize: 11, fontWeight: 600, color: COLORS.textLight, letterSpacing: "0.06em", marginBottom: 8, textTransform: "uppercase" }}>Current Question</div>
            <div style={{ fontSize: 15, fontWeight: 500, color: COLORS.text, lineHeight: 1.6, padding: 16, borderRadius: 8, background: COLORS.bg, border: `1px solid ${COLORS.border}` }}>
              "{currentQ.text}"
            </div>
          </div>

          {currentQ.keyPoints.length > 0 && (
            <div>
              <div style={{ fontSize: 11, fontWeight: 600, color: COLORS.textLight, letterSpacing: "0.06em", marginBottom: 10, textTransform: "uppercase" }}>Key Points to Address</div>
              <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
                {currentQ.keyPoints.map((pt, i) => (
                  <div key={i} style={{ display: "flex", gap: 9, alignItems: "flex-start" }}>
                    <div style={{ width: 16, height: 16, borderRadius: 4, border: `1.5px solid ${COLORS.border}`, flexShrink: 0, marginTop: 1, display: "flex", alignItems: "center", justifyContent: "center" }} />
                    <span style={{ fontSize: 12.5, color: COLORS.text, lineHeight: 1.5 }}>{pt}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {currentQ.tips.length > 0 && (
            <div>
              <div style={{ fontSize: 11, fontWeight: 600, color: COLORS.textLight, letterSpacing: "0.06em", marginBottom: 10, textTransform: "uppercase" }}>Coaching Tips</div>
              {currentQ.tips.map((tip, i) => (
                <div key={i} style={{ padding: 12, borderRadius: 6, background: COLORS.brandLight, border: "1px solid #C7D2FE", marginBottom: 8 }}>
                  <div style={{ fontSize: 12, color: COLORS.brand, lineHeight: 1.6 }}>{tip}</div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Right panel */}
        <div style={{ display: "flex", flexDirection: "column", padding: 24, gap: 16, overflowY: "auto" }}>
          <div>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 10 }}>
              <div style={{ fontSize: 13.5, fontWeight: 600, color: COLORS.text }}>Your Answer</div>
              <span style={{ fontSize: 12, color: wordCount > 300 ? COLORS.dangerMid : wordCount > 150 ? COLORS.successMid : COLORS.textLight }}>
                {wordCount} words {wordCount > 250 ? "· Getting long" : wordCount > 100 ? "· Good length" : "· Keep going"}
              </span>
            </div>
            <textarea
              value={answer}
              onChange={(e) => setAnswer(e.target.value)}
              placeholder="Type your answer here. Use the STAR method — Situation, Task, Action, Result…"
              disabled={stage === "evaluated"}
              style={{ width: "100%", minHeight: 180, padding: "14px 16px", borderRadius: 8, border: `1px solid ${COLORS.border}`, fontSize: 13.5, color: COLORS.text, lineHeight: 1.7, resize: "vertical", fontFamily: "inherit", background: stage === "evaluated" ? COLORS.borderLight : COLORS.card, boxSizing: "border-box" }}
            />
            <div style={{ marginTop: 6, height: 3, borderRadius: 2, background: COLORS.borderLight, overflow: "hidden" }}>
              <div style={{ height: "100%", borderRadius: 2, background: wordCount > 250 ? COLORS.warningMid : COLORS.brand, width: `${Math.min((wordCount / 300) * 100, 100)}%`, transition: "width 0.3s" }} />
            </div>
          </div>

          <div style={{ display: "flex", justifyContent: "flex-end", gap: 8 }}>
            {stage === "session" && (
              <>
                <button
                  onClick={handleNext}
                  style={{ padding: "8px 16px", borderRadius: 6, border: `1px solid ${COLORS.border}`, background: COLORS.card, fontSize: 13, color: COLORS.textMuted, cursor: "pointer" }}
                >
                  Skip
                </button>
                <button
                  onClick={handleEvaluate}
                  disabled={!answer.trim() || evaluating}
                  style={{ padding: "8px 20px", borderRadius: 6, border: "none", background: !answer.trim() ? COLORS.borderLight : COLORS.brand, fontSize: 13, color: !answer.trim() ? COLORS.textLight : "#fff", fontWeight: 500, cursor: answer.trim() ? "pointer" : "default", display: "flex", alignItems: "center", gap: 7 }}
                >
                  {evaluating
                    ? <><Icon name="refresh-cw" size={13} color="#fff" style={{ animation: "spin 1s linear infinite" }} /> Evaluating…</>
                    : <><Icon name="zap" size={13} color={!answer.trim() ? COLORS.textLight : "#fff"} /> Evaluate Answer</>
                  }
                </button>
              </>
            )}
            {stage === "evaluated" && (
              <button
                onClick={handleNext}
                style={{ padding: "8px 20px", borderRadius: 6, border: "none", background: COLORS.brand, fontSize: 13, color: "#fff", fontWeight: 500, cursor: "pointer", display: "flex", alignItems: "center", gap: 6 }}
              >
                {isLastQ ? "Finish Session" : "Next Question"} <Icon name="arrow-right" size={13} color="#fff" />
              </button>
            )}
          </div>

          {/* Evaluation result */}
          {stage === "evaluated" && evaluation && (
            <Card style={{ overflow: "hidden" }}>
              <div style={{ padding: "14px 16px", borderBottom: `1px solid ${COLORS.borderLight}`, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <span style={{ fontSize: 13.5, fontWeight: 600, color: COLORS.text }}>AI Evaluation</span>
                <div style={{ display: "flex", gap: 6 }}>
                  {evaluation.score > 0 && (
                    <span style={{ fontSize: 11, padding: "3px 8px", borderRadius: 4, background: COLORS.successBg, color: COLORS.success, fontWeight: 600, border: "1px solid #A7F3D0" }}>
                      Score: {evaluation.score}/100
                    </span>
                  )}
                  <span style={{ fontSize: 11, padding: "3px 8px", borderRadius: 4, background: COLORS.brandLight, color: COLORS.brand, fontWeight: 600 }}>
                    {ROUND_TYPES.find((r) => r.value === roundType)?.label}
                  </span>
                </div>
              </div>
              <div style={{ display: "grid", gridTemplateColumns: evaluation.strengths.length > 0 ? "1fr 1fr" : "1fr", gap: 0 }}>
                {evaluation.strengths.length > 0 && (
                  <div style={{ padding: 16, borderRight: `1px solid ${COLORS.borderLight}` }}>
                    <div style={{ fontSize: 12, fontWeight: 600, color: COLORS.success, marginBottom: 10, display: "flex", alignItems: "center", gap: 5 }}>
                      <Icon name="award" size={13} color={COLORS.success} /> Strengths
                    </div>
                    {evaluation.strengths.map((s, i) => (
                      <div key={i} style={{ display: "flex", gap: 7, marginBottom: 7 }}>
                        <Icon name="check" size={13} color={COLORS.successMid} style={{ flexShrink: 0, marginTop: 1 }} />
                        <span style={{ fontSize: 12.5, color: COLORS.text, lineHeight: 1.5 }}>{s}</span>
                      </div>
                    ))}
                  </div>
                )}
                <div style={{ padding: 16 }}>
                  <div style={{ fontSize: 12, fontWeight: 600, color: COLORS.brand, marginBottom: 10, display: "flex", alignItems: "center", gap: 5 }}>
                    <Icon name="message-square" size={13} color={COLORS.brand} /> Suggested Rewrite
                  </div>
                  <div style={{ fontSize: 12, color: COLORS.text, lineHeight: 1.7, padding: 10, borderRadius: 6, background: COLORS.bg, border: `1px solid ${COLORS.border}` }}>
                    {evaluation.suggestedAnswer}
                  </div>
                </div>
              </div>
            </Card>
          )}
        </div>
      </div>

      <style>{`
        @keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
        @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.4; } }
      `}</style>
    </div>
  );
};
