/* Shared UI kit — every visual primitive the hub uses. */

import { useEffect, useRef, useState } from "react";

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

// ---------- Music Player (Singleton) ----------
const PLAYLIST_ID = "PLt7bG0K25iXj2h1eql20RZIPB_2CtK659";

// These live outside React so they survive page changes
let globalPlayer = null;
let globalMuted = true;
let globalTitle = "Lofi Study Beats";
let globalReady = false;
const listeners = new Set();

function notify() {
  listeners.forEach((fn) => fn());
}

function createGlobalPlayer() {
  if (globalPlayer) return;

  const container = document.createElement("div");
  container.style.cssText = "position:absolute;left:-9999px;width:0;height:0;";
  document.body.appendChild(container);

  globalPlayer = new window.YT.Player(container, {
    height: "0",
    width: "0",
    playerVars: {
      listType: "playlist",
      list: PLAYLIST_ID,
      autoplay: 1,
      mute: 1,
      controls: 0,
      disablekb: 1,
      fs: 0,
      modestbranding: 1,
      playsinline: 1,
      rel: 0,
    },
    events: {
      onReady: (e) => {
        e.target.playVideo();
        e.target.mute();
        globalReady = true;
        updateTitle(e.target);
        notify();
      },
      onStateChange: (e) => {
        if (e.data === window.YT.PlayerState.PLAYING) {
          updateTitle(e.target);
        }
      },
    },
  });
}

function updateTitle(player) {
  try {
    const data = player.getVideoData();
    if (data && data.title) {
      globalTitle = data.title;
      notify();
    }
  } catch (_) {}
}

function ensureYT() {
  return new Promise((resolve) => {
    if (window.YT && window.YT.Player) {
      resolve();
      return;
    }
    if (!window._ytLoading) {
      window._ytLoading = true;
      const tag = document.createElement("script");
      tag.src = "https://www.youtube.com/iframe_api";
      document.head.appendChild(tag);
    }
    const prev = window.onYouTubeIframeAPIReady;
    window.onYouTubeIframeAPIReady = () => {
      if (prev) prev();
      resolve();
    };
  });
}

// Start loading the API as soon as this module is imported
ensureYT().then(createGlobalPlayer);

function MusicControls() {
  const [, forceUpdate] = useState(0);

  useEffect(() => {
    const listener = () => forceUpdate((n) => n + 1);
    listeners.add(listener);
    return () => listeners.delete(listener);
  }, []);

  function toggleMute() {
    if (!globalPlayer || !globalReady) return;
    if (globalMuted) {
      globalPlayer.unMute();
      globalMuted = false;
    } else {
      globalPlayer.mute();
      globalMuted = true;
    }
    notify();
  }

  function prevTrack() {
    if (!globalPlayer || !globalReady) return;
    globalPlayer.previousVideo();
  }

  function nextTrack() {
    if (!globalPlayer || !globalReady) return;
    globalPlayer.nextVideo();
  }

  return (
    <div className="flex items-center gap-2.5 min-w-0">
    {/* Previous */}
    <button
    onClick={prevTrack}
    title="Previous track"
    className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full border border-line bg-panel2 text-crumb hover:text-ink transition text-sm"
    >
    ⏮
    </button>

    {/* Now Playing + Title */}
    <div className="min-w-0 text-center">
    <div className="text-[10px] font-mono uppercase tracking-wider text-crumb/70">
    {globalMuted ? "Muted" : "Now Playing"}
    </div>
    <div className="truncate text-[12.5px] text-crumb max-w-[200px]">
    {globalTitle}
    </div>
    </div>

    {/* Next */}
    <button
    onClick={nextTrack}
    title="Next track"
    className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full border border-line bg-panel2 text-crumb hover:text-ink transition text-sm"
    >
    ⏭
    </button>

    {/* Mute / Unmute */}
    <button
    onClick={toggleMute}
    title={globalMuted ? "Unmute" : "Mute"}
    className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full border border-line bg-panel2 text-crumb hover:text-ink transition ml-1"
    >
    <MusicNoteIcon muted={globalMuted} />
    </button>
    </div>
  );
}

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
    <div className="flex-1 flex justify-center min-w-0">
    <MusicControls />
    </div>

    {badge && (
      <span className="hidden rounded-full border border-line px-2.5 py-1.5 font-mono text-[10px] font-semibold tracking-[0.12em] text-crumb sm:inline">
      {badge}
      </span>
    )}
    <ThemeToggle theme={theme} onToggle={onToggle} />
    </div>
    </header>
  );
}
