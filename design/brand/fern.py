#!/usr/bin/env python3
"""Seeded procedural fern for the fraktal logo.

A frond is one curved spine (the rachis), pinnae branching off it that shrink toward the
tip, and leaflets branching off each pinna. The same seed always draws the same frond,
which is the point: the logo is a fraktal seed.

    python3 fern.py                       # seed 7, writes svg/fraktal-scene.svg
    python3 fern.py --seed 12 --frond-only --out /tmp/frond.svg

Standard library only.
"""
import argparse
import math
import random
from pathlib import Path

# Colours from the fraktal tile (see README.md)
BG, DISC = "#5f7f25", "#6c9030"
SPINE, PINNA, LEAF = "#fbf4e4", "#eef6cf", "#d5ec9a"


def frond(seed, pinnae=13):
    """Return (spine, pinna, leaflet) path-data strings in a 400x400 box."""
    rng = random.Random(seed)
    bx, by, cx, cy, tx, ty = 110, 360, 150, 120, 330, 60  # base, control, tip

    def point(t):
        x = (1 - t) ** 2 * bx + 2 * (1 - t) * t * cx + t * t * tx
        y = (1 - t) ** 2 * by + 2 * (1 - t) * t * cy + t * t * ty
        dx = 2 * (1 - t) * (cx - bx) + 2 * t * (tx - cx)
        dy = 2 * (1 - t) * (cy - by) + 2 * t * (ty - cy)
        return x, y, math.atan2(dy, dx)

    spine = f"M{bx} {by}Q{cx} {cy} {tx} {ty}"
    pinna, leaf = [], []
    for i in range(1, pinnae):
        x, y, a = point(i / pinnae)
        size = 120 * (1 - i / pinnae) ** 0.8 + 10
        for side in (-1, 1):
            ang = a + side * math.radians(62 + rng.uniform(-5, 5))
            length = size * rng.uniform(0.9, 1.05)
            ex, ey = x + length * math.cos(ang), y + length * math.sin(ang)
            mx = x + length * 0.5 * math.cos(ang + side * 0.18)
            my = y + length * 0.5 * math.sin(ang + side * 0.18)
            pinna.append(f"M{x:.0f} {y:.0f}Q{mx:.0f} {my:.0f} {ex:.0f} {ey:.0f}")
            k = max(3, int(length / 13))
            for j in range(1, k):
                u = j / k
                px = (1 - u) ** 2 * x + 2 * (1 - u) * u * mx + u * u * ex
                py = (1 - u) ** 2 * y + 2 * (1 - u) * u * my + u * u * ey
                ll = length * 0.32 * (1 - u * 0.8)
                for s2 in (-1, 1):
                    a2 = ang + s2 * math.radians(64)
                    leaf.append(f"M{px:.0f} {py:.0f}l{ll * math.cos(a2):.0f} {ll * math.sin(a2):.0f}")
    return spine, "".join(pinna), "".join(leaf)


def frond_group(seed, transform):
    spine, pinna, leaf = frond(seed)
    return (
        f'<g transform="{transform}" fill="none" stroke-linecap="round">\n'
        f'<path d="{spine}" stroke="{SPINE}" stroke-width="7"/>\n'
        f'<path d="{pinna}" stroke="{PINNA}" stroke-width="5"/>\n'
        f'<path d="{leaf}" stroke="{LEAF}" stroke-width="3.2"/>\n</g>'
    )


def scene(seed):
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 460 340" role="img" '
        f'aria-label="fraktal: a fern frond generated from seed {seed}">\n'
        f"<title>fraktal (seed {seed})</title>\n"
        f'<rect width="460" height="340" fill="{BG}"/>\n'
        f'<circle cx="250" cy="165" r="132" fill="{DISC}"/>\n'
        f'{frond_group(seed, "translate(70 12) scale(.8)")}\n'
        f'<text x="24" y="318" font-family="ui-monospace, Menlo, monospace" font-size="14" '
        f'fill="{LEAF}">seed {seed}</text>\n</svg>\n'
    )


def frond_only(seed):
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400" role="img" '
        f'aria-label="fern frond, seed {seed}">\n<title>fern frond (seed {seed})</title>\n'
        f'{frond_group(seed, "translate(0 0)")}\n</svg>\n'
    )


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    p.add_argument("--seed", type=int, default=7)
    p.add_argument("--frond-only", action="store_true", help="transparent frond, no tile or disc")
    p.add_argument("--out", type=Path, default=Path(__file__).parent / "svg" / "fraktal-scene.svg")
    a = p.parse_args()
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(frond_only(a.seed) if a.frond_only else scene(a.seed))
    print(f"wrote {a.out}")
