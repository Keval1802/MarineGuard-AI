"use client";

import React, { useState } from "react";
import { setAuthToken } from "@/lib/auth";
import { useRouter } from "next/navigation";
import { ShieldCheck, User, Key } from "lucide-react";

export default function LoginPage() {
  const router = useRouter();
  const [role, setRole] = useState<"admin" | "user">("admin");

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    const token = role === "admin" ? "dev-admin-token" : "dev-test-token";
    setAuthToken(token);
    router.push("/dashboard");
  };

  return (
    <div className="max-w-md mx-auto space-y-6 py-12">
      <div className="bg-slate-900 border border-slate-800 p-8 rounded-2xl shadow-2xl space-y-6 text-center">
        
        <div className="w-12 h-12 rounded-xl bg-marine-500/15 border border-marine-500/30 text-marine-400 flex items-center justify-center mx-auto">
          <ShieldCheck className="w-6 h-6" />
        </div>

        <div>
          <h1 className="text-2xl font-extrabold text-slate-100">Session Authentication</h1>
          <p className="text-xs text-slate-400 mt-1">Local Development & Testing Session Access</p>
        </div>

        <form onSubmit={handleLogin} className="space-y-4 text-left">
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-2">Select User Role Session</label>
            <select
              value={role}
              onChange={(e) => setRole(e.target.value as "admin" | "user")}
              className="w-full bg-slate-950 border border-slate-800 text-slate-200 rounded-xl p-3 text-sm focus:outline-none focus:border-marine-500"
            >
              <option value="admin">Administrator (Full Access & Re-Analysis)</option>
              <option value="user">Authenticated Investigator</option>
            </select>
          </div>

          <button
            type="submit"
            className="w-full py-3 rounded-xl font-bold bg-marine-500 hover:bg-marine-400 text-white shadow-lg transition-all text-sm"
          >
            Authenticate Session & Launch Dashboard
          </button>
        </form>

      </div>
    </div>
  );
}
