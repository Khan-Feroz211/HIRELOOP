"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { clsx } from "clsx";
import { authApi } from "@/lib/api";

const navLinks = [
  { href: "/dashboard", label: "Dashboard", emoji: "📊" },
  { href: "/tracker", label: "Tracker", emoji: "📋" },
  { href: "/jobs", label: "Jobs", emoji: "💼" },
  { href: "/prep", label: "Interview Prep", emoji: "🎤" },
  { href: "/safety", label: "Safety", emoji: "🛡️" },
];

export default function Navbar() {
  const pathname = usePathname();
  const router = useRouter();

  const { data: user } = useQuery({
    queryKey: ["me"],
    queryFn: () => authApi.me().then((r) => r.data),
    retry: false,
  });

  const handleLogout = () => {
    localStorage.removeItem("token");
    router.push("/login");
  };

  return (
    <nav className="bg-white border-b border-gray-200 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6">
        <div className="flex items-center justify-between h-14">
          {/* Logo */}
          <Link href="/dashboard" className="font-bold text-brand-700 text-lg">
            🔁 HireLoop PK
          </Link>

          {/* Nav links */}
          <div className="hidden md:flex items-center gap-1">
            {navLinks.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                className={clsx(
                  "flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium transition-colors",
                  pathname === link.href
                    ? "bg-brand-50 text-brand-700"
                    : "text-gray-600 hover:text-gray-900 hover:bg-gray-100"
                )}
              >
                <span>{link.emoji}</span>
                {link.label}
              </Link>
            ))}
          </div>

          {/* Right side */}
          <div className="flex items-center gap-2">
            {user?.subscription_tier === "free" && (
              <Link
                href="/upgrade"
                className="hidden sm:inline-flex items-center gap-1 bg-brand-600 text-white text-xs font-semibold px-3 py-1.5 rounded-lg hover:bg-brand-700 transition-colors"
              >
                ✨ Upgrade
              </Link>
            )}
            <Link
              href="/profile"
              className={clsx(
                "flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium transition-colors",
                pathname === "/profile"
                  ? "bg-brand-50 text-brand-700"
                  : "text-gray-600 hover:text-gray-900 hover:bg-gray-100"
              )}
            >
              👤
              <span className="hidden sm:inline">Profile</span>
            </Link>
            <button
              onClick={handleLogout}
              className="text-sm text-gray-500 hover:text-gray-900 transition-colors px-2 py-1.5"
            >
              Sign out
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
}
