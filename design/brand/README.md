# abang-ai brand marks

Master SVGs for the suite. A logo's background belongs to where it is used, so each product ships
as a set of variants (below). Every product also has two tiers:

- **Tier 1, `svg/<name>-icon.svg`**: a 64x64 rounded-square tile with a solid glyph. Works at 16px, in one
  colour and on dark grounds. Use for cards, docs headers and lockups.
- **Tier 2, `svg/<name>-scene.svg`**: a 460x340 illustration for hero sections and the back graphic of
  t-shirts. `abang-ai` has no scene; the ketupat is the umbrella mark.

## Variants (in `svg/`)

| File | Use |
|---|---|
| `<name>-icon.svg` | Primary mark: rounded tile. Product cards, docs headers, in-app icons. (Browser favicons use a bare transparent glyph; see the landing page `AGENTS.md`.) |
| `<name>-icon-square.svg` | Full-bleed square, no rounded corners. Avatars and app icons (GitHub, Slack and iOS round it themselves). |
| `<name>-mono.svg` | Glyph only on a transparent background, one colour via `currentColor` (defaults to the product colour). Sits on any background; set `color` to recolour. |
| `<name>-scene.svg` | Tier 2 illustration. |

`variants.py` derives the square and mono files from the tile icons, with per-mark overrides for the
two that need help (sibei-flow keeps a gap at the waterline, vikaki keeps its hat separate from the
face). Re-run it after editing a master icon:

```bash
python3 variants.py
```

Not done yet: horizontal and stacked wordmark lockups as files (they need the wordmark converted to
outlines so they render without the font).

## Rules the set follows

- Solid flat shapes only. No outlines, gradients, glow or texture in the masters (add grain at export).
- One tile colour per product, a cream glyph (`#fbf4e4`) and at most one accent.
- Scenes put a large soft disc behind the subject and use the tile colour as the ground.
- Check every new mark at 48, 32 and 16px, in one colour, and on a dark ground before adding it.

## Palette

| Product | Tile | Accent |
|---|---|---|
| abang-ai | `#de5f1c` | |
| sibei-flow | `#1f6f9b` | `#c98b52` capybara, `#9bd8ee` water |
| kampong-agents | `#2f7a55` | |
| kopicode | `#5a3622` | `#c98f5c` coffee |
| cuttlefish-crew | `#6b4fa0` | `#e3d6bd` fins |
| satay | `#3a3036` | `#f0a93c`, `#d98a24` |
| vikaki | `#f4c13d` | `#2c7fb8` beanie |
| fraktal | `#5f7f25` | `#d5ec9a` leaves |

indah and semula keep their existing marks (`indah/assets/brand/`, `semula/docs/design/logo/`).
tingkat is deliberately not part of the set.

## The fraktal frond

`svg/fraktal-scene.svg` is generated, not drawn. `fern.py` builds a curved spine, pinnae that shrink
toward the tip and leaflets on each pinna, from a seed. The same seed always gives the same frond.

```bash
python3 fern.py                                          # seed 7, rewrites svg/fraktal-scene.svg
python3 fern.py --seed 12 --frond-only --out frond.svg   # transparent frond only
```

Standard library only. Edit the palette constants at the top of the script to recolour.

## Notes

- The vikaki mascot is redrawn flat from the "Snowy" persona. It is not the CC0 Snowy VRM model.
- The marks are hand-built SVGs. For print production, trace or refine silhouettes in Inkscape or Figma.
