"use client";

import { useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { Suspense } from "react";

function CallbackHandler() {
  const router = useRouter();
  const params = useSearchParams();

  useEffect(() => {
    const token = params.get("token");
    if (token) {
      localStorage.setItem("token", token);
      // Remove the token from the URL immediately for security
      if (typeof window !== "undefined") {
        window.history.replaceState({}, document.title, "/auth/callback");
      }
      router.push("/dashboard");
    } else {
      router.push("/login?error=oauth_failed");
    }
  }, [params, router]);

  return (
    <div className="min-h-screen flex items-center justify-center">
      <p className="text-gray-500">Signing you in…</p>
    </div>
  );
}

export default function AuthCallbackPage() {
  return (
    <Suspense fallback={<div className="min-h-screen flex items-center justify-center"><p>Loading…</p></div>}>
      <CallbackHandler />
    </Suspense>
  );
}
