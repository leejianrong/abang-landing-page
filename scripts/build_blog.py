#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["markdown==3.7", "pyyaml==6.0.2"]
# ///
"""Build the Abang blog from Markdown into static HTML.

    uv run scripts/build_blog.py --out _site          # what CI does (published posts only)
    uv run scripts/build_blog.py --out /tmp/preview --drafts   # include Draft posts, marked noindex

Posts live in blog/posts/<slug>.md and open with the metadata comment used by the
write-tech-blog-post skill:

    <!--
    title: "..."
    description: One or two sentences.
    slug: the-file-name-without-md
    author: Jian
    date: 2026-11-07
    status: Draft            # Draft | Published (only Published is built unless --drafts)
    tags: [engineering, semula]
    product: semula          # optional
    sources: [...]           # optional, for reviewers; never rendered
    -->

    ---

    # Title again

    Body...

The page chrome (styles, nav, footer, theme script) is lifted from index.html so the blog
cannot drift from the landing page. Output: blog/index.html, blog/<slug>/index.html,
blog/feed.xml, sitemap.xml and robots.txt.
"""
import argparse
import datetime as dt
import html
import re
import sys
from email.utils import format_datetime
from pathlib import Path

import markdown
import yaml

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://abangai.dev"
WPM = 220

BLOG_CSS = """
  /* ---------- blog ---------- */
  .container.col { max-width:808px; }
  .blog { padding:56px 0 76px; }
  .blog h1 { margin:0; font-size:clamp(32px,4.6vw,46px); font-weight:800; letter-spacing:-.035em; line-height:1.08; }
  .blog .deck { margin:14px 0 0; }
  .navlinks a[aria-current="page"] { color:var(--ink); font-weight:600; }
  .post-list { list-style:none; margin:36px 0 0; padding:0; }
  .post-item { padding:24px 0; border-top:1px solid var(--line); }
  .post-item:last-child { border-bottom:1px solid var(--line); }
  .post-item time, .post-meta { font-family:var(--mono); font-size:12px; color:var(--muted); }
  .post-item h2 { margin:8px 0 8px; font-size:22px; font-weight:750; letter-spacing:-.02em; line-height:1.25; }
  .post-item h2 a { text-decoration:none; }
  .post-item h2 a:hover { color:var(--ember); }
  .post-item p { margin:0; color:var(--muted); font-size:15.5px; line-height:1.55; }
  .tags { display:flex; gap:8px; flex-wrap:wrap; margin-top:12px; padding:0; list-style:none; }
  .tag { font-family:var(--mono); font-size:11.5px; color:var(--muted); border:1px solid var(--line); border-radius:999px; padding:2px 10px; }
  .empty { margin-top:36px; padding:28px; background:var(--card); border:1px solid var(--line); border-radius:16px; color:var(--muted); }
  .empty a { color:var(--ember); font-weight:600; }
  .post-head { margin-bottom:36px; }
  .post-head .post-meta { margin-top:16px; display:block; }
  .draft-note { margin:0 0 20px; font-family:var(--mono); font-size:12px; color:var(--chili); }
  .back { display:inline-block; margin-bottom:28px; font-size:14px; color:var(--muted); text-decoration:none; }
  .back:hover { color:var(--ember); }
  .prose { font-size:17.5px; line-height:1.72; }
  .prose > :first-child { margin-top:0; }
  .prose h2 { margin:2.1em 0 .5em; font-size:27px; font-weight:760; letter-spacing:-.025em; line-height:1.2; }
  .prose h3 { margin:1.8em 0 .4em; font-size:21px; font-weight:740; letter-spacing:-.02em; }
  .prose p, .prose ul, .prose ol { margin:0 0 1.15em; }
  .prose li { margin:.3em 0; }
  .prose a { color:var(--ember); }
  .prose code { font-family:var(--mono); font-size:.88em; background:var(--bg2); padding:.12em .38em; border-radius:5px; }
  .prose pre { overflow-x:auto; background:var(--bg2); border:1px solid var(--line); border-radius:12px; padding:16px 18px; font-size:14px; line-height:1.55; margin:0 0 1.3em; }
  .prose pre code { background:none; padding:0; font-size:inherit; }
  .prose blockquote { margin:1.4em 0; padding:0 0 0 1.2em; color:var(--muted); }
  .prose table { display:block; overflow-x:auto; border-collapse:collapse; font-size:15px; margin:0 0 1.3em; }
  .prose th, .prose td { text-align:left; padding:8px 14px; border-bottom:1px solid var(--line); }
  .prose th { font-weight:650; }
  .prose img { max-width:100%; height:auto; border-radius:10px; }
  .prose hr { border:0; border-top:1px solid var(--line); margin:2.4em 0; }
  @media (max-width:600px){ .navlinks a.keep { display:inline; } .prose { font-size:17px; } }
"""


