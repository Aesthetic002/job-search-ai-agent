"use client";

import React, { useState, useRef } from "react";
import { COLORS, Icon, Card, EmptyState } from "./ui";
import { uploadResume, analyzeResume, runATSAnalysis } from "@/lib/api";
import type { ResumeFile, ATSResult } from "@/lib/types";

type Stage = "idle" | "uploading" | "parsed" | "analyzing" | "result" | "error";

function fmtSize(bytes: number) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export const ResumePage = () => {
  const [stage, setStage] = useState<Stage>("idle");
  const [resumeFile, setResumeFile] = useState<ResumeFile | null>(null);
  const [resumeId, setResumeId] = useState<string | null>(null);   // backend resume_id
  const [jdText, setJdText] = useState("");
  const [atsResult, setAtsResult] = useState<ATSResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [dragOver, setDragOver] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFile = async (file: File) => {
    const allowed = ["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"];
    if (!allowed.includes(file.type)) {
      setError("Only PDF and DOCX files are supported.");
      return;
    }
    if (file.size > 5 * 1024 * 1024) {
      setError("File must be under 5 MB.");
      return;
    }
    setError(null);
    setStage("uploading");
    const meta: ResumeFile = {
      id: crypto.randomUUID(),
      name: file.name,
      sizeBytes: file.size,
      uploadedAt: new Date().toISOString(),
      status: "uploading",
    };
    setResumeFile(meta);
    try {
      const { resumeId: rid } = await uploadResume(file);
      setResumeId(rid);
      setResumeFile({ ...meta, status: "ready" });
      setStage("parsed");
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : "Upload failed.";
      setError(msg);
      setResumeFile({ ...meta, status: "error" });
      setStage("error");
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files[0];
    if (file) handleFile(file);
  };

  const handleAnalyze = async () => {
    if (!jdText.trim() || !resumeId) return;
    setStage("analyzing");
    setError(null);
    try {
      // Step 1: Run AI structured extraction (saves to Firestore)
      await analyzeResume(resumeId);
      // Step 2: Score resume against the pasted JD
      const result = await runATSAnalysis(resumeId, jdText);
      setAtsResult(result);
      setStage("result");
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : "Analysis failed.";
      setError(msg);
      setStage("error");
    }
  };

  const reset = () => {
    setStage("idle");
    setResumeFile(null);
    setResumeId(null);
    setJdText("");
    setAtsResult(null);
    setError(null);
  };

  return (
    <div style={{ flex: 1, display: "flex", flexDirection: "column", background: COLORS.bg, minHeight: "100vh" }}>
      <div style={{ padding: "20px 28px 0" }}>
        <h1 style={{ fontSize: 18, fontWeight: 600, color: COLORS.text, margin: 0 }}>Resume & ATS Analysis</h1>
        <p style={{ fontSize: 13, color: COLORS.textMuted, margin: "4px 0 0" }}>
          Upload your resume and paste a job description to get your ATS match score and keyword gaps.
        </p>
      </div>

      <div style={{ padding: "20px 28px 0", display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
        {/* Upload card */}
        <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
          <div style={{ fontSize: 13, fontWeight: 600, color: COLORS.text }}>Step 1 — Upload Resume</div>

          {stage === "idle" || stage === "error" ? (
            <Card
              style={{
                border: `1.5px dashed ${dragOver ? COLORS.brand : COLORS.border}`,
                background: dragOver ? COLORS.brandLight : COLORS.card,
                padding: 32,
                textAlign: "center",
                cursor: "pointer",
                transition: "all 0.15s",
              }}
              onDragOver={(e: React.DragEvent) => { e.preventDefault(); setDragOver(true); }}
              onDragLeave={() => setDragOver(false)}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
            >
              <input
                ref={fileInputRef}
                type="file"
                accept=".pdf,.docx"
                style={{ display: "none" }}
                onChange={(e) => { const f = e.target.files?.[0]; if (f) handleFile(f); }}
              />
              <Icon name="upload" size={32} color={dragOver ? COLORS.brand : COLORS.textLight} style={{ marginBottom: 12 }} />
              <div style={{ fontSize: 14, fontWeight: 500, color: COLORS.text, marginBottom: 4 }}>
                Drop your resume here
              </div>
              <div style={{ fontSize: 12, color: COLORS.textMuted, marginBottom: 16 }}>
                Supports PDF and DOCX · max 5 MB
              </div>
              <button
                style={{ padding: "8px 20px", borderRadius: 6, border: "none", background: COLORS.brand, color: "#fff", fontSize: 13, fontWeight: 500, cursor: "pointer" }}
                onClick={(e) => { e.stopPropagation(); fileInputRef.current?.click(); }}
              >
                Browse Files
              </button>
              {error && (
                <div style={{ marginTop: 14, fontSize: 12, color: COLORS.dangerMid, fontWeight: 500 }}>
                  {error}
                </div>
              )}
            </Card>
          ) : (
            <Card style={{ padding: "14px 16px" }}>
              <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                <div style={{ width: 36, height: 36, borderRadius: 6, background: COLORS.brandLight, display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
                  <Icon name="file-text" size={16} color={COLORS.brand} />
                </div>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ fontSize: 13, fontWeight: 500, color: COLORS.text, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
                    {resumeFile?.name}
                  </div>
                  <div style={{ fontSize: 11, color: COLORS.textMuted }}>
                    {resumeFile ? fmtSize(resumeFile.sizeBytes) : ""} · {stage === "uploading" ? "Uploading…" : "Uploaded"}
                  </div>
                </div>
                <div style={{ display: "flex", alignItems: "center", gap: 8, flexShrink: 0 }}>
                  {stage === "uploading" ? (
                    <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
                      <Icon name="refresh-cw" size={13} color={COLORS.textMuted} style={{ animation: "spin 1s linear infinite" }} />
                      <span style={{ fontSize: 12, color: COLORS.textMuted }}>Parsing…</span>
                    </div>
                  ) : (
                    <span style={{ fontSize: 12, color: COLORS.success, fontWeight: 500 }}>
                      <Icon name="check" size={13} color={COLORS.success} style={{ verticalAlign: "middle", marginRight: 3 }} />
                      Parsed
                    </span>
                  )}
                  <button
                    onClick={reset}
                    style={{ padding: "4px 10px", borderRadius: 5, border: `1px solid ${COLORS.border}`, background: COLORS.bg, fontSize: 12, color: COLORS.textMuted, cursor: "pointer" }}
                  >
                    Replace
                  </button>
                </div>
              </div>

              {stage === "uploading" && (
                <div style={{ marginTop: 10, height: 3, borderRadius: 2, background: COLORS.borderLight, overflow: "hidden" }}>
                  <div style={{ height: "100%", background: COLORS.brand, borderRadius: 2, width: "60%", animation: "pulse 1.2s ease-in-out infinite" }} />
                </div>
              )}

            </Card>
          )}
        </div>

        {/* JD input */}
        <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
          <div style={{ fontSize: 13, fontWeight: 600, color: COLORS.text }}>Step 2 — Paste Job Description</div>
          <Card style={{ padding: 0, flex: 1, display: "flex", flexDirection: "column", overflow: "hidden" }}>
            <textarea
              value={jdText}
              onChange={(e) => setJdText(e.target.value)}
              placeholder="Paste the full job description here. The AI will compare it against your resume to identify matching and missing keywords…"
              style={{
                flex: 1,
                width: "100%",
                minHeight: 220,
                padding: "14px 16px",
                border: "none",
                outline: "none",
                fontSize: 13,
                color: COLORS.text,
                lineHeight: 1.7,
                resize: "vertical",
                fontFamily: "inherit",
                background: "transparent",
                boxSizing: "border-box",
              }}
            />
            <div style={{ padding: "8px 16px", borderTop: `1px solid ${COLORS.borderLight}`, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <span style={{ fontSize: 11, color: COLORS.textLight }}>
                {jdText.trim().split(/\s+/).filter(Boolean).length} words
              </span>
              <button
                onClick={handleAnalyze}
              disabled={!jdText.trim() || stage !== "parsed" || !resumeId}
                style={{
                  padding: "7px 18px",
                  borderRadius: 6,
                  border: "none",
                  background: jdText.trim() && stage === "parsed" ? COLORS.brand : COLORS.borderLight,
                  fontSize: 13,
                  color: jdText.trim() && stage === "parsed" ? "#fff" : COLORS.textLight,
                  fontWeight: 500,
                  cursor: jdText.trim() && stage === "parsed" ? "pointer" : "default",
                  display: "flex",
                  alignItems: "center",
                  gap: 6,
                }}
              >
                {stage === "analyzing" ? (
                  <><Icon name="refresh-cw" size={13} color="#fff" style={{ animation: "spin 1s linear infinite" }} /> Analyzing…</>
                ) : (
                  <><Icon name="zap" size={13} color={jdText.trim() && stage === "parsed" ? "#fff" : COLORS.textLight} /> Run ATS Analysis</>
                )}
              </button>
            </div>
          </Card>
        </div>
      </div>

      {/* Results */}
      <div style={{ padding: "20px 28px 28px" }}>
        {stage === "result" && atsResult ? (
          <Card>
            <div style={{ padding: "14px 16px", borderBottom: `1px solid ${COLORS.borderLight}`, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <span style={{ fontSize: 13.5, fontWeight: 600, color: COLORS.text }}>ATS Analysis Results</span>
              <div style={{ display: "flex", alignItems: "center", gap: 8, padding: "5px 12px", borderRadius: 6, background: COLORS.successBg, border: `1px solid #A7F3D0` }}>
                <span style={{ fontSize: 20, fontWeight: 700, color: COLORS.success }}>{atsResult.score}</span>
                <div>
                  <div style={{ fontSize: 10, color: COLORS.success, fontWeight: 600 }}>ATS SCORE</div>
                  <div style={{ fontSize: 10, color: COLORS.successMid }}>out of 100</div>
                </div>
              </div>
            </div>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 0 }}>
              <div style={{ padding: 16, borderRight: `1px solid ${COLORS.borderLight}` }}>
                <div style={{ fontSize: 12, fontWeight: 600, color: COLORS.success, marginBottom: 10, display: "flex", alignItems: "center", gap: 5 }}>
                  <Icon name="check" size={12} color={COLORS.success} /> Matched Keywords ({atsResult.matchedKeywords.length})
                </div>
                <div style={{ display: "flex", flexWrap: "wrap", gap: 5 }}>
                  {atsResult.matchedKeywords.map((k, i) => (
                    <span key={i} style={{ fontSize: 12, padding: "3px 8px", borderRadius: 4, background: COLORS.successBg, color: COLORS.success, border: "1px solid #A7F3D0" }}>{k}</span>
                  ))}
                </div>
              </div>
              <div style={{ padding: 16 }}>
                <div style={{ fontSize: 12, fontWeight: 600, color: COLORS.warning, marginBottom: 10, display: "flex", alignItems: "center", gap: 5 }}>
                  <Icon name="alert-triangle" size={12} color={COLORS.warning} /> Missing Keywords ({atsResult.missingKeywords.length})
                </div>
                <div style={{ display: "flex", flexWrap: "wrap", gap: 5 }}>
                  {atsResult.missingKeywords.map((k, i) => (
                    <span key={i} style={{ fontSize: 12, padding: "3px 8px", borderRadius: 4, background: COLORS.warningBg, color: COLORS.warning, border: "1px solid #FDE68A" }}>{k}</span>
                  ))}
                </div>
              </div>
            </div>
            {atsResult.courseRecommendations && atsResult.courseRecommendations.length > 0 && (
              <div style={{ padding: "16px", borderTop: `1px solid ${COLORS.borderLight}` }}>
                <div style={{ fontSize: 13, fontWeight: 600, color: COLORS.brand, marginBottom: 8, display: "flex", alignItems: "center", gap: 6 }}>
                  <Icon name="book-open" size={14} color={COLORS.brand} /> Course Recommendations to Fill Gaps
                </div>
                <ul style={{ margin: 0, paddingLeft: 20, fontSize: 13, color: COLORS.text, lineHeight: 1.6 }}>
                  {atsResult.courseRecommendations.map((course, i) => (
                    <li key={i}>{course}</li>
                  ))}
                </ul>
              </div>
            )}
          </Card>
        ) : stage !== "result" ? (
          <Card style={{ background: COLORS.borderLight, border: "none" }}>
            <EmptyState
              icon="target"
              title="ATS results will appear here"
              description="Upload your resume and paste a job description, then click 'Run ATS Analysis' to see your keyword match score and improvement tips."
            />
          </Card>
        ) : null}
      </div>

      <style>{`
        @keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
        @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
      `}</style>
    </div>
  );
};
