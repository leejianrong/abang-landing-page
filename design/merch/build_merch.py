#!/usr/bin/env python3
"""Stamp the light and dark colourways of each print design from src/ into svg/.

    python3 build_merch.py            # committed build, placeholder critter -> svg/
    python3 build_merch.py --private  # local build, real critter from private/ -> private/svg/

A design in src/ is written once with CSS variables and a `way-light` class on the root.
This copies it to <out>/<name>-light.svg and <out>/<name>-dark.svg with the matching class.
semula's back has a placeholder critter between `critter:start` and `critter:end` comments;
--private swaps in private/critter.svgfrag, which is gitignored. Standard library only.
PNG export is a separate step (see README.md).
"""
import re
import sys
from pathlib import Path

HERE = Path(__file__).parent
private = "--private" in sys.argv
out_dir = HERE / ("private/svg" if private else "svg")
out_dir.mkdir(parents=True, exist_ok=True)

frag = None
if private:
    frag_file = HERE / "private" / "critter.svgfrag"
    if not frag_file.exists():
        sys.exit(f"missing {frag_file.relative_to(HERE)}; --private needs the local critter fragment")
    frag = frag_file.read_text()

for src in sorted((HERE / "src").glob("*.svg")):
    text = src.read_text()
    assert 'class="way-light"' in text, f"{src.name}: root needs class=\"way-light\""
    if frag is not None:
        text = re.sub(r"( *<!-- critter:start.*?-->\n).*?( *<!-- critter:end -->)",
                      lambda m: frag, text, flags=re.S)
    for way in ("light", "dark"):
        out = out_dir / f"{src.stem}-{way}.svg"
        out.write_text(text.replace('class="way-light"', f'class="way-{way}"', 1))
        print("wrote", out.relative_to(HERE))
