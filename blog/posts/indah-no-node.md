<!--
title: "A Python UI framework with no Node: shipping a prebuilt frontend"
description: How indah serves a full web UI from one Python package, with one port, no WebSockets and no Node at install or runtime, and what each choice costs.
slug: indah-no-node
author: Jian
date: 2026-11-26
status: Published
tags: [engineering, indah]
product: indah
sources:
  - indah/README.md
  - indah/CHANGELOG.md
  - indah/pyproject.toml
  - indah/docs/POSITIONING.md
  - indah/docs/adr/0001-single-port-asgi-app.md
  - indah/docs/adr/0002-sse-plus-post-transport.md
  - indah/docs/adr/0003-reactive-signals-model.md
  - indah/docs/adr/0004-svelte-prebuilt-shell.md
  - indah/docs/adr/0042-extras-and-size.md
  - indah/docs/size-budget.json
  - indah/scripts/cleanroom.sh
  - indah/Makefile
-->

---

# A Python UI framework with no Node: shipping a prebuilt frontend

indah is a Python library for building small web UIs, and it is made for cloud notebooks such as Colab and Runpod. You install it with `pip`, write a Python file, and get a page in the browser, with no Node, npm or bun anywhere. This post explains the four design choices that make that work, and for each one, the problem that forced it. It also lists what we gave up.

The measurements below come from the architecture notes in the repository (ADR-0042) and were taken at the dates they give. The size limits are the current ones from `docs/size-budget.json`.

## The notebook constraint

A Colab or Runpod session is short-lived. When it ends, the machine is gone, so every new session starts with a clean install. That has two effects on a UI framework. Install time counts every time, and you cannot count on a JavaScript toolchain being there. Some frameworks build their frontend when you first run them. In a fresh container that step is slow, and it fails if the container cannot reach npm or GitHub. Our positioning notes say Reflex works this way, and that this is the failure indah was built to avoid. We have not re-tested Reflex ourselves.

There is a second limit. Both platforms show you your server through a proxy that exposes one port. ADR-0002 records that Colab's proxy does not support WebSockets. So the design has to work with one port and plain HTTP, and the frontend has to arrive ready to run.

## One port, one ASGI app

