import { useEffect, useMemo, useState } from "react";
import { makeApi, useTheme } from "../theme.js";
import { Bubble, Empty, Panel, Speaking, TopBar, useSound } from "../ui.jsx";
import { speakClickLine, voiceState } from "../sound.js";
import Playground from "../features/Playground.jsx";
import Drill from "../features/Drill.jsx";
import SqlDrill from "../features/SqlDrill.jsx";
import Mastery from "../features/Mastery.jsx";
import Guide from "../features/Guide.jsx";

/* Mascot dock size, px. It used to be 240 — bump this back up if you miss
 * the big portrait; everything scales off this one constant. */
const PORTRAIT_SIZE = 150;

const WORK_TIME = 25 * 60; // 25 minutes
const BREAK_TIME = 5 * 60; // 5 minutes

function PomodoroTimer() {
  const [secondsLeft, setSecondsLeft] = useState(WORK_TIME);
  const [isRunning, setIsRunning] = useState(false);
  const [isBreak, setIsBreak] = useState(false);

  useEffect(() => {
    if (!isRunning) return;
    const id = setInterval(() => {
      setSecondsLeft((prev) => {
        if (prev <= 1) {
          const nextIsBreak = !isBreak;
          setIsBreak(nextIsBreak);
          return nextIsBreak ? BREAK_TIME : WORK_TIME;
        }
        return prev - 1;
      });
    }, 1000);
    return () => clearInterval(id);
  }, [isRunning, isBreak]);

  function toggle() {
    setIsRunning((v) => !v);
  }

  function reset() {
    setIsRunning(false);
    setIsBreak(false);
    setSecondsLeft(WORK_TIME);
  }

  const total = isBreak ? BREAK_TIME : WORK_TIME;
  const pct = Math.round((100 * (total - secondsLeft)) / total);
  const mins = String(Math.floor(secondsLeft / 60)).padStart(2, "0");
  const secs = String(secondsLeft % 60).padStart(2, "0");

  return (
    <div className="w-[168px] rounded-2xl border border-line bg-panel/95 px-4 py-3 text-center shadow-xl backdrop-blur-md">
    <div
    className={
      "mb-0.5 font-mono text-[10.5px] font-semibold uppercase tracking-[0.16em] " +
      (isBreak ? "text-ok" : "text-gold")
    }
    >
    {isBreak ? "Break" : "Focus"}
    </div>
    <div className="font-mono text-[28px] font-bold tracking-tight text-ink">
    {mins}:{secs}
    </div>
    <div className="mt-1.5 h-1 overflow-hidden rounded-full bg-panel2">
    <i
    className={
      "block h-full transition-[width] duration-1000 ease-linear " +
      (isBreak ? "bg-ok" : "bg-gold")
    }
    style={{ width: pct + "%" }}
    />
    </div>
    <div className="mt-2.5 flex justify-center gap-2">
    <button
    onClick={toggle}
    className="cursor-pointer rounded-lg bg-gold px-3 py-1.5 text-[12px] font-semibold text-goldink transition hover:brightness-105"
    >
    {isRunning ? "Pause" : "Start"}
    </button>
    <button
    onClick={reset}
    className="cursor-pointer rounded-lg border border-line bg-panel2 px-3 py-1.5 text-[12px] font-semibold text-mut transition hover:text-ink"
    >
    Reset
    </button>
    </div>
    </div>
  );
}

/** Bottom-right study buddy: clickable portrait + pomodoro, with a speech
 *  bubble while a voice line plays. Collapsible (the ✕) so it never has to
 *  sit on top of a drill — it shrinks to a small round button. */
