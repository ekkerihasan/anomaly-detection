import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "standalone",
  // Without this, opening the dev server at http://127.0.0.1:3000 instead of
  // http://localhost:3000 silently blocks /_next/hmr and the client bundle,
  // so "use client" components render but never hydrate -- the triage buttons
  // look fine and do nothing, with no console error. Both hostnames are the
  // same machine, and people type either one.
  allowedDevOrigins: ["127.0.0.1", "localhost"],
};

export default nextConfig;
