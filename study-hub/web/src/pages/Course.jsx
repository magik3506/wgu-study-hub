import { useEffect, useMemo, useState, useRef } from "react";
import { makeApi, useTheme } from "../theme.js";
import { Empty, Panel, TopBar } from "../ui.jsx";
import Playground from "../features/Playground.jsx";
import Drill from "../features/Drill.jsx";
import SqlDrill from "../features/SqlDrill.jsx";
import Mastery from "../features/Mastery.jsx";
import Guide from "../features/Guide.jsx";

const VOICE_LINES = [
  { src: "/static/voice/01_systems_online.wav" },
{ src: "/static/voice/02_whos_ready.wav" },
{ src: "/static/voice/03_hello_world.wav" },
{ src: "/static/voice/04_poke_ui.wav" },
{ src: "/static/voice/05_algorithms.wav" },
{ src: "/static/voice/06_night_owl.wav" },
{ src: "/static/voice/07_at_your_service.wav" },
{ src: "/static/voice/08_compile_knowledge.wav" },
{ src: "/static/voice/09_catch_bugs.wav" },
{ src: "/static/voice/10_fully_charged.wav" },
];

function PomodoroTimer() {
  const WORK_TIME = 25 * 60; // 25 minutes
  const BREAK_TIME = 5 * 60; // 5 minutes

  const [secondsLeft, setSecondsLeft] = useState(WORK_TIME);
  const [isRunning, setIsRunning] = useState(false);
  const [isBreak, setIsBreak] = useState(false);
  const intervalRef = useRef(null);

  useEffect(() => {
    if (isRunning) {
      intervalRef.current = setInterval(() => {
        setSecondsLeft((prev) => {
          if (prev <= 1) {
            const nextIsBreak = !isBreak;
            setIsBreak(nextIsBreak);
            return nextIsBreak ? BREAK_TIME : WORK_TIME;
          }
          return prev - 1;
        });
      }, 1000);
    }

    return () => clearInterval(intervalRef.current);
  }, [isRunning, isBreak]);

  function toggle() {
    setIsRunning((v) => !v);
  }

  function reset() {
    setIsRunning(false);
    setIsBreak(false);
    setSecondsLeft(WORK_TIME);
  }

  const mins = String(Math.floor(secondsLeft / 60)).padStart(2, "0");
  const secs = String(secondsLeft % 60).padStart(2, "0");

  return (
    <div className="w-[240px] rounded-2xl border border-line bg-panel/95 backdrop-blur-md px-4 py-3 shadow-xl text-center">
    <div className="text-[11px] font-mono uppercase tracking-wider text-mut mb-1">
    {isBreak ? "Break" : "Focus"}
    </div>
    <div className="font-mono text-[28px] font-bold text-ink tracking-tight">
    {mins}:{secs}
    </div>
    <div className="mt-2 flex justify-center gap-2">
    <button
    onClick={toggle}
    className="rounded-lg bg-gold px-3 py-1.5 text-[12px] font-semibold text-goldink hover:brightness-105 transition"
    >
    {isRunning ? "Pause" : "Start"}
    </button>
    <button
    onClick={reset}
    className="rounded-lg border border-line bg-panel2 px-3 py-1.5 text-[12px] font-semibold text-mut hover:text-ink transition"
    >
    Reset
    </button>
    </div>
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
  const audioRef = useRef(null);

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

  function playRandomLine() {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current = null;
    }

    const line = VOICE_LINES[Math.floor(Math.random() * VOICE_LINES.length)];
    const audio = new Audio(line.src);
    audioRef.current = audio;
    audio.play().catch(() => {});
    audio.onended = () => {
      audioRef.current = null;
    };
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

      {/* Fixed Portrait + Pomodoro */}
      <div className="fixed bottom-5 right-5 z-40 flex flex-col items-center gap-3">
      {/* Portrait */}
      <div
      className="cursor-pointer"
      onClick={playRandomLine}
      title="Click me!"
      >
      <img
      src="/static/hero-portrait.png"
      alt="Study Hub guide — click me!"
      className="rounded-full border-2 border-gold/50 shadow-xl object-cover transition hover:scale-105 hover:border-gold active:scale-95"
      style={{ width: "240px", height: "240px" }}
      />
      </div>

      {/* Pomodoro Timer */}
      <PomodoroTimer />
      </div>
      </>
    );
}
