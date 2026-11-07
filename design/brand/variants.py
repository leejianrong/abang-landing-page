#!/usr/bin/env python3
"""Derive the logo variants from the master tile icons in svg/.

For every svg/<name>-icon.svg this writes:

  <name>-icon-square.svg   full-bleed square (no rounded corners). Use for avatars and app
                           icons: GitHub, Slack and iOS apply their own rounding, so
                           pre-rounded corners would show as a pale fringe.
  <name>-mono.svg          the glyph alone on a transparent background, one colour
                           (currentColor, defaulting to the product colour). The tile colour
                           and dark features become true holes, so it sits on any background.

The tile icon (<name>-icon.svg) stays the primary mark for favicons and cards.
Standard library only.
"""
import re
from pathlib import Path

SVG = Path(__file__).parent / "svg"
DARK = 0.22  # luminance below which a colour counts as a "feature" (eyes, mouth) and becomes a hole

# Per-mark overrides where the default rule merges shapes that need to stay apart.
#   dark:  luminance threshold for holes     holes: extra colours to cut out
#   color: the mono mark's default colour (defaults to the tile colour)
OVERRIDE = {
    # the light water becomes a gap, so the waterline visibly eats into the head
    "sibei-flow": {"holes": {"#9bd8ee"}},
    # the brim band becomes a gap between hat and face, and the nose a hole
    "vikaki": {"holes": {"#f08a2d", "#1f5f8e"}, "color": "#2b2f3a"},
}


def lum(hexcol):
    h = hexcol.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    return 0.299 * r + 0.587 * g + 0.114 * b


def tile_colour(svg):
    m = re.search(r'<rect width="64" height="64" rx="14" fill="(#[0-9a-fA-F]{6})"/>', svg)
    return m.group(1).lower()


def square(svg):
    # drop the tile's rounded corners, and the matching clip some marks use for bleeding shapes
    svg = svg.replace('<rect width="64" height="64" rx="14"', '<rect width="64" height="64"')
    return svg.replace('<clipPath id="clip-sibei"><rect width="64" height="64" rx="14"/>', '<clipPath id="clip-sibei"><rect width="64" height="64"/>')


def mono(svg, name):
    tile = tile_colour(svg)
    o = OVERRIDE.get(name, {})
    dark, holes, colour = o.get("dark", DARK), o.get("holes", set()), o.get("color", tile)
    body = re.search(r"<title>.*?</title>\n(.*)</svg>", svg, re.S).group(1)
    body = body.replace(f'<rect width="64" height="64" rx="14" fill="{tile}"/>\n', "", 1)

    def recolour(m):
        attr, col = m.group(1), m.group(2).lower()
        hole = col == tile or col in holes or lum(col) < dark
        return f'{attr}="{"#000" if hole else "#fff"}"'

    body = re.sub(r'(fill|stroke)="(#[0-9a-fA-F]{6})"', recolour, body)
    # drop the tile-shaped clip: a mono mark has no tile, so bleeding shapes end at the viewBox edge
    body = re.sub(r'<clipPath id="clip-sibei">.*?</clipPath>\n?', "", body, flags=re.S)
    body = body.replace(' clip-path="url(#clip-sibei)"', "")
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" role="img" aria-label="{name}" '
        f'style="color:{colour}">\n<title>{name}</title>\n'
        f'<mask id="m-{name}" maskUnits="userSpaceOnUse" x="0" y="0" width="64" height="64">\n'
        f'<rect width="64" height="64" fill="#000"/>\n{body.strip()}\n</mask>\n'
        f'<rect width="64" height="64" fill="currentColor" mask="url(#m-{name})"/>\n</svg>\n'
    )


for f in sorted(SVG.glob("*-icon.svg")):
    name = f.name[: -len("-icon.svg")]
    s = f.read_text()
    (SVG / f"{name}-icon-square.svg").write_text(square(s))
    (SVG / f"{name}-mono.svg").write_text(mono(s, name))
    print("wrote", name)
