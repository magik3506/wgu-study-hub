/* Shared UI kit — every visual primitive the hub uses. */

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
    <div
      className={
        "h-1.5 overflow-hidden rounded-full bg-panel2 " + className
      }
    >
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
        <span className="flex-1" />
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
