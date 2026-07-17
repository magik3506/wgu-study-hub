"""Fallback page only. The real frontend lives in core/webdist/ (built from
web/ by `npm run build`); this renders when webdist is missing so the hub
degrades with instructions instead of a blank screen."""

FALLBACK_HTML = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>WGU Study Hub — frontend missing</title>
<style>
  body { background:#041423; color:#e9f1fa; font:15px/1.6 system-ui,sans-serif;
         display:grid; place-items:center; min-height:100vh; margin:0; }
  main { max-width:52ch; padding:32px; background:#0a2540; border:1px solid
         #16406b; border-radius:16px; }
  h1 { font-size:20px; margin:0 0 10px; }
  code { font-family:ui-monospace,Menlo,Consolas,monospace; color:#ffb81c; }
  a { color:#8fbce8; }
</style>
</head>
<body>
<main>
  <h1>&#129417; The hub server is running, but its frontend is missing.</h1>
  <p>The folder <code>core/webdist/</code> (the built web app) wasn't found
  next to the server code.</p>
  <p>If you downloaded a release zip, re-download it &mdash; the zip ships
  with <code>webdist</code> included. If you're hacking on the UI, build it
  once with:</p>
  <p><code>cd web &amp;&amp; npm install &amp;&amp; npm run build</code></p>
  <p>The APIs still work in the meantime (try
  <a href="/api/courses">/api/courses</a>).</p>
</main>
</body>
</html>"""
