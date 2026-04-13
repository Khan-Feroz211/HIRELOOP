"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useEffect } from "react";
import Navbar from "@/components/Navbar";
import toast from "react-hot-toast";
import { api } from "@/lib/api";

const FEATURES = {
  free: [
    { label: "Up to 5 application slots", included: true },
    { label: "Ghost Risk Scorer", included: true },
    { label: "Company Safety Scorer", included: true },
    { label: "Follow-up Email AI", included: true },
    { label: "Interview Prep AI", included: false },
    { label: "Unlimited applications", included: false },
    { label: "Priority AI speed", included: false },
  ],
  pro: [
    { label: "Unlimited applications", included: true },
    { label: "Ghost Risk Scorer", included: true },
    { label: "Company Safety Scorer", included: true },
    { label: "Follow-up Email AI (unlimited)", included: true },
    { label: "Interview Prep AI ✨", included: true },
    { label: "Weekly AI Summary", included: true },
    { label: "Priority AI speed", included: true },
  ],
};

export default function UpgradePage() {
  const router = useRouter();
  const [loading, setLoading] = useState<string | null>(null);

  useEffect(() => {
    if (!localStorage.getItem("token")) router.push("/login");
  }, [router]);

  const handleUpgrade = async (plan: "pro" | "university") => {
    setLoading(plan);
    try {
      const res = await api.post<{ checkout_url: string }>("/payments/checkout", { plan });
      window.location.href = res.data.checkout_url;
    } catch {
      toast.error("Could not start checkout. Please try again.");
    } finally {
      setLoading(null);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <main className="max-w-4xl mx-auto px-4 sm:px-6 py-12">
        <div className="text-center mb-10">
          <h1 className="text-3xl font-bold text-gray-900 mb-3">Upgrade to HireLoop Pro</h1>
          <p className="text-gray-500 max-w-xl mx-auto">
            Pakistan&apos;s most powerful job application intelligence platform.
            Stop getting ghosted. Start getting hired.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 items-start">
          {/* Free Plan */}
          <div className="card">
            <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-1">Current</p>
            <h2 className="text-xl font-bold text-gray-900 mb-1">Free</h2>
            <p className="text-3xl font-bold text-gray-900 mb-4">PKR 0<span className="text-base font-normal text-gray-500">/mo</span></p>
            <ul className="space-y-2 mb-6">
              {FEATURES.free.map((f) => (
                <li key={f.label} className={`flex items-center gap-2 text-sm ${f.included ? "text-gray-700" : "text-gray-300"}`}>
                  <span>{f.included ? "✓" : "—"}</span> {f.label}
                </li>
              ))}
            </ul>
            <button disabled className="btn-secondary w-full opacity-60 cursor-not-allowed">Current Plan</button>
          </div>

          {/* Pro Plan */}
          <div className="card border-2 border-brand-500 relative">
            <div className="absolute -top-3 left-1/2 -translate-x-1/2 bg-brand-600 text-white text-xs font-bold px-3 py-1 rounded-full">
              MOST POPULAR
            </div>
            <p className="text-xs font-semibold text-brand-600 uppercase tracking-wide mb-1">Recommended</p>
            <h2 className="text-xl font-bold text-gray-900 mb-1">Pro ✨</h2>
            <p className="text-3xl font-bold text-gray-900 mb-4">PKR 299<span className="text-base font-normal text-gray-500">/mo</span></p>
            <ul className="space-y-2 mb-6">
              {FEATURES.pro.map((f) => (
                <li key={f.label} className="flex items-center gap-2 text-sm text-gray-700">
                  <span className="text-green-500">✓</span> {f.label}
                </li>
              ))}
            </ul>
            <button
              onClick={() => handleUpgrade("pro")}
              disabled={loading !== null}
              className="btn-primary w-full"
            >
              {loading === "pro" ? "Redirecting…" : "Get Pro →"}
            </button>
          </div>

          {/* University Plan */}
          <div className="card border-purple-200">
            <p className="text-xs font-semibold text-purple-600 uppercase tracking-wide mb-1">For Institutions</p>
            <h2 className="text-xl font-bold text-gray-900 mb-1">University 🎓</h2>
            <p className="text-3xl font-bold text-gray-900 mb-4">PKR 999<span className="text-base font-normal text-gray-500">/mo</span></p>
            <ul className="space-y-2 mb-6">
              {[
                "Everything in Pro",
                "Batch license for 500+ students",
                "Career center dashboard",
                "Analytics &amp; reporting",
                "Dedicated support",
              ].map((f) => (
                <li key={f} className="flex items-center gap-2 text-sm text-gray-700">
                  <span className="text-green-500">✓</span>
                  <span dangerouslySetInnerHTML={{ __html: f }} />
                </li>
              ))}
            </ul>
            <button
              onClick={() => handleUpgrade("university")}
              disabled={loading !== null}
              className="btn-secondary w-full"
            >
              {loading === "university" ? "Redirecting…" : "Get University"}
            </button>
          </div>
        </div>

        <p className="text-center text-xs text-gray-400 mt-8">
          Secure payments via Safepay Pakistan 🔒 · Cancel anytime · No hidden fees
        </p>
      </main>
    </div>
  );
}
