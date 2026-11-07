#!/usr/bin/env python3
"""Stamp the light and dark colourways of each print design from src/ into svg/.

    python3 build_merch.py

A design in src/ is written once with CSS variables and a `way-light` class on the root.
This copies it to svg/<name>-light.svg and svg/<name>-dark.svg with the matching class.
Standard library only. PNG export is a separate step (see README.md).
"""
from pathlib import Path

HERE = Path(__file__).parent
(HERE / "svg").mkdir(exist_ok=True)
for src in sorted((HERE / "src").glob("*.svg")):
    text = src.read_text()
    assert 'class="way-light"' in text, f"{src.name}: root needs class=\"way-light\""
    for way in ("light", "dark"):
        out = HERE / "svg" / f"{src.stem}-{way}.svg"
        out.write_text(text.replace('class="way-light"', f'class="way-{way}"', 1))
        print("wrote", out.relative_to(HERE))
