import type { Metadata } from "next";
import "./globals.css";
import { Providers } from "./providers";
import { Toaster } from "react-hot-toast";

export const metadata: Metadata = {
  title: "HireLoop PK — Stop getting ghosted. Start getting hired.",
  description:
    "Pakistan's first AI-powered job application intelligence platform for students and fresh graduates.",
  keywords: ["jobs pakistan", "job tracker", "internship pakistan", "AI job application"],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <Providers>
          {children}
          <Toaster
            position="top-right"
            toastOptions={{
              duration: 4000,
              style: { borderRadius: "8px", fontSize: "14px" },
            }}
          />
        </Providers>
      </body>
    </html>
  );
}
