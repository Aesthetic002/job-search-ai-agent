"use client";

import React, { useState, useRef } from "react";
import { COLORS, Icon } from "./ui";

type UploadStage = "idle" | "uploading" | "parsing" | "done" | "error";

const STEPS = [
  { icon: "upload", label: "Upload Resume", active: true },
  { icon: "target", label: "ATS Analysis", active: false },
  { icon: "briefcase", label: "Job Matches", active: false },
];

function fmtSize(bytes: number) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export const OnboardingPage = ({
  onComplete,
  onSkip,
}: {
  onComplete: (fileName: string) => void;
  onSkip: () => void;
}) => {
  const [stage, setStage] = useState<UploadStage>("idle");
  const [fileName, setFileName] = useState("");
  const [fileSize, setFileSize] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [dragOver, setDragOver] = useState(false);
  const [progress, setProgress] = useState(0);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFile = async (file: File) => {
    const allowed = [
      "application/pdf",
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ];
    if (!allowed.includes(file.type)) {
      setError("Please upload a PDF or DOCX file.");
      return;
    }
    if (file.size > 5 * 1024 * 1024) {
      setError("File must be under 5 MB.");
      return;
    }

    setError(null);
    setFileName(file.name);
    setFileSize(file.size);
    setStage("uploading");
    setProgress(0);

    // Simulate upload progress
    const uploadInterval = setInterval(() => {
      setProgress((p) => {
        if (p >= 60) {
          clearInterval(uploadInterval);
          return 60;
        }
        return p + 12;
      });
    }, 150);

    try {
      // TODO: replace with real uploadResume(file) call
      // const { resumeId } = await uploadResume(file);
      await new Promise((r) => setTimeout(r, 900));
      clearInterval(uploadInterval);
      setProgress(60);

      // Simulate parsing
      setStage("parsing");
      const parseInterval = setInterval(() => {
        setProgress((p) => {
          if (p >= 100) {
            clearInterval(parseInterval);
            return 100;
          }
          return p + 10;
        });
      }, 120);

      await new Promise((r) => setTimeout(r, 1200));
      clearInterval(parseInterval);
      setProgress(100);
      setStage("done");

      await new Promise((r) => setTimeout(r, 600));
      onComplete(file.name);
    } catch {
      clearInterval(uploadInterval);
      setError("Upload failed. Please try again.");
      setStage("error");
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files[0];
    if (file) handleFile(file);
  };

  const isProcessing = stage === "uploading" || stage === "parsing";
  const isDone = stage === "done";

  return (
    <div
      style={{
        minHeight: "100vh",
        background: COLORS.bg,
        display: "flex",
        flexDirection: "column",
        fontFamily: "'Instrument Sans', 'Inter', sans-serif",
      }}
    >
      {/* Top bar */}
      <div
        style={{
          padding: "18px 32px",
          borderBottom: `1px solid ${COLORS.border}`,
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          background: COLORS.card,
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <div
            style={{
              width: 30,
              height: 30,
              borderRadius: 7,
              background: COLORS.brand,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            <Icon name="cpu" size={14} color="#fff" />
          </div>
          <span
            style={{ fontSize: 15, fontWeight: 700, color: COLORS.text, letterSpacing: "-0.2px" }}
          >
            Job Search AI
          </span>
        </div>

        <button
          onClick={onSkip}
          style={{
            padding: "6px 14px",
            borderRadius: 6,
            border: `1px solid ${COLORS.border}`,
            background: "transparent",
            fontSize: 13,
            color: COLORS.textMuted,
            cursor: "pointer",
            fontWeight: 500,
          }}
        >
          Skip for now
        </button>
      </div>

      {/* Progress steps */}
      <div
        style={{
          padding: "20px 32px 0",
          display: "flex",
          justifyContent: "center",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 0 }}>
          {STEPS.map((step, i) => (
            <React.Fragment key={i}>
              <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                <div
                  style={{
                    width: 28,
                    height: 28,
                    borderRadius: "50%",
                    background: i === 0 ? COLORS.brand : COLORS.borderLight,
                    border: `2px solid ${i === 0 ? COLORS.brand : COLORS.border}`,
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                  }}
                >
                  <Icon
                    name={step.icon}
                    size={13}
                    color={i === 0 ? "#fff" : COLORS.textLight}
                  />
                </div>
                <span
                  style={{
                    fontSize: 12,
                    fontWeight: i === 0 ? 600 : 400,
                    color: i === 0 ? COLORS.text : COLORS.textLight,
                  }}
                >
                  {step.label}
                </span>
              </div>
              {i < STEPS.length - 1 && (
                <div
                  style={{
                    width: 48,
                    height: 1,
                    background: COLORS.border,
                    margin: "0 10px",
                  }}
                />
              )}
            </React.Fragment>
          ))}
        </div>
      </div>

      {/* Main content */}
      <div
        style={{
          flex: 1,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          padding: "32px 24px 48px",
        }}
      >
        <div style={{ width: "100%", maxWidth: 560 }}>
          {/* Heading */}
          <div style={{ textAlign: "center", marginBottom: 32 }}>
            <h1
              style={{
                fontSize: 28,
                fontWeight: 800,
                color: COLORS.text,
                margin: "0 0 12px",
                letterSpacing: "-0.5px",
                lineHeight: 1.2,
              }}
            >
              Start by uploading your resume
            </h1>
            <p
              style={{
                fontSize: 14,
                color: COLORS.textMuted,
                margin: 0,
                lineHeight: 1.7,
                maxWidth: 420,
                marginLeft: "auto",
                marginRight: "auto",
              }}
            >
              We'll parse your skills and experience to match you with the right
              jobs and give you an instant ATS score on any role you apply to.
            </p>
          </div>

          {/* Upload card */}
          {stage === "idle" || stage === "error" ? (
            <div
              onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
              onDragLeave={() => setDragOver(false)}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
              style={{
                border: `2px dashed ${dragOver ? COLORS.brand : COLORS.border}`,
                borderRadius: 16,
                background: dragOver ? COLORS.brandLight : COLORS.card,
                padding: "52px 32px",
                textAlign: "center",
                cursor: "pointer",
                transition: "all 0.15s",
                boxShadow: "0 1px 4px rgba(0,0,0,0.04)",
              }}
            >
              <input
                ref={fileInputRef}
                type="file"
                accept=".pdf,.docx"
                style={{ display: "none" }}
                onChange={(e) => {
                  const f = e.target.files?.[0];
                  if (f) handleFile(f);
                }}
              />
              <div
                style={{
                  width: 64,
                  height: 64,
                  borderRadius: 16,
                  background: dragOver ? COLORS.brand : COLORS.brandLight,
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  margin: "0 auto 20px",
                  transition: "all 0.15s",
                }}
              >
                <Icon
                  name="upload"
                  size={28}
                  color={dragOver ? "#fff" : COLORS.brand}
                />
              </div>

              <div
                style={{
                  fontSize: 16,
                  fontWeight: 700,
                  color: COLORS.text,
                  marginBottom: 8,
                }}
              >
                {dragOver ? "Drop it here" : "Drag & drop your resume"}
              </div>
              <div
                style={{
                  fontSize: 13,
                  color: COLORS.textMuted,
                  marginBottom: 24,
                  lineHeight: 1.6,
                }}
              >
                PDF or DOCX · Max 5 MB
              </div>

              <button
                onClick={(e) => {
                  e.stopPropagation();
                  fileInputRef.current?.click();
                }}
                style={{
                  padding: "11px 28px",
                  borderRadius: 8,
                  border: "none",
                  background: COLORS.brand,
                  color: "#fff",
                  fontSize: 14,
                  fontWeight: 600,
                  cursor: "pointer",
                  display: "inline-flex",
                  alignItems: "center",
                  gap: 8,
                }}
              >
                <Icon name="upload" size={15} color="#fff" />
                Browse Files
              </button>

              {error && (
                <div
                  style={{
                    marginTop: 20,
                    padding: "10px 16px",
                    borderRadius: 8,
                    background: COLORS.dangerBg,
                    border: `1px solid #FECACA`,
                    fontSize: 13,
                    color: COLORS.danger,
                    fontWeight: 500,
                    display: "inline-flex",
                    alignItems: "center",
                    gap: 6,
                  }}
                >
                  <Icon name="alert-triangle" size={13} color={COLORS.danger} />
                  {error}
                </div>
              )}
            </div>
          ) : (
            /* Progress card */
            <div
              style={{
                borderRadius: 16,
                background: COLORS.card,
                border: `1px solid ${isDone ? COLORS.successMid : COLORS.border}`,
                padding: 32,
                boxShadow: isDone
                  ? `0 0 0 3px ${COLORS.successBg}`
                  : "0 1px 4px rgba(0,0,0,0.04)",
                transition: "all 0.3s",
              }}
            >
              {/* File info */}
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 14,
                  marginBottom: 24,
                }}
              >
                <div
                  style={{
                    width: 44,
                    height: 44,
                    borderRadius: 10,
                    background: isDone ? COLORS.successBg : COLORS.brandLight,
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    transition: "all 0.3s",
                    flexShrink: 0,
                  }}
                >
                  <Icon
                    name={isDone ? "check" : "file-text"}
                    size={20}
                    color={isDone ? COLORS.successMid : COLORS.brand}
                  />
                </div>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div
                    style={{
                      fontSize: 14,
                      fontWeight: 600,
                      color: COLORS.text,
                      whiteSpace: "nowrap",
                      overflow: "hidden",
                      textOverflow: "ellipsis",
                    }}
                  >
                    {fileName}
                  </div>
                  <div style={{ fontSize: 12, color: COLORS.textMuted, marginTop: 2 }}>
                    {fmtSize(fileSize)}
                  </div>
                </div>
                <div
                  style={{
                    fontSize: 13,
                    fontWeight: 600,
                    color: isDone ? COLORS.success : COLORS.brand,
                    flexShrink: 0,
                  }}
                >
                  {isDone ? "Ready" : `${progress}%`}
                </div>
              </div>

              {/* Progress bar */}
              <div
                style={{
                  height: 6,
                  borderRadius: 3,
                  background: COLORS.borderLight,
                  overflow: "hidden",
                  marginBottom: 16,
                }}
              >
                <div
                  style={{
                    height: "100%",
                    borderRadius: 3,
                    background: isDone ? COLORS.successMid : COLORS.brand,
                    width: `${progress}%`,
                    transition: "width 0.25s ease, background 0.3s",
                  }}
                />
              </div>

              {/* Status label */}
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  gap: 8,
                }}
              >
                {!isDone ? (
                  <>
                    <Icon
                      name="refresh-cw"
                      size={14}
                      color={COLORS.brand}
                      style={{ animation: "spin 1s linear infinite" }}
                    />
                    <span style={{ fontSize: 13, color: COLORS.textMuted }}>
                      {stage === "uploading"
                        ? "Uploading your resume…"
                        : "Parsing skills and experience…"}
                    </span>
                  </>
                ) : (
                  <>
                    <Icon name="check" size={14} color={COLORS.successMid} />
                    <span
                      style={{
                        fontSize: 13,
                        color: COLORS.success,
                        fontWeight: 600,
                      }}
                    >
                      Resume parsed successfully — taking you in…
                    </span>
                  </>
                )}
              </div>
            </div>
          )}

          {/* What happens next */}
          {(stage === "idle" || stage === "error") && (
            <div
              style={{
                marginTop: 32,
                display: "grid",
                gridTemplateColumns: "repeat(3, 1fr)",
                gap: 12,
              }}
            >
              {[
                {
                  icon: "target",
                  title: "Instant ATS Score",
                  desc: "See how your resume scores against any job description",
                },
                {
                  icon: "briefcase",
                  title: "Smart Job Matches",
                  desc: "Get job recommendations ranked by your match percentage",
                },
                {
                  icon: "mic",
                  title: "Interview Prep",
                  desc: "Practice role-specific questions with AI feedback",
                },
              ].map((f, i) => (
                <div
                  key={i}
                  style={{
                    padding: "16px 14px",
                    borderRadius: 10,
                    background: COLORS.card,
                    border: `1px solid ${COLORS.border}`,
                    textAlign: "center",
                  }}
                >
                  <div
                    style={{
                      width: 34,
                      height: 34,
                      borderRadius: 8,
                      background: COLORS.brandLight,
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      margin: "0 auto 10px",
                    }}
                  >
                    <Icon name={f.icon} size={15} color={COLORS.brand} />
                  </div>
                  <div
                    style={{
                      fontSize: 12,
                      fontWeight: 700,
                      color: COLORS.text,
                      marginBottom: 5,
                    }}
                  >
                    {f.title}
                  </div>
                  <div
                    style={{ fontSize: 11.5, color: COLORS.textMuted, lineHeight: 1.5 }}
                  >
                    {f.desc}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      <style>{`
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
};
