import { useEffect, useState } from "react";
import { makeApi, useTheme } from "../theme.js";
import { Chip, TopBar } from "../ui.jsx";

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
        <div className="relative z-10 mx-auto grid max-w-[1180px] items-center gap-6 px-5 py-12 md:grid-cols-[1fr_230px] md:py-14">
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
          <img
            src="/static/owl-hero.webp"
            alt="Study Hub owl mascot"
            className="owl-hero hidden justify-self-end md:block"
            width="200"
            height="301"
          />
        </div>
      </section>

      <main className="mx-auto max-w-[1180px] px-5">
        <div className="grid grid-cols-[repeat(auto-fill,minmax(330px,1fr))] gap-4.5 py-8">
          {data === null && !err && (
            <p className="text-mut">Loading courses…</p>
          )}
          {err && (
            <p className="text-bad">
              Couldn't reach the hub server: {err}
            </p>
          )}
          {data?.courses.map((c) => (
            <CourseCard key={c.slug} c={c} />
          ))}
          {data?.planned.map((c) => (
            <PlannedCard key={c.code} c={c} />
          ))}
          {data && !data.courses.length && (
            <p className="text-mut">
              No course packs installed — unzip a{" "}
              <span className="font-mono">&lt;slug&gt;-pack.zip</span> into{" "}
              <span className="font-mono">courses/</span> and restart.
            </p>
          )}
        </div>
        <p className="pb-9 text-[12.5px] text-mut">
          Unofficial personal study tool — not affiliated with or endorsed by
          Western Governors University. Progress is stored locally in{" "}
          <span className="font-mono">~/.wgu_study_hub</span> and is shared with
          the terminal version.
        </p>
      </main>
    </>
  );
}
