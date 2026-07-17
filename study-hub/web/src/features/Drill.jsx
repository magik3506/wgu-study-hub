import { useEffect, useRef, useState } from "react";
import { Btn, Kbd, Panel, ProgressBar, Tag } from "../ui.jsx";
import Summary from "./Summary.jsx";

const LETTERS = "ABCDE";

export default function Drill({ api, meta, active }) {
  const [n, setN] = useState("10");
  const [topic, setTopic] = useState("");
  const [sess, setSess] = useState(null); // {sid, q, reveal, summary, err}
  const stateRef = useRef(null);
  stateRef.current = sess;
  const nextRef = useRef(null);

  async function start(count, focusTopic) {
    const d = await api("/api/quiz/start", {
      mode: "mcq",
      n: +count,
      topic: focusTopic,
    });
    if (d.error) {
      setSess({ err: d.error });
      return;
    }
    setSess({ sid: d.session, q: d.question, reveal: null, summary: null });
  }

  async function answer(idx, skip) {
    const s = stateRef.current;
    if (!s || s.reveal || s.summary) return;
    const body = { session: s.sid };
    if (skip) body.action = "skip";
    else body.answer = idx;
    const d = await api("/api/quiz/answer", body);
    if (d.error) {
      setSess({ err: d.error });
      return;
    }
    setSess({ ...s, reveal: { ...d, picked: skip ? null : idx, skip } });
  }

  function advance() {
    const s = stateRef.current;
    const d = s.reveal;
    if (d.next) setSess({ sid: s.sid, q: d.next, reveal: null, summary: null });
    else setSess({ summary: d.summary });
  }

  // keyboard: A–E / 1–5 to answer, Enter handled by focused Next button
  useEffect(() => {
    function onKey(e) {
      const s = stateRef.current;
      if (!active || !s || !s.q || s.reveal || s.summary) return;
      const t = e.target.tagName;
      if (t === "TEXTAREA" || t === "INPUT" || t === "SELECT") return;
      const i = "abcde".indexOf(e.key.toLowerCase());
      const j = "12345".indexOf(e.key);
      const k = i >= 0 ? i : j;
      if (k >= 0 && k < s.q.options.length) {
        e.preventDefault();
        answer(k, false);
      }
    }
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, [active]); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    if (sess?.reveal && nextRef.current) nextRef.current.focus();
  }, [sess]);

  if (!sess || sess.err)
    return (
      <Panel id="drillsetup">
        <h3 className="m-0 font-display text-[16px] font-semibold">
          Exam drill
        </h3>
        <p className="mb-3 mt-0.5 text-[13px] text-mut">
          Multiple choice, like the real OA. Weighted by the practice-test
          blueprint and by what you've been missing.
        </p>
        <div className="flex flex-wrap items-center gap-2.5">
          <label htmlFor="qn" className="text-[13px] text-mut">
            questions
          </label>
          <select
            id="qn"
            value={n}
            onChange={(e) => setN(e.target.value)}
            className="rounded-lg border border-line bg-panel px-2.5 py-2 text-[14px] text-ink"
          >
            {[5, 10, 15, 20, 30].map((x) => (
              <option key={x}>{x}</option>
            ))}
          </select>
          <label htmlFor="qtopic" className="text-[13px] text-mut">
            focus
          </label>
          <select
            id="qtopic"
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            className="max-w-[340px] rounded-lg border border-line bg-panel px-2.5 py-2 text-[14px] text-ink"
          >
            <option value="">Everything (blueprint-weighted)</option>
            {meta.chapters.map((c) => (
              <option key={c.ch} value={String(c.ch)}>
                {meta.unit_label} {c.ch}
                {c.name ? ` · ${c.name}` : ""}
              </option>
            ))}
            {meta.topics.map((t) => (
              <option key={t.value} value={t.value}>
                {t.label}
              </option>
            ))}
          </select>
          <Btn variant="gold" id="qstart" onClick={() => start(n, topic)}>
            Start drill
          </Btn>
        </div>
        {sess?.err && (
          <div className="mt-3 rounded-lg border-l-4 border-bad bg-badbg px-3 py-2 text-[13px] text-bad">
            {sess.err}
          </div>
        )}
      </Panel>
    );

  if (sess.summary)
    return (
      <Panel id="quizarea">
        <Summary
          s={sess.summary}
          mode="mcq"
          onAgain={() => setSess(null)}
          onWeakDrill={(w) => start(8, w.name.toLowerCase())}
        />
      </Panel>
    );

  const q = sess.q;
  const r = sess.reveal;
  return (
    <Panel id="quizarea">
      <div className="flex items-center justify-between gap-3">
        <Tag>{q.tag}</Tag>
        <span className="font-mono text-[13px] font-bold text-mut">
          Question {q.index} of {q.total}
        </span>
      </div>
      <ProgressBar
        pct={Math.round((100 * (q.index - 1)) / q.total)}
        className="mb-4 mt-2.5"
      />
      <p className="m-0 mb-3.5 whitespace-pre-wrap text-[16.5px] leading-normal">
        {q.prompt}
      </p>
      <div className="grid gap-2">
        {q.options.map((o, i) => {
          let cls =
            "flex cursor-pointer gap-2.5 rounded-xl border-[1.5px] border-line bg-panel p-3 text-left text-[14px] leading-snug text-ink transition";
          if (r) {
            cls += " cursor-default";
            if (i === r.correct_index)
              cls += " border-ok bg-okbg";
            else if (!r.skip && i === r.picked)
              cls += " border-bad bg-badbg";
          } else {
            cls += " hover:border-mut";
          }
          return (
            <button
              key={i}
              disabled={!!r}
              onClick={() => answer(i, false)}
              className={cls}
            >
              <b
                className={
                  "min-w-4 font-mono " +
                  (r && i === r.correct_index
                    ? "text-ok"
                    : r && !r.skip && i === r.picked
                      ? "text-bad"
                      : "text-mut")
                }
              >
                {LETTERS[i]}
              </b>
              <span>{o}</span>
            </button>
          );
        })}
      </div>
      {!r && (
        <div className="mt-3.5 flex items-center gap-2.5">
          <Btn variant="ghost" onClick={() => answer(null, true)}>
            Skip
          </Btn>
          <span className="text-[13px] text-mut">
            keys <Kbd>A</Kbd>–<Kbd>{LETTERS[q.options.length - 1]}</Kbd>
          </span>
        </div>
      )}
      {r && (
        <div>
          {r.skip ? (
            <div className="mb-1 mt-3.5 text-[14px] font-bold text-bad">
              Skipped
            </div>
          ) : r.correct ? (
            <div className="mb-1 mt-3.5 text-[14px] font-bold text-ok">
              ✔ Correct
            </div>
          ) : (
            <div className="mb-1 mt-3.5 text-[14px] font-bold text-bad">
              ✘ Not quite
            </div>
          )}
          <div className="rounded-lg border-l-4 border-line bg-panel2 px-3.5 py-2.5 text-[13.5px] text-ink">
            {r.explain}
          </div>
          <div className="mt-4 flex items-center gap-2.5">
            <Btn variant="gold" ref={nextRef} onClick={advance}>
              {r.next ? "Next question" : "See summary"}
            </Btn>
            <span className="text-[13px] text-mut">
              <Kbd>Enter</Kbd>
            </span>
          </div>
        </div>
      )}
    </Panel>
  );
}
