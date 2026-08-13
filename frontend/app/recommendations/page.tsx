"use client";

import Link from "next/link";
import { useState } from "react";

type Rec = {
  id: string;
  brand: string;
  outfitName: string;
  confidence: number | string;
  reason: string;
  tryOnPreviewUrl?: string;
  stylistNote?: string;
};
type Data = { recommendations: Rec[]; confidenceReport: Record<string, string> };

const API_BASE = "/api";

export default function RecommendationsPage() {
  const [data] = useState<Data | null>(() => {
    if (typeof window === "undefined") return null;
    const raw = sessionStorage.getItem("vela-recommendations");
    if (!raw) return null;
    try {
      return JSON.parse(raw) as Data;
    } catch {
      return null;
    }
  });
  const [selected, setSelected] = useState(0);
  const [completeLookUrl, setCompleteLookUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [orderConfirmed, setOrderConfirmed] = useState(false);
  const [orderedLook, setOrderedLook] = useState("");

  function orderLook(look: Rec) {
    setOrderedLook(look.outfitName);
    setOrderConfirmed(true);
  }

  if (!data) {
    return (
      <main className="page-background min-h-screen px-6 py-20">
        <div className="mx-auto max-w-xl rounded-3xl bg-white p-10 text-center shadow-sm">
          <p className="text-sm font-semibold uppercase tracking-[.16em] text-violet-600">
            FASHION RETAIL AI STYLIST
          </p>
          <h1 className="mt-3 text-3xl font-semibold">
            Your edit is not loaded yet.
          </h1>
          <p className="mt-3 text-slate-600">Start the AI Stylist again.</p>
          <Link
            href="/upload"
            className="mt-7 inline-flex rounded-full bg-violet-700 px-6 py-3 text-sm font-medium text-white"
          >
            Start AI Stylist
          </Link>
        </div>
      </main>
    );
  }

  const recommendation = data.recommendations[selected];
  const imageUrl = completeLookUrl || recommendation?.tryOnPreviewUrl;

  async function completeTheLook() {
    if (!imageUrl) return;

    setLoading(true);
    setError("");

    try {
      const response = await fetch(`${API_BASE}/tryon`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          recommendationId: "leather-loafer",
          photoUrl: imageUrl,
        }),
      });

      const body = await response.json();

      if (!response.ok || !body.imageUrl) {
        throw new Error(body?.message || "Complete-the-look VTO failed.");
      }

      setCompleteLookUrl(body.imageUrl);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Complete-the-look VTO failed."
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="page-background min-h-screen">
      <header className="mx-auto flex max-w-7xl items-center justify-between px-5 py-5 sm:px-8">
        <Link href="/" className="text-lg font-semibold">
          Fashion Retail
        </Link>
        <Link href="/upload" className="text-sm text-slate-600">
          Start over
        </Link>
      </header>

      <section className="mx-auto max-w-7xl px-5 pb-20 pt-8 sm:px-8">
        <p className="text-sm font-medium text-violet-600">
          YOUR PERSONALISED EDIT
        </p>

        <h1 className="mt-3 text-4xl font-semibold tracking-tight sm:text-5xl">
          See the look on you.
        </h1>

        <p className="mt-4 max-w-2xl leading-7 text-slate-600">
          See your recommended outfit full-body, then complete the look with
          another AI try-on.
        </p>

        <section className="mt-10 overflow-hidden rounded-[2rem] border border-violet-100 bg-white shadow-sm">
          <div className="grid lg:grid-cols-[1.2fr_.8fr]">
            <div className="min-h-[700px] bg-slate-50 p-3 sm:p-6">
              {imageUrl ? (
                <img
                  src={imageUrl}
                  alt={`Full-body virtual try-on for ${recommendation.outfitName}`}
                  className="mx-auto h-[700px] w-full object-contain object-center"
                />
              ) : (
                <div className="grid h-[700px] place-items-center text-sm text-slate-500">
                  VTO preview unavailable
                </div>
              )}
            </div>

            <div className="flex flex-col justify-center p-7 sm:p-10">
              <p className="text-xs font-semibold uppercase tracking-[.16em] text-violet-600">
                {completeLookUrl
                  ? "COMPLETE THE LOOK"
                  : "FULL-BODY VIRTUAL TRY-ON"}
              </p>

              <h2 className="mt-3 text-3xl font-semibold">
                {completeLookUrl
                  ? "Your complete look."
                  : recommendation.outfitName}
              </h2>

              <p className="mt-4 leading-7 text-slate-600">
                {completeLookUrl
                  ? "The finishing piece has been generated on the same virtual look."
                  : recommendation.reason}
              </p>

              <button type="button" onClick={() => orderLook(recommendation)} className="mt-7 rounded-full bg-[#17152b] px-5 py-3 text-sm font-semibold text-white transition hover:bg-violet-800">Order This Look</button>

              {!completeLookUrl ? (
                <div className="mt-8 rounded-2xl border border-stone-200 bg-stone-50 p-5">
                  <p className="text-xs font-semibold uppercase tracking-[.14em] text-stone-500">
                    COMPLETE THE LOOK
                  </p>

                  <p className="mt-2 text-xl font-semibold">
                    Black Leather Loafer
                  </p>

                  <p className="mt-1 text-sm text-stone-500">
                    See the complete outfit on you.
                  </p>

                  <button
                    type="button"
                    onClick={completeTheLook}
                    disabled={loading || !imageUrl}
                    className="mt-5 w-full rounded-full bg-violet-700 px-5 py-3 text-sm font-semibold text-white disabled:opacity-50"
                  >
                    {loading
                      ? "Creating your complete look..."
                      : "Try the complete look →"}
                  </button>

                  {error && (
                    <p role="alert" className="mt-3 text-sm text-red-600">
                      {error}
                    </p>
                  )}
                </div>
              ) : (
                <button
                  type="button"
                  onClick={() => setCompleteLookUrl(null)}
                  className="mt-8 rounded-full border border-stone-300 px-5 py-3 text-sm font-semibold"
                >
                  Back to outfit VTO
                </button>
              )}
            </div>
          </div>
        </section>

        <section className="mt-12">
          <p className="text-sm font-semibold uppercase tracking-[.16em] text-violet-600">
            COMPARE YOUR LOOKS
          </p>

          <div className="mt-5 grid gap-5 md:grid-cols-3">
            {data.recommendations.map((item, i) => (
              <article
                key={item.id}
                className={`overflow-hidden rounded-3xl border bg-white text-left shadow-sm ${
                  selected === i
                    ? "border-violet-400 ring-2 ring-violet-100"
                    : "border-white"
                }`}
              >
                <div className="h-80 bg-slate-50">
                  {item.tryOnPreviewUrl && (
                    <img
                      src={item.tryOnPreviewUrl}
                      alt={`Virtual try-on for ${item.outfitName}`}
                      className="h-full w-full object-contain object-center"
                    />
                  )}
                </div>

                <div className="p-5">
                  <p className="text-xs font-semibold uppercase tracking-[.14em] text-violet-600">
                    {item.brand}
                  </p>
                  <h3 className="mt-1 text-xl font-semibold">
                    {item.outfitName}
                  </h3>
                  <p className="mt-2 text-sm font-semibold text-emerald-700">
                    {item.confidence}% match
                  </p>
                  <div className="mt-4 flex gap-3"><button type="button" onClick={() => { setSelected(i); setCompleteLookUrl(null); setError(""); }} className="text-sm font-semibold text-violet-700 underline underline-offset-4">View look</button><button type="button" onClick={() => orderLook(item)} className="rounded-full border border-stone-300 px-4 py-2 text-sm font-semibold transition hover:border-violet-700 hover:text-violet-700">Order</button></div>
                </div>
              </article>
            ))}
          </div>
        </section>

        <section className="mt-12 rounded-3xl border border-violet-100 bg-white p-7 shadow-sm sm:p-10">
          <p className="text-sm font-semibold uppercase tracking-[.16em] text-violet-600">
            YOUR CONFIDENCE REPORT
          </p>
          <h2 className="mt-3 text-3xl font-semibold">
            {data.confidenceReport?.title || "You look great!"}
          </h2>
          <p className="mt-3 max-w-2xl leading-7 text-slate-600">
            {data.confidenceReport?.subtitle ||
              "Your personalised edit is ready."}
          </p>
        </section>
      </section>
      {orderConfirmed && <div className="fixed inset-0 z-50 grid place-items-center bg-slate-950/40 p-5 backdrop-blur-sm" role="dialog" aria-modal="true" aria-labelledby="order-title"><div className="order-success w-full max-w-sm rounded-[2rem] bg-white p-9 text-center shadow-2xl"><div className="order-check mx-auto grid h-16 w-16 place-items-center rounded-full bg-emerald-500 text-3xl text-white">✓</div><p className="mt-6 text-xs font-semibold tracking-[.18em] text-emerald-700">ORDER CONFIRMED</p><h2 id="order-title" className="mt-3 text-3xl font-semibold tracking-tight">Your look is on the way.</h2><p className="mt-3 text-slate-600">{orderedLook} has been added to your demo order.</p><button type="button" autoFocus onClick={() => setOrderConfirmed(false)} className="mt-7 rounded-full bg-[#17152b] px-6 py-3 text-sm font-semibold text-white">Continue exploring</button></div></div>}
    </main>
  );
}
