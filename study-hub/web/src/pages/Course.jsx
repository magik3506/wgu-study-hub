import { useEffect, useMemo, useState } from "react";
import { makeApi, useTheme } from "../theme.js";
import { Empty, Panel, TopBar } from "../ui.jsx";
import Playground from "../features/Playground.jsx";
import Drill from "../features/Drill.jsx";
import SqlDrill from "../features/SqlDrill.jsx";
import Mastery from "../features/Mastery.jsx";
import Guide from "../features/Guide.jsx";

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
    </>
  );
}