ASGI is the standard Python interface for async web servers. indah is one ASGI app (Starlette, run by Uvicorn) on one port. The same app serves the frontend files and all the live traffic, which lives under `/api/*` ([ADR-0001](https://github.com/leejianrong/indah/blob/main/docs/adr/0001-single-port-asgi-app.md)).

The ADR names the alternative we rejected: a separate frontend server and backend server, as Reflex does with Next.js and FastAPI. A second port cannot be reached through the Colab or Runpod proxy. Serving everything from one origin also means there is no CORS to configure (the browser rule about calling other origins).

The cost is that you cannot scale the frontend and the backend on their own. The ADR calls that acceptable for a notebook tool, and we agree. If you need to scale them separately, you want a different tool.

`launch()` finds out whether it is running in Colab, Runpod or locally, and prints or embeds the right URL. This is a complete app from the README:

```python
import indah
from indah import Signal, computed, Column, Slider, Text, Session

a, b = Signal(2), Signal(3)
total = computed(lambda: f"a + b = {a.value + b.value}")

page = Column(
    children=[
        Slider(a, min=0, max=10, label="a"),
        Slider(b, min=0, max=10, label="b"),
        Text(total),
    ]
)

indah.launch(
    indah.create_app(session=Session(page))
)  # prints the URL; embeds inline in Colab/Runpod
```

## Server-sent events and POST

With no WebSockets, the live connection has to be something else. [ADR-0002](https://github.com/leejianrong/indah/blob/main/docs/adr/0002-sse-plus-post-transport.md) picks two plain HTTP pieces. Server-sent events (SSE) carry updates from the server to the browser over one long-lived `GET /api/stream`. A normal `POST /api/event` carries clicks and input from the browser to the server.

The ADR gives these reasons. Both pieces pass the Colab and Runpod proxies with no extra dependency. The other option on Colab was a WebSocket plus a Cloudflared tunnel, which adds a binary and a slower start. And SSE suits streaming text token by token, which is most of what an AI demo does. indah still tries a WebSocket upgrade when the platform allows it, and uses it only where it works.

The ADR also lists what this costs. The channel is not truly two-way, so fast input such as a dragged slider needs debouncing (waiting a moment before sending). The server also has to send a heartbeat and the browser has to reconnect on its own, because Runpod's proxy has a 100 second timeout.

The real run on Colab found one more problem. The ADR's "real-hardware note" says Colab's proxy holds back a response until a fixed-size block fills, and ignores the usual header that turns buffering off. A small update just sat there, and the page stayed on "connecting...". The fix is to pad each frame with ignored SSE comment text so the block fills and the proxy lets it through. The padding first cost about 8 KB per frame, which is a lot when you stream tokens. The server now sends a burst of queued frames together and pads once, and it pads only up to the next block boundary. A single small update still costs about one block, and the ADR says that cannot be avoided with this kind of proxy. A test in `tests/e2e/test_proxy_buffering.py` reproduces the buffering locally so it cannot come back unnoticed.

## Signals instead of reruns

The model is a small part of the pitch but it matters for the transport. [ADR-0003](https://github.com/leejianrong/indah/blob/main/docs/adr/0003-reactive-signals-model.md) chose signals: named values you bind to components. The core records which components and handlers read each signal. When a handler changes one, only those dependents are recomputed, and the server sends a small set of JSON patches addressed by component ID. Your script is not run again from the top, which is what Streamlit does on every interaction.

For notebooks this keeps each message small, and that fits SSE, where every message has a cost. It also lets state live in memory between interactions. The ADR is open about the risk. The dependency graph and the patch logic are the part most likely to break, and a wrong patch corrupts the UI without any error. So that code has the most unit and end-to-end tests.

## The prebuilt Svelte shell

The browser side is a Svelte app, which we call the shell. [ADR-0004](https://github.com/leejianrong/indah/blob/main/docs/adr/0004-svelte-prebuilt-shell.md) says it is built in CI and bundled as static files inside the Python wheel. Building the wheel needs Node, but installing and running it never does. Svelte compiles to small direct DOM updates with no virtual DOM at run time, which suits a renderer that applies many small patches.

The ADR admits the price: React has a much bigger ecosystem of ready-made components, so early indah components were built by hand. Because users never see the shell, we could change framework later, and the JSON protocol is the stable boundary that would make that survivable.

We test the "no Node" claim. `make cleanroom` builds the wheel and installs it into a throwaway virtual environment. In that environment `node`, `npm`, `npx`, `bun`, `yarn`, `pnpm`, `vite`, `svelte` and `esbuild` are fake commands that log a call and exit with an error. The script fails if any one of them runs, at install or when the app starts and serves the shell.

### Keeping the size down

A frontend shipped ahead of time is a download on every first page load, so size needs a limit. [ADR-0042](https://github.com/leejianrong/indah/blob/main/docs/adr/0042-extras-and-size.md) records what we measured on 2026-10-23, at version 0.6.0 plus later merges. The wheel was 555,280 bytes. The shell was 569,673 bytes raw and 239,950 bytes gzipped. The base install pulls in 13 packages including indah, and most of its disk weight is `pydantic`, not our code.

Three tools came out of that ADR:

- Extras keep third-party libraries out of the base install. `pip install "indah[plot]"` adds matplotlib, and there are `data`, `redis`, `live`, `demos` and `all` as well (see `pyproject.toml`). indah does not import them unless you use the feature. The ADR is honest that an extra only adds packages and cannot shrink the wheel or the shell.
- Lazy modules are first-party scripts that the shell fetches the first time a component needs them. The code editor (`editor.js`), the map (`map.js`) and the graph (`graph.js`) work this way. An app that never shows a map never downloads Leaflet.
- A size budget, `docs/size-budget.json`, sets a maximum for the wheel, the shell, each lazy module and the dependency counts. CI runs `scripts/size_report.py` against it and fails the build when a number goes over. Each limit is about 15 percent above the measured value, and a pull request that needs more room must raise the limit in the same diff and say why.

Moving the map out of the shell is the clearest case, and it was measured. The shell went from 581,046 to 428,605 bytes raw, and from 243,354 to 199,839 gzipped. The ADR also measured the cost on a slow 4G profile (median of five runs). A page without a map loaded 0.94 seconds faster, and a page with a map took 0.23 seconds longer. We left the chart library (uPlot) in the shell because it is small, 23.8 KB gzipped, and charts are common.

Today the budget allows 231,000 bytes of gzipped shell and 645,000 bytes of wheel.

## What you give up

- One process, one port. You cannot scale the frontend and backend apart.
- A lot of first-page weight compared with a tiny page. The shell is a few hundred KB even for a hello-world app. indah itself sends no compression header, so unless a proxy in front compresses it, the browser downloads the raw file. ADR-0042 saw 270,534 bytes through Fly's edge and 240,877 bytes through a Cloudflare Worker. It did not measure Colab's or Runpod's proxies.
- A smaller component ecosystem than React or Streamlit. If a component you need is missing, you can register a custom one against the JSON protocol, but you will be writing a render spec, not dropping in a package.
- Heavy reliance on SSE behaviour. The Colab buffering bug shows that proxies can surprise you, and we only know about the ones we have tested.
- No speed comparison. We have not measured indah against Streamlit, so we make no speed claim. The claim is about how often the server does work, not how fast.

The project is also young. The classifier in `pyproject.toml` says Beta, and the version is 0.x, so a minor release may change behaviour (the CHANGELOG lists each such change).

## Try it

Install with `pip install indah`, or `pip install "indah[all]"` for the plotting and data extras. To see everything running, open the [live demo gallery](https://indah-demos.fly.dev) (no install). Or run it from a clone:

```bash
git clone https://github.com/leejianrong/indah && cd indah
uv sync --extra dev
make demo
```

`make demo` starts the indah Studio and prints a URL. The docs are at [indah.abangai.dev](https://indah.abangai.dev/docs/).