def die(msg):
    sys.exit(f"build_blog: {msg}")


def chrome():
    """Pull styles, nav, footer and script out of index.html."""
    s = (ROOT / "index.html").read_text()

    def between(a, b):
        i, j = s.index(a), s.index(b, s.index(a))
        return s[i + len(a):j]

    style = re.search(r"<style>(.*?)</style>", s, re.S).group(1)
    nav = between("<!-- ============ NAV ============ -->", "<!-- ============ HERO ============ -->")
    foot = between("<!-- ============ FOOTER ============ -->", "<script>")
    script = s[s.rindex("<script>"):s.rindex("</script>") + len("</script>")]

    def absolute(frag):
        frag = frag.replace('href="#products"', 'href="/#products"').replace('href="#top"', 'href="/"')
        return frag.replace('href="blog/', 'href="/blog/')

    return style, absolute(nav), absolute(foot), script


def parse(path):
    text = path.read_text()
    m = re.match(r"\s*<!--\s*(.*?)\s*-->\s*\n---\s*\n(.*)$", text, re.S)
    if not m:
        die(f"{path.name}: missing the metadata comment followed by a --- line")
    meta = yaml.safe_load(m.group(1)) or {}
    for key in ("title", "description", "slug", "author", "date", "status"):
        if not meta.get(key):
            die(f"{path.name}: metadata is missing '{key}'")
    if meta["slug"] != path.stem:
        die(f"{path.name}: slug '{meta['slug']}' must match the file name")
    d = meta["date"]
    meta["date"] = d if isinstance(d, dt.date) else dt.date.fromisoformat(str(d))
    meta["tags"] = [str(t) for t in meta.get("tags") or []]
    body = re.sub(r"^\s*#\s+.*\n", "", m.group(2), count=1)  # the H1 becomes the page header
    meta["body_md"] = body
    meta["words"] = len(re.findall(r"\w+", body))
    return meta


def render_md(md_text):
    md = markdown.Markdown(extensions=["fenced_code", "tables", "sane_lists", "toc"])
    return md.convert(md_text)


def page(*, title, description, path, content, style, nav, foot, script, og_type="website",
         noindex=False, current_blog=True, date=None):
    e = html.escape
    url = f"{SITE}{path}"
    nav = nav.replace('<a href="/blog/" class="keep">Blog</a>', '<a href="/blog/" class="keep" aria-current="page">Blog</a>') if current_blog else nav
    robots = '<meta name="robots" content="noindex">\n' if noindex else ""
    published = f'<meta property="article:published_time" content="{date}">\n' if date else ""
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(description)}">
<meta name="color-scheme" content="light dark">
<meta name="theme-color" content="#f7f2ea" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#17110c" media="(prefers-color-scheme: dark)">
{robots}<link rel="canonical" href="{e(url)}">
<link rel="alternate" type="application/rss+xml" title="Abang blog" href="{SITE}/blog/feed.xml">
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
<link rel="icon" href="/assets/favicon-32.png" type="image/png" sizes="32x32">
<link rel="apple-touch-icon" href="/assets/apple-touch-icon.png">
<meta property="og:type" content="{og_type}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(description)}">
<meta property="og:url" content="{e(url)}">
{published}<meta property="og:image" content="{SITE}/assets/og.png">
<meta property="og:image:alt" content="Abang: building AI agents and agentic tools, with the logos of nine products in a row.">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{e(title)}">
<meta name="twitter:description" content="{e(description)}">
<meta name="twitter:image" content="{SITE}/assets/og.png">
</head>
<body>
<style>{style}{BLOG_CSS}</style>
{nav}
{content}
{foot}
{script}
</body>
</html>
"""


def tags_html(tags):
    if not tags:
        return ""
    return '<ul class="tags">' + "".join(f'<li class="tag">{html.escape(t)}</li>' for t in tags) + "</ul>"


def build(out, drafts):
    style, nav, foot, script = chrome()
    posts = []
    for f in sorted((ROOT / "blog" / "posts").glob("*.md")):
        meta = parse(f)
        if str(meta["status"]).lower() == "published" or drafts:
            meta["draft"] = str(meta["status"]).lower() != "published"
            posts.append(meta)
    posts.sort(key=lambda p: p["date"], reverse=True)

    kw = dict(style=style, nav=nav, foot=foot, script=script)
    blog = out / "blog"
    blog.mkdir(parents=True, exist_ok=True)

    # ---- index
    if posts:
        items = "\n".join(
            f"""<li class="post-item">
  <time datetime="{p['date']}">{p['date'].strftime('%-d %B %Y')}{' · draft' if p['draft'] else ''}</time>
  <h2><a href="/blog/{p['slug']}/">{html.escape(p['title'])}</a></h2>
  <p>{html.escape(p['description'])}</p>
  {tags_html(p['tags'])}
