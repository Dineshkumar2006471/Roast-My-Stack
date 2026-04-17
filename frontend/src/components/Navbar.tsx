"use client";

import React from "react";

const Navbar = () => {
  return (
    <header className="fixed top-0 w-full z-50 bg-white/70 dark:bg-zinc-950/70 backdrop-blur-3xl shadow-[0_20px_40px_rgba(0,0,0,0.04)] no-border">
      <div className="flex justify-between items-center max-w-7xl mx-auto px-8 py-4">
        <div className="text-xl font-extrabold tracking-tighter text-zinc-900 dark:text-white cursor-pointer" onClick={() => window.location.href = '/'}>
          RoastMyStack
        </div>
        <nav className="hidden md:flex space-x-8">
          <a className="text-zinc-500 dark:text-zinc-400 font-medium hover:scale-105 transition-transform duration-200 ease-out" href="#">Roasts</a>
          <a className="text-zinc-500 dark:text-zinc-400 font-medium hover:scale-105 transition-transform duration-200 ease-out" href="#">Leaderboard</a>
          <a className="text-zinc-500 dark:text-zinc-400 font-medium hover:scale-105 transition-transform duration-200 ease-out" href="#">Pricing</a>
        </nav>
        <div className="flex items-center space-x-4">
          <button className="hidden md:block font-['Inter'] tracking-[-0.04em] font-bold text-blue-600 dark:text-blue-400 hover:scale-105 transition-transform duration-200 ease-out active:scale-95 transition-all">
            Join Waitlist
          </button>
          <span className="material-symbols-outlined text-zinc-500 dark:text-zinc-400 cursor-pointer hover:scale-105 transition-transform duration-200 ease-out">
            settings
          </span>
        </div>
      </div>
    </header>
  );
};

export default Navbar;
