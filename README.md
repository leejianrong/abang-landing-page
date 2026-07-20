# abang-landing-page

The landing page for **Abang** and its first product, **Satay**: a transparent,
durable runtime for AI workflows.

The site is a single self-contained `index.html`. All CSS and JS are inline, there
are no external fonts, scripts, or trackers, and it works in light and dark themes.

## Structure

```
index.html                 the live site (the only file that gets published)
.github/workflows/deploy.yml   builds and deploys to GitHub Pages on push to main
design/                    design explorations and logo options, kept for reference
                           (not deployed)
```

## Deploying

Every push to `main` runs the Pages workflow, which publishes `index.html` only.
`design/` stays in the repo but never goes live.

First-time setup: in the repo's **Settings → Pages**, set the source to
**GitHub Actions**.

## Local preview

It's a static file, so just open it:

```
open index.html      # macOS
xdg-open index.html  # Linux
```