</li>"""
            for p in posts
        )
        listing = f'<ol class="post-list">\n{items}\n</ol>'
    else:
        listing = ('<p class="empty">The first posts are on the way. Until then, the code is on '
                   '<a href="https://github.com/leejianrong">GitHub</a>.</p>')
    index = f"""<main class="blog"><div class="container col">
<h1>Blog</h1>
<p class="deck">Engineering notes, release posts and how-tos from the Abang tools.</p>
{listing}
</div></main>"""
    (blog / "index.html").write_text(page(
        title="Blog · Abang", description="Engineering notes, release posts and how-tos from the Abang tools.",
        path="/blog/", content=index, **kw))

    # ---- posts
    for p in posts:
        mins = max(1, round(p["words"] / WPM))
        body = render_md(p["body_md"])
        note = '<p class="draft-note">Draft: not published, not indexed.</p>' if p["draft"] else ""
        content = f"""<main class="blog"><div class="container col"><article>
<a class="back" href="/blog/">&larr; All posts</a>
{note}<header class="post-head">
  {tags_html(p['tags'])}
  <h1>{html.escape(p['title'])}</h1>
  <span class="post-meta"><time datetime="{p['date']}">{p['date'].strftime('%-d %B %Y')}</time> · {html.escape(str(p['author']))} · {mins} min read</span>
</header>
<div class="prose">
{body}
</div>
</article></div></main>"""
        d = blog / p["slug"]
        d.mkdir(parents=True, exist_ok=True)
        (d / "index.html").write_text(page(
            title=f"{p['title']} · Abang", description=p["description"], path=f"/blog/{p['slug']}/",
            content=content, og_type="article", noindex=p["draft"], date=p["date"], **kw))

    # ---- feed, sitemap, robots (published posts only)
    live = [p for p in posts if not p["draft"]]
    e = html.escape
    now = format_datetime(dt.datetime.now(dt.timezone.utc))
    entries = "\n".join(
        f"""<item><title>{e(p['title'])}</title><link>{SITE}/blog/{p['slug']}/</link>
<guid isPermaLink="true">{SITE}/blog/{p['slug']}/</guid>
<pubDate>{format_datetime(dt.datetime.combine(p['date'], dt.time(9), dt.timezone.utc))}</pubDate>
<description>{e(p['description'])}</description></item>"""
        for p in live)
    (blog / "feed.xml").write_text(f"""<?xml version="1.0" encoding="utf-8"?>
<rss version="2.0"><channel><title>Abang blog</title><link>{SITE}/blog/</link>
<description>Engineering notes, release posts and how-tos from the Abang tools.</description>
<language>en</language><lastBuildDate>{now}</lastBuildDate>
{entries}
</channel></rss>
""")
    urls = [f"{SITE}/", f"{SITE}/blog/"] + [f"{SITE}/blog/{p['slug']}/" for p in live]
    (out / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="utf-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(f"<url><loc>{u}</loc></url>" for u in urls) + "\n</urlset>\n")
    (out / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n")
    print(f"built {len(posts)} post(s) ({len(live)} published) into {out}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", type=Path, default=ROOT / "_site")
    ap.add_argument("--drafts", action="store_true", help="also build Draft posts (marked noindex, left out of feed and sitemap)")
    a = ap.parse_args()
    build(a.out, a.drafts)
