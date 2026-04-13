"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useQueryClient } from "@tanstack/react-query";

export default function PaymentSuccessPage() {
  const router = useRouter();
  const qc = useQueryClient();

  useEffect(() => {
    // Invalidate user cache so the new subscription tier loads
    qc.invalidateQueries({ queryKey: ["me"] });
    // Auto-redirect to dashboard after 5 seconds
    const timer = setTimeout(() => router.push("/dashboard"), 5000);
    return () => clearTimeout(timer);
  }, [router, qc]);

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4">
      <div className="bg-white rounded-2xl shadow-lg p-8 max-w-sm w-full text-center">
        <div className="text-6xl mb-4">🎉</div>
        <h1 className="text-2xl font-bold text-gray-900 mb-2">You&apos;re Pro now!</h1>
        <p className="text-gray-500 text-sm mb-6">
          Your subscription is active. Unlock unlimited tracking, Interview Prep AI, and more.
        </p>
        <Link href="/dashboard" className="btn-primary block">
          Go to Dashboard
        </Link>
        <p className="text-xs text-gray-400 mt-4">Redirecting automatically in 5 seconds…</p>
      </div>
    </div>
  );
}
