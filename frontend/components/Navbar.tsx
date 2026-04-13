"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { clsx } from "clsx";

const navLinks = [
  { href: "/dashboard", label: "Dashboard", emoji: "📊" },
  { href: "/tracker", label: "Tracker", emoji: "📋" },
  { href: "/jobs", label: "Jobs", emoji: "💼" },
  { href: "/prep", label: "Interview Prep", emoji: "🎤" },
];

export default function Navbar() {
  const pathname = usePathname();
  const router = useRouter();

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
          <button
            onClick={handleLogout}
            className="text-sm text-gray-500 hover:text-gray-900 transition-colors"
          >
            Sign out
          </button>
        </div>
      </div>
    </nav>
  );
}
