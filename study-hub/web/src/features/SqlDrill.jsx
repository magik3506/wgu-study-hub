import { useRef, useState } from "react";
import { Btn, Kbd, Note, Panel, ProgressBar, ResultTable, Tag } from "../ui.jsx";
import { reportAnswer } from "../sound.js";
import Summary from "./Summary.jsx";

export default function SqlDrill({ api }) {
  const [n, setN] = useState("5");
  const [sess, setSess] = useState(null);
  const [ans, setAns] = useState("");
  const [hint, setHint] = useState(null);
  const ansRef = useRef("");
  ansRef.current = ans;

  async function start() {
    const d = await api("/api/quiz/start", { mode: "sql", n: +n });
    if (d.error) {
      setSess({ err: d.error });
      return;
    }
    setAns("");
    setHint(null);
    setSess({ sid: d.session, q: d.question, reveal: null, summary: null });
  }

  async function answer(skip) {
    if (!sess || sess.reveal) return;
    const body = { session: sess.sid };
    if (skip) body.action = "skip";
    else body.answer = ansRef.current;
    const d = await api("/api/quiz/answer", body);
    if (d.error) {
      setSess({ err: d.error });
      return;
    }
    reportAnswer(d); // mascot: right/wrong line, or the score line at the end
    setSess({ ...sess, reveal: { ...d, skip } });
  }

  async function showHint() {
    const d = await api("/api/quiz/answer", {
      session: sess.sid,
      action: "hint",
    });
    setHint(d.hint);
  }

  function advance() {
    const d = sess.reveal;
    setAns("");
    setHint(null);
    if (d.next) setSess({ sid: sess.sid, q: d.next, reveal: null, summary: null });
    else setSess({ summary: d.summary });
  }

  if (!sess || sess.err)
    return (
      <Panel id="ssetup">
        <h3 className="m-0 font-display text-[16px] font-semibold">SQL drill</h3>
        <p className="mb-3 mt-0.5 text-[13px] text-mut">
          Write real statements against fresh copies of the course data. Graded
          by running your SQL and comparing results — messy-but-correct passes.
        </p>
        <div className="flex flex-wrap items-center gap-2.5">
          <label htmlFor="sn" className="text-[13px] text-mut">
            tasks
          </label>
          <select
            id="sn"
            value={n}
            onChange={(e) => setN(e.target.value)}
            className="rounded-lg border border-line bg-panel px-2.5 py-2 text-[14px] text-ink"
          >
            {[3, 5, 8, 10, 15].map((x) => (
              <option key={x}>{x}</option>
            ))}
          </select>
          <Btn variant="gold" id="sstart" onClick={start}>
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
      <Panel id="sqlarea">
        <Summary s={sess.summary} mode="sql" onAgain={() => setSess(null)} />
      </Panel>
    );

  const q = sess.q;
  const r = sess.reveal;
  return (
    <Panel id="sqlarea">
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
      <p className="m-0 mb-2.5 whitespace-pre-wrap text-[16.5px] leading-normal">
        {q.prompt}
      </p>
      <p className="m-0 mb-2.5 font-mono text-[12.5px] text-mut">
        database: <b className="text-ink">{q.db}</b> · tables:{" "}
        {q.tables.join(", ")}
      </p>
      {!r ? (
        <>
          <textarea
            id="anssql"
            className="editor"
            spellCheck="false"
            autoFocus
            placeholder="-- write your statement(s), then Submit"
            value={ans}
            onChange={(e) => setAns(e.target.value)}
            onKeyDown={(e) => {
              if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
                e.preventDefault();
                answer(false);
              }
            }}
          />
          <div className="mt-3 flex flex-wrap items-center gap-2.5">
            <Btn variant="gold" onClick={() => answer(false)}>
              Submit
            </Btn>
            {q.has_hint && (
              <Btn variant="ghost" onClick={showHint}>
                Show hint
              </Btn>
            )}
            <Btn variant="ghost" onClick={() => answer(true)}>
              Skip
            </Btn>
            <span className="text-[13px] text-mut">
              <Kbd>Ctrl</Kbd>+<Kbd>Enter</Kbd> submits
            </span>
          </div>
          {hint && <Note>{hint}</Note>}
        </>
      ) : (
        <div>
          {r.skip ? (
            <div className="mb-1 text-[14px] font-bold text-bad">Skipped</div>
          ) : r.correct ? (
            <div className="mb-1 text-[14px] font-bold text-ok">✔ Correct</div>
          ) : (
            <div className="mb-1 text-[14px] font-bold text-bad">
              ✘ Not quite
            </div>
          )}
          {(r.feedback || []).map((f, i) => (
            <ul key={i} className="my-1.5 list-disc pl-5 text-[13.5px] text-bad">
              <li>{f}</li>
            </ul>
          ))}
          <div className="mb-1.5 mt-3 text-[13px] text-mut">
            Reference solution
          </div>
          <pre className="m-0 overflow-auto whitespace-pre-wrap rounded-xl border border-conline bg-console p-3.5 font-mono text-[13px] leading-relaxed text-constext">
            {r.reference}
          </pre>
          {r.expected && (
            <>
              <div className="mb-1.5 mt-3 text-[13px] text-mut">
                Expected result
              </div>
              <ResultTable
                headers={r.expected.headers}
                rows={r.expected.rows}
                total={r.expected.total}
                truncated={false}
              />
            </>
          )}
          <div className="mt-4 flex items-center gap-2.5">
            <Btn variant="gold" autoFocus onClick={advance}>
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
