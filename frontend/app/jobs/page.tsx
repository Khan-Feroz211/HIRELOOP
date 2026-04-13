"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { useEffect } from "react";
import Navbar from "@/components/Navbar";
import { jobsApi, type JobListing } from "@/lib/api";

const DOMAINS = ["All", "AI", "Engineering", "Design", "Marketing", "Finance", "HR", "Sales"];
const CITIES = ["All", "Islamabad", "Lahore", "Karachi", "Rawalpindi", "Peshawar"];

export default function JobsPage() {
  const router = useRouter();
  const [filters, setFilters] = useState({
    remote: undefined as boolean | undefined,
    paid: undefined as boolean | undefined,
    domain: "",
    city: "",
  });

  useEffect(() => {
    if (!localStorage.getItem("token")) router.push("/login");
  }, [router]);

  const { data: jobs = [], isLoading } = useQuery({
    queryKey: ["jobs", filters],
    queryFn: () =>
      jobsApi
        .list({
          remote: filters.remote,
          paid: filters.paid,
          domain: filters.domain || undefined,
          city: filters.city || undefined,
          limit: 50,
        })
        .then((r) => r.data),
  });

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <main className="max-w-7xl mx-auto px-4 sm:px-6 py-8">
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-gray-900">Job Board</h1>
          <p className="text-gray-500 text-sm mt-0.5">
            Verified listings from Rozee.pk, LinkedIn, and Mustakbil — with
            safety scores
          </p>
        </div>

        {/* Filters */}
        <div className="card mb-6">
          <div className="flex flex-wrap gap-4">
            {/* Remote filter */}
            <div>
              <label className="block text-xs font-medium text-gray-500 mb-1">
                Work Mode
              </label>
              <div className="flex gap-2">
                {[
                  { label: "All", value: undefined },
                  { label: "Remote", value: true },
                  { label: "On-site", value: false },
                ].map((opt) => (
                  <button
                    key={String(opt.value)}
                    onClick={() => setFilters({ ...filters, remote: opt.value })}
                    className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                      filters.remote === opt.value
                        ? "bg-brand-600 text-white"
                        : "bg-gray-100 text-gray-600 hover:bg-gray-200"
                    }`}
                  >
                    {opt.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Paid filter */}
            <div>
              <label className="block text-xs font-medium text-gray-500 mb-1">
                Compensation
              </label>
              <div className="flex gap-2">
                {[
                  { label: "All", value: undefined },
                  { label: "Paid Only", value: true },
                ].map((opt) => (
                  <button
                    key={String(opt.value)}
                    onClick={() => setFilters({ ...filters, paid: opt.value })}
                    className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                      filters.paid === opt.value
                        ? "bg-brand-600 text-white"
                        : "bg-gray-100 text-gray-600 hover:bg-gray-200"
                    }`}
                  >
                    {opt.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Domain filter */}
            <div>
              <label className="block text-xs font-medium text-gray-500 mb-1">
                Domain
              </label>
              <select
                className="input !w-auto"
                value={filters.domain}
                onChange={(e) =>
                  setFilters({
                    ...filters,
                    domain: e.target.value === "All" ? "" : e.target.value,
                  })
                }
              >
                {DOMAINS.map((d) => (
                  <option key={d}>{d}</option>
                ))}
              </select>
            </div>

            {/* City filter */}
            <div>
              <label className="block text-xs font-medium text-gray-500 mb-1">
                City
              </label>
              <select
                className="input !w-auto"
                value={filters.city}
                onChange={(e) =>
                  setFilters({
                    ...filters,
                    city: e.target.value === "All" ? "" : e.target.value,
                  })
                }
              >
                {CITIES.map((c) => (
                  <option key={c}>{c}</option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {/* Results */}
        {isLoading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {[1, 2, 3, 4, 5, 6].map((i) => (
              <div key={i} className="card animate-pulse">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1 space-y-2">
                    <div className="h-5 bg-gray-200 rounded w-3/4" />
                    <div className="h-4 bg-gray-100 rounded w-1/2" />
                  </div>
                  <div className="h-5 bg-gray-200 rounded w-12 ml-2" />
                </div>
                <div className="flex gap-1.5 mb-3">
                  <div className="h-5 bg-gray-100 rounded w-16" />
                  <div className="h-5 bg-gray-100 rounded w-20" />
                </div>
                <div className="h-4 bg-gray-100 rounded w-24" />
              </div>
            ))}
          </div>
        ) : jobs.length === 0 ? (
          <div className="text-center py-20">
            <p className="text-4xl mb-4">💼</p>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">No jobs match your filters</h3>
            <p className="text-gray-400 text-sm mb-6 max-w-xs mx-auto">
              Try removing some filters, or check back later — new listings are scraped daily from Rozee.pk, LinkedIn, and Mustakbil.
            </p>
            <button
              onClick={() => setFilters({ remote: undefined, paid: undefined, domain: "", city: "" })}
              className="btn-secondary"
            >
              Clear all filters
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {jobs.map((job: JobListing) => (
              <JobCard key={job.id} job={job} />
            ))}
          </div>
        )}
      </main>
    </div>
  );
}

function JobCard({ job }: { job: JobListing }) {
  const safetyColor =
    job.safety_score >= 7
      ? "text-green-600"
      : job.safety_score >= 4
      ? "text-yellow-600"
      : "text-red-600";

  return (
    <div className="card hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1 min-w-0">
          <h3 className="font-semibold text-gray-900 truncate">{job.title}</h3>
          <p className="text-gray-500 text-sm truncate">{job.company}</p>
        </div>
        <div className={`text-sm font-bold ml-2 ${safetyColor}`}>
          🛡️ {job.safety_score}/10
        </div>
      </div>

      <div className="flex flex-wrap gap-1.5 mb-3">
        {job.remote && (
          <span className="badge bg-green-100 text-green-700">🌐 Remote</span>
        )}
        {job.paid && (
          <span className="badge bg-blue-100 text-blue-700">
            {job.stipend_pkr
              ? `PKR ${job.stipend_pkr.toLocaleString()}/mo`
              : "Paid"}
          </span>
        )}
        {job.domain && (
          <span className="badge bg-purple-100 text-purple-700">
            {job.domain}
          </span>
        )}
        <span className="badge bg-gray-100 text-gray-600">
          {job.source}
        </span>
      </div>

      {job.location && (
        <p className="text-xs text-gray-400 flex items-center gap-1">
          📍 {job.location}
        </p>
      )}
    </div>
  );
}
