"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { useEffect } from "react";
import Navbar from "@/components/Navbar";
import { ErrorBoundary } from "@/components/ErrorBoundary";
import toast from "react-hot-toast";
import { aiApi, authApi } from "@/lib/api";
import Link from "next/link";

interface PrepResult {
  role_summary: string;
  likely_questions: string[];
  suggested_answers: string[];
  weak_areas: string[];
  preparation_tips: string;
}

export default function PrepPage() {
  const router = useRouter();
  const [jobDesc, setJobDesc] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<PrepResult | null>(null);
  const [activeTab, setActiveTab] = useState<"qa" | "tips">("qa");

  useEffect(() => {
    if (!localStorage.getItem("token")) router.push("/login");
  }, [router]);

  const { data: user } = useQuery({
    queryKey: ["me"],
    queryFn: () => authApi.me().then((r) => r.data),
    retry: false,
  });

  const isPro = user?.subscription_tier === "pro" || user?.subscription_tier === "university";

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (jobDesc.length < 50) {
      toast.error("Please paste a full job description (50+ characters)");
      return;
    }
    setLoading(true);
    try {
      const res = await aiApi.interviewPrep({ job_description: jobDesc });
      setResult(res.data);
    } catch {
      toast.error("Failed to generate prep. Try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <ErrorBoundary>
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <main className="max-w-4xl mx-auto px-4 sm:px-6 py-8">
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-gray-900">Interview Prep AI</h1>
          <p className="text-gray-500 text-sm mt-0.5">
            Paste any job description and get 10 questions, STAR-format answers,
            and tailored tips
          </p>
        </div>

        {/* Pro gate */}
        {user && !isPro && (
          <div className="card mb-6 bg-gradient-to-r from-brand-50 to-white border-brand-200">
            <div className="flex items-start gap-3">
              <span className="text-2xl">🔒</span>
              <div>
                <p className="font-semibold text-brand-900 mb-1">Interview Prep is a Pro feature</p>
                <p className="text-brand-700 text-sm mb-3">
                  Get 10 AI-generated questions, STAR-format answers, and weak area analysis tailored to any job description.
                </p>
                <Link href="/upgrade" className="btn-primary inline-block">
                  Upgrade to Pro — PKR 299/month
                </Link>
              </div>
            </div>
          </div>
        )}

        {/* Input Form */}
        <div className={`card mb-6 ${user && !isPro ? "opacity-50 pointer-events-none" : ""}`}>
          <form onSubmit={handleSubmit}>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Job Description
            </label>
            <textarea
              className="input resize-none mb-4"
              rows={10}
              placeholder="Paste the full job description here…

Example:
We are looking for an AI Engineer Intern at XYZ Tech, Islamabad.
Responsibilities:
- Develop ML models using Python and TensorFlow
- Collaborate with the data team
Requirements:
- Final year or fresh graduate
- Strong Python skills
- Familiarity with machine learning concepts"
              value={jobDesc}
              onChange={(e) => setJobDesc(e.target.value)}
              required
            />
            <button
              type="submit"
              className="btn-primary flex items-center gap-2"
              disabled={loading}
            >
              {loading ? (
                <>
                  <span className="animate-spin">⚙️</span> Analyzing with Claude
                  AI…
                </>
              ) : (
                <>🎤 Generate Interview Prep</>
              )}
            </button>
          </form>
        </div>

        {/* Results */}
        {result && (
          <div className="space-y-6">
            {/* Role Summary */}
            <div className="card bg-brand-50 border-brand-100">
              <h2 className="font-semibold text-brand-900 mb-2 flex items-center gap-2">
                <span>🎯</span> Role Summary
              </h2>
              <p className="text-brand-800 text-sm leading-relaxed">
                {result.role_summary}
              </p>
            </div>

            {/* Tabs */}
            <div className="card">
              <div className="flex gap-4 mb-6 border-b border-gray-100 pb-4">
                <button
                  onClick={() => setActiveTab("qa")}
                  className={`text-sm font-medium pb-1 ${
                    activeTab === "qa"
                      ? "text-brand-600 border-b-2 border-brand-600"
                      : "text-gray-500 hover:text-gray-700"
                  }`}
                >
                  10 Questions &amp; Answers
                </button>
                <button
                  onClick={() => setActiveTab("tips")}
                  className={`text-sm font-medium pb-1 ${
                    activeTab === "tips"
                      ? "text-brand-600 border-b-2 border-brand-600"
                      : "text-gray-500 hover:text-gray-700"
                  }`}
                >
                  Tips &amp; Weak Areas
                </button>
              </div>

              {activeTab === "qa" && (
                <div className="space-y-6">
                  {result.likely_questions.map((q, i) => (
                    <div key={i}>
                      <p className="font-medium text-gray-900 mb-2">
                        <span className="text-brand-600 font-bold mr-2">
                          Q{i + 1}.
                        </span>
                        {q}
                      </p>
                      <div className="bg-gray-50 rounded-lg p-3 ml-5">
                        <p className="text-gray-600 text-sm leading-relaxed">
                          {result.suggested_answers[i]}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {activeTab === "tips" && (
                <div className="space-y-6">
                  {/* Weak Areas */}
                  <div>
                    <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                      <span>⚠️</span> Potential Weak Areas
                    </h3>
                    <div className="space-y-2">
                      {result.weak_areas.map((area, i) => (
                        <div
                          key={i}
                          className="flex items-center gap-2 text-sm text-gray-600 bg-yellow-50 rounded-lg px-3 py-2"
                        >
                          <span className="text-yellow-500">•</span> {area}
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Prep Tips */}
                  <div>
                    <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                      <span>💡</span> Preparation Tips
                    </h3>
                    <p className="text-gray-600 text-sm leading-relaxed bg-blue-50 rounded-lg p-4">
                      {result.preparation_tips}
                    </p>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </main>
    </div>
    </ErrorBoundary>
  );
}
