"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useEffect } from "react";
import Navbar from "@/components/Navbar";
import toast from "react-hot-toast";
import { aiApi } from "@/lib/api";

interface SafetyResult {
  remote_verified: boolean;
  safety_score: number;
  female_friendly_score: number;
  flags: string[];
  recommendation: string;
}

const JOB_TYPES = ["Full-time", "Part-time", "Remote", "On-site", "Internship", "Contract"];
const CITIES = ["Karachi", "Lahore", "Islamabad", "Rawalpindi", "Peshawar", "Quetta", "Other"];

export default function SafetyPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<SafetyResult | null>(null);
  const [form, setForm] = useState({
    company_name: "",
    job_type: "Full-time",
    claimed_location: "Karachi",
    job_description: "",
  });

  useEffect(() => {
    if (!localStorage.getItem("token")) router.push("/login");
  }, [router]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (form.job_description.length < 30) {
      toast.error("Please paste more of the job description (30+ characters)");
      return;
    }
    setLoading(true);
    try {
      const res = await aiApi.companySafety(form);
      setResult(res.data);
    } catch {
      toast.error("Analysis failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const scoreColor = (score: number) =>
    score >= 7 ? "text-green-600" : score >= 4 ? "text-yellow-600" : "text-red-600";

  const scoreBarColor = (score: number) =>
    score >= 7 ? "bg-green-500" : score >= 4 ? "bg-yellow-500" : "bg-red-500";

  const recommendationStyle = (rec: string) => {
    if (rec.toLowerCase().includes("safe")) return "bg-green-50 text-green-800 border-green-200";
    if (rec.toLowerCase().includes("caution")) return "bg-yellow-50 text-yellow-800 border-yellow-200";
    return "bg-red-50 text-red-800 border-red-200";
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <main className="max-w-4xl mx-auto px-4 sm:px-6 py-8">
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-gray-900">🛡️ Company Safety Scorer</h1>
          <p className="text-gray-500 text-sm mt-0.5">
            Verify if a company and job posting are legitimate before accepting an in-person meeting or sharing personal info.
            Especially important for female job seekers.
          </p>
        </div>

        {/* Input Form */}
        <div className="card mb-6">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Company Name *
                </label>
                <input
                  className="input"
                  placeholder="e.g. TechCorp Pakistan"
                  value={form.company_name}
                  onChange={(e) => setForm({ ...form, company_name: e.target.value })}
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Job Type *
                </label>
                <select
                  className="input"
                  value={form.job_type}
                  onChange={(e) => setForm({ ...form, job_type: e.target.value })}
                >
                  {JOB_TYPES.map((t) => (
                    <option key={t}>{t}</option>
                  ))}
                </select>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Claimed Location *
              </label>
              <select
                className="input"
                value={form.claimed_location}
                onChange={(e) => setForm({ ...form, claimed_location: e.target.value })}
              >
                {CITIES.map((c) => (
                  <option key={c}>{c}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Job Description / Posting Text *
              </label>
              <textarea
                className="input resize-none"
                rows={8}
                placeholder={`Paste the full job description here…\n\nExample:\nWe are looking for a Marketing Executive at XYZ Digital, Lahore.\nSalary: PKR 35,000–50,000\nRequirements: Fresh graduate…\n\nContact: Only WhatsApp HR at +92 300 XXXXXXX`}
                value={form.job_description}
                onChange={(e) => setForm({ ...form, job_description: e.target.value })}
                required
              />
              <p className="text-xs text-gray-400 mt-1">
                Include as much of the original posting as possible for accurate analysis
              </p>
            </div>

            <button
              type="submit"
              className="btn-primary flex items-center gap-2"
              disabled={loading}
            >
              {loading ? (
                <>
                  <span className="animate-spin">⚙️</span> Analyzing with AI…
                </>
              ) : (
                <>🛡️ Analyze Safety</>
              )}
            </button>
          </form>
        </div>

        {/* Results */}
        {result && (
          <div className="space-y-4">
            {/* Recommendation Banner */}
            <div className={`rounded-xl border-2 p-4 font-semibold text-lg flex items-center gap-3 ${recommendationStyle(result.recommendation)}`}>
              <span className="text-2xl">
                {result.recommendation.toLowerCase().includes("safe")
                  ? "✅"
                  : result.recommendation.toLowerCase().includes("caution")
                  ? "⚠️"
                  : "🚫"}
              </span>
              {result.recommendation}
            </div>

            {/* Score Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              {/* Safety Score */}
              <div className="card">
                <p className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-2">Safety Score</p>
                <p className={`text-3xl font-bold ${scoreColor(result.safety_score)}`}>
                  {result.safety_score}/10
                </p>
                <div className="mt-2 h-2 bg-gray-100 rounded-full overflow-hidden">
                  <div
                    className={`h-full rounded-full ${scoreBarColor(result.safety_score)}`}
                    style={{ width: `${result.safety_score * 10}%` }}
                  />
                </div>
              </div>

              {/* Female Friendly Score */}
              <div className="card">
                <p className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-2">Female-Friendly Score</p>
                <p className={`text-3xl font-bold ${scoreColor(result.female_friendly_score)}`}>
                  {result.female_friendly_score}/10
                </p>
                <div className="mt-2 h-2 bg-gray-100 rounded-full overflow-hidden">
                  <div
                    className={`h-full rounded-full ${scoreBarColor(result.female_friendly_score)}`}
                    style={{ width: `${result.female_friendly_score * 10}%` }}
                  />
                </div>
              </div>

              {/* Remote Verified */}
              <div className="card flex flex-col justify-between">
                <p className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-2">Remote Claim</p>
                <div className="flex items-center gap-2">
                  <span className="text-2xl">{result.remote_verified ? "✅" : "❌"}</span>
                  <p className={`font-semibold ${result.remote_verified ? "text-green-700" : "text-red-700"}`}>
                    {result.remote_verified ? "Appears genuine" : "Unverified / Suspicious"}
                  </p>
                </div>
              </div>
            </div>

            {/* Red Flags */}
            {result.flags.length > 0 && (
              <div className="card border-red-100">
                <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                  <span>🚩</span> Red Flags Detected ({result.flags.length})
                </h3>
                <div className="space-y-2">
                  {result.flags.map((flag, i) => (
                    <div
                      key={i}
                      className="flex items-start gap-2 text-sm text-red-700 bg-red-50 rounded-lg px-3 py-2"
                    >
                      <span className="text-red-500 mt-0.5 flex-shrink-0">•</span>
                      {flag}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Safe indicators when no flags */}
            {result.flags.length === 0 && (
              <div className="card border-green-100 bg-green-50">
                <p className="text-green-800 font-medium flex items-center gap-2">
                  <span>✅</span> No red flags detected — this posting appears legitimate
                </p>
              </div>
            )}

            {/* Disclaimer */}
            <p className="text-xs text-gray-400 text-center">
              AI analysis is a guide, not a guarantee. Always research independently and trust your instincts.
              Never attend an in-person meeting at an unmarked or residential address.
            </p>
          </div>
        )}
      </main>
    </div>
  );
}
