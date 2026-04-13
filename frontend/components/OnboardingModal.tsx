"use client";

import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";

const STEPS = [
  {
    emoji: "📋",
    title: "Track your first application",
    description: "Go to the Tracker and add any job you've applied to. HireLoop will monitor it for ghosting risk automatically.",
    cta: "Go to Tracker",
    href: "/tracker",
  },
  {
    emoji: "📧",
    title: "Connect Gmail (optional)",
    description: "Connect your Gmail account so HireLoop can auto-detect when you receive interview invitations and rejection emails — and update your tracker instantly.",
    cta: "Connect Gmail",
    href: "/profile",
  },
  {
    emoji: "👻",
    title: "Run your first Ghost Scan",
    description: "Open any application in the Tracker and click \"Check Ghost Risk\" to get an AI score on how likely that company is to ghost you.",
    cta: "Open Tracker",
    href: "/tracker",
  },
];

interface OnboardingModalProps {
  userName: string;
}

export default function OnboardingModal({ userName }: OnboardingModalProps) {
  const router = useRouter();
  const qc = useQueryClient();
  const [step, setStep] = useState(0);

  const completeMutation = useMutation({
    mutationFn: () => api.post("/auth/onboarding-complete"),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["me"] }),
  });

  const handleCta = () => {
    const href = STEPS[step].href;
    if (step === STEPS.length - 1) {
      completeMutation.mutate();
    }
    router.push(href);
  };

  const handleSkip = () => {
    completeMutation.mutate();
  };

  const current = STEPS[step];

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-2xl w-full max-w-md p-6 relative">
        {/* Progress dots */}
        <div className="flex justify-center gap-1.5 mb-6">
          {STEPS.map((_, i) => (
            <div
              key={i}
              className={`h-1.5 rounded-full transition-all ${
                i === step ? "w-6 bg-brand-600" : i < step ? "w-3 bg-brand-300" : "w-3 bg-gray-200"
              }`}
            />
          ))}
        </div>

        {/* Content */}
        <div className="text-center mb-6">
          <div className="text-5xl mb-4">{current.emoji}</div>
          {step === 0 && (
            <p className="text-sm text-brand-600 font-medium mb-1">
              Welcome to HireLoop, {userName}! 🎉
            </p>
          )}
          <h2 className="text-xl font-bold text-gray-900 mb-2">{current.title}</h2>
          <p className="text-gray-500 text-sm leading-relaxed">{current.description}</p>
        </div>

        {/* Actions */}
        <div className="space-y-2">
          <button onClick={handleCta} className="btn-primary w-full">
            {current.cta} →
          </button>
          {step < STEPS.length - 1 ? (
            <button
              onClick={() => setStep(step + 1)}
              className="btn-secondary w-full"
            >
              Next tip →
            </button>
          ) : null}
          <button
            onClick={handleSkip}
            className="text-gray-400 hover:text-gray-600 text-sm w-full text-center py-1 transition-colors"
          >
            Skip for now
          </button>
        </div>

        {/* Step counter */}
        <p className="text-xs text-gray-400 text-center mt-4">
          Step {step + 1} of {STEPS.length}
        </p>
      </div>
    </div>
  );
}
