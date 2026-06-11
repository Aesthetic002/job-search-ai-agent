"use client";

import React, { useState, useCallback } from "react";
import { COLORS, Icon, Card, Badge, EmptyState, Skeleton } from "./ui";
import { searchJobs, syncJobSources, fetchCompanyResearch, fetchSalaryBenchmark } from "@/lib/api";
import type { Job, CompanyResearch, SalaryBenchmark } from "@/lib/types";

// ─── Filter option lists ──────────────────────────────────────────────────────

const SOURCES = [
  { value: "", label: "All Sources" },
  { value: "linkedin", label: "LinkedIn" },
  { value: "naukri", label: "Naukri" },
  { value: "indeed", label: "Indeed" },
];

const WORK_MODES = [
  { value: "any", label: "Any Mode" },
  { value: "remote", label: "Remote / WFH" },
  { value: "hybrid", label: "Hybrid" },
  { value: "onsite", label: "On-site" },
];

const NOTICE_PERIODS = [
  { value: "any", label: "Any Notice" },
  { value: "immediate", label: "Immediate" },
  { value: "15days", label: "≤ 15 Days" },
  { value: "30days", label: "≤ 30 Days" },
  { value: "60days", label: "≤ 60 Days" },
  { value: "90days", label: "≤ 90 Days" },
];

// ─── Utility helpers ──────────────────────────────────────────────────────────

function sourceLabel(src: string) {
  const map: Record<string, string> = { linkedin: "LinkedIn", naukri: "Naukri", indeed: "Indeed" };
  return map[src] ?? src;
}

function matchColor(score: number) {
  if (score >= 90) return { bg: COLORS.successBg, color: COLORS.success };
  if (score >= 80) return { bg: COLORS.brandLight, color: COLORS.brand };
  return { bg: COLORS.warningBg, color: COLORS.warning };
}

function fmtDate(iso: string) {
  return new Date(iso).toLocaleDateString("en-IN", { day: "numeric", month: "short" });
}

const INPUT_STYLE: React.CSSProperties = {
  padding: "8px 12px",
  borderRadius: 6,
  border: `1px solid ${COLORS.border}`,
  fontSize: 13,
  color: COLORS.text,
  background: COLORS.bg,
  outline: "none",
};

const SELECT_STYLE: React.CSSProperties = {
  ...INPUT_STYLE,
  cursor: "pointer",
};

// ─── Component ────────────────────────────────────────────────────────────────

