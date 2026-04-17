"use client";

import { useState } from "react";
import { Coffee, Skull, Terminal, GitBranch, Code2 } from "lucide-react";

type RoastInputProps = {
  onSubmit: (type: "github" | "snippet", content: string, intensity: string) => void;
  isLoading: boolean;
};

export default function RoastInput({ onSubmit, isLoading }: RoastInputProps) {
  const [activeTab, setActiveTab] = useState<"github" | "snippet">("github");
  const [content, setContent] = useState("");
  const [intensity, setIntensity] = useState<"junior" | "senior" | "staff">("senior");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!content.trim()) return;
    onSubmit(activeTab, content, intensity);
  };

  return (
    <div className="glass-panel rounded-2xl p-6 sm:p-8 w-full max-w-3xl mx-auto mt-12 relative overflow-hidden">
      {/* Decorative background glow */}
      <div className="absolute -top-32 -right-32 w-64 h-64 bg-[var(--electric-purple)] rounded-full mix-blend-multiply filter blur-[128px] opacity-20"></div>
      <div className="absolute -bottom-32 -left-32 w-64 h-64 bg-[var(--neon-green)] rounded-full mix-blend-multiply filter blur-[128px] opacity-20"></div>

      <div className="relative z-10">
        <div className="flex bg-black/40 p-1 rounded-lg w-fit mx-auto mb-8 border border-white/5">
          <button
            type="button"
            onClick={() => setActiveTab("github")}
            className={`flex items-center gap-2 px-6 py-2.5 rounded-md text-sm font-medium transition-all duration-300 ${
              activeTab === "github"
                ? "bg-white/10 text-white shadow-sm"
                : "text-gray-400 hover:text-white hover:bg-white/5"
            }`}
          >
            <GitBranch className="w-4 h-4" />
            GitHub URL
          </button>
          <button
            type="button"
            onClick={() => setActiveTab("snippet")}
            className={`flex items-center gap-2 px-6 py-2.5 rounded-md text-sm font-medium transition-all duration-300 ${
              activeTab === "snippet"
                ? "bg-[var(--electric-purple)]/20 text-[var(--electric-purple)] shadow-sm"
                : "text-gray-400 hover:text-[var(--electric-purple)] hover:bg-white/5"
            }`}
          >
            <Code2 className="w-4 h-4" />
            Paste Code
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-8">
          <div className="space-y-2">
            <label className="text-sm font-medium text-gray-400 uppercase tracking-wider font-mono">
              {activeTab === "github" ? "Repository Link" : "Source Code"}
            </label>
            {activeTab === "github" ? (
              <input
                type="url"
                value={content}
                onChange={(e) => setContent(e.target.value)}
                placeholder="https://github.com/owner/repo"
                className="w-full bg-black/50 border border-white/10 rounded-xl px-4 py-4 text-white placeholder-gray-600 focus:outline-none focus:border-[var(--neon-green)] focus:ring-1 focus:ring-[var(--neon-green)] transition-all font-mono"
                required
              />
            ) : (
              <textarea
                value={content}
                onChange={(e) => setContent(e.target.value)}
                placeholder="function doSomethingBad() { ... }"
                rows={6}
                className="w-full bg-black/50 border border-white/10 rounded-xl px-4 py-4 text-white placeholder-gray-600 focus:outline-none focus:border-[var(--electric-purple)] focus:ring-1 focus:ring-[var(--electric-purple)] transition-all font-mono resize-none"
                required
              />
            )}
          </div>

          <div className="space-y-4">
            <label className="text-sm font-medium text-gray-400 uppercase tracking-wider font-mono">
              Roast Intensity
            </label>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <label
                className={`cursor-pointer flex flex-col items-center gap-2 p-4 rounded-xl border transition-all duration-300 ${
                  intensity === "junior"
                    ? "bg-blue-500/10 border-blue-500/50 text-blue-400"
                    : "bg-black/40 border-white/5 text-gray-500 hover:border-white/20 hover:text-gray-300"
                }`}
              >
                <input
                  type="radio"
                  name="intensity"
                  value="junior"
                  checked={intensity === "junior"}
                  onChange={() => setIntensity("junior")}
                  className="sr-only"
                />
                <Coffee className="w-6 h-6 mb-1" />
                <span className="font-semibold">Junior Review</span>
                <span className="text-xs opacity-70 text-center">Gentle but firm.</span>
              </label>
              
              <label
                className={`cursor-pointer flex flex-col items-center gap-2 p-4 rounded-xl border transition-all duration-300 ${
                  intensity === "senior"
                    ? "bg-[var(--electric-purple)]/10 border-[var(--electric-purple)]/50 text-[var(--electric-purple)]"
                    : "bg-black/40 border-white/5 text-gray-500 hover:border-white/20 hover:text-gray-300"
                }`}
              >
                <input
                  type="radio"
                  name="intensity"
                  value="senior"
                  checked={intensity === "senior"}
                  onChange={() => setIntensity("senior")}
                  className="sr-only"
                />
                <Terminal className="w-6 h-6 mb-1" />
                <span className="font-semibold">Senior Review</span>
                <span className="text-xs opacity-70 text-center">Direct & no-nonsense.</span>
              </label>

              <label
                className={`cursor-pointer flex flex-col items-center gap-2 p-4 rounded-xl border transition-all duration-300 ${
                  intensity === "staff"
                    ? "bg-[var(--danger-red)]/10 border-[var(--danger-red)]/50 text-[var(--danger-red)]"
                    : "bg-black/40 border-white/5 text-gray-500 hover:border-white/20 hover:text-gray-300"
                }`}
              >
                <input
                  type="radio"
                  name="intensity"
                  value="staff"
                  checked={intensity === "staff"}
                  onChange={() => setIntensity("staff")}
                  className="sr-only"
                />
                <Skull className="w-6 h-6 mb-1" />
                <span className="font-semibold">Staff Wrath</span>
                <span className="text-xs opacity-70 text-center">Brutal & merciless.</span>
              </label>
            </div>
          </div>

          <button
            type="submit"
            disabled={isLoading || !content.trim()}
            className="w-full bg-white text-black hover:bg-gray-200 disabled:bg-white/20 disabled:text-white/40 font-bold py-4 px-8 rounded-xl transition-all duration-300 hover:scale-[1.02] active:scale-95 glow-border relative overflow-hidden"
          >
            {isLoading ? (
              <span className="flex items-center justify-center gap-3">
                <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                </svg>
                Roasting Code...
              </span>
            ) : (
              "Roast My Code"
            )}
          </button>
        </form>
      </div>
    </div>
  );
}
