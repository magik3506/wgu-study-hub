import { useEffect, useState } from "react";

const KEY = "wgu-hub-theme";

function stored() {
  try {
    return localStorage.getItem(KEY) === "light" ? "light" : "dark";
  } catch {
    return "dark";
  }
}

export function useTheme() {
  const [theme, setTheme] = useState(stored);
  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    try {
      localStorage.setItem(KEY, theme);
    } catch {
      /* private mode — theme just won't persist */
    }
  }, [theme]);
  return [theme, () => setTheme((t) => (t === "dark" ? "light" : "dark"))];
}

/** API helper. `base` is "" on the homepage or "/c/<slug>" on a course page;
 *  paths starting with /api are prefixed with it, mirroring the old client. */
export function makeApi(base) {
  return async function api(path, body) {
    const url = path.startsWith("/api/") ? base + path : path;
    const res = await fetch(
      url,
      body === undefined
        ? {}
        : {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(body),
          }
    );
    return res.json();
  };
}
