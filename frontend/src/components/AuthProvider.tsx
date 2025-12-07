"use client";

export function AuthProvider({ children }: { children: React.ReactNode }) {
  // Auth disabled - all routes are public
  return <>{children}</>;
}
