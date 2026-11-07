# Brief 05: indah

- slug: `indah-no-node`
- working title: A Python UI framework with no Node: shipping a prebuilt frontend
- tags: engineering, indah   product: indah   length: 1,400 to 1,800 words
- launch order: 5

## Angle
indah is built for ephemeral cloud notebooks (Colab, Runpod), where install time and a missing Node
toolchain are real constraints. The design follows from that: one port, a frontend built ahead of time,
no Node at install or runtime. Explain each choice by the constraint that forced it.

## Reader
A Python developer who builds small UIs for notebooks and has hit Streamlit's limits or a Node install.

## Outline
1. The notebook constraint.
2. One port, one ASGI app. ADR-0001.
3. Server-sent events plus POST for the transport. ADR-0002 (state the reasons the ADR gives).
4. A reactive model of signals. ADR-0003.
5. The prebuilt Svelte shell, and how its size is budgeted. ADR-0004, ADR-0042 and `docs/size-budget.json`.
6. What you give up compared with a full-stack app.
7. Try it: install and the live demo gallery.

## Read first
`indah-python-ui/README.md`, `indah-python-ui/docs/POSITIONING.md`, `docs/adr/0001`, `0002`, `0003`,
`0004`, `0042`, `docs/size-budget.json`, `indah-python-ui/CHANGELOG.md`.

## Verify in the source
Package and extras names, the install line, the demo gallery URL, current version.

## Do not
Compare benchmark speed with Streamlit unless a file in the repo measures it.
