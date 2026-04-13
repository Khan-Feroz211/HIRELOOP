"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useEffect } from "react";
import Navbar from "@/components/Navbar";
import toast from "react-hot-toast";
import { aiApi } from "@/lib/api";

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

        {/* Input Form */}
        <div className="card mb-6">
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
  );
}
