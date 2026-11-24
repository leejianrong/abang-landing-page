<!--
title: "Launch a Python dashboard from a Colab cell with indah"
description: Install indah in a Colab cell, write a small app with sliders and a button, launch it, and see it appear inside the notebook.
slug: tutorial-indah-colab
author: Jian
date: 2026-12-06
status: Draft
tags: [tutorial, indah]
product: indah
sources:
  - indah/README.md
  - indah/pyproject.toml
  - indah/website/docs/quickstart.md
  - indah/website/docs/components.md
  - indah/website/docs/gallery.md
  - indah/docs/adr/0002-sse-plus-post-transport.md
  - indah/src/indah/launch.py
  - indah/examples/colab/chatbot.ipynb
  - indah/examples/colab/sorting.ipynb
-->

---

# Launch a Python dashboard from a Colab cell with indah

In this tutorial we build a small interactive page in a Colab notebook with indah, a Python library for web UIs. It takes two cells: one to install indah and one to define and launch the app. Then we add a button. The page shows up inside the notebook, with no Node, no npm and no second server to start. Why indah can work this way is covered in [another post](/blog/indah-no-node/), so we skip it here.

You need a Colab notebook and nothing else.

## What we are building

The app has two sliders, called `a` and `b`, and one line of text that shows their sum. Move a slider and the text changes. It is the first app in the indah quickstart, and we use it because it is short enough to read in one go.

The app is made of three ideas:

- A signal is a value that the page watches. When it changes, the parts of the page that use it update.
- A component is a piece of the page, such as a slider or a line of text.
- A computed value is one that is worked out from signals, and is worked out again when they change.

## Install in a fresh cell

A new Colab session starts with a clean machine, so the first cell installs indah. The Colab notebooks in the indah repo (`examples/colab/`) all start with this cell:

```python
# Install indah from PyPI (plus any demo extras).
!pip install -q "indah"
```

The `!` tells Colab to run the line in a shell. The quickstart gives the plain command, `pip install indah`. indah has no Node step because the frontend is already built and packed inside the package.

We ran `pip install indah` into a clean Python 3.12 environment on a laptop (not in Colab). It installed the latest release on PyPI at that time. The repository may be ahead of what you get from `pip`. We did not run the install cell inside Colab itself.

## The single Python file

Put this in the next cell. It is the "Your first app" example from the quickstart, copied as it is:

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

indah.launch(indah.create_app(session=Session(page)))
```

Here is what each part does.

`a, b = Signal(2), Signal(3)` makes two signals with starting values 2 and 3. You read one with `.value` and set one with `.set(...)`.

`total = computed(...)` builds the text from `a` and `b`. indah notes that the function reads both signals, so it runs the function again only when one of them changes.

`Column(children=[...])` stacks its children from top to bottom. Each `Slider` is tied to one signal, with a minimum, a maximum and a label. `Text(total)` shows the computed value.

`Session(page)` holds the page, and `indah.create_app(...)` wraps the session in a web app. Last, `indah.launch(...)` starts that app.

## Launch it and read the output

Run the cell. `launch()` finds a free port, starts the server, and prints one line:

```text
indah is running at http://127.0.0.1:8001
```

That is the line we got when we ran this same file as a script on a laptop. On Colab the address is the one Colab's proxy gives you, so it will differ. We could not check what it looks like on Colab, and we do not guess it here.

What the repo does document is this. In a notebook, `launch()` starts the server on a background thread, so the cell finishes instead of waiting. It also shows the app inline, in the cell's output, as an iframe (a page inside the page). On Colab it binds all network interfaces so that Colab's proxy can reach the app. As a plain script, the same call blocks until you stop it.

Colab's proxy does not carry WebSockets. ADR-0002 in the indah repo says this is why indah sends updates with server-sent events and takes input with ordinary POST requests. You do not need to set anything up for it.

Drag a slider. The text under it changes, and only the text is updated, not the whole page.

## Add an interaction with a signal

A slider is one way to change a signal. A button is another. This example is from the indah components docs ("Buttons and async handlers"):

```python
from indah import Button, Signal, Text, Column

count = Signal(0)


def bump():
    count.set(count.value + 1)


page = Column(
    children=[
        Button("Add one", on_click=bump),
        Text(lambda: f"count = {count.value}"),
    ]
)
```

When you press the button, indah calls `bump`. It sets `count` to one more than it was, and the `Text` that reads `count` updates.

The docs show only the page. To run it in a cell, we added the imports and the launch line from the quickstart, so the cell looks like this:

```python
import indah
from indah import Button, Signal, Text, Column, Session

count = Signal(0)


def bump():
    count.set(count.value + 1)


page = Column(
    children=[
        Button("Add one", on_click=bump),
        Text(lambda: f"count = {count.value}"),
    ]
)

indah.launch(indah.create_app(session=Session(page)))
```

We ran this version as a script on a laptop and the page loaded (HTTP 200). We did not click the button in a browser.

To keep the sliders and the button on one page, put all of their components in the same `Column`.

## What we left out

The indah docs say little about Colab itself. They show that `launch()` works in a cell, and they show the install cell. They do not describe the Colab address, a recommended runtime type or how to fix a blank frame. So we have not covered those.

indah is at 0.x and marked Beta in `pyproject.toml`, so some behaviour may change between minor versions. The CHANGELOG lists each change.

## Where to go next

The [demo gallery](https://indah-demos.fly.dev) runs every demo in your browser with no install, and the README links an "Open In Colab" badge for each one. The notebooks are a good way to see bigger apps. The streaming chatbot is walked through step by step in the docs under [Build a chatbot](https://indah.abangai.dev/docs/chatbot/), and the rest of the docs are at [indah.abangai.dev](https://indah.abangai.dev/docs/).
