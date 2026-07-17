/* Shared UI kit — every visual primitive the hub uses. */

import { useEffect, useRef, useState } from "react";
import {
  bannerState,
  dismissBanner,
  musicState,
  nextTrack,
  prevTrack,
  stopAllSound,
  subscribe,
  toggleMute,
} from "./sound.js";

export function Btn({ variant = "solid", className = "", ...props }) {
  const styles = {
    gold: "bg-gold text-goldink border-gold hover:brightness-105",
    ghost: "bg-panel text-ink border-line hover:border-mut",
    solid:
    "bg-wgu text-white border-wgu hover:brightness-125 " +
    "[data-theme=dark]_&:bg-panel2 [data-theme=dark]_&:border-line",
  }[variant];
  return (
    <button
    className={
      "cursor-pointer rounded-lg border px-4 py-2.5 text-[13.5px] font-semibold " +
      "transition disabled:cursor-default disabled:opacity-45 " +
      styles +
      " " +
      className
    }
    {...props}
    />
  );
}

export function Panel({ className = "", children }) {
  return (
    <div className={"rounded-2xl border border-line bg-panel p-5 " + className}>
    {children}
    </div>
  );
}

export function PanelTitle({ title, sub, right }) {
  return (
    <div className="mb-3 flex flex-wrap items-start justify-between gap-3">
    <div>
    <h3 className="m-0 font-display text-[17px] font-semibold">{title}</h3>
    {sub && <p className="m-0 mt-0.5 text-[13px] text-mut">{sub}</p>}
    </div>
    {right && <div className="flex items-center gap-2.5">{right}</div>}
    </div>
  );
}

export function Chip({ children }) {
  return (
    <span className="rounded-full border border-line bg-panel2 px-2.5 py-1.5 font-mono text-[11.5px] font-semibold text-mut">
    {children}
    </span>
  );
}

export function Tag({ children }) {
  return (
    <span className="inline-block rounded-full border border-line bg-panel2 px-2.5 py-1.5 font-mono text-[11px] tracking-wide text-mut">
    {children}
    </span>
  );
}

export function Kbd({ children }) {
  return (
    <kbd className="rounded-md border border-line border-b-2 bg-panel2 px-1.5 py-0.5 font-mono text-[11px] font-semibold text-mut">
    {children}
    </kbd>
  );
}

export function Note({ children }) {
  return (
    <div className="mt-2 rounded-lg border-l-4 border-gold bg-notebg px-3 py-2 text-[12.5px] text-noteink">
    {children}
    </div>
  );
}

export function Empty({ children }) {
  return (
    <div className="px-2 py-7 text-center text-[14px] text-mut">{children}</div>
  );
}

export function ProgressBar({ pct, className = "" }) {
  return (
    <div className={"h-1.5 overflow-hidden rounded-full bg-panel2 " + className}>
    <i
    className="block h-full bg-gold transition-[width] duration-300"
    style={{ width: pct + "%" }}
    />
    </div>
  );
}

export function ResultTable({ headers, rows, total, truncated }) {
  return (
    <div>
    <div className="tablewrap">
    <table className="res">
    <thead>
    <tr>
    {headers.map((h, i) => (
      <th key={i}>{h}</th>
    ))}
    </tr>
    </thead>
    <tbody>
    {rows.map((r, i) => (
      <tr key={i}>
      {r.map((v, j) => (
        <td key={j}>
        {v === null ? <span className="nullv">NULL</span> : String(v)}
        </td>
      ))}
      </tr>
    ))}
    </tbody>
    </table>
    </div>
    <div className="mx-0.5 mt-1.5 font-mono text-[12px] text-mut">
    {total} row{total === 1 ? "" : "s"} in set
    {truncated ? ` (showing first ${rows.length})` : ""}
    </div>
    </div>
  );
}

function MoonIcon() {
  return (
    <svg viewBox="0 0 16 16" className="h-3.5 w-3.5" aria-hidden="true">
    <path
    d="M13.2 10.2A6 6 0 0 1 5.8 2.8a6 6 0 1 0 7.4 7.4Z"
    fill="currentColor"
    />
    </svg>
  );
}

function SunIcon() {
  return (
    <svg viewBox="0 0 16 16" className="h-3.5 w-3.5" aria-hidden="true">
    <circle cx="8" cy="8" r="3.2" fill="currentColor" />
    <g stroke="currentColor" strokeWidth="1.4" strokeLinecap="round">
    <path d="M8 1.2v1.8M8 13v1.8M1.2 8H3M13 8h1.8M3.2 3.2l1.3 1.3M11.5 11.5l1.3 1.3M12.8 3.2l-1.3 1.3M4.5 11.5l-1.3 1.3" />
    </g>
    </svg>
  );
}

