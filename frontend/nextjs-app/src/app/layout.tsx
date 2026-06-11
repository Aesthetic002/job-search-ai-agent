import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Job Search AI — Your AI-Powered Job Search Agent",
  description:
    "Your intelligent AI-powered job search assistant. Track applications, optimize your resume for ATS, and ace interviews with real-time coaching.",
  keywords: ["job search", "AI agent", "resume ATS", "interview prep", "application tracker"],
  openGraph: {
    title: "Job Search AI — Your AI-Powered Job Search Agent",
    description:
      "Track applications, optimize your resume for ATS, and ace interviews with AI-powered coaching.",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" style={{ height: "100%" }}>
      <body style={{ height: "100%", display: "flex", flexDirection: "column" }}>
        {children}
      </body>
    </html>
  );
}
