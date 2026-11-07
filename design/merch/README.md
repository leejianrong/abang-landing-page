# Abang tee designs

Print files for the indah and semula tees. Each design is a small mark for the left chest and a large
illustration for the back, in a light and a dark colourway (the colours come from each product's own
light and dark theme).

| Design | Shirt | Back | Chest |
|---|---|---|---|
| indah light | natural `#efe6d6` | `png/indah-back-light.png` | `png/indah-chest-light.png` |
| indah dark | dark plum `#191319` | `png/indah-back-dark.png` | `png/indah-chest-dark.png` |
| semula light | natural `#efe6d6` | `png/semula-back-light.png` | `png/semula-chest-light.png` |
| semula dark | ink green `#14201B` | `png/semula-back-dark.png` | `png/semula-chest-dark.png` |

## Print specs

- Back: 4500 x 5400 px (indah) and 4500 x 6300 px (semula, taller to leave room for the critter), transparent
  PNG. At 12 in wide that is 375 effective DPI, at 15 in wide 300. 15 x 21 in is beyond some providers' print
  area, so check semula's against the provider's maximum before ordering.
- Left chest: 1500 x 1500 px, transparent PNG. The mark fills about 1200 px, so it prints about 4 in wide
  at 300 DPI.
- Flat solid colours only, no gradients or semi-transparent effects. Dark shirts need a white underbase
  and soft edges print badly, so this is deliberate.
- The sources print text as live type. The PNGs have the fonts rendered in (Bricolage Grotesque, Hanken
  Grotesk, IBM Plex Mono).
- Confirm the maximum print area for the exact shirt on the print provider's File guidelines tab before
  ordering. Providers differ (roughly 12 x 16 to 15 x 18 in for the back) and order a sample first.

## Files

- indah's back: the same four-petal mark as the chest, large and centred, with the wordmark and "Beautiful
  designs with Python" under it. Labelled interface elements ring it (chart, graph, heatmap, chat), and
  bars and a table sit in a bottom row. The table's left edge lines up with the middle of the mark.
- semula's back: a two-bubble chat ("Still paying for LLM credits?" / "Try semula"), the loop mark centred,
  the wordmark, "Let Claude answer your LLM API calls", and a critter on a rotary phone, off
  centre to the right. The critter's orange (`--cl`) is the only colour outside semula's palette.
- `src/`: one SVG per design with CSS variables and a `way-light` class.
- `build_merch.py`: stamps `svg/<name>-light.svg` and `svg/<name>-dark.svg` from `src/`.
- `png/`: the print files, rendered from `svg/` in Chromium with fonts loaded, transparent background,
  back at 4.5x and chest at 1x.

```bash
python3 build_merch.py
```

The SVGs reference web fonts, so open them in a browser with network access, or outline the text in
Inkscape or Figma before sending them to anyone who has not got the fonts.

## Placeholder critter and the private build

semula's back is meant to carry the Claude Code mascot, which is Anthropic's trademarked artwork, so the
committed files use a generic placeholder critter instead. The real one lives in `private/`, which is
gitignored:

- `private/critter.svgfrag`: the mascot group that replaces the placeholder.
- `python3 build_merch.py --private` writes the real-critter SVGs to `private/svg/`.
- Export PNGs from `private/svg/` into `private/png/` the same way as for `svg/` and `png/`.

Order the shirt from `private/png/`. Do not commit anything under `private/`.
