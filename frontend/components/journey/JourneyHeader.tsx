import Link from "next/link";

export default function JourneyHeader({ step }: { step: number }) {
  return <header className="mx-auto flex w-full max-w-5xl items-center justify-between px-5 py-5 sm:px-8"><Link href="/" className="flex items-center gap-2.5 text-lg font-semibold tracking-tight"><span className="grid h-8 w-8 place-items-center rounded-xl bg-[#17152b] text-sm text-white">V</span>Fashion Retail</Link><div className="hidden items-center gap-2 sm:flex">{[1,2,3].map((item) => <span key={item} className={`h-1.5 w-10 rounded-full ${item <= step ? "bg-violet-600" : "bg-slate-200"}`} />)}</div><span className="text-sm text-slate-500">Step {Math.min(step, 3)} of 3</span></header>;
}
