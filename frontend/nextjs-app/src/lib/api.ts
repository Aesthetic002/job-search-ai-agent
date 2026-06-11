/**
 * API Client — Wired to real FastAPI microservices.
 *
 * Architecture:
 *   - All calls go through Next.js API rewrites (see next.config.ts) to avoid
 *     CORS issues and keep service URLs out of the browser bundle.
 *   - JWT token is read from localStorage (set by the auth flow) and injected
 *     as Authorization: Bearer <token> on every authenticated request.
 *   - Graceful fallback: if the backend is down the UI shows empty states, not crashes.
 *
 * Service port map (local dev):
 *   Auth Service        → localhost:8001  → /api/auth/*
 *   Jobs Service        → localhost:8002  → /api/jobs/*
 *   Resume Service      → localhost:8003  → /api/resumes/*
 *   Interview Service   → localhost:8004  → /api/interview/*
 *   Analytics Service   → localhost:8005  → /api/analytics/*
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
  SalaryBenchmark,
  CompanyResearch,
} from "./types";

// ─── Auth Helpers ────────────────────────────────────────────────────────────

/** Read the JWT token stored after login. */
function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("access_token");
}

/** Standard auth + JSON headers. */
function authHeaders(): HeadersInit {
  const token = getToken();
  return {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
}

// ─── Core fetch wrapper ───────────────────────────────────────────────────────

async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(path, {
    headers: { ...authHeaders(), ...options?.headers },
    ...options,
  });

  if (res.status === 401) {
    // Token expired — clear and force re-login
    localStorage.removeItem("access_token");
    throw new Error("Session expired. Please log in again.");
  }

  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail ?? body.message ?? detail;
    } catch {
      // ignore parse error
    }
    throw new Error(`[${res.status}] ${detail}`);
  }

  // 204 No Content
  if (res.status === 204) return undefined as unknown as T;
  return res.json() as Promise<T>;
}

// ─── Dashboard ───────────────────────────────────────────────────────────────

export async function fetchDashboardStats(): Promise<DashboardStats> {
  try {
    return await apiFetch<DashboardStats>("/api/analytics/dashboard");
  } catch {
    // Return safe defaults so the UI renders an empty-but-working dashboard
    return {
      totalApplications: 0,
      scheduledInterviews: 0,
      avgAtsScore: null,
      offerRate: null,
    };
  }
}

// ─── Jobs ─────────────────────────────────────────────────────────────────────

export interface JobsFilter {
  query?: string;
  source?: string;
  location?: string;
  // Indian-specific filters
  minSalaryLpa?: number;    // Minimum salary in Lakhs Per Annum
  maxSalaryLpa?: number;    // Maximum salary in LPA
  workMode?: string;        // "remote" | "hybrid" | "onsite" | "any"
  noticePeriod?: string;    // "immediate" | "15days" | "30days" | "60days" | "90days" | "any"
  // Pagination
  page?: number;
  limit?: number;
  tags?: string[];
}

function buildQS(filter: JobsFilter): string {
  const params = new URLSearchParams();
  if (filter.query) params.set("query", filter.query);
  if (filter.source) params.set("source", filter.source);
  if (filter.location) params.set("location", filter.location);
  if (filter.minSalaryLpa != null) params.set("min_salary_lpa", String(filter.minSalaryLpa));
  if (filter.maxSalaryLpa != null) params.set("max_salary_lpa", String(filter.maxSalaryLpa));
  if (filter.workMode && filter.workMode !== "any") params.set("work_mode", filter.workMode);
  if (filter.noticePeriod && filter.noticePeriod !== "any") params.set("notice_period", filter.noticePeriod);
  if (filter.page) params.set("page", String(filter.page));
  if (filter.limit) params.set("limit", String(filter.limit));
  if (filter.tags?.length) params.set("tags", filter.tags.join(","));
  return params.toString() ? `?${params.toString()}` : "";
}

export async function fetchRecommendedJobs(filter?: JobsFilter): Promise<Job[]> {
  try {
    const qs = filter ? buildQS(filter) : "";
    return await apiFetch<Job[]>(`/api/jobs/recommended${qs}`);
  } catch {
    return [];
  }
}

export async function searchJobs(filter: JobsFilter): Promise<Job[]> {
  try {
    const qs = buildQS(filter);
    return await apiFetch<Job[]>(`/api/jobs/search${qs}`);
  } catch {
    return [];
  }
}

