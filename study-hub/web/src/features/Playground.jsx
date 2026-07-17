import { useEffect, useRef, useState } from "react";
import { Btn, Kbd, Note, Panel, ResultTable } from "../ui.jsx";

function Block({ b }) {
  return (
    <Panel className="mt-3.5">
      {b.kind === "table" ? (
        <ResultTable
          headers={b.headers}
          rows={b.rows}
          total={b.total}
          truncated={b.truncated}
        />
      ) : b.kind === "error" ? (
        <div className="rounded-lg border-l-4 border-bad bg-badbg px-3 py-2 font-mono text-[13px] text-bad">
          {b.text}
        </div>
      ) : b.kind === "ok" ? (
        <div className="rounded-lg border-l-4 border-ok bg-okbg px-3 py-2 font-mono text-[13px] text-ok">
          {b.text}
        </div>
      ) : (
        <pre className="m-0 whitespace-pre-wrap font-mono text-[13px] text-ink">
          {b.text}
        </pre>
      )}
      {(b.notes || []).map((n, i) => (
        <Note key={i}>{n}</Note>
      ))}
    </Panel>
  );
}

export default function Playground({ api, pg }) {
  const [side, setSide] = useState(null);
  const [selector, setSelector] = useState(null);
  const [out, setOut] = useState(null);
  const [src, setSrc] = useState("");
  const [stdin, setStdin] = useState("");
  const srcRef = useRef("");
  srcRef.current = src;

  async function loadSide() {
    const d = await api("/api/side");
    setSide(d.sidebar);
    setSelector(d.selector);
  }
  useEffect(() => {
    loadSide();
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  async function run(source) {
    const d = await api("/api/run", { source, stdin });
    setOut(d);
    loadSide();
  }
  async function reset(target) {
    const d = await api("/api/reset", { target });
    setOut({ blocks: [{ kind: "ok", text: d.message || "Restored." }] });
    loadSide();
  }
  function chipRun(code) {
    setSrc(code);
    run(code);
  }
  function onKey(e) {
    if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
      e.preventDefault();
      run(srcRef.current);
    }
  }

  return (
    <div
      className={
        "grid items-start gap-4.5 " +
        (side ? "md:grid-cols-[262px_1fr]" : "")
      }
    >
      {side && (
        <Panel id="sidepane">
          <h3 className="m-0 font-display text-[16px] font-semibold">
            {side.title}
          </h3>
          <p
            className="m-0 mb-2 text-[13px] text-mut"
            dangerouslySetInnerHTML={{ __html: side.sub || "" }}
          />
          <div>
            {(side.groups || []).map((g) => (
              <div
                key={g.name}
                className="border-b border-line py-2.5 last:border-b-0"
              >
                <div className="flex items-center gap-2 font-mono text-[13px] font-bold text-ink">
                  <span
                    className={
                      "h-2 w-2 rounded-full " +
                      (g.on ? "bg-gold" : "bg-line")
                    }
                  />
                  {g.name}
                </div>
                <div className="mb-2 mt-1 text-[11.5px] text-mut">
                  {g.desc}
                  {g.reset && (
                    <>
                      {" · "}
                      <button
                        onClick={() => reset(g.name)}
                        className="cursor-pointer border-0 bg-transparent p-0 text-[11.5px] text-crumb underline"
                      >
                        reset
                      </button>
                    </>
                  )}
                </div>
                <div className="flex flex-wrap gap-1.5">
                  {(g.items || []).map((it) => (
                    <span
                      key={it.label}
                      className="inline-flex overflow-hidden rounded-lg border border-line bg-panel"
                    >
                      <button
                        title={it.title || ""}
                        onClick={() => chipRun(it.run)}
                        className="cursor-pointer border-0 bg-transparent px-2 py-1.5 font-mono text-[12px] font-semibold text-ink hover:bg-panel2"
                      >
                        {it.label}
                      </button>
                      {it.alt_run && (
                        <button
                          title={it.alt_title || ""}
                          onClick={() => chipRun(it.alt_run)}
                          className="cursor-pointer border-0 border-l border-line bg-transparent px-2 py-1.5 font-mono text-[11px] text-mut hover:bg-panel2"
                        >
                          i
                        </button>
                      )}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
          {side.reset_all && (
            <p className="m-0 mt-3">
              <button
                onClick={() => reset("all")}
                className="cursor-pointer border-0 bg-transparent p-0 text-[12.5px] text-crumb underline"
              >
                {side.reset_all}
              </button>
            </p>
          )}
        </Panel>
      )}

      <div>
        <Panel>
          <div className="mb-3 flex flex-wrap items-center justify-between gap-2.5">
            <h3 className="m-0 font-display text-[16px] font-semibold">
              {pg.label}
            </h3>
            <div className="flex items-center gap-2.5">
              {selector && (
                <>
                  <label
                    htmlFor="pgsel"
                    className="text-[13px] text-mut"
                  >
                    {selector.label}
                  </label>
                  <select
                    id="pgsel"
                    defaultValue={selector.current}
                    onChange={(e) =>
                      run(
                        (selector.run_template || "")
                          .split("{value}")
                          .join(e.target.value)
                      )
                    }
                    className="rounded-lg border border-line bg-panel px-2.5 py-2 text-[14px] text-ink"
                  >
                    {selector.options.map((o) => (
                      <option key={o}>{o}</option>
                    ))}
                  </select>
                </>
              )}
              <Btn variant="gold" onClick={() => run(src)}>
                Run
              </Btn>
              <span className="text-[13px] text-mut">
                <Kbd>Ctrl</Kbd>+<Kbd>Enter</Kbd>
              </span>
            </div>
          </div>
          <textarea
            id="pgbox"
            className="editor"
            spellCheck="false"
            placeholder={pg.placeholder}
            value={src}
            onChange={(e) => setSrc(e.target.value)}
            onKeyDown={onKey}
          />
          <div id="stdinwrap" className={pg.stdin ? "" : "hidden"}>
            <label
              htmlFor="pgstdin"
              className="mb-1 mt-2.5 block text-[13px] text-mut"
            >
              program input (stdin)
            </label>
            <textarea
              id="pgstdin"
              className="editor stdin"
              spellCheck="false"
              value={stdin}
              onChange={(e) => setStdin(e.target.value)}
              onKeyDown={onKey}
            />
          </div>
        </Panel>
        <div id="results">
          {out === null ? (
            <Panel className="mt-3.5">
              <div className="text-center text-[14px] text-mut">
                Nothing to run yet.
              </div>
            </Panel>
          ) : (
            <>
              {(out.blocks || []).map((b, i) => (
                <Block key={i} b={b} />
              ))}
              {(out.notes || []).map((n, i) => (
                <Panel key={"n" + i} className="mt-3.5">
                  <Note>{n}</Note>
                </Panel>
              ))}
              {!(out.blocks || []).length && !(out.notes || []).length && (
                <Panel className="mt-3.5">
                  <div className="text-center text-[14px] text-mut">
                    Nothing to run yet.
                  </div>
                </Panel>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}
