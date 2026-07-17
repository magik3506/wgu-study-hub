import { useEffect, useState } from "react";
import Home from "./pages/Home.jsx";
import Course from "./pages/Course.jsx";
import { BreakBanner } from "./ui.jsx";
import "./sound.js"; // boot the shared music/voice system once per page load

/* Client-side routing.
 *
 * The hub used to navigate with full page loads (<a href> everywhere), which
 * tore down the whole document between the homepage and course pages — taking
 * the hidden YouTube player with it. Every hop rebuilt the player, and since
 * browsers only allow MUTED autoplay, it always came back muted.
 *
 * Now internal navigation is intercepted: we pushState and re-render instead
 * of reloading. The document (and the music player, its track position, and
 * your mute choice) survives the trip. Only a genuinely fresh launch starts
 * muted — that part is the browser's autoplay policy, not us.
 *
 * Interception is deliberately narrow: only plain left-clicks on same-origin
 * links to "/" or "/c/<slug>". Downloads (guide.pdf), hash links, new-tab
 * clicks, and anything with a modifier key keep their native behavior.
 */

const SPA_ROUTE = /^\/(?:c\/[\w.-]*[\w-])?\/?$/;

function currentPath() {
  return window.location.pathname;
}

export default function App() {
  const [path, setPath] = useState(currentPath);

  useEffect(() => {
    const onPop = () => setPath(currentPath());
    window.addEventListener("popstate", onPop);

    const onClick = (e) => {
      if (e.defaultPrevented || e.button !== 0) return;
      if (e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
      const a = e.target.closest && e.target.closest("a[href]");
      if (!a || a.target || a.hasAttribute("download")) return;
      const href = a.getAttribute("href") || "";
      if (!href.startsWith("/") || href.startsWith("//")) return;
      const clean = href.split("#")[0].split("?")[0];
      if (!SPA_ROUTE.test(clean)) return; // guide.pdf, /api/…, etc. stay native
      e.preventDefault();
      if (clean !== currentPath()) {
        window.history.pushState(null, "", href);
        setPath(clean);
      }
      window.scrollTo(0, 0);
    };
    document.addEventListener("click", onClick);

    return () => {
      window.removeEventListener("popstate", onPop);
      document.removeEventListener("click", onClick);
    };
  }, []);

  const m = path.match(/^\/c\/([^/]+)/);
  useEffect(() => {
    if (!m) document.title = "WGU Study Hub";
  }, [path]); // eslint-disable-line react-hooks/exhaustive-deps

  return (
    <>
      <BreakBanner />
      {m ? <Course key={m[1]} slug={m[1]} /> : <Home />}
    </>
  );
}
