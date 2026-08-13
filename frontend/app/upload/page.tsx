"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";

const occasions = ["Interview", "Business Meeting", "Casual", "Date Night", "Wedding", "Travel", "Summer"];
const loadingMessages = ["Understanding your occasion…", "Reading your style preferences…", "Exploring looks that work together…", "Matching pieces from the collection…", "Adding the finishing touches…", "Your stylist is almost ready…"];

export default function UploadPage() {
  const router = useRouter();
  const [preview, setPreview] = useState("");
  const [occasion, setOccasion] = useState("Interview");
  const [gender, setGender] = useState("Men");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [loadingMessage, setLoadingMessage] = useState(0);

  useEffect(() => {
    if (!busy) return;
    const timer = window.setInterval(() => setLoadingMessage(current => (current + 1) % loadingMessages.length), 2400);
    return () => window.clearInterval(timer);
  }, [busy]);

  async function prepareImage(file: File) {
    // Preserve the single upload exactly. The backend derives a separate crop
    // exclusively for Skin Analysis and sends these original bytes to Clothes VTO.
    return await new Promise<string>((resolve, reject) => {
      const reader = new FileReader();
      reader.onerror = () => reject(new Error("Could not read the image."));
      reader.onload = () => resolve(String(reader.result));
      reader.readAsDataURL(file);
    });
  }

  async function submit() {
    if (!preview) {
      setError("Upload a full-body photo first.");
      return;
    }
    setBusy(true);
    setLoadingMessage(0);
    setError("");

    try {
      const response = await fetch("/api/recommend", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          occasion,
          photoUrl: preview,
          category: null,
          gender,
          preferredColors: [],
        }),
      });

      const rawBody = await response.text();
      let body: { message?: string; detail?: unknown };
      try {
        body = JSON.parse(rawBody) as { message?: string; detail?: unknown };
      } catch {
        throw new Error("The AI Stylist service returned an invalid response. Please try again after the deployment is updated.");
      }
      if (!response.ok) {
        const detail = body.message || (typeof body.detail === "string" ? body.detail : undefined) || "The AI Stylist could not complete your edit.";
        throw new Error(detail);
      }

      sessionStorage.setItem("vela-recommendations", JSON.stringify(body));
      sessionStorage.setItem("vela-photo", preview);
      router.push("/recommendations");
    } catch (e) {
      setError(e instanceof Error ? e.message : "The AI Stylist could not complete your edit.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="page-background min-h-screen" aria-busy={busy}>
      <header className="mx-auto flex max-w-7xl items-center justify-between px-5 py-5 sm:px-8">
        <Link href="/" className="text-lg font-semibold">Fashion Retail</Link>
        <Link href="/" className="text-sm text-slate-500">Back to store</Link>
      </header>
      <section className="mx-auto max-w-5xl px-5 pb-20 pt-10 sm:px-8">
        <p className="text-sm font-semibold uppercase tracking-[.16em] text-violet-600">AI STYLIST</p>
        <h1 className="mt-3 text-4xl font-semibold tracking-tight sm:text-5xl">Let&apos;s find the look that feels like you.</h1>
        <p className="mt-4 max-w-2xl leading-7 text-slate-600">
          Upload one clear full-body photo. We&apos;ll create a separate face and upper-body crop for appearance analysis, then prepare your virtual try-on from the original image.
        </p>

        <div className="mt-10 grid gap-8 lg:grid-cols-[1fr_.8fr]">
          <label className="grid min-h-[460px] cursor-pointer place-items-center overflow-hidden rounded-3xl border-2 border-dashed border-slate-300 bg-white shadow-sm focus-within:outline focus-within:outline-2 focus-within:outline-offset-4 focus-within:outline-violet-700">
            <input
              type="file"
              accept="image/jpeg,image/png,image/webp"
              className="sr-only"
              onChange={async e => {
                const file = e.target.files?.[0];
                if (!file) return;
                try {
                  setPreview(await prepareImage(file));
                  setError("");
                } catch (err) {
                  setError(err instanceof Error ? err.message : "Could not read the image.");
                }
              }}
            />
            {preview
              ? <img src={preview} alt="Your full-body photo" className="h-full w-full object-cover" />
              : <div className="p-10 text-center"><div className="mx-auto grid h-16 w-16 place-items-center rounded-full bg-violet-50 text-2xl">↑</div><h2 className="mt-5 text-xl font-semibold">Upload your photo</h2><p className="mt-2 text-sm text-slate-500">JPG or PNG · clear face · good lighting</p></div>}
          </label>

          <div className="rounded-3xl border border-slate-200 bg-white p-7 shadow-sm">
            <p className="text-sm font-semibold">What are you dressing for?</p>
            <div className="mt-4 grid grid-cols-2 gap-2">
              {occasions.map(item => (
                <button key={item} type="button" onClick={() => setOccasion(item)}
                  className={`rounded-xl border px-3 py-3 text-sm ${occasion === item ? "border-violet-600 bg-violet-50 text-violet-800" : "border-slate-200 text-slate-600"}`}>
                  {item}
                </button>
              ))}
            </div>

            <p className="mt-7 text-sm font-semibold">Style profile</p>
            <div className="mt-3 flex gap-2">
              {["Men", "Women"].map(item => (
                <button key={item} type="button" onClick={() => setGender(item)}
                  className={`rounded-full border px-4 py-2 text-sm ${gender === item ? "border-violet-600 bg-violet-50 text-violet-800" : "border-slate-200 text-slate-600"}`}>
                  {item}
                </button>
              ))}
            </div>

            {error && <div role="alert" aria-live="assertive" className="mt-5 rounded-2xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">{error}</div>}

            <button type="button" disabled={!preview || busy} onClick={submit}
              className="mt-7 w-full rounded-full bg-violet-700 px-6 py-4 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:opacity-40">
              {busy ? "Analysing & preparing your looks…" : "Create My Personalised Edit →"}
            </button>
          </div>
        </div>
      </section>
      {busy && <div className="fixed inset-0 z-50 grid place-items-center bg-slate-950/35 p-5 backdrop-blur-sm" role="status" aria-live="polite"><div className="w-full max-w-md rounded-[2rem] bg-white p-8 text-center shadow-2xl"><div className="mx-auto grid h-16 w-16 place-items-center rounded-full bg-violet-100 text-2xl text-violet-700"><span className="animate-pulse-dot">✦</span></div><p className="mt-6 text-xs font-semibold tracking-[.18em] text-violet-700">YOUR AI STYLIST</p><p className="mt-3 min-h-7 text-xl font-semibold text-slate-900">{loadingMessages[loadingMessage]}</p><div className="mt-6 h-1.5 overflow-hidden rounded-full bg-violet-100"><div className="animate-shimmer h-full w-1/2 rounded-full bg-gradient-to-r from-violet-500 via-fuchsia-400 to-violet-500" /></div><p className="mt-5 text-sm text-slate-500">Putting together a considered edit for you.</p></div></div>}
    </main>
  );
}