export const JobsFeedPage = () => {
  // Core search state
  const [query, setQuery] = useState("");
  const [source, setSource] = useState("");
  const [location, setLocation] = useState("");
  const [jobs, setJobs] = useState<Job[]>([]);
  const [selectedJob, setSelectedJob] = useState<Job | null>(null);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);
  const [syncing, setSyncing] = useState(false);

  // Indian-specific filters
  const [workMode, setWorkMode] = useState("any");
  const [noticePeriod, setNoticePeriod] = useState("any");
  const [minSalaryLpa, setMinSalaryLpa] = useState("");
  const [maxSalaryLpa, setMaxSalaryLpa] = useState("");
  const [showFilters, setShowFilters] = useState(false);

  // Insights State
  const [showCompanyModal, setShowCompanyModal] = useState(false);
  const [companyResearch, setCompanyResearch] = useState<CompanyResearch | null>(null);
  const [loadingCompany, setLoadingCompany] = useState(false);
  
  const [showSalaryModal, setShowSalaryModal] = useState(false);
  const [salaryBenchmark, setSalaryBenchmark] = useState<SalaryBenchmark | null>(null);
  const [loadingSalary, setLoadingSalary] = useState(false);

  const doSearch = useCallback(async () => {
    setLoading(true);
    setSearched(true);
    try {
      const results = await searchJobs({
        query,
        source,
        location,
        workMode,
        noticePeriod,
        minSalaryLpa: minSalaryLpa ? parseFloat(minSalaryLpa) : undefined,
        maxSalaryLpa: maxSalaryLpa ? parseFloat(maxSalaryLpa) : undefined,
      });
      setJobs(results);
      setSelectedJob(results[0] ?? null);
    } finally {
      setLoading(false);
    }
  }, [query, source, location, workMode, noticePeriod, minSalaryLpa, maxSalaryLpa]);

  const handleSync = async () => {
    setSyncing(true);
    try {
      await syncJobSources();
      await doSearch();
    } finally {
      setSyncing(false);
    }
  };

  const handleResearchCompany = async () => {
    if (!selectedJob) return;
    setShowCompanyModal(true);
    setLoadingCompany(true);
    try {
      const data = await fetchCompanyResearch(selectedJob.company);
      setCompanyResearch(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoadingCompany(false);
    }
  };

  const handleBenchmarkSalary = async () => {
    if (!selectedJob) return;
    setShowSalaryModal(true);
    setLoadingSalary(true);
    try {
      const data = await fetchSalaryBenchmark(selectedJob.title, selectedJob.location);
      setSalaryBenchmark(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoadingSalary(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") doSearch();
  };

  const hasActiveFilters =
    workMode !== "any" || noticePeriod !== "any" || minSalaryLpa !== "" || maxSalaryLpa !== "";

  return (
    <div style={{ flex: 1, display: "flex", flexDirection: "column", background: COLORS.bg, minHeight: "100vh" }}>
      {/* Header */}
      <div style={{ padding: "20px 28px 0", display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
        <div>
          <h1 style={{ fontSize: 18, fontWeight: 600, color: COLORS.text, margin: 0 }}>Jobs Feed</h1>
          <p style={{ fontSize: 13, color: COLORS.textMuted, margin: "4px 0 0" }}>
            Search Naukri, Indeed &amp; LinkedIn — results cached for 30 minutes
          </p>
        </div>
        <button
          onClick={handleSync}
          disabled={syncing}
          style={{
            padding: "7px 14px", borderRadius: 6, border: `1px solid ${COLORS.border}`,
            background: COLORS.card, fontSize: 13, color: COLORS.textMuted,
            cursor: syncing ? "default" : "pointer", display: "flex", alignItems: "center",
            gap: 6, opacity: syncing ? 0.7 : 1,
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
          {/* Primary search row */}
          <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
            {/* Query */}
            <div style={{ flex: 1, minWidth: 200, position: "relative" }}>
              <Icon name="search" size={14} color={COLORS.textMuted}
                style={{ position: "absolute", left: 10, top: "50%", transform: "translateY(-50%)" }} />
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Search by title, skill, or company…"
                style={{ ...INPUT_STYLE, width: "100%", paddingLeft: 32 }}
              />
            </div>

            {/* Location */}
            <div style={{ position: "relative" }}>
              <Icon name="map-pin" size={14} color={COLORS.textMuted}
                style={{ position: "absolute", left: 10, top: "50%", transform: "translateY(-50%)", pointerEvents: "none" }} />
              <input
                type="text"
                value={location}
                onChange={(e) => setLocation(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="City or India"
                style={{ ...INPUT_STYLE, paddingLeft: 32, width: 160 }}
              />
            </div>

            {/* Source */}
            <select value={source} onChange={(e) => setSource(e.target.value)} style={SELECT_STYLE}>
              {SOURCES.map((s) => <option key={s.value} value={s.value}>{s.label}</option>)}
            </select>

            {/* Filter toggle */}
            <button
              onClick={() => setShowFilters((v) => !v)}
              style={{
                ...SELECT_STYLE,
                display: "flex", alignItems: "center", gap: 5,
                background: hasActiveFilters ? COLORS.brandLight : COLORS.bg,
                color: hasActiveFilters ? COLORS.brand : COLORS.textMuted,
                borderColor: hasActiveFilters ? COLORS.brand : COLORS.border,
              }}
            >
              <Icon name="sliders-horizontal" size={13} color={hasActiveFilters ? COLORS.brand : COLORS.textMuted} />
              Filters{hasActiveFilters ? " ●" : ""}
            </button>

            {/* Search button */}
            <button
              onClick={doSearch}
              disabled={loading}
              style={{
                padding: "8px 20px", borderRadius: 6, border: "none",
                background: COLORS.brand, fontSize: 13, color: "#fff", fontWeight: 500,
                cursor: "pointer", display: "flex", alignItems: "center", gap: 6,
                opacity: loading ? 0.7 : 1,
              }}
            >
              <Icon name="search" size={13} color="#fff" />
              Search
            </button>
          </div>

          {/* ── Indian-specific advanced filters ── */}
          {showFilters && (
            <div style={{
              marginTop: 12, paddingTop: 12,
              borderTop: `1px solid ${COLORS.borderLight}`,
              display: "flex", gap: 10, flexWrap: "wrap", alignItems: "center",
            }}>
              {/* Work Mode */}
              <div style={{ display: "flex", flexDirection: "column", gap: 3 }}>
                <label style={{ fontSize: 11, color: COLORS.textMuted, fontWeight: 500 }}>WORK MODE</label>
                <select value={workMode} onChange={(e) => setWorkMode(e.target.value)} style={SELECT_STYLE}>
                  {WORK_MODES.map((w) => <option key={w.value} value={w.value}>{w.label}</option>)}
                </select>
              </div>

              {/* Notice Period */}
              <div style={{ display: "flex", flexDirection: "column", gap: 3 }}>
                <label style={{ fontSize: 11, color: COLORS.textMuted, fontWeight: 500 }}>NOTICE PERIOD</label>
                <select value={noticePeriod} onChange={(e) => setNoticePeriod(e.target.value)} style={SELECT_STYLE}>
                  {NOTICE_PERIODS.map((n) => <option key={n.value} value={n.value}>{n.label}</option>)}
                </select>
              </div>

              {/* Salary LPA Range */}
              <div style={{ display: "flex", flexDirection: "column", gap: 3 }}>
                <label style={{ fontSize: 11, color: COLORS.textMuted, fontWeight: 500 }}>SALARY (LPA)</label>
                <div style={{ display: "flex", gap: 6, alignItems: "center" }}>
                  <input
                    type="number"
                    value={minSalaryLpa}
                    onChange={(e) => setMinSalaryLpa(e.target.value)}
                    placeholder="Min"
                    min={0}
                    style={{ ...INPUT_STYLE, width: 72 }}
                  />
                  <span style={{ fontSize: 12, color: COLORS.textMuted }}>–</span>
                  <input
                    type="number"
                    value={maxSalaryLpa}
                    onChange={(e) => setMaxSalaryLpa(e.target.value)}
                    placeholder="Max"
                    min={0}
                    style={{ ...INPUT_STYLE, width: 72 }}
                  />
                </div>
              </div>

              {/* Clear filters */}
              {hasActiveFilters && (
                <button
                  onClick={() => {
                    setWorkMode("any");
                    setNoticePeriod("any");
                    setMinSalaryLpa("");
                    setMaxSalaryLpa("");
                  }}
                  style={{
                    alignSelf: "flex-end", padding: "8px 12px", borderRadius: 6,
                    border: `1px solid ${COLORS.border}`, background: "transparent",
                    fontSize: 12, color: COLORS.textMuted, cursor: "pointer",
                  }}
                >
                  Clear filters
                </button>
              )}
            </div>
          )}
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
              description="Enter a title, skill, or company. Use filters to narrow by salary (LPA), work mode, or notice period."
            />
          ) : jobs.length === 0 ? (
            <EmptyState
              icon="briefcase"
              title="No results found"
              description="Try adjusting your search or sync sources to get fresh listings."
              action={
                <button
                  onClick={handleSync}
                  style={{
                    padding: "8px 18px", borderRadius: 6, border: "none",
                    background: COLORS.brand, color: "#fff", fontSize: 13,
                    fontWeight: 500, cursor: "pointer", display: "flex", alignItems: "center", gap: 6,
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
                        padding: "14px 16px", cursor: "pointer",
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
                          {job.salary && (
                            <div style={{ fontSize: 11, color: COLORS.brand, marginTop: 2, fontWeight: 500 }}>
                              {job.salary}
                            </div>
                          )}
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
                      {selectedJob.company} · {selectedJob.location}
                      {selectedJob.salary ? ` · ${selectedJob.salary}` : ""}
                    </div>
                  </div>
                  <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
                    <button onClick={handleResearchCompany} style={{ padding: "7px 14px", borderRadius: 6, border: `1px solid ${COLORS.border}`, background: COLORS.card, fontSize: 13, color: COLORS.brand, cursor: "pointer", display: "flex", alignItems: "center", gap: 5 }}>
                      <Icon name="search" size={13} color={COLORS.brand} /> Research
                    </button>
                    <button onClick={handleBenchmarkSalary} style={{ padding: "7px 14px", borderRadius: 6, border: `1px solid ${COLORS.border}`, background: COLORS.card, fontSize: 13, color: COLORS.brand, cursor: "pointer", display: "flex", alignItems: "center", gap: 5 }}>
                      <Icon name="bar-chart-2" size={13} color={COLORS.brand} /> Benchmark
                    </button>
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

      {/* Modals */}
      {showCompanyModal && (
        <div style={{ position: "fixed", inset: 0, background: "rgba(0,0,0,0.5)", display: "flex", alignItems: "center", justifyContent: "center", zIndex: 100 }}>
          <Card style={{ width: 500, maxWidth: "90%", padding: 24, position: "relative" }}>
            <button onClick={() => setShowCompanyModal(false)} style={{ position: "absolute", top: 16, right: 16, background: "transparent", border: "none", cursor: "pointer" }}>
              <Icon name="x" size={18} color={COLORS.textMuted} />
            </button>
            <h2 style={{ fontSize: 18, margin: "0 0 16px" }}>Company Research</h2>
            {loadingCompany ? (
              <div style={{ padding: "20px 0", textAlign: "center", color: COLORS.textMuted }}>
                <Icon name="loader" size={24} style={{ animation: "spin 1s linear infinite" }} />
                <p style={{ marginTop: 12, fontSize: 14 }}>Analyzing {selectedJob?.company}...</p>
              </div>
            ) : companyResearch ? (
              <div>
                <h3 style={{ fontSize: 16, margin: "0 0 8px", color: COLORS.brand }}>{companyResearch.companyName}</h3>
                <p style={{ fontSize: 14, color: COLORS.text, lineHeight: 1.5, marginBottom: 16 }}>{companyResearch.cultureSummary}</p>
                <div style={{ marginBottom: 16 }}>
                  <strong style={{ fontSize: 13, color: COLORS.textMuted }}>Interview Process:</strong>
                  <p style={{ fontSize: 14, margin: "4px 0 0" }}>{companyResearch.interviewProcess}</p>
                </div>
                <div style={{ display: "flex", gap: 20 }}>
                  <div style={{ flex: 1 }}>
                    <strong style={{ fontSize: 13, color: COLORS.success }}>Pros:</strong>
                    <ul style={{ margin: "4px 0 0", paddingLeft: 20, fontSize: 13, color: COLORS.text }}>
                      {companyResearch.pros.map((p, i) => <li key={i}>{p}</li>)}
                    </ul>
                  </div>
                  <div style={{ flex: 1 }}>
                    <strong style={{ fontSize: 13, color: COLORS.warning }}>Cons:</strong>
                    <ul style={{ margin: "4px 0 0", paddingLeft: 20, fontSize: 13, color: COLORS.text }}>
                      {companyResearch.cons.map((c, i) => <li key={i}>{c}</li>)}
                    </ul>
                  </div>
                </div>
              </div>
            ) : null}
          </Card>
        </div>
      )}

      {showSalaryModal && (
        <div style={{ position: "fixed", inset: 0, background: "rgba(0,0,0,0.5)", display: "flex", alignItems: "center", justifyContent: "center", zIndex: 100 }}>
          <Card style={{ width: 450, maxWidth: "90%", padding: 24, position: "relative" }}>
            <button onClick={() => setShowSalaryModal(false)} style={{ position: "absolute", top: 16, right: 16, background: "transparent", border: "none", cursor: "pointer" }}>
              <Icon name="x" size={18} color={COLORS.textMuted} />
            </button>
            <h2 style={{ fontSize: 18, margin: "0 0 16px" }}>Salary Benchmark</h2>
            {loadingSalary ? (
              <div style={{ padding: "20px 0", textAlign: "center", color: COLORS.textMuted }}>
                <Icon name="loader" size={24} style={{ animation: "spin 1s linear infinite" }} />
                <p style={{ marginTop: 12, fontSize: 14 }}>Calculating market rate...</p>
              </div>
            ) : salaryBenchmark ? (
              <div>
                <p style={{ fontSize: 14, color: COLORS.textMuted, marginBottom: 20 }}>
                  Role: <strong>{selectedJob?.title}</strong><br />
                  Location: <strong>{selectedJob?.location}</strong>
                </p>
                <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 24, padding: "16px", background: COLORS.bg, borderRadius: 8 }}>
                  <div style={{ textAlign: "center" }}>
                    <div style={{ fontSize: 12, color: COLORS.textMuted }}>Minimum</div>
                    <div style={{ fontSize: 18, fontWeight: 600, color: COLORS.text }}>{salaryBenchmark.minLpa} LPA</div>
                  </div>
                  <div style={{ textAlign: "center" }}>
                    <div style={{ fontSize: 12, color: COLORS.textMuted }}>Median</div>
                    <div style={{ fontSize: 24, fontWeight: 700, color: COLORS.brand }}>{salaryBenchmark.midLpa} LPA</div>
                  </div>
                  <div style={{ textAlign: "center" }}>
                    <div style={{ fontSize: 12, color: COLORS.textMuted }}>Maximum</div>
                    <div style={{ fontSize: 18, fontWeight: 600, color: COLORS.text }}>{salaryBenchmark.maxLpa} LPA</div>
                  </div>
                </div>
                <p style={{ fontSize: 14, color: COLORS.text, lineHeight: 1.5, marginBottom: 12 }}>{salaryBenchmark.summary}</p>
                <div style={{ fontSize: 12, color: COLORS.textMuted, display: "flex", alignItems: "center", gap: 4 }}>
                  <Icon name="info" size={12} /> Confidence: <strong>{salaryBenchmark.confidence}</strong>
                </div>
              </div>
            ) : null}
          </Card>
        </div>
      )}

      <style>{`
        @keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
      `}</style>
    </div>
  );
};

