import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Short Links",
  description: "Trade a long web address for a short one.",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
