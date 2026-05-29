"use client";

import React, { useEffect, useState, useCallback } from "react";
import { COLORS, Icon, Card, Badge, EmptyState, StatCard, Skeleton } from "./ui";
import {
  fetchDashboardStats,
  fetchRecommendedJobs,
  syncJobSources,
} from "@/lib/api";
import type { DashboardStats, Job } from "@/lib/types";

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

export const DashboardPage = () => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [jobs, setJobs] = useState<Job[]>([]);
  const [selectedJobId, setSelectedJobId] = useState<string | null>(null);
  const [loadingStats, setLoadingStats] = useState(true);
  const [loadingJobs, setLoadingJobs] = useState(true);
  const [syncing, setSyncing] = useState(false);

  const selectedJob = jobs.find((j) => j.id === selectedJobId) ?? null;

  const loadData = useCallback(async () => {
    setLoadingStats(true);
    setLoadingJobs(true);
    try {
      const [s, j] = await Promise.all([
        fetchDashboardStats(),
        fetchRecommendedJobs(),
      ]);
      setStats(s);
      setJobs(j);
      if (j.length > 0) setSelectedJobId(j[0].id);
    } finally {
      setLoadingStats(false);
      setLoadingJobs(false);
    }
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const handleSync = async () => {
    setSyncing(true);
    try {
      await syncJobSources();
      await loadData();
    } catch {
      // TODO: toast error
    } finally {
      setSyncing(false);
    }
  };

  const statItems = [
    {
      label: "Active Applications",
      value: stats ? String(stats.totalApplications) : "—",
      trend: stats?.totalApplications ? undefined : "Connect sources to track",
      color: COLORS.brand,
    },
    {
      label: "Scheduled Interviews",
      value: stats ? String(stats.scheduledInterviews) : "—",
      color: COLORS.successMid,
    },
    {
      label: "Offer Rate",
      value:
        stats?.offerRate != null ? `${stats.offerRate.toFixed(0)}%` : "—",
      color: COLORS.warningMid,
    },
    {
      label: "Avg ATS Score",
      value: stats?.avgAtsScore != null ? String(Math.round(stats.avgAtsScore)) : "—",
      color: "#8B5CF6",
    },
  ];

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
          padding: "20px 28px 0",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "flex-start",
        }}
      >
        <div>
          <h1
            style={{ fontSize: 18, fontWeight: 600, color: COLORS.text, margin: 0 }}
          >
            Dashboard
          </h1>
          <p style={{ fontSize: 13, color: COLORS.textMuted, margin: "4px 0 0" }}>
            Your job search overview at a glance
          </p>
        </div>
        <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
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
              opacity: syncing ? 0.6 : 1,
            }}
          >
            <Icon
              name="refresh-cw"
              size={13}
              color={COLORS.textMuted}
              style={syncing ? { animation: "spin 1s linear infinite" } : {}}
            />
            {syncing ? "Syncing…" : "Sync Jobs"}
          </button>
        </div>
      </div>

      {/* Stats */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(4, 1fr)",
          gap: 12,
          padding: "20px 28px 0",
        }}
      >
        {statItems.map((s, i) => (
          <StatCard
            key={i}
            label={s.label}
            value={s.value}
            trend={s.trend}
            color={s.color}
            loading={loadingStats}
          />
        ))}
      </div>

      {/* Feed split */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "380px 1fr",
          gap: 12,
          padding: "16px 28px 28px",
          flex: 1,
        }}
      >
        {/* Left: Job list */}
        <div style={{ display: "flex", flexDirection: "column" }}>
          <div
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              marginBottom: 10,
            }}
          >
            <span
              style={{ fontSize: 13.5, fontWeight: 600, color: COLORS.text }}
            >
              Recommended for You
            </span>
            <div style={{ display: "flex", gap: 6 }}>
              <button
                style={{
                  padding: "5px 10px",
                  borderRadius: 5,
                  border: `1px solid ${COLORS.border}`,
                  background: COLORS.card,
                  fontSize: 12,
                  color: COLORS.textMuted,
                  cursor: "pointer",
                  display: "flex",
                  alignItems: "center",
                  gap: 5,
                }}
              >
                <Icon name="filter" size={12} color={COLORS.textMuted} />
                Filter
              </button>
            </div>
          </div>

          <Card style={{ overflow: "hidden", flex: 1 }}>
            {loadingJobs ? (
              <div style={{ padding: "14px 16px", display: "flex", flexDirection: "column", gap: 12 }}>
                {[1, 2, 3].map((i) => (
                  <div key={i} style={{ display: "flex", flexDirection: "column", gap: 6 }}>
                    <Skeleton width="70%" height={14} />
                    <Skeleton width="45%" height={12} />
                    <div style={{ display: "flex", gap: 5 }}>
                      <Skeleton width={48} height={20} borderRadius={3} />
                      <Skeleton width={48} height={20} borderRadius={3} />
                    </div>
                  </div>
                ))}
              </div>
            ) : jobs.length === 0 ? (
              <EmptyState
                icon="briefcase"
                title="No job recommendations yet"
                description="Sync your LinkedIn, Naukri, or Indeed account to start seeing tailored job matches."
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
                    Sync Now
                  </button>
                }
              />
            ) : (
              jobs.map((job, i) => {
                const mc = job.matchScore != null ? matchColor(job.matchScore) : null;
                return (
                  <div
                    key={job.id}
                    onClick={() => setSelectedJobId(job.id)}
                    style={{
                      padding: "14px 16px",
                      cursor: "pointer",
                      borderBottom:
                        i < jobs.length - 1
                          ? `1px solid ${COLORS.borderLight}`
                          : "none",
                      background:
                        selectedJobId === job.id
                          ? COLORS.brandLight
                          : "transparent",
                      transition: "background 0.1s",
                    }}
                  >
                    <div
                      style={{
                        display: "flex",
                        justifyContent: "space-between",
                        alignItems: "flex-start",
                        marginBottom: 6,
                      }}
                    >
                      <div>
                        <div
                          style={{
                            fontSize: 13.5,
                            fontWeight: 500,
                            color: COLORS.text,
                          }}
                        >
                          {job.title}
                        </div>
                        <div
                          style={{
                            fontSize: 12,
                            color: COLORS.textMuted,
                            marginTop: 2,
                          }}
                        >
                          {job.company} · {job.location}
                        </div>
                      </div>
                      <div
                        style={{
                          display: "flex",
                          flexDirection: "column",
                          alignItems: "flex-end",
                          gap: 4,
                          flexShrink: 0,
                          marginLeft: 8,
                        }}
                      >
                        {mc && job.matchScore != null && (
                          <span
                            style={{
                              fontSize: 12,
                              fontWeight: 600,
                              padding: "2px 8px",
                              borderRadius: 4,
                              background: mc.bg,
                              color: mc.color,
                            }}
                          >
                            {job.matchScore}%
                          </span>
                        )}
                        <Badge
                          variant={job.source as "linkedin" | "naukri" | "indeed"}
                          size="xs"
                        >
                          {sourceLabel(job.source)}
                        </Badge>
                      </div>
                    </div>
                    <div style={{ display: "flex", gap: 4, flexWrap: "wrap" }}>
                      {job.tags.slice(0, 3).map((t, ti) => (
                        <span
                          key={ti}
                          style={{
                            fontSize: 11,
                            padding: "2px 6px",
                            borderRadius: 3,
                            background: COLORS.borderLight,
                            color: COLORS.textMuted,
                          }}
                        >
                          {t}
                        </span>
                      ))}
                      <span
                        style={{
                          fontSize: 11,
                          color: COLORS.textLight,
                          marginLeft: "auto",
                        }}
                      >
                        {new Date(job.postedAt).toLocaleDateString("en-IN", {
                          day: "numeric",
                          month: "short",
                        })}
                      </span>
                    </div>
                  </div>
                );
              })
            )}
          </Card>
        </div>

        {/* Right: Job detail */}
        <Card
          style={{
            padding: 0,
            display: "flex",
            flexDirection: "column",
            overflow: "hidden",
          }}
        >
          {!selectedJob ? (
            <EmptyState
              icon="file-text"
              title="Select a job to preview"
              description="Click any job on the left to see its full description, required skills, and ATS match score."
            />
          ) : (
            <>
              <div
                style={{
                  padding: "20px 24px 16px",
                  borderBottom: `1px solid ${COLORS.borderLight}`,
                }}
              >
                <div
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "flex-start",
                  }}
                >
                  <div>
                    <div
                      style={{
                        display: "flex",
                        alignItems: "center",
                        gap: 8,
                        marginBottom: 4,
                      }}
                    >
                      <span
                        style={{
                          fontSize: 16,
                          fontWeight: 600,
                          color: COLORS.text,
                        }}
                      >
                        {selectedJob.title}
                      </span>
                      <Badge
                        variant={
                          selectedJob.source as "linkedin" | "naukri" | "indeed"
                        }
                      >
                        {sourceLabel(selectedJob.source)}
                      </Badge>
                    </div>
                    <div
                      style={{ fontSize: 13, color: COLORS.textMuted }}
                    >
                      {selectedJob.company} · {selectedJob.location}
                      {selectedJob.salary ? ` · ${selectedJob.salary}` : ""}
                    </div>
                  </div>
                  <div style={{ display: "flex", gap: 8 }}>
                    <button
                      style={{
                        padding: "7px 14px",
                        borderRadius: 6,
                        border: `1px solid ${COLORS.border}`,
                        background: COLORS.card,
                        fontSize: 13,
                        color: COLORS.textMuted,
                        cursor: "pointer",
                        display: "flex",
                        alignItems: "center",
                        gap: 5,
                      }}
                    >
                      <Icon name="star" size={13} color={COLORS.textMuted} />
                      Save
                    </button>
                    <a
                      href={selectedJob.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      style={{
                        padding: "7px 16px",
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
                        textDecoration: "none",
                      }}
                    >
                      Apply{" "}
                      <Icon name="external-link" size={12} color="#fff" />
                    </a>
                  </div>
                </div>
                <div style={{ display: "flex", gap: 6, marginTop: 12, flexWrap: "wrap" }}>
                  {selectedJob.matchScore != null && (
                    <span
                      style={{
                        display: "inline-flex",
                        alignItems: "center",
                        gap: 5,
                        padding: "4px 10px",
                        borderRadius: 4,
                        border: `1px solid ${COLORS.border}`,
                        fontSize: 12,
                        color: COLORS.text,
                        fontWeight: 600,
                      }}
                    >
                      <Icon name="target" size={12} color={COLORS.brand} />
                      {selectedJob.matchScore}% ATS Match
                    </span>
                  )}
                  {selectedJob.tags.map((t, ti) => (
                    <span
                      key={ti}
                      style={{
                        fontSize: 12,
                        padding: "4px 10px",
                        borderRadius: 4,
                        background: COLORS.borderLight,
                        color: COLORS.textMuted,
                        border: `1px solid ${COLORS.border}`,
                      }}
                    >
                      {t}
                    </span>
                  ))}
                </div>
              </div>
              <div
                style={{
                  padding: "20px 24px",
                  flex: 1,
                  overflowY: "auto",
                }}
              >
                <div
                  style={{
                    fontSize: 13,
                    color: COLORS.text,
                    lineHeight: 1.8,
                    whiteSpace: "pre-line",
                  }}
                >
                  {selectedJob.description}
                </div>
              </div>
            </>
          )}
        </Card>
      </div>

      <style>{`
        @keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
        @keyframes shimmer { 0% { background-position: -200% 0; } 100% { background-position: 200% 0; } }
      `}</style>
    </div>
  );
};
