"use client";

import React, { useEffect, useState, useCallback } from "react";
import { COLORS, Icon, Badge, Card, EmptyState, Skeleton } from "./ui";
import {
  fetchApplications,
  createApplication,
  updateApplicationStage,
} from "@/lib/api";
import type { Application, ApplicationStage, JobSource } from "@/lib/types";

const STAGE_CONFIG: Record<
  ApplicationStage,
  { label: string; color: string; bg: string }
> = {
  applied: { label: "Applied", color: "#6366F1", bg: "#EEF2FF" },
  screening: { label: "Screening", color: "#F59E0B", bg: "#FFFBEB" },
  interviewing: { label: "Interviewing", color: "#8B5CF6", bg: "#F5F3FF" },
  offer: { label: "Offer", color: "#10B981", bg: "#ECFDF5" },
  rejected: { label: "Rejected", color: "#EF4444", bg: "#FEF2F2" },
  archived: { label: "Archived", color: "#94A3B8", bg: "#F1F5F9" },
};

const STAGE_ORDER: ApplicationStage[] = [
  "applied",
  "screening",
  "interviewing",
  "offer",
  "archived",
];

const SOURCES: JobSource[] = ["linkedin", "naukri", "indeed", "other"];

function sourceLabel(src: string) {
  if (src === "linkedin") return "LinkedIn";
  if (src === "naukri") return "Naukri";
  if (src === "indeed") return "Indeed";
  return src;
}

interface AddFormState {
  jobTitle: string;
  company: string;
  location: string;
  source: JobSource;
  url: string;
  notes: string;
}

const BLANK_FORM: AddFormState = {
  jobTitle: "",
  company: "",
  location: "",
  source: "linkedin",
  url: "",
  notes: "",
};

