/**
 * HireLoop PK — Centralized API client
 * All HTTP calls go through this file using Axios + React Query.
 */

import axios from "axios";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// ─── Axios Instance ─────────────────────────────────────────────────────────

export const api = axios.create({
  baseURL: API_URL,
  headers: { "Content-Type": "application/json" },
});

// Attach JWT to every request automatically
api.interceptors.request.use((config) => {
  const token = typeof window !== "undefined" ? localStorage.getItem("token") : null;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Redirect to login on 401
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401 && typeof window !== "undefined") {
      localStorage.removeItem("token");
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

// ─── Auth ────────────────────────────────────────────────────────────────────

export interface RegisterPayload {
  email: string;
  name: string;
  password: string;
}

export interface LoginPayload {
  email: string;
  password: string;
}

export interface User {
  id: string;
  email: string;
  name: string;
  role: string;
  subscription_tier: string;
  email_verified: boolean;
  onboarded: boolean;
  created_at: string;
}

export const authApi = {
  register: (data: RegisterPayload) =>
    api.post<{ access_token: string }>("/auth/register", data),

  login: (data: LoginPayload) =>
    api.post<{ access_token: string }>("/auth/login", data),

  me: () => api.get<User>("/auth/me"),

  googleLogin: () => {
    window.location.href = `${API_URL}/auth/google`;
  },
};

// ─── Applications ─────────────────────────────────────────────────────────────

export interface Application {
  id: string;
  user_id: string;
  company_name: string;
  job_title: string;
  linkedin_url?: string;
  status: "applied" | "confirmed" | "interview" | "offer" | "rejected" | "ghosted";
  applied_at?: string;
  last_contact_at?: string;
  ghost_score: number;
  days_since_contact: number;
  notes?: string;
  created_at: string;
}

export interface ApplicationCreate {
  company_name: string;
  job_title: string;
  linkedin_url?: string;
  status?: string;
  applied_at?: string;
  notes?: string;
}

export interface ApplicationUpdate {
  company_name?: string;
  job_title?: string;
  linkedin_url?: string;
  status?: string;
  notes?: string;
}

export const applicationsApi = {
  list: (status?: string) =>
    api.get<Application[]>("/applications/", { params: { status } }),

  get: (id: string) => api.get<Application>(`/applications/${id}`),

  create: (data: ApplicationCreate) =>
    api.post<Application>("/applications/", data),

  update: (id: string, data: ApplicationUpdate) =>
    api.patch<Application>(`/applications/${id}`, data),

  delete: (id: string) => api.delete(`/applications/${id}`),
};

// ─── AI Features ──────────────────────────────────────────────────────────────

export const aiApi = {
  ghostScore: (data: {
    company_name: string;
    days_since_contact: number;
    industry?: string;
    application_id?: string;
  }) => api.post("/ai/ghost-score", data),

  followupEmail: (data: {
    applicant_name: string;
    company: string;
    job_title: string;
    days_since_applied: number;
    prior_contact: boolean;
    application_id?: string;
  }) => api.post("/ai/followup-email", data),

  interviewPrep: (data: { job_description: string }) =>
    api.post("/ai/interview-prep", data),

  companySafety: (data: {
    company_name: string;
    job_type: string;
    claimed_location: string;
    job_description: string;
  }) => api.post("/ai/company-safety", data),

  weeklySummary: (data?: { applications?: unknown[] }) =>
    api.post("/ai/weekly-summary", data || {}),
};

// ─── Jobs ─────────────────────────────────────────────────────────────────────

export interface JobListing {
  id: string;
  title: string;
  company: string;
  location?: string;
  remote: boolean;
  paid: boolean;
  stipend_pkr?: number;
  domain?: string;
  source: string;
  safety_score: number;
  posted_at?: string;
  scraped_at: string;
}

export const jobsApi = {
  list: (params?: {
    remote?: boolean;
    paid?: boolean;
    domain?: string;
    city?: string;
    skip?: number;
    limit?: number;
  }) => api.get<JobListing[]>("/jobs/", { params }),
};

// ─── Helpers ──────────────────────────────────────────────────────────────────

export function getGhostScoreColor(score: number): string {
  if (score < 40) return "text-green-600";
  if (score < 70) return "text-yellow-600";
  return "text-red-600";
}

export function getStatusColor(status: string): string {
  const colors: Record<string, string> = {
    applied: "bg-blue-100 text-blue-800",
    confirmed: "bg-green-100 text-green-800",
    interview: "bg-purple-100 text-purple-800",
    offer: "bg-emerald-100 text-emerald-800",
    rejected: "bg-red-100 text-red-800",
    ghosted: "bg-gray-100 text-gray-800",
  };
  return colors[status] || "bg-gray-100 text-gray-800";
}

export function formatDate(dateStr?: string): string {
  if (!dateStr) return "—";
  return new Date(dateStr).toLocaleDateString("en-PK", {
    day: "numeric",
    month: "short",
    year: "numeric",
  });
}
