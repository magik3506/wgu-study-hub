/* Render check — executed by the harness (core/harness.py) when node and
 * web/node_modules are available. Boots the BUILT bundle from webdist inside
 * jsdom with a stubbed fetch that returns a real pack's /api/meta payload,
 * then asserts the rendered DOM is capability-true:
 *   - tab buttons match the pack's tabs, in order
 *   - playground section present iff stipulated; stdin box visibility right
 *   - focus dropdown contains every chapter and every topic label
 * Usage: node scripts/render_check.mjs <webdist-dir> <meta.json>
 * Exit 0 = pass; exit 1 with a message on stderr = fail.
 */
import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { JSDOM } from "jsdom";

const [, , webdist, metaPath] = process.argv;
const fail = (msg) => {
  console.error(msg);
  process.exit(1);
};

if (!webdist || !metaPath) fail("usage: render_check.mjs <webdist> <meta.json>");
const meta = JSON.parse(fs.readFileSync(metaPath, "utf8"));
const indexHtml = fs.readFileSync(path.join(webdist, "index.html"), "utf8");
const entry = indexHtml.match(/src="(\/assets\/[^"]+\.js)"/);
if (!entry) fail("render: no /assets/*.js entry in webdist/index.html");

const dom = new JSDOM(
  '<!doctype html><html><head></head><body><div id="root"></div></body></html>',
  { url: "http://127.0.0.1" + meta.base + "/", pretendToBeVisual: true }
);
// global-jsdom pattern: expose the whole window on global so the browser
// bundle (React, Vite preload polyfill, our code) finds everything it needs.
const FORCE = new Set([
  "window", "document", "navigator", "localStorage", "sessionStorage",
  "location", "history", "self", "top", "parent",
]);
const SKIP = new Set(["global", "globalThis", "process", "Buffer",
  "undefined", "eval", "console"]);
for (const k of Object.getOwnPropertyNames(dom.window)) {
  if (SKIP.has(k) || k.startsWith("_")) continue;
  if (k in global && !FORCE.has(k)) continue;
  try {
    // node 22 ships some of these as read-only getters — override explicitly
    Object.defineProperty(global, k, {
      value: dom.window[k],
      configurable: true,
      writable: true,
    });
  } catch {
    /* leave node's own global in place if it refuses */
  }
}

global.fetch = async (url) => {
  const u = String(url);
  const j = (o) => ({ ok: true, status: 200, json: async () => o });
  if (u.endsWith("/api/meta")) return j(meta);
  if (u.endsWith("/api/stats")) return j({ concepts: [], weak: [], blueprint: [] });
  if (u.endsWith("/api/side")) return j({ sidebar: null, selector: null });
  if (u.endsWith("/api/courses")) return j({ courses: [], planned: [] });
  return j({});
};

process.on("unhandledRejection", (e) => fail("render: async JS error: " + (e && e.message)));
dom.window.addEventListener("error", (e) => fail("render: JS error: " + e.message));

await import(pathToFileURL(path.join(webdist, entry[1])).href);

// wait for React to fetch meta + paint, up to 5s
const started = Date.now();
while (
  !document.querySelector("button[data-tab]") &&
  Date.now() - started < 5000
) {
  await new Promise((r) => setTimeout(r, 50));
}
await new Promise((r) => setTimeout(r, 120));

const tabs = [...document.querySelectorAll("button[data-tab]")].map((b) =>
  b.getAttribute("data-tab")
);
const want = meta.tabs.map((t) => t.id);
if (JSON.stringify(tabs) !== JSON.stringify(want))
  fail(`render: tabs [${tabs}] != capabilities [${want}]`);

const pgEl = document.getElementById("playground");
if (meta.playground) {
  if (!pgEl) fail("render: stipulated playground missing from page");
  const sw = document.getElementById("stdinwrap");
  if (!sw) fail("render: stdin wrap missing");
  const hidden = sw.classList.contains("hidden");
  if (hidden !== !meta.playground.stdin)
    fail("render: stdin box visibility wrong for backend");
} else if (pgEl) {
  fail("render: console markup on a course with no playground");
}

const sel = document.getElementById("qtopic");
if (!sel) fail("render: focus dropdown missing");
const text = sel.textContent;
for (const t of meta.topics)
  if (!text.includes(t.label))
    fail(`render: topic label ${JSON.stringify(t.label)} missing from focus dropdown`);
for (const c of meta.chapters)
  if (!text.includes(`${meta.unit_label} ${c.ch}`))
    fail(`render: '${meta.unit_label} ${c.ch}' missing from focus dropdown`);

console.log(`RENDER OK tabs=[${tabs.join(",")}] options=${sel.querySelectorAll("option").length}`);
process.exit(0);
