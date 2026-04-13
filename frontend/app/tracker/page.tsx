"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { useEffect } from "react";
import Navbar from "@/components/Navbar";
import toast from "react-hot-toast";
import {
  applicationsApi,
  authApi,
  aiApi,
  getStatusColor,
  formatDate,
  type Application,
  type ApplicationCreate,
  type User,
} from "@/lib/api";

const STATUSES = ["applied", "confirmed", "interview", "offer", "rejected", "ghosted"] as const;
type Status = typeof STATUSES[number];

export default function TrackerPage() {
  const router = useRouter();
  const qc = useQueryClient();
  const [showAddModal, setShowAddModal] = useState(false);
  const [activeApp, setActiveApp] = useState<Application | null>(null);

  useEffect(() => {
    if (!localStorage.getItem("token")) router.push("/login");
  }, [router]);

  const { data: currentUser } = useQuery({
    queryKey: ["me"],
    queryFn: () => authApi.me().then((r) => r.data),
  });

  const { data: apps = [], isLoading } = useQuery({
    queryKey: ["applications"],
    queryFn: () => applicationsApi.list().then((r) => r.data),
  });

  const createMutation = useMutation({
    mutationFn: (data: ApplicationCreate) => applicationsApi.create(data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["applications"] });
      setShowAddModal(false);
      toast.success("Application added!");
    },
    onError: (err: unknown) => {
      const error = err as { response?: { data?: { detail?: string } } };
      toast.error(error.response?.data?.detail || "Failed to add application");
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<Application> }) =>
      applicationsApi.update(id, data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["applications"] });
      setActiveApp(null);
      toast.success("Updated!");
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => applicationsApi.delete(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["applications"] });
      setActiveApp(null);
      toast.success("Deleted");
    },
  });

  // Group apps by status for Kanban view
  const byStatus = STATUSES.reduce((acc, s) => {
    acc[s] = (apps as Application[]).filter((a) => a.status === s);
    return acc;
  }, {} as Record<Status, Application[]>);

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <main className="max-w-full px-4 sm:px-6 py-8">
        <div className="flex items-center justify-between mb-8 max-w-7xl mx-auto">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Application Tracker</h1>
            <p className="text-gray-500 text-sm mt-0.5">
              {(apps as Application[]).length} applications total
            </p>
          </div>
          <button onClick={() => setShowAddModal(true)} className="btn-primary">
            + Add Application
          </button>
        </div>

        {/* Kanban Board */}
        {isLoading ? (
          <div className="flex gap-4 overflow-x-auto pb-6">
            {STATUSES.map((s) => (
              <div key={s} className="flex-shrink-0 w-72">
                <div className="bg-gray-100 rounded-xl p-3">
                  <div className="h-5 bg-gray-200 rounded animate-pulse mb-3 w-24" />
                  <div className="space-y-2">
                    {[1, 2].map((i) => (
                      <div key={i} className="bg-white rounded-lg p-3 h-16 animate-pulse" />
                    ))}
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (apps as Application[]).length === 0 ? (
          <div className="flex flex-col items-center justify-center py-24">
            <p className="text-5xl mb-4">📋</p>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">No applications yet</h3>
            <p className="text-gray-500 text-sm mb-6 text-center max-w-xs">
              Start tracking your job applications to see your Kanban board and get ghost risk scores.
            </p>
            <button onClick={() => setShowAddModal(true)} className="btn-primary">
              + Add Your First Application
            </button>
          </div>
        ) : (
          <div className="flex gap-4 overflow-x-auto pb-6">
            {STATUSES.map((status) => (
              <KanbanColumn
                key={status}
                status={status}
                apps={byStatus[status]}
                onCardClick={setActiveApp}
              />
            ))}
          </div>
        )}
      </main>

      {/* Add Application Modal */}
      {showAddModal && (
        <AddApplicationModal
          onClose={() => setShowAddModal(false)}
          onSubmit={(data) => createMutation.mutate(data)}
          loading={createMutation.isPending}
        />
      )}

      {/* Application Detail Modal */}
      {activeApp && (
        <ApplicationDetailModal
          app={activeApp}
          currentUser={currentUser}
          onClose={() => setActiveApp(null)}
          onStatusChange={(status) =>
            updateMutation.mutate({ id: activeApp.id, data: { status } })
          }
          onDelete={() => deleteMutation.mutate(activeApp.id)}
        />
      )}
    </div>
  );
}

function KanbanColumn({
  status,
  apps,
  onCardClick,
}: {
  status: Status;
  apps: Application[];
  onCardClick: (app: Application) => void;
}) {
  const labels: Record<Status, string> = {
    applied: "📤 Applied",
    confirmed: "✅ Confirmed",
    interview: "🎤 Interview",
    offer: "🎉 Offer",
    rejected: "❌ Rejected",
    ghosted: "👻 Ghosted",
  };

  return (
    <div className="flex-shrink-0 w-72">
      <div className="bg-gray-100 rounded-xl p-3">
        <div className="flex items-center justify-between mb-3">
          <h3 className="font-semibold text-gray-700 text-sm">{labels[status]}</h3>
          <span className="text-xs text-gray-500 bg-white px-2 py-0.5 rounded-full">
            {apps.length}
          </span>
        </div>
        <div className="space-y-2 min-h-32">
          {apps.map((app) => (
            <ApplicationCard
              key={app.id}
              app={app}
              onClick={() => onCardClick(app)}
            />
          ))}
        </div>
      </div>
    </div>
  );
}

function ApplicationCard({
  app,
  onClick,
}: {
  app: Application;
  onClick: () => void;
}) {
  const ghostLevel =
    app.ghost_score >= 70 ? "high" : app.ghost_score >= 40 ? "medium" : "low";
  const ghostColors = {
    low: "text-green-600",
    medium: "text-yellow-600",
    high: "text-red-600",
  };

  return (
    <button
      onClick={onClick}
      className="w-full text-left bg-white rounded-lg p-3 shadow-sm hover:shadow-md transition-shadow border border-gray-100"
    >
      <p className="font-semibold text-gray-900 text-sm truncate">
        {app.company_name}
      </p>
      <p className="text-gray-500 text-xs truncate mt-0.5">{app.job_title}</p>
      <div className="flex items-center justify-between mt-2">
        <span className="text-xs text-gray-400">{formatDate(app.applied_at)}</span>
        {app.ghost_score > 0 && (
          <span className={`text-xs font-medium ${ghostColors[ghostLevel]}`}>
            {app.ghost_score}% ghost
          </span>
        )}
      </div>
    </button>
  );
}

function AddApplicationModal({
  onClose,
  onSubmit,
  loading,
}: {
  onClose: () => void;
  onSubmit: (data: ApplicationCreate) => void;
  loading: boolean;
}) {
  const [form, setForm] = useState<ApplicationCreate>({
    company_name: "",
    job_title: "",
    linkedin_url: "",
    status: "applied",
    notes: "",
  });

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-xl w-full max-w-md p-6">
        <h2 className="text-lg font-bold mb-4">Add New Application</h2>
        <form
          onSubmit={(e) => {
            e.preventDefault();
            onSubmit(form);
          }}
          className="space-y-4"
        >
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Company Name *
            </label>
            <input
              className="input"
              placeholder="e.g. Netsol Technologies"
              value={form.company_name}
              onChange={(e) => setForm({ ...form, company_name: e.target.value })}
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Job Title *
            </label>
            <input
              className="input"
              placeholder="e.g. AI Engineer Intern"
              value={form.job_title}
              onChange={(e) => setForm({ ...form, job_title: e.target.value })}
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              LinkedIn URL
            </label>
            <input
              className="input"
              placeholder="https://linkedin.com/jobs/..."
              value={form.linkedin_url}
              onChange={(e) => setForm({ ...form, linkedin_url: e.target.value })}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Notes
            </label>
            <textarea
              className="input resize-none"
              rows={2}
              placeholder="Any notes about this application…"
              value={form.notes}
              onChange={(e) => setForm({ ...form, notes: e.target.value })}
            />
          </div>
          <div className="flex gap-3 pt-2">
            <button type="button" onClick={onClose} className="btn-secondary flex-1">
              Cancel
            </button>
            <button type="submit" className="btn-primary flex-1" disabled={loading}>
              {loading ? "Adding…" : "Add Application"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

function ApplicationDetailModal({
  app,
  currentUser,
  onClose,
  onStatusChange,
  onDelete,
}: {
  app: Application;
  currentUser?: User;
  onClose: () => void;
  onStatusChange: (status: string) => void;
  onDelete: () => void;
}) {
  const [generating, setGenerating] = useState(false);
  const [followUpEmails, setFollowUpEmails] = useState<null | {
    variant_a: { subject: string; body: string; tone: string };
    variant_b: { subject: string; body: string; tone: string };
    variant_c: { subject: string; body: string; tone: string };
  }>(null);

  const handleGenerateFollowUp = async () => {
    setGenerating(true);
    try {
      const res = await aiApi.followupEmail({
        applicant_name: currentUser?.name || "Applicant",
        company: app.company_name,
        job_title: app.job_title,
        days_since_applied: app.days_since_contact || 7,
        prior_contact: app.status === "confirmed",
        application_id: app.id,
      });
      setFollowUpEmails(res.data);
    } catch {
      toast.error("Failed to generate emails. Try again.");
    } finally {
      setGenerating(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-xl w-full max-w-2xl p-6 max-h-[90vh] overflow-y-auto">
        <div className="flex items-start justify-between mb-4">
          <div>
            <h2 className="text-xl font-bold">{app.company_name}</h2>
            <p className="text-gray-500">{app.job_title}</p>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 text-xl"
          >
            ×
          </button>
        </div>

        {/* Status */}
        <div className="mb-4">
          <p className="text-sm font-medium text-gray-700 mb-2">Status</p>
          <div className="flex flex-wrap gap-2">
            {STATUSES.map((s) => (
              <button
                key={s}
                onClick={() => onStatusChange(s)}
                className={`badge cursor-pointer ${
                  app.status === s
                    ? getStatusColor(s) + " ring-2 ring-offset-1 ring-brand-500"
                    : "bg-gray-100 text-gray-600 hover:bg-gray-200"
                }`}
              >
                {s}
              </button>
            ))}
          </div>
        </div>

        {/* Ghost Score */}
        <div className="bg-gray-50 rounded-lg p-3 mb-4">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-gray-700">Ghost Risk Score</span>
            <span
              className={`text-lg font-bold ${
                app.ghost_score >= 70
                  ? "text-red-600"
                  : app.ghost_score >= 40
                  ? "text-yellow-600"
                  : "text-green-600"
              }`}
            >
              {app.ghost_score}%{app.ghost_score >= 70 ? " 👻" : ""}
            </span>
          </div>
          <div className="mt-2 h-2 bg-gray-200 rounded-full overflow-hidden">
            <div
              className={`h-full rounded-full ${
                app.ghost_score >= 70
                  ? "bg-red-500"
                  : app.ghost_score >= 40
                  ? "bg-yellow-500"
                  : "bg-green-500"
              }`}
              style={{ width: `${app.ghost_score}%` }}
            />
          </div>
        </div>

        {/* Notes */}
        {app.notes && (
          <div className="mb-4">
            <p className="text-sm font-medium text-gray-700 mb-1">Notes</p>
            <p className="text-sm text-gray-600 bg-gray-50 rounded-lg p-3">
              {app.notes}
            </p>
          </div>
        )}

        {/* AI Follow-Up */}
        <div className="mb-4">
          <button
            onClick={handleGenerateFollowUp}
            disabled={generating}
            className="btn-secondary w-full flex items-center justify-center gap-2"
          >
            <span>✉️</span>
            {generating ? "Generating emails…" : "Generate Follow-Up Emails (AI)"}
          </button>

          {followUpEmails && (
            <div className="mt-3 space-y-3">
              {(["variant_a", "variant_b", "variant_c"] as const).map((v) => (
                <div
                  key={v}
                  className="border border-gray-200 rounded-lg p-3 text-sm"
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-medium text-gray-700 capitalize">
                      {followUpEmails[v].tone}
                    </span>
                    <button
                      onClick={() => {
                        navigator.clipboard.writeText(
                          `Subject: ${followUpEmails[v].subject}\n\n${followUpEmails[v].body}`
                        );
                        toast.success("Copied!");
                      }}
                      className="text-xs text-brand-600 hover:underline"
                    >
                      Copy
                    </button>
                  </div>
                  <p className="text-gray-500 text-xs mb-1">
                    <strong>Subject:</strong> {followUpEmails[v].subject}
                  </p>
                  <p className="text-gray-600 text-xs whitespace-pre-wrap">
                    {followUpEmails[v].body}
                  </p>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Actions */}
        <div className="flex gap-3 pt-2 border-t border-gray-100">
          <button
            onClick={onDelete}
            className="text-red-500 hover:text-red-700 text-sm font-medium"
          >
            Delete
          </button>
          <div className="flex-1" />
          <button onClick={onClose} className="btn-secondary">
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
