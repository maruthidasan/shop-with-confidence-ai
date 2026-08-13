import Link from "next/link";

export default function Navbar() {
  return (
    <nav className="mx-auto flex w-full max-w-7xl items-center justify-between px-5 py-5 sm:px-8">
      <Link href="/" className="flex items-center gap-2.5 text-lg font-semibold tracking-tight">
        <span className="grid h-8 w-8 place-items-center rounded-xl bg-[#17152b] text-sm text-white shadow-lg shadow-violet-300">V</span>
        Fashion Retail
      </Link>
      <Link href="/upload" className="rounded-full bg-[#17152b] px-4 py-2 text-sm font-medium text-white transition hover:bg-[#353052]">Find My Outfit</Link>
    </nav>
  );
}
