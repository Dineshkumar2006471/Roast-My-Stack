import React from "react";

const Footer = () => {
  return (
    <footer className="w-full py-12 bg-zinc-50 dark:bg-zinc-900 border-t border-zinc-200/5 dark:border-zinc-800/15 flex flex-col md:flex-row justify-between items-center px-8 max-w-7xl mx-auto">
      <div className="text-lg font-bold text-zinc-900 dark:text-white mb-4 md:mb-0">RoastMyStack</div>
      <div className="text-sm font-medium text-zinc-500 dark:text-zinc-400 mb-4 md:mb-0 text-center md:text-left">
        © 2024 RoastMyStack. Editorial Precision Guaranteed.
      </div>
      <div className="flex space-x-6">
        <a className="text-sm font-medium text-zinc-500 hover:text-zinc-900 hover:underline transition-colors duration-200" href="#">Terms</a>
        <a className="text-sm font-medium text-zinc-500 hover:text-zinc-900 hover:underline transition-colors duration-200" href="#">Privacy</a>
        <a className="text-sm font-medium text-zinc-500 hover:text-zinc-900 hover:underline transition-colors duration-200" href="#">Twitter</a>
        <a className="text-sm font-medium text-zinc-500 hover:text-zinc-900 hover:underline transition-colors duration-200" href="#">GitHub</a>
      </div>
    </footer>
  );
};

export default Footer;