function MascotDock() {
  useSound();
  const v = voiceState();
  const [open, setOpen] = useState(true);

  if (!open)
    return (
      <button
      onClick={() => setOpen(true)}
      title="Bring back the study buddy"
      aria-label="Show mascot and pomodoro timer"
      className={
        "fixed bottom-5 right-5 z-40 h-12 w-12 cursor-pointer overflow-hidden " +
        "rounded-full border-2 shadow-xl transition hover:scale-105 " +
        (v ? "border-gold" : "border-gold/60 hover:border-gold")
      }
      >
      <img
      src="/static/hero-portrait.png"
      alt=""
      className="h-full w-full object-cover object-top"
      />
      </button>
    );

  return (
    <div className="fixed bottom-5 right-5 z-40 flex flex-col items-center gap-3">
    <div className="float-slow relative">
    {v && (
      <div className="absolute bottom-full left-1/2 z-10 mb-3.5 w-max -translate-x-1/2">
      <Bubble tail="bottom" className="max-w-[220px] text-[12.5px]">
      {v.text ? (
        v.text
      ) : (
        <span className="flex items-center gap-2 text-mut">
        <Speaking /> hoo-hoo…
        </span>
      )}
      </Bubble>
      </div>
    )}
    <img
    src="/static/hero-portrait.png"
    alt="Study Hub guide — click me!"
    title="Click me!"
    onClick={speakClickLine}
    className={
      "cursor-pointer rounded-full border-2 object-cover object-top shadow-xl " +
      "transition hover:scale-105 active:scale-95 " +
      (v
        ? "border-gold shadow-[0_0_26px_rgba(255,184,28,0.4)]"
        : "border-gold/50 hover:border-gold")
    }
    style={{ width: PORTRAIT_SIZE, height: PORTRAIT_SIZE }}
    />
    <button
    onClick={() => setOpen(false)}
    title="Hide the study buddy"
    aria-label="Hide mascot and pomodoro timer"
    className="absolute -right-0.5 -top-0.5 z-10 flex h-6 w-6 cursor-pointer items-center justify-center rounded-full border border-line bg-panel text-[11px] text-mut shadow transition hover:border-mut hover:text-ink"
    >
    ✕
    </button>
    </div>
    <PomodoroTimer />
    </div>
  );
}

export default function Course({ slug }) {
  const [theme, toggle] = useTheme();
  const base = "/c/" + slug;
  const api = useMemo(() => makeApi(base), [base]);
  const [meta, setMeta] = useState(null);
  const [err, setErr] = useState(null);
  const [tab, setTab] = useState(null);

  useEffect(() => {
    api("/api/meta")
    .then((m) => {
      if (m.error) throw new Error(m.error);
      setMeta(m);
      document.title = m.code + " · WGU Study Hub";
      const want = window.location.hash.replace("#", "");
      const ids = m.tabs.map((t) => t.id);
      setTab(ids.includes(want) ? want : ids[0]);
    })
    .catch((e) => setErr(String(e.message || e)));
  }, [api]);

  function openTab(id) {
    setTab(id);
    window.history.replaceState(null, "", "#" + id);
  }

  if (err)
    return (
      <>
      <TopBar theme={theme} onToggle={toggle} />
      <main className="mx-auto max-w-[1180px] px-5 py-8">
      <Panel>
      <Empty>
      This course isn't loaded: {err}
      <br />
      <a href="/">Back to the hub</a>
      </Empty>
      </Panel>
      </main>
      </>
    );
    if (!meta) return <TopBar theme={theme} onToggle={toggle} />;

    return (
      <>
      <TopBar
      crumb={`${meta.code} · ${meta.name}`}
      badge={meta.badge}
      theme={theme}
      onToggle={toggle}
      />
      <nav className="border-b border-line bg-panel">
      <div className="mx-auto flex max-w-[1180px] gap-1 overflow-x-auto px-5">
      {meta.tabs.map((t) => (
        <button
        key={t.id}
        data-tab={t.id}
        onClick={() => openTab(t.id)}
        className={
          "cursor-pointer whitespace-nowrap border-0 border-b-[3px] bg-transparent px-3.5 pb-2.5 pt-3 text-[13.5px] font-semibold transition " +
          (tab === t.id
          ? "border-gold text-ink"
          : "border-transparent text-mut hover:text-ink")
        }
        >
        {t.label}
        </button>
      ))}
      </div>
      </nav>

      <main className="mx-auto max-w-[1180px] px-5 pb-16 pt-6">
      {meta.playground && (
        <section
        id="playground"
        className={tab === "playground" ? "" : "hidden"}
        >
        <Playground api={api} pg={meta.playground} />
        </section>
      )}
      <section id="drill" className={tab === "drill" ? "" : "hidden"}>
      <Drill api={api} meta={meta} active={tab === "drill"} />
      </section>
      {meta.has_sql_drill && (
        <section id="sqldrill" className={tab === "sqldrill" ? "" : "hidden"}>
        <SqlDrill api={api} active={tab === "sqldrill"} />
        </section>
      )}
      <section id="mastery" className={tab === "mastery" ? "" : "hidden"}>
      <Mastery api={api} meta={meta} active={tab === "mastery"} />
      </section>
      <section id="guide" className={tab === "guide" ? "" : "hidden"}>
      <Guide base={base} meta={meta} />
      </section>
      </main>

      <MascotDock />
      </>
    );
}
