"use client";
import { useEffect, useState } from "react";

export default function ConfidenceScore() {
  const [ready, setReady] = useState(false);
  useEffect(() => { const timer = setTimeout(() => setReady(true), 100); return () => clearTimeout(timer); }, []);
  return <div className="relative mx-auto grid h-56 w-56 place-items-center sm:h-64 sm:w-64" aria-label="96 percent confidence score">
    <svg className="absolute inset-0 -rotate-90" viewBox="0 0 120 120" aria-hidden="true"><circle cx="60" cy="60" r="51" fill="none" stroke="rgba(105,86,232,.12)" strokeWidth="7"/><circle cx="60" cy="60" r="51" fill="none" stroke="url(#score-gradient)" strokeLinecap="round" strokeWidth="7" strokeDasharray="320.44" strokeDashoffset={ready ? "12.82" : "320.44"} className="transition-[stroke-dashoffset] duration-[1600ms] ease-out"/><defs><linearGradient id="score-gradient" x1="5" x2="115" y1="15" y2="105"><stop stopColor="#6d59e8"/><stop offset="1" stopColor="#d365d8"/></linearGradient></defs></svg>
    <div className="grid h-40 w-40 place-items-center rounded-full bg-white/70 shadow-xl shadow-violet-200/40"><div><p className="text-5xl font-semibold tracking-[-.08em] text-[#1b1834] sm:text-6xl">96<span className="text-2xl tracking-normal text-violet-600">%</span></p><p className="mt-1 text-center text-xs font-medium tracking-wider text-slate-500">CONFIDENCE</p></div></div>
  </div>;
}
