import { useEffect, useState } from "react";
import { makeApi, useTheme } from "../theme.js";
import { Bubble, Chip, Speaking, TopBar, useSound } from "../ui.jsx";
import { speakClickLine, voiceState } from "../sound.js";

const api = makeApi("");

function CodeMark({ code }) {
  return (
    <div className="font-mono text-[30px] font-bold text-ink">
    {code[0]}
    <b className="text-gold">{code.slice(1)}</b>
    </div>
  );
}

function CourseCard({ c }) {
  return (
    <a
    href={"/c/" + c.slug}
    className="group relative block rounded-2xl border border-line bg-panel p-6 no-underline transition duration-150 hover:-translate-y-1 hover:shadow-[var(--card-shadow)]"
    >
    <span className="absolute right-4 top-4 rounded-full bg-gold px-2.5 py-1.5 font-mono text-[10px] font-bold tracking-[0.14em] text-goldink">
    READY
    </span>
    <CodeMark code={c.code} />
    <h2 className="mb-1.5 mt-2 font-display text-[17px] font-semibold text-ink">
    {c.name}
    </h2>
    <p className="m-0 mb-3.5 text-[13.5px] text-mut">{c.blurb}</p>
    <div className="flex flex-wrap gap-1.5">
    {c.chips.map((ch) => (
      <Chip key={ch}>{ch}</Chip>
    ))}
    </div>
    </a>
  );
}

function PlannedCard({ c }) {
  return (
    <div
    aria-disabled="true"
    className="relative rounded-2xl border border-dashed border-line bg-panel p-6 opacity-60"
    >
    <span className="absolute right-4 top-4 rounded-full bg-panel2 px-2.5 py-1.5 font-mono text-[10px] font-bold tracking-[0.14em] text-mut">
    PLANNED
    </span>
    <CodeMark code={c.code} />
    <h2 className="mb-1.5 mt-2 font-display text-[17px] font-semibold text-ink">
    {c.name}
    </h2>
    <p className="m-0 text-[13.5px] text-mut">{c.blurb}</p>
    </div>
  );
}

/** The hero mascot: portrait anchored right; the bubble floats to its left
 *  (absolutely positioned — appearing/disappearing never shifts the layout).
 *  Bubble colors come from the theme, so its tail always matches the panel
 *  in both night-owl and day-roost modes. */
function HeroMascot() {
  useSound();
  const v = voiceState();
  return (
    <div className="relative flex justify-end max-md:justify-center">
    <div className="relative">
    {v && (
      <div className="absolute right-full top-[16%] z-10 mr-4 w-max max-w-[min(240px,38vw)] max-md:hidden">
      <Bubble tail="right">
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
    onClick={speakClickLine}
    title="Click me!"
    className={
      "float-slow block w-auto cursor-pointer select-none rounded-2xl " +
      "border-2 shadow-xl transition duration-200 hover:scale-[1.02] " +
      "active:scale-95 " +
      (v ? "border-gold shadow-[0_0_34px_rgba(255,184,28,0.35)]"
         : "border-gold/40 hover:border-gold")
    }
    style={{ maxHeight: "400px" }}
    />
    </div>
    </div>
  );
}

export default function Home() {
  const [theme, toggle] = useTheme();
  const [data, setData] = useState(null);
  const [err, setErr] = useState(null);

  useEffect(() => {
    api("/api/courses").then(setData).catch((e) => setErr(String(e)));
  }, []);

  return (
    <>
    <TopBar badge="LOCAL · PRIVATE · OFFLINE" theme={theme} onToggle={toggle} />

    <section className="starsky text-white">
    <div className="relative z-10 mx-auto grid max-w-[1180px] items-center gap-8 px-5 py-12 md:grid-cols-2 md:py-14">
    <div>
    <span className="font-mono text-[11px] font-semibold uppercase tracking-[0.18em] text-gold">
    Night-owl study hub
    </span>
    <h1 className="my-3 font-display text-[38px] font-bold leading-[1.12] tracking-tight md:text-[44px]">
    Pick a course.
    <br />
    Start drilling.
    </h1>
    <p className="m-0 max-w-[52ch] text-[15px] text-[#8fbce8]">
    Your personal study tools, running entirely on this machine.
    Playgrounds use each course's own lab data; drills are weighted
    the way the real assessments are.
    </p>
    </div>

    <HeroMascot />
    </div>
    </section>

    <main className="mx-auto max-w-[1180px] px-5">
    <div className="grid grid-cols-[repeat(auto-fill,minmax(330px,1fr))] gap-4.5 py-8">
    {data === null && !err && <p className="text-mut">Loading courses…</p>}
    {err && <p className="text-bad">Couldn't reach the hub server: {err}</p>}
    {data?.courses.map((c) => (
      <CourseCard key={c.slug} c={c} />
    ))}
    {data?.planned.map((c) => (
      <PlannedCard key={c.code} c={c} />
    ))}
    {data && !data.courses.length && (
      <p className="text-mut">
      No course packs installed — unzip a <span className="font-mono">&lt;slug&gt;-pack.zip</span> into <span className="font-mono">courses/</span> and restart.
      </p>
    )}
    </div>
    <p className="pb-9 text-[12.5px] text-mut">
    Unofficial personal study tool — not affiliated with or endorsed by Western Governors University. Progress is stored locally in <span className="font-mono">~/.wgu_study_hub</span> and is shared with the terminal version.
    </p>
    </main>
    </>
  );
}
