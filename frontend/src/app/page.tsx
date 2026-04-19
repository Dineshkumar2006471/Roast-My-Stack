"use client";

import { useState, useEffect } from "react";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import ScoreBoard from "@/components/ScoreBoard";
import { submitRoast, RoastResult } from "@/lib/api";

export default function Home() {
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<RoastResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  
  const [activeTab, setActiveTab] = useState<"github" | "snippet">("github");
  const [content, setContent] = useState("");
  const [intensity, setIntensity] = useState<"mild" | "spicy" | "brutal">("spicy");

  const handleRoast = async () => {
    if (!content.trim()) return;
    setIsLoading(true);
    setError(null);
    try {
      // Map intensities to backend expectations if necessary
      const mappedIntensity = intensity === "mild" ? "junior" : intensity === "spicy" ? "senior" : "staff";
      const data = await submitRoast(activeTab, content, mappedIntensity);
      setResult(data);
      // Scroll to result
      setTimeout(() => {
        document.getElementById("results")?.scrollIntoView({ behavior: "smooth" });
      }, 100);
    } catch (err: any) {
      setError(err?.response?.data?.detail || err.message || "An error occurred.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="text-on-surface antialiased bg-surface min-h-screen">
      <Navbar />

      <main className="pt-32 pb-24" id="main-content" role="main" aria-label="Code roast results">
        {/* Hero Section */}
        <section className="py-24 relative overflow-hidden flex flex-col items-center justify-center text-center px-4">
          <div className="absolute inset-0 pointer-events-none flex justify-center items-center opacity-10">
            <span className="material-symbols-outlined text-[120px] text-primary absolute top-10 left-1/4 animate-bounce">code</span>
            <span className="material-symbols-outlined text-[100px] text-secondary absolute bottom-20 right-1/4 animate-bounce" style={{ animationDelay: '1s' }}>bug_report</span>
          </div>

          <div className="relative z-10 max-w-3xl mx-auto w-full">
            <h1 className="text-5xl md:text-7xl font-extrabold tracking-[-0.04em] text-on-surface mb-6">
              Your Code. <span className="gradient-text">Senior Style.</span>
            </h1>
            <p className="text-xl md:text-2xl text-on-surface-variant font-medium mb-12 max-w-2xl mx-auto">
              Explore your architectural sins with the best AI code roaster.
            </p>

            <div className="flex flex-col items-center gap-4">
              <div className="flex bg-surface-container-low p-1 rounded-full mb-4 outline outline-1 outline-outline-variant/20">
                <button 
                  onClick={() => setActiveTab("github")}
                  className={`px-6 py-2 rounded-full text-sm font-bold transition-all ${activeTab === 'github' ? 'bg-primary text-on-primary shadow-md' : 'text-on-surface-variant hover:bg-surface-container-high'}`}
                >
                  GitHub URL
                </button>
                <button 
                  onClick={() => setActiveTab("snippet")}
                  className={`px-6 py-2 rounded-full text-sm font-bold transition-all ${activeTab === 'snippet' ? 'bg-primary text-on-primary shadow-md' : 'text-on-surface-variant hover:bg-surface-container-high'}`}
                >
                  Code Snippet
                </button>
              </div>

              <div className="w-full max-w-[700px] relative glass-morphism rounded-2xl md:rounded-full p-2 flex flex-col md:flex-row items-center outline outline-1 outline-outline-variant/20 ambient-shadow">
                <span className="material-symbols-outlined text-on-surface-variant ml-4 hidden md:block">
                  {activeTab === 'github' ? 'link' : 'code'}
                </span>
                {activeTab === 'github' ? (
                  <input
                    type="text"
                    value={content}
                    onChange={(e) => setContent(e.target.value)}
                    className="w-full bg-transparent border-none text-on-surface focus:ring-0 px-4 py-3 placeholder:text-on-surface-variant/60 font-medium"
                    placeholder="Paste your GitHub repo URL..."
                  />
                ) : (
                  <textarea
                    value={content}
                    onChange={(e) => setContent(e.target.value)}
                    className="w-full bg-transparent border-none text-on-surface focus:ring-0 px-4 py-3 placeholder:text-on-surface-variant/60 font-medium resize-none"
                    placeholder="Paste your nasty code snippet here..."
                    rows={1}
                  />
                )}
                <button 
                  disabled={isLoading}
                  onClick={handleRoast}
                  className="w-full md:w-auto btn-gradient text-on-primary font-bold py-3 px-8 rounded-full hover:scale-[1.02] active:scale-95 transition-all shadow-md whitespace-nowrap disabled:opacity-50"
                >
                  {isLoading ? "Roasting..." : "Roast Now"}
                </button>
              </div>

              {/* Intensity Selector */}
              <div className="mt-8 inline-flex items-center space-x-2 glass-morphism rounded-full px-4 py-2 outline outline-1 outline-outline-variant/20">
                <span className="text-sm font-bold text-on-surface-variant mr-2">Roast Intensity:</span>
                <button 
                  onClick={() => setIntensity("mild")}
                  className={`px-3 py-1 rounded-full text-sm font-medium transition-colors ${intensity === 'mild' ? 'bg-primary text-on-primary shadow-sm' : 'bg-surface-container-low text-on-surface hover:bg-primary-container hover:text-on-primary-container'}`}
                >
                  Mild
                </button>
                <button 
                  onClick={() => setIntensity("spicy")}
                  className={`px-3 py-1 rounded-full text-sm font-medium transition-colors ${intensity === 'spicy' ? 'bg-primary text-on-primary shadow-sm' : 'bg-surface-container-low text-on-surface hover:bg-primary-container hover:text-on-primary-container'}`}
                >
                  Spicy
                </button>
                <button 
                  onClick={() => setIntensity("brutal")}
                  className={`px-3 py-1 rounded-full text-sm font-medium transition-colors ${intensity === 'brutal' ? 'bg-secondary text-on-secondary shadow-sm' : 'bg-surface-container-low text-on-surface hover:bg-secondary-container hover:text-on-secondary-container'}`}
                >
                  Brutal
                </button>
              </div>
            </div>

            {error && (
              <div className="mt-8 p-4 bg-error-container text-on-error-container rounded-xl font-mono text-sm max-w-xl mx-auto border border-error/20">
                {error}
              </div>
            )}
          </div>
        </section>

        {/* Results Section */}
        {result && (
          <section id="results" className="max-w-[1200px] mx-auto px-4 py-16 animate-in fade-in slide-in-from-bottom-8 duration-700" aria-label="Analysis Results">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {/* The Roast Card */}
              <div className="col-span-1 md:col-span-2 bg-surface-container-lowest rounded-xl p-8 card-hover transition-all duration-300 ambient-shadow flex flex-col min-h-[500px]" aria-labelledby="roast-heading">
                <div className="flex items-center space-x-3 mb-6">
                  <span className="material-symbols-outlined text-secondary text-2xl" aria-hidden="true">local_fire_department</span>
                  <h2 id="roast-heading" className="text-xl font-bold tracking-tight text-on-surface">The Roast</h2>
                </div>
                <blockquote className="flex-grow bg-inverse-surface rounded-lg p-6 font-mono text-sm text-inverse-on-surface shadow-inner whitespace-pre-wrap leading-relaxed" aria-label="AI code review">
                  <div className="text-secondary-fixed-dim/80 mb-4 italic border-b border-white/5 pb-2">
                    "Detected some major architectural sins. Pulling up the red marker..."
                  </div>
                  {result.roast}
                </blockquote>
              </div>

              {/* The Scores Card */}
              <ScoreBoard scores={result.scores} />

              {/* The Fix Plan Card */}
              <div className="col-span-1 md:col-span-3 bg-surface-container-lowest rounded-xl p-8 card-hover transition-all duration-300 ambient-shadow" aria-labelledby="fixplan-heading">
                <div className="flex items-center space-x-3 mb-8">
                  <span className="material-symbols-outlined text-tertiary text-2xl" aria-hidden="true">construction</span>
                  <h2 id="fixplan-heading" className="text-xl font-bold tracking-tight text-on-surface">The Fix Plan</h2>
                </div>
                <ol className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6" aria-label="Ordered fix plan">
                  {result.fixPlan.map((step, idx) => (
                    <li key={idx} className="p-6 rounded-xl bg-surface-container-low border border-outline-variant/20 hover:border-primary/30 transition-colors">
                      <div className="flex items-center gap-3 mb-4">
                        <span className="w-8 h-8 rounded-full bg-primary text-on-primary flex items-center justify-center font-bold text-sm">
                          {step.priority}
                        </span>
                        <h4 className="font-bold text-on-surface">{step.issue}</h4>
                      </div>
                      <p className="text-sm text-on-surface-variant leading-relaxed italic">
                        "{step.fix}"
                      </p>
                    </li>
                  ))}
                </ol>
              </div>
            </div>
          </section>
        )}

        {/* Feature Demo (Bento Preview) - Only show if no result yet */}
        {!result && (
          <section className="max-w-[1200px] mx-auto px-4 py-16 opacity-50 grayscale hover:grayscale-0 transition-all duration-700">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="bg-surface-container-lowest rounded-xl p-8 ambient-shadow h-[300px] flex flex-col">
                <div className="flex items-center space-x-3 mb-4">
                  <span className="material-symbols-outlined text-secondary">local_fire_department</span>
                  <h3 className="font-bold">The Roast</h3>
                </div>
                <div className="bg-inverse-surface flex-grow rounded p-4 text-[10px] font-mono text-inverse-on-surface opacity-50">
                  // Example output...
                </div>
              </div>
              <div className="bg-surface-container-lowest rounded-xl p-8 ambient-shadow h-[300px] flex flex-col justify-center items-center">
                 <div className="w-32 h-32 rounded-full border-8 border-surface-container flex items-center justify-center text-3xl font-black">42</div>
                 <p className="mt-4 font-bold text-sm">Design Quality</p>
              </div>
              <div className="bg-surface-container-lowest rounded-xl p-8 ambient-shadow h-[300px]">
                <div className="flex items-center space-x-3 mb-4">
                  <span className="material-symbols-outlined text-tertiary">history</span>
                  <h3 className="font-bold">The History</h3>
                </div>
                <div className="space-y-2">
                  {[1, 2, 3].map(i => <div key={i} className="h-4 bg-surface-container-low rounded w-full"></div>)}
                </div>
              </div>
            </div>
          </section>
        )}
      </main>

      <Footer />
    </div>
  );
}
