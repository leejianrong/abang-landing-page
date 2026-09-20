# abang-landing-page — agent brief

## What this is

A single self-contained `index.html` (all CSS/JS inline, no build step) that is the
umbrella marketing page for Abang, Jian's suite of durable/inspectable AI tools. It is
**not** any one product's docs site — each product with real docs has its own
Zensical/mkdocs site in its own repo (see the Products section of `index.html` for the
current list and links). This repo only owns the top-level pitch and the roster.

## The one rule that matters here: status must match the sibling repo, not memory

This page has gone stale in the past by copying a status once and never revisiting it —
it called cuttlefish "sotong" for weeks after the rename, and kept kopicode's status pill
at "Planned" long after it shipped a real tagged release with a one-line installer. Before
touching any product tile, check that product's own README.md/CLAUDE.md and its latest
git tag/release, not what this file currently says or what you remember. The status pills
(`Alpha`, `Available`, `Planned`, `Research`) are deliberately honest, not aspirational —
see the CSS comment above `.status.plan` in `index.html` for why "Planned" is styled to be
the quietest one.

## Structure

```
index.html                     the live site — the only file that gets published
.github/workflows/deploy.yml   builds and deploys to GitHub Pages on push to main
design/                        design explorations/logo options, kept for reference, never deployed
```

## Deploy

Push to `main` → GitHub Actions publishes `index.html` to GitHub Pages. First-time repo
setup: Settings → Pages → source = GitHub Actions.

**Domain migration in progress (2026-09-20):** moving off `leejianrong.github.io/*` /
Netlify / Fly.io product-by-product onto `abangai.dev` (Cloudflare-managed DNS), with
one subdomain per product (e.g. `satay.abangai.dev`, `kopicode.abangai.dev`). This repo's
own site is meant to move to the apex domain (`abangai.dev`). Until DNS is live and each
repo's GitHub Pages custom domain is configured, `index.html` still links to the
`leejianrong.github.io/*` URLs — don't half-migrate a link (pointing it at a subdomain
that doesn't resolve yet is worse than the stale-but-working URL it replaces). Update all
absolute URLs — `<link rel="canonical">`, `og:url`, `twitter` tags, nav "Docs" link,
footer product links — in one pass, in the same commit as adding the CNAME file, once the
corresponding DNS record actually resolves. Full plan lives in Jian's memory system
(`abang-ai-domain-migration`); short version: any product needing both a docs site and a
live demo on one subdomain (indah is the first case) gets a Cloudflare Worker path-proxy
in front, not a merged codebase or a DNS trick — DNS routes by hostname, not by path.

**tingkat is deliberately excluded** from this page (Jian's call, 2026-09-20 — not
interested in showing it publicly). Don't re-add it from git history or an old memory of
the roster without checking with him first.

**cuttlefish is "cuttlefish-crew" here, ahead of the actual rename.** The sibling repo is
still named/hosted as `cuttlefish-agent` — the rename to `cuttlefish-crew` is decided in
its own `docs/QUESTIONS.md` Q30 but not yet executed (deferred: a live session was working
in that directory when this came up). This page uses the new external name already since
that's the name users should see; it has no GitHub link yet because the URL would still
say the old name — add one once the sibling repo's rename lands.

## Local preview

Static file: `open index.html` (macOS) or `xdg-open index.html` (Linux).