export async function syncJobSources(): Promise<{ synced: number }> {
  return apiFetch<{ synced: number }>("/api/jobs/sync", { method: "POST" });
}

// ─── Applications ────────────────────────────────────────────────────────────

export async function fetchApplications(): Promise<Application[]> {
  try {
    return await apiFetch<Application[]>("/api/applications");
  } catch {
    return [];
  }
}

export async function createApplication(
  data: Omit<Application, "id" | "appliedAt">
): Promise<Application> {
  return apiFetch<Application>("/api/applications", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function updateApplicationStage(
  id: string,
  stage: ApplicationStage
): Promise<Application> {
  return apiFetch<Application>(`/api/applications/${id}/stage`, {
    method: "PATCH",
    body: JSON.stringify({ stage }),
  });
}

export async function deleteApplication(id: string): Promise<void> {
  return apiFetch<void>(`/api/applications/${id}`, { method: "DELETE" });
}

// ─── Resume ──────────────────────────────────────────────────────────────────

/** Upload a resume PDF/DOCX to the Resume Service. Returns the new resume_id. */
export async function uploadResume(file: File): Promise<{ resumeId: string }> {
  const form = new FormData();
  form.append("file", file);

  const token = getToken();
  const res = await fetch("/api/resumes/upload", {
    method: "POST",
    headers: token ? { Authorization: `Bearer ${token}` } : {},
    body: form,
    // Do NOT set Content-Type — browser sets it with boundary for FormData
  });

  if (!res.ok) {
    let detail = res.statusText;
    try { detail = (await res.json()).detail ?? detail; } catch { /* ignore */ }
    throw new Error(`Upload failed: ${detail}`);
  }

  const data = await res.json();
  // Normalise backend's snake_case → camelCase for the frontend
  return { resumeId: data.resume_id ?? data.resumeId };
}

/** Fetch AI-structured resume data from Firestore after analysis. */
export async function fetchParsedResume(resumeId: string): Promise<ParsedResume> {
  const data = await apiFetch<{
    resume_id: string;
    structured_data: {
      skills?: { technical_skills?: string[] };
      experience?: Array<{ title?: string; company?: string; duration?: string; responsibilities?: string[] }>;
      education?: Array<{ degree?: string; institution?: string; graduation_year?: string }>;
    };
    parsed_text?: string;
  }>(`/api/resumes/${resumeId}`);

  // Map backend snake_case shape → frontend types.ts shape
  return {
    resumeId: data.resume_id,
    rawText: data.parsed_text ?? "",
    skills: data.structured_data?.skills?.technical_skills ?? [],
    experience: (data.structured_data?.experience ?? []).map((e) => ({
      role: e.title ?? "",
      company: e.company ?? "",
      period: e.duration ?? "",
      bullets: e.responsibilities ?? [],
    })),
    education: (data.structured_data?.education ?? []).map((e) => ({
      degree: e.degree ?? "",
      institution: e.institution ?? "",
      year: e.graduation_year ?? "",
    })),
  };
}

/** Trigger AI resume analysis (resume_parser.py) — saves structured_data to Firestore. */
export async function analyzeResume(resumeId: string): Promise<ParsedResume> {
  await apiFetch<unknown>(`/api/resumes/${resumeId}/analyze`, { method: "POST" });
  return fetchParsedResume(resumeId);
}

/** Run ATS scoring against a job description. */
export async function runATSAnalysis(
  resumeId: string,
  jobDescription: string
): Promise<ATSResult> {
  const data = await apiFetch<{
    resume_id: string;
    ats_report: {
      overall_score: number;
      keyword_matches?: Array<{ keyword: string; found: boolean }>;
      recommendations?: string[];
      course_recommendations?: string[];
    };
  }>(`/api/resumes/${resumeId}/score`, {
    method: "POST",
    body: JSON.stringify({ job_description: jobDescription }),
  });

  const report = data.ats_report;
  return {
    resumeId: data.resume_id,
    score: report.overall_score,
    matchedKeywords: (report.keyword_matches ?? [])
      .filter((k) => k.found)
      .map((k) => k.keyword),
    missingKeywords: (report.keyword_matches ?? [])
      .filter((k) => !k.found)
      .map((k) => k.keyword),
    courseRecommendations: report.course_recommendations ?? [],
    suggestedRewrite: undefined,
    tip: report.recommendations?.[0],
  };
}

// ─── Interview ───────────────────────────────────────────────────────────────

/**
 * Generate AI-powered interview questions from the Interview Service.
 * Maps the backend's InterviewQuestionBank shape → frontend InterviewQuestion[].
 */
export async function fetchInterviewQuestions(
  roundType: string,
  jobTitle: string,
  resumeSummary?: string
): Promise<InterviewQuestion[]> {
  const data = await apiFetch<{
    questions: Array<{
      question: string;
      category: string;
      difficulty: string;
      hint?: string;
      expected_topics?: string[];
    }>;
    preparation_tips?: string[];
  }>("/api/interview/generate", {
    method: "POST",
    body: JSON.stringify({
      job_title: jobTitle,
      // Use the round type as the resume_summary when no resume is available
      resume_summary: resumeSummary ?? `Candidate is applying for a ${jobTitle} position. Focus on ${roundType} questions.`,
      num_questions: 8,
    }),
  });

  // Map backend shape → frontend InterviewQuestion type
  return data.questions.map((q, i) => ({
    id: `q-${i}-${Date.now()}`,
    text: q.question,
    keyPoints: q.expected_topics ?? [],
    tips: q.hint ? [q.hint] : [],
    category: q.category,
  }));
}

/**
 * Evaluate a candidate's answer using the Interview Service.
 * Maps the backend's AnswerEvaluation shape → frontend InterviewEvaluation.
 */
export async function evaluateAnswer(
  questionId: string,
  answer: string,
  jobTitle: string,
  question?: string,
  category?: string,
  expectedTopics?: string[]
): Promise<InterviewEvaluation> {
  const data = await apiFetch<{
    evaluation: {
      score: number;
      verdict: string;
      strengths: string[];
      improvements: string[];
      ideal_answer_summary: string;
      missing_topics?: string[];
      communication_feedback?: string;
      star_compliance?: {
        situation_present: boolean;
        task_present: boolean;
        action_present: boolean;
        result_present: boolean;
        star_score: number;
      } | null;
    };
  }>("/api/interview/evaluate", {
    method: "POST",
    body: JSON.stringify({
      question: question ?? `Question ID: ${questionId}`,
      candidate_answer: answer,
      job_title: jobTitle,
      category: category ?? "General",
      expected_topics: expectedTopics ?? [],
    }),
  });

  const ev = data.evaluation;
  return {
    questionId,
    score: ev.score,
    strengths: ev.strengths,
    improvements: ev.improvements,
    suggestedAnswer: ev.ideal_answer_summary,
  };
}

export async function chatNegotiation(
  jobTitle: string,
  targetSalaryLpa: number,
  history: Array<{ role: string; content: string }>,
  userMessage: string
): Promise<{ aiResponse: string; feedback: string; sentiment: string }> {
  const data = await apiFetch<any>("/api/interview/negotiation/chat", {
    method: "POST",
    body: JSON.stringify({
      job_title: jobTitle,
      target_salary_lpa: targetSalaryLpa,
      history,
      user_message: userMessage,
    }),
  });

  return {
    aiResponse: data.ai_response,
    feedback: data.feedback,
    sentiment: data.sentiment,
  };
}

// ─── Connected Sources ────────────────────────────────────────────────────────

export async function fetchConnectedSources(): Promise<ConnectedSource[]> {
  try {
    return await apiFetch<ConnectedSource[]>("/api/sources");
  } catch {
    return [];
  }
}

export async function connectSource(source: string): Promise<ConnectedSource> {
  return apiFetch<ConnectedSource>("/api/sources/connect", {
    method: "POST",
    body: JSON.stringify({ source }),
  });
}

// ─── Insights ────────────────────────────────────────────────────────

export async function fetchSalaryBenchmark(role: string, location: string): Promise<SalaryBenchmark> {
  const data = await apiFetch<any>(`/api/jobs/insights/salary?role=${encodeURIComponent(role)}&location=${encodeURIComponent(location)}`);
  return {
    minLpa: data.min_lpa,
    midLpa: data.mid_lpa,
    maxLpa: data.max_lpa,
    confidence: data.confidence,
    summary: data.summary,
  };
}

export async function fetchCompanyResearch(companyName: string): Promise<CompanyResearch> {
  const data = await apiFetch<any>(`/api/jobs/insights/company?name=${encodeURIComponent(companyName)}`);
  return {
    companyName: data.company_name,
    cultureSummary: data.culture_summary,
    interviewProcess: data.interview_process,
    pros: data.pros,
    cons: data.cons,
  };
}

