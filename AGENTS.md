# abang-landing-page — agent brief

## What this is

A single self-contained `index.html` (all CSS/JS inline, no build step) that is the
umbrella marketing page for Abang, Jian's suite of AI agents and agentic tools. It is
**not** any one product's docs site — each product with real docs has its own
Zensical/mkdocs site (or, for satay, a planned separate marketing site — see below) in
its own repo (see the Products section of `index.html` for the current list and links).
This repo only owns the top-level pitch and the roster.

## No status pills, no shipped/building split (2026-09-21)

The page used to badge every product tile `Alpha` / `Available` / `Planned` / `Research`
and group them into separate "shipping" and "in the kitchen" grids. Both were removed
deliberately: Jian's call was that the suite moves fast enough that a stage badge goes
stale quickly, and it read as building hierarchy the products don't actually have. All
named products (satay, sibei-flow, kopicode, indah, kampong-agents, cuttlefish-crew) now
sit in one unified grid with equal visual weight, no badge, no tier. Only the two
not-yet-real items (an open-weights model, synthetic-data tooling) are called out
separately, as a single one-line sentence, since they have no repo or link yet. Don't
reintroduce status pills or a shipped/building visual split without checking with Jian —
this was an explicit, considered decision, not an oversight.

Still true from before: keep whatever *is* said about a product (links, one-line
description) matching that product's own README.md/CLAUDE.md and latest git tag/release,
not what this file currently says or what you remember. This page called cuttlefish
"sotong" for weeks after the rename, so don't trust a stale copy of the roster either.

## Copy/tone (2026-09-21 rewrite)

The page went through a full copy pass: dropped the old "AI tools that show their work"
tagline for "Building AI agents and agentic tools", cut per-product copy down to one line
each (no more two-paragraph blurbs), and dropped "self-hosted" as a stated selling point
per Jian's call — it's true of every product but he doesn't want it framed as the pitch.
Product one-line descriptions should stay concrete (name what the tool actually does) over
generic ("agent orchestration platform"-style copy). No em dashes anywhere on this page —
commas or a full stop instead, per Jian's house style.

## Satay's marketing content moved out, not deleted

The old page had a full second act after the product grid: a satay code sample, a
LangGraph/satay comparison table, and a Satay Studio screenshot mockup. All of that is
gone from this page and is meant to land on a separate satay marketing site (same
Worker-proxy split-origin pattern as indah: root = marketing, `/docs` = the existing
Zensical docs at `satay.abangai.dev`) — not built yet, tracked as a follow-up, not
something to recreate here. Until that site exists, satay's tile just links to its
current docs site like every other product.

## Structure

```
index.html                     the live site
assets/                        published with the site: favicon.svg, favicon-32.png,
                               apple-touch-icon.png, og.png (social card)
.github/workflows/deploy.yml   builds and deploys to GitHub Pages on push to main
design/                        design explorations and logo options, never deployed
design/brand/                  master logo SVGs and their generators (see its README)
blog/                          blog posts (posts/), Codex briefs (briefs/), AGENTS.md for the
                               writing agent, PLAN.md, run-codex.sh
scripts/build_blog.py          builds the blog from Markdown; CI runs it into _site
deploy/cloudflare/             Cloudflare Worker sources (fraktal.abangai.dev placeholder)
```

## Deploy

Push to `main` → GitHub Actions publishes `index.html`, `CNAME` and `assets/` to GitHub Pages.
First-time repo setup: Settings → Pages → source = GitHub Actions.

## Blog

Posts are Markdown in `blog/posts/<slug>.md` with the metadata comment described in
`scripts/build_blog.py`. CI builds every `status: Published` post into `/blog/`, plus a feed,
`sitemap.xml` and `robots.txt`. The page chrome (styles, nav, footer) is lifted from `index.html`
at build time, so edit it there, never in the script. Prose is written by a Codex agent from a brief
(`blog/PLAN.md`, `blog/run-codex.sh`) and reviewed by Jian; agents working on this repo should not
write post prose themselves. Preview drafts with
`uv run scripts/build_blog.py --drafts --out /tmp/blog-preview`.

## Logos and backgrounds

Each logo ships as variants, because a logo's background is a property of where it is used, not
of the mark (`design/brand/README.md` lists the files):

- **Favicon:** `assets/favicon.svg` is the ketupat on a transparent background and switches
  colour for dark tabs, with `favicon-32.png` as the fallback. The orange tile is *not* used
  here: the bare glyph is larger and clearer at 16px.
- **`apple-touch-icon.png`:** opaque and full-bleed (iOS fills transparency with black and
  rounds the corners itself).
- **Product tiles on the page** are the rounded tile icons with a 1px ring from `--line`, so a
  dark tile (satay) stays visible on the dark card.
- **Nav and footer** use the inline ketupat in `currentColor`, the transparent mono form.
- **`og.png`** is rendered from the master SVGs; regenerate it when a product is added.

Do not bake a background or rounded corners into a logo that goes on someone else's surface
(avatars, app icons): use the `-icon-square.svg` or `-mono.svg` variants.

**Domain migration done (landed 2026-09-21):** this site and every shipped product's docs
site now live under `abangai.dev` (Cloudflare-managed DNS) — `satay.abangai.dev`,
`sibeiflow.abangai.dev`, `indah.abangai.dev`, this repo at the apex `abangai.dev` — no more
`leejianrong.github.io/*` links in `index.html`. kopicode, cuttlefish-crew, vikaki and
fraktal don't have a live docs/marketing site yet, so their tiles link straight to GitHub
(`fraktal.abangai.dev` is only a placeholder page). kampong-agents and semula have docs sites
and link to them. Full plan and what's still open lives in Jian's memory system
(`abang-ai-domain-migration`); short version: any product needing both a docs site and a
live demo on one subdomain (indah is the first case, satay is next) gets a Cloudflare
Worker path-proxy in front, not a merged codebase or a DNS trick — DNS routes by hostname,
not by path.

**tingkat is deliberately excluded** from this page (Jian's call, 2026-09-20 — not
interested in showing it publicly). Don't re-add it from git history or an old memory of
the roster without checking with him first.

**cuttlefish-crew is the real name now** — the `cuttlefish-agent` → `cuttlefish-crew`
rename (repo, remote, docs) landed 2026-09-21, so this page's GitHub link is real, not
provisional.

## Local preview

Static file: `open index.html` (macOS) or `xdg-open index.html` (Linux).
