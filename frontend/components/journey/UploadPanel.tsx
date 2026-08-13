"use client";
import { DragEvent, useRef, useState } from "react";
import { useRouter } from "next/navigation";

export default function UploadPanel() {
  const [image, setImage] = useState<string | null>(null); const [dragging, setDragging] = useState(false); const input = useRef<HTMLInputElement>(null); const router = useRouter();
  const pick = (file?: File) => { if (file?.type.startsWith("image/")) { const reader = new FileReader(); reader.onload = () => setImage(reader.result as string); reader.readAsDataURL(file); } };
  const drop = (event: DragEvent<HTMLDivElement>) => { event.preventDefault(); setDragging(false); pick(event.dataTransfer.files[0]); };
  return <div className="glass w-full max-w-2xl rounded-[2rem] p-5 sm:p-9">
    <p className="text-sm font-medium text-violet-600">STEP 01 — YOUR PHOTO</p><h1 className="mt-3 text-3xl font-semibold tracking-tight sm:text-4xl">Let&apos;s start with your photo.</h1><p className="mt-3 max-w-lg leading-7 text-slate-500">A clear, front-facing photo helps us shape recommendations around you. It stays right here in this browser.</p>
    <div onClick={() => input.current?.click()} onDrop={drop} onDragOver={(e) => { e.preventDefault(); setDragging(true); }} onDragLeave={() => setDragging(false)} className={`relative mt-8 grid min-h-72 cursor-pointer place-items-center overflow-hidden rounded-3xl border-2 border-dashed transition ${dragging ? "border-violet-500 bg-violet-50" : "border-violet-200 bg-white/50 hover:border-violet-400 hover:bg-violet-50/40"}`}>
      {image ? <><img src={image} alt="Your selected photo" className="h-72 w-full object-contain" /><button type="button" onClick={(e) => { e.stopPropagation(); setImage(null); }} className="absolute right-4 top-4 rounded-full bg-white px-3 py-1.5 text-xs font-medium shadow">Remove</button></> : <div className="px-6 text-center"><div className="mx-auto grid h-14 w-14 place-items-center rounded-2xl bg-violet-100 text-2xl text-violet-700">↑</div><p className="mt-4 text-base font-medium">Drop your photo here</p><p className="mt-1 text-sm text-slate-500">or click to browse · JPG, PNG or WEBP</p></div>}
    </div>
    <input ref={input} onChange={(e) => pick(e.target.files?.[0])} type="file" accept="image/*" className="hidden" />
    <div className="mt-7 flex items-center justify-between gap-4"><p className="text-xs leading-5 text-slate-400">Your photo is used only to personalise this style experience.</p><button disabled={!image} onClick={() => router.push("/occasion")} className="shrink-0 rounded-full bg-[#17152b] px-5 py-3 text-sm font-medium text-white transition hover:bg-[#353052] disabled:cursor-not-allowed disabled:opacity-35">Continue <span className="ml-1">→</span></button></div>
  </div>;
}
