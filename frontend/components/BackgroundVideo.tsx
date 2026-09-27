"use client";

import { useEffect, useRef } from "react";

export default function BackgroundVideo() {
  const videoRef = useRef<HTMLVideoElement>(null);

  useEffect(() => {
    if (videoRef.current) {
      videoRef.current.play().catch((err) => {
        console.warn("Autoplay was prevented by browser policy:", err);
      });
    }
  }, []);

  return (
    <div className="fixed inset-0 -z-10 overflow-hidden pointer-events-none select-none">
      {/* Dolphins Background Video - High Visibility */}
      <video
        ref={videoRef}
        autoPlay
        loop
        muted
        playsInline
        preload="auto"
        className="absolute inset-0 w-full h-full object-cover opacity-40 filter brightness-105 contrast-105 transition-opacity duration-700"
      >
        <source src="/dolphins_no_gemini.mp4" type="video/mp4" />
      </video>

      {/* Balanced Overlay for Content Readability */}
      <div className="absolute inset-0 bg-gradient-to-b from-slate-950/25 via-slate-950/45 to-slate-950/70" />
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,_var(--tw-gradient-stops))] from-cyan-950/20 via-transparent to-slate-950/60" />
    </div>
  );
}
