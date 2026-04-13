import Link from "next/link";

export default function LandingPage() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-brand-900 via-brand-700 to-brand-500">
      {/* Navbar */}
      <nav className="flex items-center justify-between px-6 py-4 max-w-7xl mx-auto">
        <div className="flex items-center gap-2">
          <span className="text-white font-bold text-xl">🔁 HireLoop PK</span>
        </div>
        <div className="flex items-center gap-4">
          <Link
            href="/login"
            className="text-white/80 hover:text-white text-sm font-medium transition-colors"
          >
            Log in
          </Link>
          <Link
            href="/register"
            className="bg-white text-brand-700 hover:bg-brand-50 font-semibold text-sm px-4 py-2 rounded-lg transition-colors"
          >
            Get Started Free
          </Link>
        </div>
      </nav>

      {/* Hero */}
      <section className="flex flex-col items-center justify-center text-center px-6 pt-20 pb-32">
        <div className="inline-flex items-center gap-2 bg-white/10 text-white/90 text-sm px-4 py-1.5 rounded-full mb-6 border border-white/20">
          <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></span>
          Built for NUTECH students &amp; Pakistani fresh graduates
        </div>

        <h1 className="text-5xl md:text-6xl font-extrabold text-white max-w-3xl leading-tight mb-6">
          Stop getting ghosted.
          <br />
          <span className="text-yellow-300">Start getting hired.</span>
        </h1>

        <p className="text-white/80 text-lg max-w-xl mb-10">
          Track every application, score ghost risk with AI, generate follow-up
          emails, and prep for interviews — all in one place built for Pakistan.
        </p>

        <div className="flex flex-col sm:flex-row gap-4 items-center">
          <Link
            href="/register"
            className="bg-yellow-400 hover:bg-yellow-300 text-brand-900 font-bold px-8 py-3.5 rounded-xl text-lg transition-colors shadow-lg"
          >
            Start Tracking Free →
          </Link>
          <Link
            href="/login"
            className="text-white/80 hover:text-white font-medium px-6 py-3 rounded-xl border border-white/20 hover:border-white/40 transition-colors"
          >
            Already have an account
          </Link>
        </div>

        <p className="mt-6 text-white/60 text-sm">
          Free forever · No credit card · PKR 299/mo for Pro
        </p>
      </section>

      {/* Features */}
      <section className="bg-white py-20 px-6">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl font-bold text-center text-gray-900 mb-4">
            Everything you need to beat the ghost
          </h2>
          <p className="text-center text-gray-500 mb-12 max-w-xl mx-auto">
            The Pakistani job market is tough. HireLoop gives you the tools to
            stay ahead of every application.
          </p>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((feature) => (
              <div
                key={feature.title}
                className="p-6 rounded-xl border border-gray-100 hover:border-brand-200 hover:shadow-md transition-all"
              >
                <div className="text-3xl mb-4">{feature.emoji}</div>
                <h3 className="font-semibold text-gray-900 mb-2">
                  {feature.title}
                </h3>
                <p className="text-gray-500 text-sm leading-relaxed">
                  {feature.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing */}
      <section className="bg-gray-50 py-20 px-6">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            Student-friendly pricing
          </h2>
          <p className="text-gray-500 mb-12">
            Start free. Upgrade when you need AI superpowers.
          </p>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Free */}
            <div className="card text-left">
              <div className="text-2xl font-bold mb-1">Free</div>
              <div className="text-gray-500 text-sm mb-6">Forever free</div>
              <ul className="space-y-3 text-sm text-gray-600 mb-8">
                {freeTier.map((f) => (
                  <li key={f} className="flex items-center gap-2">
                    <span className="text-green-500">✓</span> {f}
                  </li>
                ))}
              </ul>
              <Link href="/register" className="btn-secondary w-full text-center block">
                Get Started
              </Link>
            </div>

            {/* Pro */}
            <div className="card text-left border-brand-500 border-2 relative">
              <div className="absolute -top-3 left-1/2 -translate-x-1/2 bg-brand-600 text-white text-xs font-semibold px-3 py-1 rounded-full">
                Most Popular
              </div>
              <div className="text-2xl font-bold mb-1">Student Pro</div>
              <div className="text-gray-500 text-sm mb-1">
                <span className="text-3xl font-extrabold text-gray-900">
                  PKR 299
                </span>
                /month
              </div>
              <div className="text-gray-400 text-xs mb-6">
                Break-even at 19 students
              </div>
              <ul className="space-y-3 text-sm text-gray-600 mb-8">
                {proTier.map((f) => (
                  <li key={f} className="flex items-center gap-2">
                    <span className="text-brand-500">✓</span> {f}
                  </li>
                ))}
              </ul>
              <Link href="/register" className="btn-primary w-full text-center block">
                Start Pro Trial
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-brand-900 py-8 px-6 text-center text-white/50 text-sm">
        <p>
          Built with ❤️ by Feroz Khan · NUTECH AI Engineering · 2024
        </p>
        <p className="mt-1">Pakistan&apos;s first AI-powered job application intelligence platform</p>
      </footer>
    </main>
  );
}

const features = [
  {
    emoji: "📊",
    title: "Kanban Application Tracker",
    description:
      "Visualize all your applications from Applied → Confirmed → Interview → Offer in one clean board.",
  },
  {
    emoji: "👻",
    title: "AI Ghost Risk Scorer",
    description:
      "Claude AI scores your ghost risk daily (0-100). Know when to follow up before it's too late.",
  },
  {
    emoji: "✉️",
    title: "Follow-Up Email Generator",
    description:
      "Get 3 tailored email variants (polite, value-add, final nudge) crafted for Pakistani hiring culture.",
  },
  {
    emoji: "🎤",
    title: "Interview Prep AI",
    description:
      "Paste any job description and get 10 likely questions with STAR-format answers.",
  },
  {
    emoji: "🏢",
    title: "Company Safety Scorer",
    description:
      "Know if a company is safe before you show up. Scam detection + female-friendly scoring.",
  },
  {
    emoji: "📬",
    title: "Gmail Auto-Parser",
    description:
      "Connect Gmail and watch your application statuses update automatically when emails arrive.",
  },
];

const freeTier = [
  "5 active applications",
  "Basic Kanban tracker",
  "Ghost score dashboard",
  "Job board access",
];

const proTier = [
  "Everything in Free",
  "Unlimited applications",
  "AI ghost scorer (daily)",
  "Follow-up email generator",
  "Interview prep AI",
  "Company safety scorer",
  "Gmail auto-parser",
  "Weekly AI summary",
];
