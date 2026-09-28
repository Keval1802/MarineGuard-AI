import "./globals.css";
import Navbar from "@/components/Navbar";
import BackgroundVideo from "@/components/BackgroundVideo";

export const metadata = {
  title: "MarineGuard AI — Marine Pollution Intelligence System",
  description: "Multi-Source Agentic Marine Pollution Early-Warning, Investigation and Response Intelligence System",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body className="bg-slate-950 text-slate-100 antialiased min-h-screen flex flex-col relative">
        <BackgroundVideo />
        <Navbar />
        <main className="flex-1 max-w-7xl w-full mx-auto p-4 sm:p-6 lg:p-8 relative z-10" style={{ paddingBottom: "0px" }}>
          {children}
        </main>
        <footer className="border-t border-slate-900/80 bg-slate-950/90 backdrop-blur-md py-6 text-center text-xs text-slate-500 relative z-10">
          MarineGuard AI &copy; 2026 — Multi-Source Agentic Marine Pollution Early-Warning System
        </footer>
      </body>
    </html>
  );
}