function MusicNoteIcon({ muted }) {
  return (
    <svg viewBox="0 0 24 24" className="h-4 w-4" fill="currentColor" aria-hidden="true">
    {muted ? (
      <>
      <path d="M12 3v10.55c-.59-.34-1.27-.55-2-.55-2.21 0-4 1.79-4 4s1.79 4 4 4 4-1.79 4-4V7h4V3h-6z" />
      <path
      d="M3.27 3L2 4.27l9 9v.28c-.59-.34-1.27-.55-2-.55-2.21 0-4 1.79-4 4s1.79 4 4 4 4-1.79 4-4v-1.73L19.73 21 21 19.73 3.27 3z"
      opacity="0.7"
      />
      </>
    ) : (
      <path d="M12 3v10.55c-.59-.34-1.27-.55-2-.55-2.21 0-4 1.79-4 4s1.79 4 4 4 4-1.79 4-4V7h4V3h-6z" />
    )}
    </svg>
  );
}

function SkipIcon({ dir }) {
  // dir: -1 previous, 1 next
  return (
    <svg
    viewBox="0 0 24 24"
    className="h-3.5 w-3.5"
    fill="currentColor"
    aria-hidden="true"
    style={dir < 0 ? { transform: "scaleX(-1)" } : undefined}
    >
    <path d="M5 5.5v13c0 .8.9 1.3 1.6.9l9.9-6.5c.6-.4.6-1.4 0-1.8L6.6 4.6C5.9 4.2 5 4.7 5 5.5z" />
    <rect x="17.2" y="5" width="2.3" height="14" rx="1.1" />
    </svg>
  );
}

export function ThemeToggle({ theme, onToggle }) {
  const dark = theme === "dark";
  return (
    <button
    onClick={onToggle}
    aria-label={dark ? "Switch to light theme" : "Switch to dark theme"}
    title={dark ? "Lights on" : "Lights off — night owl mode"}
    className="relative h-8 w-14 cursor-pointer rounded-full border border-line bg-panel2 transition"
    >
    <span
    className={
      "absolute top-0.5 flex h-6 w-6 items-center justify-center rounded-full " +
      "bg-gold text-goldink shadow transition-all duration-300 " +
      (dark ? "left-0.5" : "left-[26px]")
    }
    >
    {dark ? <MoonIcon /> : <SunIcon />}
    </span>
    </button>
  );
}

/* ---------- Music controls (state lives in sound.js, page-load scoped) ---- */

export function useSound() {
  const [, forceUpdate] = useState(0);
  useEffect(() => subscribe(() => forceUpdate((n) => n + 1)), []);
}

function MusicControls() {
  useSound();
  const m = musicState();
  const dead = !m.ready;

  const iconBtn =
    "flex h-7 w-7 shrink-0 cursor-pointer items-center justify-center " +
    "rounded-full border border-line bg-panel2 text-crumb transition " +
    "hover:text-ink hover:border-mut disabled:cursor-default " +
    "disabled:opacity-40 disabled:hover:text-crumb disabled:hover:border-line";

  return (
    <div
    className="flex min-w-0 items-center gap-2"
    title={m.unavailable ? "YouTube couldn't load — music is off for this session" : undefined}
    >
    <button onClick={prevTrack} disabled={dead} title="Previous track" className={iconBtn}>
    <SkipIcon dir={-1} />
    </button>

    <div className="min-w-0 text-center leading-tight">
    <div
    className={
      "font-mono text-[9.5px] uppercase tracking-[0.14em] " +
      (!dead && !m.muted ? "text-gold" : "text-crumb/70")
    }
    >
    {m.unavailable ? "Offline" : m.muted ? "Muted" : "Now playing"}
    </div>
    <div className="max-w-[200px] truncate text-[12.5px] text-crumb" title={m.title}>
    {m.title}
    </div>
    </div>

    <button onClick={nextTrack} disabled={dead} title="Next track" className={iconBtn}>
    <SkipIcon dir={1} />
    </button>

    <button
    onClick={toggleMute}
    disabled={dead}
    title={m.muted ? "Unmute music" : "Mute music"}
    aria-label={m.muted ? "Unmute music" : "Mute music"}
    className={
      "ml-1 flex h-8 w-8 shrink-0 cursor-pointer items-center justify-center " +
      "rounded-full border transition disabled:cursor-default disabled:opacity-40 " +
      (!dead && !m.muted
        ? "border-gold/60 bg-golddim text-gold hover:brightness-110"
        : "border-line bg-panel2 text-crumb hover:text-ink hover:border-mut")
    }
    >
    <MusicNoteIcon muted={m.muted || dead} />
    </button>
    </div>
  );
}

/* ---------- Speech bubble + speaking indicator (shared by both pages) ----- */

export function Speaking() {
  return (
    <span className="eq inline-flex items-end gap-[2.5px]" aria-hidden="true">
    <i /><i /><i /><i />
    </span>
  );
}

/** Themed speech bubble with a tail. tail: "right" (hero) | "bottom" (dock). */
export function Bubble({ tail = "right", children, className = "" }) {
  return (
    <div
    className={
      "bubble-pop relative max-w-[240px] rounded-2xl border border-line " +
      "bg-panel px-4 py-3 text-[13.5px] leading-snug text-ink " +
      "shadow-[var(--card-shadow)] " +
      className
    }
    >
    {children}
    <span className={"bubble-tail bubble-tail-" + tail} aria-hidden="true" />
    </div>
  );
}

