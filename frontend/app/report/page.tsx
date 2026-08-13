import Link from "next/link";
import ConfidenceScore from "@/components/journey/ConfidenceScore";
import MatchCard from "@/components/journey/MatchCard";
import AccessoryCard from "@/components/journey/AccessoryCard";

const matches = [
  ["Skin Tone Match", "Navy brings a rich, balanced contrast to your complexion."],
  ["Occasion Match", "The polished tailoring fits the tone of an interview beautifully."],
  ["Color Harmony", "Each neutral works together to create a calm, intentional palette."],
  ["Professional Appearance", "The structured silhouette reads confident, capable and composed."],
] as const;
const accessories = [
  ["Shoes", "◒", "Leather loafers", "from-stone-100 to-stone-300"],
  ["Watch", "◷", "Minimal steel", "from-slate-100 to-slate-300"],
  ["Belt", "◌", "Soft brown leather", "from-amber-100 to-orange-200"],
  ["Bag", "▱", "Structured tote", "from-violet-100 to-fuchsia-100"],
  ["Tie", "◇", "Textured navy", "from-blue-100 to-indigo-200"],
] as const;

export default function ReportPage() {
  return <main className="page-background"><header className="mx-auto flex max-w-7xl items-center justify-between px-5 py-5 sm:px-8"><Link href="/" className="flex items-center gap-2.5 text-lg font-semibold"><span className="grid h-8 w-8 place-items-center rounded-xl bg-[#17152b] text-sm text-white">V</span>Fashion Retail</Link><Link href="/recommendations" className="text-sm font-medium text-slate-600 transition hover:text-violet-700">← Your edit</Link></header><section className="mx-auto max-w-6xl px-5 pb-20 pt-8 sm:px-8"><div className="glass overflow-hidden rounded-[2.5rem] px-6 py-12 text-center sm:px-12"><p className="text-sm font-medium tracking-widest text-violet-600">YOUR CONFIDENCE REPORT</p><div className="mt-6"><ConfidenceScore /></div><h1 className="mt-5 text-4xl font-semibold tracking-tight sm:text-5xl">You Look Great!</h1><p className="mx-auto mt-4 max-w-md leading-7 text-slate-600">Our AI believes this outfit is highly suitable. You have a considered look that&apos;s ready to make an impression.</p></div><section className="mt-14"><div className="max-w-xl"><p className="text-sm font-medium text-violet-600">WHY IT WORKS</p><h2 className="mt-2 text-3xl font-semibold tracking-tight">A closer look at your match.</h2></div><div className="mt-7 grid gap-4 sm:grid-cols-2">{matches.map(([label, detail]) => <MatchCard key={label} label={label} detail={detail} />)}</div></section><section className="mt-14 grid gap-7 lg:grid-cols-[.9fr_1.1fr] lg:items-start"><div><p className="text-sm font-medium text-violet-600">THE REASONING</p><h2 className="mt-2 text-3xl font-semibold tracking-tight">Why AI selected this outfit</h2><ul className="mt-6 space-y-4">{["Navy complements your complexion with a rich, balanced contrast.", "The formal style matches interview expectations without looking rigid.", "A controlled neutral palette creates balanced color harmony.", "The professional silhouette feels sharp, considered and approachable.", "It is a confidence-boosting look that keeps the focus on you."].map((item) => <li key={item} className="flex gap-3 text-slate-600"><span className="mt-1 grid h-5 w-5 shrink-0 place-items-center rounded-full bg-violet-100 text-xs text-violet-700">✓</span><span className="leading-6">{item}</span></li>)}</ul></div><div className="glass rounded-[2rem] p-7"><p className="text-sm font-medium text-slate-500">The feeling to take with you</p><p className="mt-3 text-2xl font-semibold leading-9 tracking-tight">“Put together, not overdone. This is your quiet-confidence look.”</p><div className="mt-8 h-1.5 overflow-hidden rounded-full bg-violet-100"><div className="animate-report-bar h-full rounded-full bg-gradient-to-r from-violet-600 to-fuchsia-500" /></div></div></section><section className="mt-16"><div className="flex flex-wrap items-end justify-between gap-3"><div><p className="text-sm font-medium text-violet-600">FINISHING TOUCHES</p><h2 className="mt-2 text-3xl font-semibold tracking-tight">Complete your look.</h2></div><p className="text-sm text-slate-500">Thoughtful additions, all in one edit.</p></div><div className="mt-7 grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-5">{accessories.map(([title, icon, caption, tint]) => <AccessoryCard key={title} title={title} icon={icon} caption={caption} tint={tint} />)}</div></section></section></main>;
}
