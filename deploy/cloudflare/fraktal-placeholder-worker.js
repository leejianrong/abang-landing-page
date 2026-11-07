// Cloudflare Worker: placeholder landing page for fraktal.abangai.dev.
//
// Serves one static page so the subdomain is live before a real site exists. When
// fraktal gets a real landing page, point the route at that origin (or replace this
// Worker with a path-proxy like indah's) and delete this file.
//
// Route: fraktal.abangai.dev/*

const MARK = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="14" fill="#5f7f25"/><path d="M25 56C16 52 17 44 17 33A15 15 0 0 1 47 33A10 10 0 0 1 27 33A5 5 0 0 1 37 33" fill="none" stroke="#fbf4e4" stroke-width="4.2" stroke-linecap="round" stroke-linejoin="round"/></svg>`;

const HTML = `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>fraktal</title>
<meta name="description" content="Procedural world generation for synthetic satellite and geospatial training data.">
<link rel="icon" href="data:image/svg+xml,${encodeURIComponent(MARK)}">
<style>
:root{color-scheme:light dark;--bg:#fbf8f2;--ink:#1d1a17;--mute:#55504a;--accent:#5f7f25}
@media (prefers-color-scheme:dark){:root{--bg:#161a10;--ink:#f1ecde;--mute:#b9b5a6;--accent:#9fc255}}
*{box-sizing:border-box}
body{margin:0;min-height:100vh;display:grid;place-items:center;padding:24px;background:var(--bg);color:var(--ink);font:17px/1.55 system-ui,-apple-system,"Segoe UI",sans-serif}
main{max-width:34rem}
.mark{width:72px;height:72px;margin-bottom:20px}
h1{margin:0 0 8px;font-size:2.4rem;letter-spacing:-.03em}
p{margin:0 0 14px;color:var(--mute)}
a{color:var(--accent)}
.tag{display:inline-block;margin-bottom:16px;padding:2px 10px;border:1px solid var(--accent);border-radius:99px;font-size:.8rem;color:var(--accent)}
</style>
</head>
<body>
<main>
<div class="mark">${MARK}</div>
<span class="tag">early</span>
<h1>fraktal</h1>
<p>Procedural world generation for synthetic satellite and geospatial training data. Deterministic, labelled worlds, conditioned on real geography and rendered with pixel-exact labels.</p>
<p>A real landing page is coming. For now, the project lives on <a href="https://github.com/leejianrong/fraktal">GitHub</a>. Part of <a href="https://abangai.dev">abang-ai</a>.</p>
</main>
</body>
</html>`;

export default {
  async fetch() {
    return new Response(HTML, {
      headers: {
        "content-type": "text/html; charset=utf-8",
        "cache-control": "public, max-age=300",
      },
    });
  },
};
