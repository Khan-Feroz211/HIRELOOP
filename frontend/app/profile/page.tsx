"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { useEffect } from "react";
import Navbar from "@/components/Navbar";
import toast from "react-hot-toast";
import { authApi, api } from "@/lib/api";

export default function ProfilePage() {
  const router = useRouter();
  const qc = useQueryClient();
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [showUpgradeModal, setShowUpgradeModal] = useState(false);
  const [checkoutLoading, setCheckoutLoading] = useState(false);

  useEffect(() => {
    if (!localStorage.getItem("token")) router.push("/login");
  }, [router]);

  const { data: user, isLoading } = useQuery({
    queryKey: ["me"],
    queryFn: () => authApi.me().then((r) => r.data),
  });

  const onboardingMutation = useMutation({
    mutationFn: () => api.post("/auth/onboarding-complete"),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["me"] }),
  });

  const handleUpgrade = async (plan: "pro" | "university") => {
    setCheckoutLoading(true);
    try {
      const res = await api.post<{ checkout_url: string }>("/payments/checkout", { plan });
      window.location.href = res.data.checkout_url;
    } catch {
      toast.error("Could not start checkout. Please try again.");
    } finally {
      setCheckoutLoading(false);
    }
  };

  const handleDeleteAccount = () => {
    localStorage.removeItem("token");
    toast.success("Account deletion request sent. You have been signed out.");
    router.push("/login");
  };

  const tierBadge = {
    free: { label: "Free", style: "bg-gray-100 text-gray-700" },
    pro: { label: "Pro ✨", style: "bg-brand-100 text-brand-700" },
    university: { label: "University 🎓", style: "bg-purple-100 text-purple-700" },
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <main className="max-w-2xl mx-auto px-4 sm:px-6 py-8 space-y-4">
          <div className="h-8 bg-gray-200 rounded animate-pulse w-40" />
          <div className="card space-y-4">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="h-6 bg-gray-100 rounded animate-pulse" />
            ))}
          </div>
        </main>
      </div>
    );
  }

  if (!user) return null;

  const tier = user.subscription_tier as "free" | "pro" | "university";
  const badge = tierBadge[tier] || tierBadge.free;

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <main className="max-w-2xl mx-auto px-4 sm:px-6 py-8">
        <h1 className="text-2xl font-bold text-gray-900 mb-6">My Profile</h1>

        {/* Account Info */}
        <div className="card mb-4">
          <h2 className="font-semibold text-gray-900 mb-4">Account Details</h2>
          <dl className="space-y-3 text-sm">
            <div className="flex justify-between">
              <dt className="text-gray-500">Name</dt>
              <dd className="font-medium text-gray-900">{user.name}</dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-gray-500">Email</dt>
              <dd className="font-medium text-gray-900 flex items-center gap-1.5">
                {user.email}
                {user.email_verified ? (
                  <span className="text-green-600 text-xs">✓ Verified</span>
                ) : (
                  <span className="text-yellow-600 text-xs">⚠ Unverified</span>
                )}
              </dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-gray-500">Plan</dt>
              <dd>
                <span className={`badge ${badge.style}`}>{badge.label}</span>
              </dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-gray-500">Gmail Connected</dt>
              <dd className="text-gray-900">
                {user.email?.endsWith("@gmail.com") ? "✅ Connected via OAuth" : "—"}
              </dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-gray-500">Member Since</dt>
              <dd className="text-gray-900">
                {new Date(user.created_at).toLocaleDateString("en-PK", {
                  day: "numeric", month: "long", year: "numeric",
                })}
              </dd>
            </div>
          </dl>
        </div>

        {/* Email Verification Notice */}
        {!user.email_verified && (
          <div className="card border-yellow-200 bg-yellow-50 mb-4">
            <div className="flex items-start gap-3">
              <span className="text-xl">📧</span>
              <div>
                <p className="font-medium text-yellow-900 text-sm">Verify your email to unlock AI features</p>
                <p className="text-yellow-700 text-xs mt-0.5">
                  Check your inbox for a verification link from noreply@hireloop.pk
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Upgrade Section */}
        {tier === "free" && (
          <div className="card mb-4 bg-gradient-to-br from-brand-50 to-white border-brand-100">
            <div className="flex items-start gap-3 mb-4">
              <span className="text-2xl">✨</span>
              <div>
                <h2 className="font-semibold text-brand-900">Upgrade to Pro</h2>
                <p className="text-brand-700 text-sm mt-0.5">
                  Unlock unlimited applications, Interview Prep AI, and priority support.
                </p>
              </div>
            </div>
            <ul className="space-y-1.5 text-sm text-gray-600 mb-4 ml-9">
              {[
                "Unlimited job application tracking",
                "Interview Prep AI (10 Q&A + STAR answers)",
                "Unlimited follow-up email generation",
                "Priority AI response speed",
              ].map((f) => (
                <li key={f} className="flex items-center gap-2">
                  <span className="text-green-500">✓</span> {f}
                </li>
              ))}
            </ul>
            <button
              onClick={() => setShowUpgradeModal(true)}
              className="btn-primary w-full"
            >
              Upgrade for PKR 299/month
            </button>
          </div>
        )}

        {/* Danger Zone */}
        <div className="card border-red-100">
          <h2 className="font-semibold text-red-700 mb-2">Danger Zone</h2>
          <p className="text-sm text-gray-500 mb-3">
            Deleting your account is permanent and cannot be undone.
            All your applications, scores, and data will be erased.
          </p>
          {!showDeleteConfirm ? (
            <button
              onClick={() => setShowDeleteConfirm(true)}
              className="text-sm text-red-600 border border-red-200 rounded-lg px-4 py-2 hover:bg-red-50 transition-colors"
            >
              Delete My Account
            </button>
          ) : (
            <div className="bg-red-50 rounded-lg p-4">
              <p className="text-sm font-medium text-red-800 mb-3">
                Are you absolutely sure? This cannot be undone.
              </p>
              <div className="flex gap-3">
                <button
                  onClick={() => setShowDeleteConfirm(false)}
                  className="btn-secondary flex-1 text-sm"
                >
                  Cancel
                </button>
                <button
                  onClick={handleDeleteAccount}
                  className="flex-1 bg-red-600 text-white rounded-lg px-4 py-2 text-sm font-medium hover:bg-red-700 transition-colors"
                >
                  Yes, Delete Account
                </button>
              </div>
            </div>
          )}
        </div>
      </main>

      {/* Upgrade Modal */}
      {showUpgradeModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl w-full max-w-md p-6">
            <div className="flex items-start justify-between mb-4">
              <h2 className="text-lg font-bold">Choose Your Plan</h2>
              <button
                onClick={() => setShowUpgradeModal(false)}
                className="text-gray-400 hover:text-gray-600 text-xl"
              >×</button>
            </div>

            <div className="space-y-3 mb-4">
              {/* Pro Plan */}
              <div className="border-2 border-brand-500 rounded-xl p-4">
                <div className="flex items-center justify-between mb-2">
                  <div>
                    <p className="font-bold text-brand-700">Pro Plan ✨</p>
                    <p className="text-xs text-gray-500">For individual students</p>
                  </div>
                  <div className="text-right">
                    <p className="font-bold text-gray-900">PKR 299</p>
                    <p className="text-xs text-gray-500">/month</p>
                  </div>
                </div>
                <button
                  onClick={() => handleUpgrade("pro")}
                  disabled={checkoutLoading}
                  className="btn-primary w-full mt-2"
                >
                  {checkoutLoading ? "Redirecting…" : "Get Pro"}
                </button>
              </div>

              {/* University Plan */}
              <div className="border border-gray-200 rounded-xl p-4">
                <div className="flex items-center justify-between mb-2">
                  <div>
                    <p className="font-bold text-purple-700">University Plan 🎓</p>
                    <p className="text-xs text-gray-500">For career centers &amp; batch licensing</p>
                  </div>
                  <div className="text-right">
                    <p className="font-bold text-gray-900">PKR 999</p>
                    <p className="text-xs text-gray-500">/month</p>
                  </div>
                </div>
                <button
                  onClick={() => handleUpgrade("university")}
                  disabled={checkoutLoading}
                  className="btn-secondary w-full mt-2"
                >
                  {checkoutLoading ? "Redirecting…" : "Get University"}
                </button>
              </div>
            </div>

            <p className="text-xs text-gray-400 text-center">
              Secure checkout via Safepay 🔒 · Cancel anytime
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
