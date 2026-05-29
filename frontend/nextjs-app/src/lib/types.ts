// ─── Shared TypeScript Interfaces ───────────────────────────────────────────

export type JobSource = "linkedin" | "naukri" | "indeed" | "other";
export type ApplicationStage =
  | "applied"
  | "screening"
  | "interviewing"
  | "offer"
  | "rejected"
  | "archived";
export type RoundType =
  | "behavioral"
  | "technical"
  | "system-design"
  | "hr";
export type ResumeStatus = "uploading" | "parsing" | "ready" | "error";

export interface Job {
  id: string;
  title: string;
  company: string;
  location: string;
  salary?: string;
  source: JobSource;
  tags: string[];
  postedAt: string; // ISO string
  url: string;
  description: string;
  matchScore?: number; // 0-100
}

export interface Application {
  id: string;
  jobTitle: string;
  company: string;
  location?: string;
  stage: ApplicationStage;
  appliedAt: string; // ISO string
  source: JobSource;
  matchScore?: number;
  notes?: string;
  nextAction?: string;
  url?: string;
}

export interface ResumeFile {
  id: string;
  name: string;
  sizeBytes: number;
  uploadedAt: string; // ISO string
  status: ResumeStatus;
}

export interface ParsedResume {
  resumeId: string;
  rawText: string;
  skills: string[];
  experience: ExperienceEntry[];
  education: EducationEntry[];
}

export interface ExperienceEntry {
  role: string;
  company: string;
  period: string;
  bullets: string[];
}

export interface EducationEntry {
  degree: string;
  institution: string;
  year: string;
  gpa?: string;
}

export interface ATSResult {
  resumeId: string;
  jobId?: string;
  score: number; // 0-100
  matchedKeywords: string[];
  missingKeywords: string[];
  suggestedRewrite?: string;
  tip?: string;
}

export interface DashboardStats {
  totalApplications: number;
  scheduledInterviews: number;
  avgAtsScore: number | null;
  offerRate: number | null; // percentage 0-100
}

export interface InterviewSession {
  id: string;
  jobTitle: string;
  company: string;
  roundType: RoundType;
  startedAt: string;
  questions: InterviewQuestion[];
  currentIndex: number;
  answers: Record<string, string>;
}

export interface InterviewQuestion {
  id: string;
  text: string;
  keyPoints: string[];
  tips: string[];
  category: string;
}

export interface InterviewEvaluation {
  questionId: string;
  score: number;
  strengths: string[];
  improvements: string[];
  suggestedAnswer: string;
}

export interface ConnectedSource {
  source: JobSource;
  connectedAt: string;
  lastSyncedAt?: string;
  status: "active" | "error" | "expired";
}