export const KanbanPage = () => {
  const [applications, setApplications] = useState<Application[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAdd, setShowAdd] = useState(false);
  const [form, setForm] = useState<AddFormState>(BLANK_FORM);
  const [submitting, setSubmitting] = useState(false);
  const [addError, setAddError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const data = await fetchApplications();
      setApplications(data);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const grouped = STAGE_ORDER.reduce<Record<ApplicationStage, Application[]>>(
    (acc, stage) => {
      acc[stage] = applications.filter((a) => a.stage === stage);
      return acc;
    },
    {} as Record<ApplicationStage, Application[]>
  );

  const handleAddSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.jobTitle.trim() || !form.company.trim()) return;
    setSubmitting(true);
    setAddError(null);
    try {
      const created = await createApplication({
        jobTitle: form.jobTitle.trim(),
        company: form.company.trim(),
        location: form.location.trim() || undefined,
        stage: "applied",
        source: form.source,
        url: form.url.trim() || undefined,
        notes: form.notes.trim() || undefined,
      });
      setApplications((prev) => [...prev, created]);
      setForm(BLANK_FORM);
      setShowAdd(false);
    } catch (err: unknown) {
      setAddError(err instanceof Error ? err.message : "Failed to add application.");
    } finally {
      setSubmitting(false);
    }
  };

  const handleStageChange = async (id: string, stage: ApplicationStage) => {
    // Optimistic update
    setApplications((prev) =>
      prev.map((a) => (a.id === id ? { ...a, stage } : a))
    );
    try {
      await updateApplicationStage(id, stage);
    } catch {
      // revert on error
      await load();
    }
  };

  return (
    <div
      style={{
        flex: 1,
        display: "flex",
        flexDirection: "column",
        background: COLORS.bg,
        minHeight: "100vh",
      }}
    >
      {/* Header */}
      <div
        style={{
          padding: "20px 28px 16px",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
        }}
      >
        <div>
          <h1 style={{ fontSize: 18, fontWeight: 600, color: COLORS.text, margin: 0 }}>
            Application Tracker
          </h1>
          <p style={{ fontSize: 13, color: COLORS.textMuted, margin: "4px 0 0" }}>
            {applications.length > 0
              ? `${applications.length} application${applications.length !== 1 ? "s" : ""} across ${STAGE_ORDER.filter((s) => grouped[s].length > 0).length} stages`
              : "Track every application in one place"}
          </p>
        </div>
        <button
          onClick={() => setShowAdd(true)}
          style={{
            padding: "7px 14px",
            borderRadius: 6,
            border: "none",
            background: COLORS.brand,
            fontSize: 13,
            color: "#fff",
            fontWeight: 500,
            cursor: "pointer",
            display: "flex",
            alignItems: "center",
            gap: 6,
          }}
        >
          <Icon name="plus" size={13} color="#fff" /> Add Application
        </button>
      </div>

      {/* Add Application Modal */}
      {showAdd && (
        <div
          style={{
            position: "fixed",
            inset: 0,
            background: "rgba(15,23,42,0.4)",
            zIndex: 50,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}
          onClick={(e) => {
            if (e.target === e.currentTarget) setShowAdd(false);
          }}
        >
          <Card style={{ width: 480, padding: 0, overflow: "hidden" }}>
            <div
              style={{
                padding: "16px 20px",
                borderBottom: `1px solid ${COLORS.borderLight}`,
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
              }}
            >
              <span style={{ fontSize: 14, fontWeight: 600, color: COLORS.text }}>
                Add Application
              </span>
              <button
                onClick={() => { setShowAdd(false); setAddError(null); }}
                style={{ border: "none", background: "none", cursor: "pointer", padding: 4 }}
              >
                <Icon name="x" size={16} color={COLORS.textMuted} />
              </button>
            </div>
            <form onSubmit={handleAddSubmit} style={{ padding: 20 }}>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12, marginBottom: 12 }}>
                <div>
                  <label style={{ fontSize: 12, fontWeight: 500, color: COLORS.textMuted, display: "block", marginBottom: 5 }}>
                    Job Title *
                  </label>
                  <input
                    required
                    value={form.jobTitle}
                    onChange={(e) => setForm({ ...form, jobTitle: e.target.value })}
                    placeholder="e.g. Senior Engineer"
                    style={{ width: "100%", padding: "8px 10px", borderRadius: 6, border: `1px solid ${COLORS.border}`, fontSize: 13, color: COLORS.text, outline: "none", boxSizing: "border-box" }}
                  />
                </div>
                <div>
                  <label style={{ fontSize: 12, fontWeight: 500, color: COLORS.textMuted, display: "block", marginBottom: 5 }}>
                    Company *
                  </label>
                  <input
                    required
                    value={form.company}
                    onChange={(e) => setForm({ ...form, company: e.target.value })}
                    placeholder="e.g. Razorpay"
                    style={{ width: "100%", padding: "8px 10px", borderRadius: 6, border: `1px solid ${COLORS.border}`, fontSize: 13, color: COLORS.text, outline: "none", boxSizing: "border-box" }}
                  />
                </div>
              </div>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12, marginBottom: 12 }}>
                <div>
                  <label style={{ fontSize: 12, fontWeight: 500, color: COLORS.textMuted, display: "block", marginBottom: 5 }}>
                    Location
                  </label>
                  <input
                    value={form.location}
                    onChange={(e) => setForm({ ...form, location: e.target.value })}
                    placeholder="e.g. Bengaluru"
                    style={{ width: "100%", padding: "8px 10px", borderRadius: 6, border: `1px solid ${COLORS.border}`, fontSize: 13, color: COLORS.text, outline: "none", boxSizing: "border-box" }}
                  />
                </div>
                <div>
                  <label style={{ fontSize: 12, fontWeight: 500, color: COLORS.textMuted, display: "block", marginBottom: 5 }}>
                    Source
                  </label>
                  <select
                    value={form.source}
                    onChange={(e) => setForm({ ...form, source: e.target.value as JobSource })}
                    style={{ width: "100%", padding: "8px 10px", borderRadius: 6, border: `1px solid ${COLORS.border}`, fontSize: 13, color: COLORS.text, outline: "none", cursor: "pointer", boxSizing: "border-box" }}
                  >
                    {SOURCES.map((s) => (
                      <option key={s} value={s}>{sourceLabel(s)}</option>
                    ))}
                  </select>
                </div>
              </div>
              <div style={{ marginBottom: 12 }}>
                <label style={{ fontSize: 12, fontWeight: 500, color: COLORS.textMuted, display: "block", marginBottom: 5 }}>
                  Job URL
                </label>
                <input
                  type="url"
                  value={form.url}
                  onChange={(e) => setForm({ ...form, url: e.target.value })}
                  placeholder="https://…"
                  style={{ width: "100%", padding: "8px 10px", borderRadius: 6, border: `1px solid ${COLORS.border}`, fontSize: 13, color: COLORS.text, outline: "none", boxSizing: "border-box" }}
                />
              </div>
              <div style={{ marginBottom: 16 }}>
                <label style={{ fontSize: 12, fontWeight: 500, color: COLORS.textMuted, display: "block", marginBottom: 5 }}>
                  Notes
                </label>
                <textarea
                  value={form.notes}
                  onChange={(e) => setForm({ ...form, notes: e.target.value })}
                  placeholder="Recruiter name, next steps, deadlines…"
                  rows={2}
                  style={{ width: "100%", padding: "8px 10px", borderRadius: 6, border: `1px solid ${COLORS.border}`, fontSize: 13, color: COLORS.text, outline: "none", resize: "vertical", fontFamily: "inherit", boxSizing: "border-box" }}
                />
              </div>
              {addError && (
                <div style={{ marginBottom: 12, fontSize: 12, color: COLORS.dangerMid }}>{addError}</div>
              )}
              <div style={{ display: "flex", justifyContent: "flex-end", gap: 8 }}>
                <button
                  type="button"
                  onClick={() => { setShowAdd(false); setAddError(null); }}
                  style={{ padding: "8px 16px", borderRadius: 6, border: `1px solid ${COLORS.border}`, background: COLORS.card, fontSize: 13, color: COLORS.textMuted, cursor: "pointer" }}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  style={{ padding: "8px 20px", borderRadius: 6, border: "none", background: COLORS.brand, fontSize: 13, color: "#fff", fontWeight: 500, cursor: submitting ? "default" : "pointer", opacity: submitting ? 0.7 : 1 }}
                >
                  {submitting ? "Adding…" : "Add Application"}
                </button>
              </div>
            </form>
          </Card>
        </div>
      )}

      {/* Board */}
      <div
        style={{
          display: "flex",
          gap: 10,
          padding: "0 28px 28px",
          overflowX: "auto",
          flex: 1,
          alignItems: "flex-start",
        }}
      >
        {loading
          ? STAGE_ORDER.map((s) => (
              <div key={s} style={{ width: 240, minWidth: 240 }}>
                <div style={{ height: 32, marginBottom: 8 }}>
                  <Skeleton width={120} height={16} style={{ marginBottom: 6 }} />
                </div>
                {[1, 2].map((i) => (
                  <div key={i} style={{ marginBottom: 8 }}>
                    <Skeleton width="100%" height={90} borderRadius={8} />
                  </div>
                ))}
              </div>
            ))
          : STAGE_ORDER.map((stage) => {
              const cfg = STAGE_CONFIG[stage];
              const cards = grouped[stage] ?? [];
              return (
                <div
                  key={stage}
                  style={{ width: 240, minWidth: 240, display: "flex", flexDirection: "column", gap: 8 }}
                >
                  {/* Column header */}
                  <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "8px 4px" }}>
                    <div style={{ display: "flex", alignItems: "center", gap: 7 }}>
                      <div style={{ width: 8, height: 8, borderRadius: "50%", background: cfg.color }} />
                      <span style={{ fontSize: 13, fontWeight: 600, color: COLORS.text }}>{cfg.label}</span>
                    </div>
                    <span style={{ fontSize: 12, padding: "2px 7px", borderRadius: 10, background: cfg.bg, color: cfg.color, fontWeight: 600 }}>
                      {cards.length}
                    </span>
                  </div>

                  {/* Cards */}
                  {cards.length === 0 ? (
                    <div style={{ padding: "20px 12px", textAlign: "center", borderRadius: 8, border: `1.5px dashed ${COLORS.border}`, background: COLORS.borderLight }}>
                      <p style={{ fontSize: 12, color: COLORS.textLight, margin: 0 }}>No applications</p>
                    </div>
                  ) : (
                    cards.map((app) => (
                      <div
                        key={app.id}
                        style={{
                          background: COLORS.card,
                          borderRadius: 8,
                          border: `1px solid ${stage === "offer" ? COLORS.successMid : COLORS.border}`,
                          boxShadow: stage === "offer"
                            ? `0 0 0 2px ${COLORS.successBg}, 0 2px 6px rgba(0,0,0,0.06)`
                            : "0 1px 3px rgba(0,0,0,0.04)",
                          padding: "12px 13px",
                          transition: "box-shadow 0.15s, transform 0.1s",
                        }}
                        onMouseEnter={(e) => {
                          (e.currentTarget as HTMLDivElement).style.boxShadow = "0 4px 12px rgba(0,0,0,0.1)";
                          (e.currentTarget as HTMLDivElement).style.transform = "translateY(-1px)";
                        }}
                        onMouseLeave={(e) => {
                          (e.currentTarget as HTMLDivElement).style.boxShadow =
                            stage === "offer"
                              ? `0 0 0 2px ${COLORS.successBg}, 0 2px 6px rgba(0,0,0,0.06)`
                              : "0 1px 3px rgba(0,0,0,0.04)";
                          (e.currentTarget as HTMLDivElement).style.transform = "translateY(0)";
                        }}
                      >
                        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 5 }}>
                          <div style={{ flex: 1, minWidth: 0, paddingRight: 6 }}>
                            <div style={{ fontSize: 12.5, fontWeight: 600, color: COLORS.text, lineHeight: 1.4 }}>{app.jobTitle}</div>
                            <div style={{ fontSize: 11.5, color: COLORS.textMuted, marginTop: 2, display: "flex", alignItems: "center", gap: 4 }}>
                              <Icon name="building" size={10} color={COLORS.textLight} />
                              {app.company}
                            </div>
                          </div>
                        </div>

                        {app.notes && (
                          <div style={{ fontSize: 11, padding: "4px 7px", borderRadius: 4, background: stage === "offer" ? COLORS.successBg : COLORS.borderLight, color: stage === "offer" ? COLORS.success : COLORS.textMuted, marginBottom: 7, lineHeight: 1.4 }}>
                            {app.notes}
                          </div>
                        )}

                        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginTop: 6, gap: 6 }}>
                          <Badge variant={app.source as "linkedin" | "naukri" | "indeed"} size="xs">
                            {sourceLabel(app.source).slice(0, 2).toUpperCase()}
                          </Badge>
                          <select
                            value={app.stage}
                            onChange={(e) => handleStageChange(app.id, e.target.value as ApplicationStage)}
                            onClick={(e) => e.stopPropagation()}
                            style={{ fontSize: 11, padding: "2px 6px", borderRadius: 4, border: `1px solid ${COLORS.border}`, background: COLORS.bg, color: COLORS.textMuted, cursor: "pointer", outline: "none" }}
                          >
                            {STAGE_ORDER.map((s) => (
                              <option key={s} value={s}>{STAGE_CONFIG[s].label}</option>
                            ))}
                          </select>
                          <span style={{ fontSize: 10.5, color: COLORS.textLight }}>
                            {new Date(app.appliedAt).toLocaleDateString("en-IN", { day: "numeric", month: "short" })}
                          </span>
                        </div>
                      </div>
                    ))
                  )}

                  {/* Add card */}
                  <button
                    onClick={() => setShowAdd(true)}
                    style={{ width: "100%", padding: "8px 12px", borderRadius: 6, border: `1.5px dashed ${COLORS.border}`, background: "transparent", fontSize: 12, color: COLORS.textLight, cursor: "pointer", display: "flex", alignItems: "center", justifyContent: "center", gap: 5 }}
                  >
                    <Icon name="plus" size={12} color={COLORS.textLight} /> Add card
                  </button>
                </div>
              );
            })}
      </div>
    </div>
  );
};
