"use client";

import { useQuery } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { useEffect } from "react";
import Navbar from "@/components/Navbar";
import {
  applicationsApi,
  aiApi,
  getStatusColor,
  formatDate,
  type Application,
} from "@/lib/api";
import Link from "next/link";

export default function DashboardPage() {
  const router = useRouter();

  // Redirect to login if no token
  useEffect(() => {
    if (!localStorage.getItem("token")) {
      router.push("/login");
    }
  }, [router]);

  const { data: apps = [], isLoading } = useQuery({
    queryKey: ["applications"],
    queryFn: () => applicationsApi.list().then((r) => r.data),
  });

  const { data: summary, isLoading: summaryLoading } = useQuery({
    queryKey: ["weekly-summary"],
    queryFn: () => aiApi.weeklySummary().then((r) => r.data),
    staleTime: 5 * 60 * 1000,
  });

  // Stats
  const total = apps.length;
  const interviews = apps.filter((a: Application) => a.status === "interview").length;
  const highRisk = apps.filter((a: Application) => a.ghost_score >= 70).length;
  const responseRate =
    total > 0
      ? Math.round(
          (apps.filter((a: Application) => ["confirmed", "interview", "offer"].includes(a.status))
            .length /
            total) *
            100
        )
      : 0;

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <main className="max-w-7xl mx-auto px-4 sm:px-6 py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
            <p className="text-gray-500 text-sm mt-0.5">
              Your job search intelligence center
            </p>
          </div>
          <Link href="/tracker" className="btn-primary">
            + Add Application
          </Link>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          <StatCard label="Total Applications" value={total} emoji="📋" />
          <StatCard label="Response Rate" value={`${responseRate}%`} emoji="📬" />
          <StatCard label="Interviews" value={interviews} emoji="🎤" />
          <StatCard
            label="High Ghost Risk"
            value={highRisk}
            emoji="👻"
            valueClass={highRisk > 0 ? "text-red-600" : "text-green-600"}
          />
        </div>

        {/* Weekly Summary */}
        {summary && (
          <div className="card mb-8 bg-gradient-to-r from-brand-50 to-white border-brand-100">
            <div className="flex items-start gap-3">
              <span className="text-2xl">🤖</span>
              <div>
                <h2 className="font-semibold text-gray-900 mb-1">
                  Weekly AI Summary
                </h2>
                <p className="text-gray-600 text-sm leading-relaxed">
                  {summary.summary_paragraph}
                </p>
                {summary.motivational_line && (
                  <p className="mt-2 text-brand-600 text-sm font-medium italic">
                    &ldquo;{summary.motivational_line}&rdquo;
                  </p>
                )}
                {summary.top_actions_this_week?.length > 0 && (
                  <div className="mt-3">
                    <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1">
                      Top Actions
                    </p>
                    <ul className="space-y-1">
                      {summary.top_actions_this_week.map(
                        (action: string, i: number) => (
                          <li
                            key={i}
                            className="text-sm text-gray-600 flex items-center gap-1.5"
                          >
                            <span className="text-brand-500">→</span> {action}
                          </li>
                        )
                      )}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Recent Applications */}
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-semibold text-gray-900">Recent Applications</h2>
            <Link
              href="/tracker"
              className="text-sm text-brand-600 hover:underline"
            >
              View all →
            </Link>
          </div>

          {isLoading ? (
            <div className="text-center py-8 text-gray-400">Loading…</div>
          ) : apps.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-gray-400 mb-4">No applications yet.</p>
              <Link href="/tracker" className="btn-primary">
                Add your first application
              </Link>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-left text-gray-500 border-b border-gray-100">
                    <th className="pb-3 font-medium">Company</th>
                    <th className="pb-3 font-medium">Role</th>
                    <th className="pb-3 font-medium">Status</th>
                    <th className="pb-3 font-medium">Ghost Risk</th>
                    <th className="pb-3 font-medium">Applied</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-50">
                  {apps.slice(0, 10).map((app: Application) => (
                    <tr key={app.id} className="hover:bg-gray-50 transition-colors">
                      <td className="py-3 font-medium text-gray-900">
                        {app.company_name}
                      </td>
                      <td className="py-3 text-gray-600">{app.job_title}</td>
                      <td className="py-3">
                        <span
                          className={`badge ${getStatusColor(app.status)}`}
                        >
                          {app.status}
                        </span>
                      </td>
                      <td className="py-3">
                        <GhostBadge score={app.ghost_score} />
                      </td>
                      <td className="py-3 text-gray-500">
                        {formatDate(app.applied_at)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

function StatCard({
  label,
  value,
  emoji,
  valueClass = "text-gray-900",
}: {
  label: string;
  value: string | number;
  emoji: string;
  valueClass?: string;
}) {
  return (
    <div className="card">
      <div className="text-2xl mb-2">{emoji}</div>
      <div className={`text-2xl font-bold ${valueClass}`}>{value}</div>
      <div className="text-xs text-gray-500 mt-1">{label}</div>
    </div>
  );
}

function GhostBadge({ score }: { score: number }) {
  const level = score >= 70 ? "high" : score >= 40 ? "medium" : "low";
  const colors = {
    low: "bg-green-100 text-green-700",
    medium: "bg-yellow-100 text-yellow-700",
    high: "bg-red-100 text-red-700",
  };
  return (
    <span className={`badge ${colors[level]}`}>
      {score}% {level === "high" ? "👻" : ""}
    </span>
  );
}
