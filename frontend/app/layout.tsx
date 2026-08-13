import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Shop with Confidence",
  description: "Your personal AI styling companion.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return <html lang="en"><body>{children}</body></html>;
}
