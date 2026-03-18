import type { Metadata } from "next";
import "@/styles/globals.css";
import { Sidebar } from "@/components/sidebar";
import { Navbar } from "@/components/navbar";

export const metadata: Metadata = {
  title: "OpsGPT Dashboard",
  description: "AI DevOps incident monitoring platform"
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body>
        <div className="flex min-h-screen">
          <Sidebar />
          <div className="flex min-h-screen flex-1 flex-col">
            <Navbar />
            <main className="flex-1 p-4 md:p-6">{children}</main>
          </div>
        </div>
      </body>
    </html>
  );
}

