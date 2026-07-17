import { Btn, Tag } from "../ui.jsx";

export default function Summary({ s, mode, onAgain, onWeakDrill }) {
  return (
    <div>
      <div className="mb-2">
        <Tag>Session summary</Tag>
      </div>
      <div className="font-mono text-[44px] font-bold leading-none text-ink">
        {s.score}
        <small className="text-[18px] text-mut">
          {" "}
          / {s.total} · {s.pct}%
        </small>
      </div>
      <div className="mb-1.5 mt-4 text-[13px] text-mut">By chapter</div>
      {s.chapters.map((c) => {
        const pct = Math.round((100 * c.correct) / c.attempts);
        return (
          <div
            key={c.ch}
            className="my-1.5 grid grid-cols-[52px_1fr_62px] items-center gap-2.5 font-mono text-[12.5px]"
          >
            <span>Ch{c.ch}</span>
            <span className="h-2 overflow-hidden rounded-full bg-panel2">
              <i
                className="block h-full bg-gold"
                style={{ width: pct + "%" }}
              />
            </span>
            <span>
              {c.correct} / {c.attempts}
            </span>
          </div>
        );
      })}
      {s.weak.length ? (
        <div className="mt-3.5 text-[13px] text-mut">
          Review next:{" "}
          {s.weak.map((w) => `${w.name} (§${w.ref})`).join("; ")} — now
          weighted more heavily.
        </div>
      ) : (
        <div className="mt-3.5 text-[13px] text-mut">
          Clean sweep — these concepts will show up a little less often now.
        </div>
      )}
      <div className="mt-4 flex flex-wrap gap-2.5">
        <Btn variant="gold" onClick={onAgain}>
          New drill
        </Btn>
        {mode === "mcq" && s.weak.length > 0 && (
          <Btn variant="ghost" onClick={() => onWeakDrill(s.weak[0])}>
            Drill weakest: {s.weak[0].name}
          </Btn>
        )}
      </div>
    </div>
  );
}
