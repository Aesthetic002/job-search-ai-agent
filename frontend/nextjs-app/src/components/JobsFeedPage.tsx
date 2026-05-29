"use client";

import React, { useEffect, useState, useCallback } from "react";
import { COLORS, Icon, Card, Badge, EmptyState, Skeleton } from "./ui";
import { searchJobs, syncJobSources } from "@/lib/api";
import type { Job, JobSource } from "@/lib/types";

const SOURCES: { value: string; label: string }[] = [
  { value: "", label: "All Sources" },
  { value: "linkedin", label: "LinkedIn" },
  { value: "naukri", label: "Naukri" },
  { value: "indeed", label: "Indeed" },
];

function sourceLabel(src: string) {
  if (src === "linkedin") return "LinkedIn";
  if (src === "naukri") return "Naukri";
  if (src === "indeed") return "Indeed";
  return src;
}

function matchColor(score: number) {
  if (score >= 90) return { bg: COLORS.successBg, color: COLORS.success };
  if (score >= 80) return { bg: COLORS.brandLight, color: COLORS.brand };
  return { bg: COLORS.warningBg, color: COLORS.warning };
}

function fmtDate(iso: string) {
  return new Date(iso).toLocaleDateString("en-IN", { day: "numeric", month: "short" });
}

export const JobsFeedPage = () => {
  const [query, setQuery] = useState("");
  const [source, setSource] = useState("");
  const [location, setLocation] = useState("");
  const [jobs, setJobs] = useState<Job[]>([]);
  const [selectedJob, setSelectedJob] = useState<Job | null>(null);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);
  const [syncing, setSyncing] = useState(false);

  const doSearch = useCallback(async () => {
    setLoading(true);
    setSearched(true);
    try {
      const results = await searchJobs({ query, source, location });
      setJobs(results);
      setSelectedJob(results[0] ?? null);
    } finally {
      setLoading(false);
    }
  }, [query, source, location]);

  const handleSync = async () => {
    setSyncing(true);
    try {
      await syncJobSources();
      await doSearch();
    } finally {
      setSyncing(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") doSearch();
  };

  return (
    <div style={{ flex: 1, display: "flex", flexDirection: "column", background: COLORS.bg, minHeight: "100vh" }}>
      {/* Header */}
      <div style={{ padding: "20px 28px 0", display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
        <div>
          <h1 style={{ fontSize: 18, fontWeight: 600, color: COLORS.text, margin: 0 }}>Jobs Feed</h1>
          <p style={{ fontSize: 13, color: COLORS.textMuted, margin: "4px 0 0" }}>
            Search and browse jobs from all connected sources
          </p>
        </div>
        <button
          onClick={handleSync}
          disabled={syncing}
          style={{
            padding: "7px 14px",
            borderRadius: 6,
            border: `1px solid ${COLORS.border}`,
            background: COLORS.card,
            fontSize: 13,
            color: COLORS.textMuted,
            cursor: syncing ? "default" : "pointer",
            display: "flex",
            alignItems: "center",
            gap: 6,
            opacity: syncing ? 0.7 : 1,
          }}
        >
          <Icon name="refresh-cw" size={13} color={COLORS.textMuted}
            style={syncing ? { animation: "spin 1s linear infinite" } : {}} />
          {syncing ? "Syncing…" : "Sync Sources"}
        </button>
      </div>

      {/* Search bar */}
      <div style={{ padding: "16px 28px 0" }}>
        <Card style={{ padding: "14px 16px" }}>
          <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
            <div style={{ flex: 1, minWidth: 200, position: "relative" }}>
              <Icon
                name="search"
                size={14}
                color={COLORS.textMuted}
                style={{ position: "absolute", left: 10, top: "50%", transform: "translateY(-50%)" }}
              />
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Search by title, skill, or company…"
                style={{
                  width: "100%",
                  padding: "8px 12px 8px 32px",
                  borderRadius: 6,
                  border: `1px solid ${COLORS.border}`,
                  fontSize: 13,
                  color: COLORS.text,
                  background: COLORS.bg,
                  outline: "none",
                }}
              />
            </div>
            <div style={{ position: "relative" }}>
              <Icon
                name="globe"
                size={14}
                color={COLORS.textMuted}
                style={{ position: "absolute", left: 10, top: "50%", transform: "translateY(-50%)", pointerEvents: "none" }}
              />
              <input
                type="text"
                value={location}
                onChange={(e) => setLocation(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Location"
                style={{
                  padding: "8px 12px 8px 32px",
                  borderRadius: 6,
                  border: `1px solid ${COLORS.border}`,
                  fontSize: 13,
                  color: COLORS.text,
                  background: COLORS.bg,
                  outline: "none",
                  width: 160,
                }}
              />
            </div>
            <select
              value={source}
              onChange={(e) => setSource(e.target.value)}
              style={{
                padding: "8px 12px",
                borderRadius: 6,
                border: `1px solid ${COLORS.border}`,
                fontSize: 13,
                color: COLORS.text,
                background: COLORS.bg,
                outline: "none",
                cursor: "pointer",
              }}
            >
              {SOURCES.map((s) => (
                <option key={s.value} value={s.value}>{s.label}</option>
              ))}
            </select>
            <button
              onClick={doSearch}
              disabled={loading}
              style={{
                padding: "8px 20px",
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
                opacity: loading ? 0.7 : 1,
              }}
            >
              <Icon name="search" size={13} color="#fff" />
              Search
            </button>
          </div>
        </Card>
      </div>

      {/* Results */}
      <div style={{ display: "grid", gridTemplateColumns: "380px 1fr", gap: 12, padding: "14px 28px 28px", flex: 1 }}>
        {/* Left: list */}
        <Card style={{ overflow: "hidden", display: "flex", flexDirection: "column" }}>
          {loading ? (
            <div style={{ padding: "14px 16px", display: "flex", flexDirection: "column", gap: 14 }}>
              {[1, 2, 3, 4].map((i) => (
                <div key={i} style={{ display: "flex", flexDirection: "column", gap: 6 }}>
                  <Skeleton width="75%" height={14} />
                  <Skeleton width="50%" height={12} />
                  <div style={{ display: "flex", gap: 5 }}>
                    <Skeleton width={50} height={20} borderRadius={3} />
                    <Skeleton width={50} height={20} borderRadius={3} />
                  </div>
                </div>
              ))}
            </div>
          ) : !searched ? (
            <EmptyState
              icon="search"
              title="Search for jobs"
              description="Enter a job title, skill, or company name to find matching positions from all your connected sources."
            />
          ) : jobs.length === 0 ? (
            <EmptyState
              icon="briefcase"
              title="No results found"
              description="Try adjusting your search query or sync your job sources to get fresh listings."
              action={
                <button
                  onClick={handleSync}
                  style={{
                    padding: "8px 18px",
                    borderRadius: 6,
                    border: "none",
                    background: COLORS.brand,
                    color: "#fff",
                    fontSize: 13,
                    fontWeight: 500,
                    cursor: "pointer",
                    display: "flex",
                    alignItems: "center",
                    gap: 6,
                  }}
                >
                  <Icon name="refresh-cw" size={13} color="#fff" />
                  Sync Sources
                </button>
              }
            />
          ) : (
            <>
              <div style={{ padding: "10px 16px 8px", borderBottom: `1px solid ${COLORS.borderLight}` }}>
                <span style={{ fontSize: 12, color: COLORS.textMuted }}>
                  {jobs.length} result{jobs.length !== 1 ? "s" : ""}
                </span>
              </div>
              <div style={{ overflowY: "auto", flex: 1 }}>
                {jobs.map((job, i) => {
                  const mc = job.matchScore != null ? matchColor(job.matchScore) : null;
                  return (
                    <div
                      key={job.id}
                      onClick={() => setSelectedJob(job)}
                      style={{
                        padding: "14px 16px",
                        cursor: "pointer",
                        borderBottom: i < jobs.length - 1 ? `1px solid ${COLORS.borderLight}` : "none",
                        background: selectedJob?.id === job.id ? COLORS.brandLight : "transparent",
                        transition: "background 0.1s",
                      }}
                    >
                      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 6 }}>
                        <div>
                          <div style={{ fontSize: 13.5, fontWeight: 500, color: COLORS.text }}>{job.title}</div>
                          <div style={{ fontSize: 12, color: COLORS.textMuted, marginTop: 2 }}>
                            {job.company} · {job.location}
                          </div>
                        </div>
                        <div style={{ display: "flex", flexDirection: "column", alignItems: "flex-end", gap: 4, flexShrink: 0, marginLeft: 8 }}>
                          {mc && job.matchScore != null && (
                            <span style={{ fontSize: 12, fontWeight: 600, padding: "2px 8px", borderRadius: 4, background: mc.bg, color: mc.color }}>
                              {job.matchScore}%
                            </span>
                          )}
                          <Badge variant={job.source as "linkedin" | "naukri" | "indeed"} size="xs">
                            {sourceLabel(job.source)}
                          </Badge>
                        </div>
                      </div>
                      <div style={{ display: "flex", gap: 4, flexWrap: "wrap" }}>
                        {job.tags.slice(0, 3).map((t, ti) => (
                          <span key={ti} style={{ fontSize: 11, padding: "2px 6px", borderRadius: 3, background: COLORS.borderLight, color: COLORS.textMuted }}>{t}</span>
                        ))}
                        <span style={{ fontSize: 11, color: COLORS.textLight, marginLeft: "auto" }}>{fmtDate(job.postedAt)}</span>
                      </div>
                    </div>
                  );
                })}
              </div>
            </>
          )}
        </Card>

        {/* Right: job detail */}
        <Card style={{ padding: 0, display: "flex", flexDirection: "column", overflow: "hidden" }}>
          {!selectedJob ? (
            <EmptyState
              icon="file-text"
              title="Select a job to preview"
              description="Click a job on the left to see the full description, required skills, and your ATS match."
            />
          ) : (
            <>
              <div style={{ padding: "20px 24px 16px", borderBottom: `1px solid ${COLORS.borderLight}` }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                  <div>
                    <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 4 }}>
                      <span style={{ fontSize: 16, fontWeight: 600, color: COLORS.text }}>{selectedJob.title}</span>
                      <Badge variant={selectedJob.source as "linkedin" | "naukri" | "indeed"}>{sourceLabel(selectedJob.source)}</Badge>
                    </div>
                    <div style={{ fontSize: 13, color: COLORS.textMuted }}>
                      {selectedJob.company} · {selectedJob.location}{selectedJob.salary ? ` · ${selectedJob.salary}` : ""}
                    </div>
                  </div>
                  <div style={{ display: "flex", gap: 8 }}>
                    <button style={{ padding: "7px 14px", borderRadius: 6, border: `1px solid ${COLORS.border}`, background: COLORS.card, fontSize: 13, color: COLORS.textMuted, cursor: "pointer", display: "flex", alignItems: "center", gap: 5 }}>
                      <Icon name="star" size={13} color={COLORS.textMuted} /> Save
                    </button>
                    <a href={selectedJob.url} target="_blank" rel="noopener noreferrer"
                      style={{ padding: "7px 16px", borderRadius: 6, border: "none", background: COLORS.brand, fontSize: 13, color: "#fff", fontWeight: 500, cursor: "pointer", display: "flex", alignItems: "center", gap: 6, textDecoration: "none" }}>
                      Apply <Icon name="external-link" size={12} color="#fff" />
                    </a>
                  </div>
                </div>
                <div style={{ display: "flex", gap: 6, marginTop: 12, flexWrap: "wrap" }}>
                  {selectedJob.matchScore != null && (
                    <span style={{ display: "inline-flex", alignItems: "center", gap: 5, padding: "4px 10px", borderRadius: 4, border: `1px solid ${COLORS.border}`, fontSize: 12, color: COLORS.text, fontWeight: 600 }}>
                      <Icon name="target" size={12} color={COLORS.brand} /> {selectedJob.matchScore}% ATS Match
                    </span>
                  )}
                  {selectedJob.tags.map((t, ti) => (
                    <span key={ti} style={{ fontSize: 12, padding: "4px 10px", borderRadius: 4, background: COLORS.borderLight, color: COLORS.textMuted, border: `1px solid ${COLORS.border}` }}>{t}</span>
                  ))}
                </div>
              </div>
              <div style={{ padding: "20px 24px", flex: 1, overflowY: "auto" }}>
                <div style={{ fontSize: 13, color: COLORS.text, lineHeight: 1.8, whiteSpace: "pre-line" }}>
                  {selectedJob.description}
                </div>
              </div>
            </>
          )}
        </Card>
      </div>
      <style>{`
        @keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
      `}</style>
    </div>
  );
};
