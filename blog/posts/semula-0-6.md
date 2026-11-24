<!--
title: "semula 0.6: a dashboard you can use on a phone and with the keyboard"
description: What changed in semula 0.6.0, released on 5 November 2026. The dashboard now works on small screens, has keyboard shortcuts, and uses new fonts.
slug: semula-0-6
author: Jian
date: 2026-12-08
status: Draft
tags: [release, semula]
product: semula
sources:
  - semula/CHANGELOG.md
  - semula/pyproject.toml
  - semula/src/semula/dashboard/skip-link.js
  - semula/src/semula/dashboard/phone-layout.js
  - semula/src/semula/dashboard/shell.py
  - semula/src/semula/dashboard/pages/review.py
  - indah/CHANGELOG.md
-->

---

# semula 0.6: a dashboard you can use on a phone and with the keyboard

semula 0.6.0 changes the dashboard and nothing else. It now works on a phone, you can drive it with the keyboard, and the live log shows the newest call first. Recording, replay and the API are the same as in 0.5.1. If you only use the CLI or the API, there is nothing here you need to act on.

## Keyboard use

The first Tab stop on a dashboard page is a "Skip to content" link. It moves focus into the page, so you do not tab through the sidebar first.

The links in the sidebar now show the same 2 px accent ring as every button and field. Before, they used the browser's thin default. The Review and Pending counts in the sidebar are drawn as a badge, and the badge hides when the count is zero.

There are also shortcuts. Press `g`, then one of these keys, to go to a screen:

- `l` for the log
- `e` for entries
- `p` for pending
- `r` for review

On the Review screen, `A` approves the selected near miss and `R` rejects it. Press `?` on any screen to see the list.

## The dashboard on a phone

On a screen under 560 px wide, the dashboard changes in these ways:

- Every button, field, menu and switch is at least 44 px tall.
- Tables turn into cards. Each value is labelled with its column, and the row actions wrap inside the card instead of being cut off.
- The project switcher and the Replay or Record control take the full width.
- The entry editor no longer scrolls sideways, because the long id wraps.
- A review diff opens in the unified layout, with whole words. Split is still one tap away.

The desktop layout is the same as before. The changelog says this part is a stylesheet and a small script that the dashboard serves itself, until indah has its own support for it.

## Live log and connection status

The live log now puts the newest call at the top. A new call lands at the top and the view stays there. This uses the `newest_first` option of indah's table.

The always-on "live" line is gone. While the connection is up, the dashboard shows nothing. If the connection drops, a red dot and "reconnecting…" appear in the top bar next to the theme switch.

## Buttons and fonts

Reject, Delete entry and Delete workspace are now indah's red-outlined danger button, where they were ghost buttons. This makes the ways to throw something away look different from the safe ones.

The page for a person with no workspace, and the page for a suspended workspace, now have a Sign out button. On the Usage screen, Delete workspace stays off until you type the workspace id back.

The dashboard has new type faces: Hanken Grotesk for text (it was IBM Plex Sans), Bricolage Grotesque for headings and IBM Plex Mono for data. Hanken Grotesk is a 35 KB Latin file under SIL OFL 1.1. It ships in the package at `src/semula/dashboard/fonts/` with its licence beside it, and the dashboard serves it from its own origin. The other two were already inside indah's page. No font comes from another host, and the content security policy is unchanged.

## Upgrade notes

semula 0.6.0 depends on indah 0.13 (`indah>=0.13,<0.14` in `pyproject.toml`). It was indah 0.11 before. The changelog says nothing on screen changes from the indah bump alone. It brings the font support, the danger button, the newest-first table and the quiet connection status that the changes above use.

Recordings made with one release open in the next. The changelog's standing note applies: the database upgrades itself on start and cannot be downgraded.

## Read more

The full list is in `CHANGELOG.md` under 0.6.0, in the semula repository at https://github.com/leejianrong/semula. The release is tagged `v0.6.0`.
