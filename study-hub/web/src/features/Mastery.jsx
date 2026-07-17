import { useEffect, useState } from "react";
import { Btn, Empty, Panel, PanelTitle } from "../ui.jsx";

export default function Mastery({ api, meta, active }) {
  const [d, setD] = useState(null);
  const [confirming, setConfirming] = useState(false);

  async function load() {
    setD(await api("/api/stats"));
  }
  useEffect(() => {
    if (active) {
      load();
      setConfirming(false);
    }
  }, [active]); // eslint-disable-line react-hooks/exhaustive-deps

  async function reset() {
    if (!confirming) {
      setConfirming(true);
      return;
    }
    await api("/api/stats/reset", {});
    setConfirming(false);
    load();
  }

  let body = null;
  if (d && !d.concepts.length)
    body = (
      <Empty>
        No drills yet — your mastery map fills in as you answer. Start with an
        exam drill.
      </Empty>
    );
  else if (d) {
    let lastCh = null;
    body = (
      <div>
        {d.concepts.map((r) => {
          const header =
            r.ch !== lastCh ? (
              <div className="mb-1 mt-4 font-mono text-[13px] font-bold uppercase tracking-wider text-mut">
                {meta.unit_label} {r.ch}
              </div>
            ) : null;
          lastCh = r.ch;
          return (
            <div key={r.ch + r.ref + r.name}>
              {header}
              <div className="grid grid-cols-[86px_1fr_150px_52px] items-center gap-3 border-b border-line/60 py-1.5 text-[13.5px] max-md:grid-cols-[70px_1fr_90px_46px]">
                <span className="font-mono text-[12px] font-semibold text-mut">
                  §{r.ref}
                </span>
                <span>{r.name}</span>
                <span className="h-2 overflow-hidden rounded-full bg-panel2">
                  <i
                    className="block h-full bg-gold"
                    style={{ width: r.pct + "%" }}
                  />
                </span>
                <span className="text-right font-mono text-[12.5px] font-bold">
                  {r.correct}/{r.attempts}
                </span>
              </div>
            </div>
          );
        })}
        {d.weak.length > 0 && (
          <div className="mt-3.5 text-[13px] text-mut">
            Weakest right now:{" "}
            {d.weak.map((w) => `${w.name} (§${w.ref})`).join("; ")}
          </div>
        )}
        <div className="mt-3.5 text-[13px] text-mut">
          OA blueprint baseline:{" "}
          {d.blueprint.map((b) => `Ch${b.ch} ${b.w}%`).join(" · ")}
        </div>
      </div>
    );
  }

  return (
    <Panel>
      <PanelTitle
        title="Mastery map"
        sub="Shared with the terminal version — every answer, either place, moves these bars and re-weights your next drill."
        right={
          <>
            <Btn variant="ghost" onClick={load}>
              Refresh
            </Btn>
            <Btn
              variant="ghost"
              onClick={reset}
              className={confirming ? "border-bad text-bad" : ""}
            >
              {confirming ? "Really reset all history?" : "Reset history"}
            </Btn>
          </>
        }
      />
      {body}
    </Panel>
  );
}