/* ---------- Break banner (3h+ session overlay over the top bar) ----------- */

export function BreakBanner() {
  useSound();
  const b = bannerState();
  const [, tick] = useState(0);

  // let the auto-hide actually repaint
  useEffect(() => {
    if (!b.visible) return;
    const t = setInterval(() => tick((n) => n + 1), 1000);
    return () => clearInterval(t);
  }, [b.shownAt, b.visible]);

  if (!b.visible) return null;
  const hours = Math.floor(b.sessionHours);
  return (
    <div className="banner-drop fixed inset-x-0 top-0 z-50">
    <div className="border-b border-gold/50 bg-gradient-to-r from-[#2b1f00] via-[#3a2a00] to-[#2b1f00] text-[#ffe9b3] shadow-[0_10px_30px_rgba(0,0,0,0.45)]">
    <div className="mx-auto flex min-h-[54px] max-w-[1180px] items-center gap-3 px-5 py-2.5">
    <span className="text-[20px]" aria-hidden="true">🦉</span>
    <div className="min-w-0 flex-1">
    <div className="font-display text-[14px] font-bold text-gold">
    Time for a break, night owl
    </div>
    <div className="truncate text-[12.5px] opacity-90">
    You've been studying for {hours}+ hour{hours === 1 ? "" : "s"} straight —
    stretch, hydrate, rest your eyes. The drills will wait.
    </div>
    </div>
    <button
    onClick={dismissBanner}
    aria-label="Dismiss break reminder"
    title="Dismiss"
    className="flex h-8 w-8 shrink-0 cursor-pointer items-center justify-center rounded-full border border-gold/40 bg-transparent text-[15px] text-gold transition hover:bg-gold hover:text-goldink"
    >
    ✕
    </button>
    </div>
    </div>
    </div>
  );
}

/* ---------- Power button (stop the local server from the app) ------------- */

function PowerIcon() {
  return (
    <svg
    viewBox="0 0 24 24"
    className="h-3.5 w-3.5"
    fill="none"
    stroke="currentColor"
    strokeWidth="2.2"
    strokeLinecap="round"
    aria-hidden="true"
    >
    <path d="M12 3v8" />
    <path d="M6.2 6.6a8 8 0 1 0 11.6 0" />
    </svg>
  );
}

/** Stops the Python server — the answer to "how do I quit this without a
 *  terminal?". Shows a friendly full-screen note afterwards. */
function PowerButton() {
  const [stopped, setStopped] = useState(false);

  async function stop() {
    const sure = window.confirm(
      "Stop the Study Hub? The server on this computer will shut down."
    );
    if (!sure) return;
    stopAllSound();
    try {
      await fetch("/api/shutdown", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: "{}",
      });
    } catch {
      /* server already gone — same outcome */
    }
    setStopped(true);
  }

  if (stopped)
    return (
      <div className="fixed inset-0 z-[70] flex items-center justify-center bg-page px-5">
      <div className="max-w-[420px] rounded-2xl border border-line bg-panel p-8 text-center shadow-[var(--card-shadow)]">
      <div className="text-[40px]" aria-hidden="true">🦉</div>
      <h2 className="mb-1.5 mt-2 font-display text-[20px] font-bold text-ink">
      The hub has stopped
      </h2>
      <p className="m-0 text-[14px] leading-relaxed text-mut">
      You can close this tab. Whenever you want it back, double-click the
      launcher (or run{" "}
      <span className="font-mono text-[12.5px]">python3 wgu_study_hub.py</span>
      ). Rest well, night owl.
      </p>
      </div>
      </div>
    );

  return (
    <button
    onClick={stop}
    title="Stop the Study Hub server"
    aria-label="Stop the Study Hub server"
    className="flex h-8 w-8 shrink-0 cursor-pointer items-center justify-center rounded-full border border-line bg-panel2 text-crumb transition hover:border-bad hover:text-bad"
    >
    <PowerIcon />
    </button>
  );
}

/* ---------- Top bar ------------------------------------------------------- */

export function TopBar({ crumb, badge, theme, onToggle }) {
  return (
    <header className="sticky top-0 z-20 border-b border-line bg-brandbar backdrop-blur-md">
    <div className="mx-auto flex min-h-[54px] max-w-[1180px] items-center gap-3.5 px-5">
    <a
    href="/"
    className="flex items-center gap-2.5 font-display text-[15px] font-bold text-brandink no-underline"
    >
    <img
    src="/static/owl-head.png"
    alt=""
    className="h-7 w-7 rounded-lg"
    />
    WGU Study Hub
    </a>
    {crumb && (
      <span className="font-mono text-[13px] text-crumb">/ {crumb}</span>
    )}

    {/* Music controls in the middle */}
    <div className="flex min-w-0 flex-1 justify-center">
    <MusicControls />
    </div>

    {badge && (
      <span className="hidden rounded-full border border-line px-2.5 py-1.5 font-mono text-[10px] font-semibold tracking-[0.12em] text-crumb sm:inline">
      {badge}
      </span>
    )}
    <ThemeToggle theme={theme} onToggle={onToggle} />
    <PowerButton />
    </div>
    </header>
  );
}
