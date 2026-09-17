import type { Metadata } from "next";
import { Space_Grotesk, Geist_Mono } from "next/font/google";
import Link from "next/link";
import "./globals.css";

const spaceGrotesk = Space_Grotesk({
  variable: "--font-space-grotesk",
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Anomaly Detection · Public Procurement Audit",
  description:
    "Ranks government tender awards by how much they deviate from normal procurement behaviour, and shows an auditor exactly why — SDG 16, GFR 2017.",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html
      lang="en"
      className={`${spaceGrotesk.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col bg-beige">
        {/* ── Navigation ── */}
        <nav className="sticky top-0 z-50 border-b-[2.5px] border-charcoal bg-white/95 backdrop-blur-sm">
          <div className="max-w-7xl mx-auto w-full flex items-center justify-between px-5 py-3">
            {/* Brand */}
            <Link href="/" className="flex items-center gap-3 group">
              <div className="w-8 h-8 bg-orange border-2 border-charcoal rounded-lg shadow-[2px_2px_0px_#2B2B2B] flex items-center justify-center transition-all group-hover:shadow-[3px_3px_0px_#2B2B2B] group-hover:translate-x-[-0.5px] group-hover:translate-y-[-0.5px]">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" />
                  <line x1="12" y1="9" x2="12" y2="13" />
                  <line x1="12" y1="17" x2="12.01" y2="17" />
                </svg>
              </div>
              <span className="text-[0.95rem] font-bold tracking-tight text-charcoal leading-tight">
                Anomaly Detection
              </span>
            </Link>

            {/* Nav links */}
            <div className="hidden md:flex items-center gap-1">
              <Link href="/" className="px-3 py-1.5 text-sm font-semibold text-concrete hover:text-charcoal rounded-lg transition-colors">
                Overview
              </Link>
              <Link href="/awards" className="px-3 py-1.5 text-sm font-semibold text-concrete hover:text-charcoal rounded-lg transition-colors">
                Review Queue
              </Link>
              <Link href="/awards/demo" className="px-3 py-1.5 text-sm font-semibold text-concrete hover:text-charcoal rounded-lg transition-colors">
                Sample Card
              </Link>
            </div>

            {/* Right: SDG badge only */}
            <div className="neo-badge neo-badge-dark">
              SDG 16
            </div>
          </div>
        </nav>

        {/* ── Content ── */}
        <div className="flex-1 flex flex-col">
          {children}
        </div>
      </body>
    </html>
  );
}
