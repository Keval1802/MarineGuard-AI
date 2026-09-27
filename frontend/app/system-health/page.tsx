"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

export default function SystemHealthPage() {
  const router = useRouter();
  useEffect(() => {
    router.replace("/dashboard");
  }, [router]);

  return <div className="p-8 text-center text-slate-500 font-mono">Redirecting to Dashboard...</div>;
}
