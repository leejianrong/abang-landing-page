<!--
title: "indah 0.16: a timeline, graphs that keep their place and more chart types"
description: What is new in indah 0.16, released on 24 November 2026, and what was added over the weeks before it. You can step through time with a Timeline, style and animate a Graph, and draw stacked bars, box plots and chart hover events.
slug: indah-0-16
author: Jian
date: 2026-12-10
status: Draft
tags: [release, indah]
product: indah
sources:
  - indah/CHANGELOG.md
-->

---

# indah 0.16: a timeline, graphs that keep their place and more chart types

indah 0.16 is about time and graphs. You can now step through a series of moments with a `Timeline`, change how a `Graph` looks from one moment to the next without it jumping around, and read hover and click events from a `Chart`. Everything in this release is opt-in, so an existing app behaves as it did before, with one small change to `Slider` described below. This post also covers the larger additions from the weeks before it.

## Timeline and graphs

`Timeline(value, points, labels=, density=, unit=, playing=, speed=)` steps through the moments that exist, however irregular they are (years now, days later). It has previous and next buttons, play and pause at 0.5, 1, 2 or 4 steps a second, and a range track you can use with the arrow keys. A screen reader hears something like "year 2003, step 4 of 11". Play is capped at 4 steps a second so that a hosted app on `Rate(per_second=5)` keeps working controls.

A `Graph` can now be styled per node and per edge. A node takes `ring`, `opacity` and `label_style` (`"strike"` or `"bold"`), and an edge takes `dash`, `opacity` and `width`. With `Graph(directed=True, layout="layered")` you get arrowheads and a top-to-bottom layout for a DAG, and a node can have a `shape` (`"circle"`, `"square"` or `"diamond"`) so that a state does not rely on colour alone.

Three options keep a graph steady while it changes:

- `layout="stable"` places nodes from their ids and edges only, so changing a style never moves a node. It is opt-in, and `"auto"` still clusters by group.
- `Graph(update="keep")` keeps the position of every id that already existed, along with the viewer's pan and zoom.
- `Graph(frames=, frame=)` takes a base graph plus a few style patches per frame, and a `Timeline(link=graph)` steps through them in the browser, so playing sends no events to the server.

## Charts

`Chart(hovered=, clicked=)` gives you two `Signal`s that report the point or bar under the pointer. Nothing is sent unless you bind one. The chart also gains stacked bars (`stack=True`), horizontal bars (`orientation="horizontal"`) and a box series (`kind="box"`), with `indah.box_rows(samples)` to summarise raw samples into the rows it needs. A `Chart` no longer rebuilds its plot on every patch, so moving a playhead or a threshold keeps the viewer's zoom.

## New components

- `Sparkline` and `TickStrip`: a small trend line and a row of pass and fail ticks. A failed tick is taller, so it does not rely on colour.
- `Spans`: nested labelled intervals as a flame chart, an icicle chart or a timeline. It is drawn with plain elements and is fine up to about 5,000 spans.
- `Svg`: an inline SVG drawing for generated diagrams. Python checks the markup against an allowlist before it is sent, so there are no scripts, event handlers or outside references.
- `ChoiceCards`: a radio group where each option is a card with a title and a sentence of explanation.
- `Slider` bounds and `Badge(tone=)` can now follow a `Signal`, a `Computed` or a callable.

## Earlier this month

`DirectUpload` sends a file from the browser straight to a presigned URL with a progress bar, so the indah server never holds the bytes. `ImageOverlay` can draw clickable rectangles and polygons in the picture's own pixels, and `Steps(on_select=fn)` can work as a stepper.

## Upgrade notes and limits

A `Slider` whose `min` or `max` is live now clamps its value when the range moves past it. Before, the thumb showed one value while the signal held another. A fixed range behaves as before.

A few limits are written down in the changelog. `Graph(update="keep")` does not ease positions, so kept nodes stay put and new ones appear already placed. A horizontal `Chart` supports bars and a category axis only, with no overlays. The size budgets also rose again for these additions, and the changelog lists the new limits.

The full list, with the issue numbers, is in `CHANGELOG.md` in the indah repository at https://github.com/leejianrong/indah.
