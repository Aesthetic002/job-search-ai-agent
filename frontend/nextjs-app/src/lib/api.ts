/**
 * API Client — Production stub layer.
 *
 * All functions here return typed data and are ready for real backend wiring.
 * Replace the stub implementations with actual fetch calls once the backend
 * endpoints are deployed.
 *
 * Backend base URL is read from NEXT_PUBLIC_API_URL env var.
 */

import type {
  Job,
  Application,
  ApplicationStage,
  DashboardStats,
  ParsedResume,
  ATSResult,
  InterviewQuestion,
  InterviewEvaluation,
  ConnectedSource,
} from "./types";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "";

async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json", ...options?.headers },
    ...options,
  });
  if (!res.ok) {
    const text = await res.text().catch(() => res.statusText);
    throw new Error(`API ${path} failed ${res.status}: ${text}`);
  }
  return res.json() as Promise<T>;
}

// ─── Dashboard ───────────────────────────────────────────────────────────────

export async function fetchDashboardStats(): Promise<DashboardStats> {
  // TODO: return apiFetch<DashboardStats>("/api/dashboard/stats");
  return {
    totalApplications: 0,
    scheduledInterviews: 0,
    avgAtsScore: null,
    offerRate: null,
  };
}

// ─── Jobs ─────────────────────────────────────────────────────────────────────

export interface JobsFilter {
  query?: string;
  source?: string;
  location?: string;
  minSalary?: number;
  tags?: string[];
  page?: number;
  limit?: number;
}

export async function fetchRecommendedJobs(_filter?: JobsFilter): Promise<Job[]> {
  // TODO: return apiFetch<Job[]>(`/api/jobs/recommended?${qs}`);
  return [];
}

export async function searchJobs(_filter: JobsFilter): Promise<Job[]> {
  // TODO: return apiFetch<Job[]>(`/api/jobs/search?${qs}`);
  return [];
}

export async function syncJobSources(): Promise<{ synced: number }> {
  // TODO: return apiFetch<{ synced: number }>("/api/jobs/sync", { method: "POST" });
  return { synced: 0 };
}

// ─── Applications ────────────────────────────────────────────────────────────

export async function fetchApplications(): Promise<Application[]> {
  // TODO: return apiFetch<Application[]>("/api/applications");
  return [];
}

export async function createApplication(
  data: Omit<Application, "id" | "appliedAt">
): Promise<Application> {
  // TODO: return apiFetch<Application>("/api/applications", { method: "POST", body: JSON.stringify(data) });
  return {
    id: crypto.randomUUID(),
    appliedAt: new Date().toISOString(),
    ...data,
  };
}

export async function updateApplicationStage(
  id: string,
  stage: ApplicationStage
): Promise<Application> {
  // TODO: return apiFetch<Application>(`/api/applications/${id}/stage`, { method: "PATCH", body: JSON.stringify({ stage }) });
  throw new Error(`updateApplicationStage(${id}, ${stage}) — backend not yet connected`);
}

export async function deleteApplication(id: string): Promise<void> {
  // TODO: return apiFetch<void>(`/api/applications/${id}`, { method: "DELETE" });
  console.warn(`deleteApplication(${id}) — backend not yet connected`);
}

// ─── Resume ──────────────────────────────────────────────────────────────────

export async function uploadResume(file: File): Promise<{ resumeId: string }> {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch(`${BASE_URL}/api/resume/upload`, {
    method: "POST",
    body: form,
  });
  if (!res.ok) throw new Error(`Upload failed: ${res.statusText}`);
  return res.json();
}

export async function fetchParsedResume(resumeId: string): Promise<ParsedResume> {
  // TODO: return apiFetch<ParsedResume>(`/api/resume/${resumeId}/parsed`);
  throw new Error(`fetchParsedResume(${resumeId}) — backend not yet connected`);
}

export async function runATSAnalysis(
  resumeId: string,
  jobDescription: string
): Promise<ATSResult> {
  // TODO: return apiFetch<ATSResult>("/api/resume/ats", { method: "POST", body: JSON.stringify({ resumeId, jobDescription }) });
  throw new Error(`runATSAnalysis — backend not yet connected`);
}

// ─── Interview ───────────────────────────────────────────────────────────────

export async function fetchInterviewQuestions(
  roundType: string,
  jobTitle: string
): Promise<InterviewQuestion[]> {
  // TODO: return apiFetch<InterviewQuestion[]>(`/api/interview/questions?round=${roundType}&role=${encodeURIComponent(jobTitle)}`);
  return [];
}

export async function evaluateAnswer(
  questionId: string,
  answer: string,
  jobTitle: string
): Promise<InterviewEvaluation> {
  // TODO: return apiFetch<InterviewEvaluation>("/api/interview/evaluate", { method: "POST", body: JSON.stringify({ questionId, answer, jobTitle }) });
  throw new Error("evaluateAnswer — backend not yet connected");
}

// ─── Connected Sources ────────────────────────────────────────────────────────

export async function fetchConnectedSources(): Promise<ConnectedSource[]> {
  // TODO: return apiFetch<ConnectedSource[]>("/api/sources");
  return [];
}

export async function connectSource(source: string): Promise<ConnectedSource> {
  // TODO: return apiFetch<ConnectedSource>("/api/sources/connect", { method: "POST", body: JSON.stringify({ source }) });
  throw new Error(`connectSource(${source}) — backend not yet connected`);
}
