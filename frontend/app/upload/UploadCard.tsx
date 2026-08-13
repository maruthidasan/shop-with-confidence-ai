"use client";

import { useRef, useState } from "react";

export default function UploadCard() {
  const [image, setImage] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFile = (file: File) => {
    const reader = new FileReader();
    reader.onload = () => {
      setImage(reader.result as string);
    };
    reader.readAsDataURL(file);
  };

  return (
    <div className="mx-auto max-w-3xl rounded-3xl border border-white/10 bg-white/5 p-8">

      <h2 className="text-3xl font-bold">
        Upload your photo
      </h2>

      <p className="mt-2 text-gray-400">
        Our AI will understand your look and recommend the best outfits.
      </p>

      <div
        className="mt-8 flex h-72 cursor-pointer flex-col items-center justify-center rounded-2xl border-2 border-dashed border-indigo-500/50 hover:border-indigo-400"
        onClick={() => fileInputRef.current?.click()}
      >
        {image ? (
          <img
            src={image}
            alt="Preview"
            className="h-full rounded-xl object-contain"
          />
        ) : (
          <>
            <div className="text-5xl">📷</div>
            <p className="mt-4 text-lg">
              Click to upload your photo
            </p>
          </>
        )}
      </div>

      <input
        type="file"
        hidden
        accept="image/*"
        ref={fileInputRef}
        onChange={(e) => {
          if (e.target.files?.[0]) {
            handleFile(e.target.files[0]);
          }
        }}
      />
    </div>
  );
}