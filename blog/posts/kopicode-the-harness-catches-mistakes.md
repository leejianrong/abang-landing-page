<!--
title: "Cheap models can code if the harness catches their mistakes"
description: How kopicode catches the mistakes cheap coding models make, what each check does, and how much of the idea we have measured so far (not much, and we say how much).
slug: kopicode-the-harness-catches-mistakes
author: Jian
date: 2026-11-26
status: Draft
tags: [engineering, kopicode]
product: kopicode
sources:
  - kopicode/README.md
  - kopicode/docs/adr/0005-benchmark-and-ab-methodology.md
  - kopicode/docs/adr/0006-hash-anchored-edits-and-failure-attribution.md
  - kopicode/docs/adr/0007-model-selection-and-harness-config-shape.md
  - kopicode/docs/adr/0012-context-compaction-strategy.md
  - kopicode/docs/adr/0028-stall-detector.md
  - kopicode/docs/adr/0033-tool-output-cap.md
  - kopicode/docs/adr/0042-verify-only-a-changed-tree.md
  - kopicode/docs/paired-ab-qwen-vs-minimax-m2-v2.md
  - kopicode/docs/paired-ab-qwen-default-vs-naive-v1.md
  - kopicode/docs/paired-ab-qwen-default-vs-naive-v1-repeats.md
  - kopicode/docs/trying-kopicode.md
  - kopicode/bench-results/ (all four directories, eight JSON files)
  - kopicode/internal/harness/registry.go
  - kopicode/internal/harness/harness.go
  - kopicode/internal/parse/repair.go
  - kopicode/internal/syntax/registry.go
  - kopicode/scripts/install.sh
-->

---

# Cheap models can code if the harness catches their mistakes

kopicode is a terminal coding agent built on one bet: the code around a model (the prompt, the tools, the checks after each step, which we call the harness) changes how well it codes more than which model you pick. We think this is most true for cheap open-weight models, because nobody tunes a harness for them. This post describes the four checks kopicode puts around a model, shows what each one catches, and says how much of the bet we have tested. As of v0.5.0 the honest answer is that it is a thesis under test, not a result.

## How a cheap model fails in a coding loop

The failures we see are small and repeat often. We can point to four.

The model writes a tool call that is not valid. The JSON is broken, or the tool name does not exist. A plain agent loop wastes the turn on this.

The model edits the wrong place. Most agents ask the model to retype the old text it wants to replace. A weak model gets a space or a line wrong, and then either the edit fails or a fuzzy matcher lands it somewhere that looks close enough. The second case is worse, because it reports success. ADR-0006 puts it this way: a harness bug gets counted as a model mistake.

The model repeats itself. In one recorded session (a JavaScript bug in `bytes.js`) the fix was right and verified by round trip 9 of 22. The other 13 round trips were the model retrying a command that had already been refused, which grew the prompt by about 16% and added nothing (ADR-0012).

The model says it is done without checking. We have a clean example from the benchmark. With forced checking switched off, one task ended at the 20-turn limit in the middle of a multi-file edit, after a single test run that came before the fix existed. The edits themselves looked sound. Nothing told the model to check again.

Each of the next four sections is one answer to one of these.

## Repairing tool calls

When a call is malformed, kopicode does not throw the turn away. It tries three ways to read a call (the model's native tool-call format, JSON inside a fenced code block, and an XML-style tag), and if none works it sends the model a specific error and lets it try again. The default harness config sets `ParseRoutes` to `native`, `fenced_json` and `xml_tag`, and `RepairBudget` to 2. After two failed repairs the call fails and the turn goes on with the failure shown to the model (`internal/parse/repair.go`).

This is the mechanism we have the least direct evidence for. The code counts parse outcomes in the journal, so the repair success rate can be read from a session. We have not published that rate, and we do not claim one here.

## Edits that reject instead of guess

In kopicode the model never retypes the old text. `read_file` gives every line a short anchor, and `edit_file` takes an anchor for the start and end of the region plus the new text. This is the format from ADR-0006:

```
a3f21b09   1| package main
5c0e77d2   2|
9b2d4a10   3| import "fmt"
```

An anchor is the first 8 hex characters of a SHA-256 hash of the line and the lines on either side of it. If the file has changed since the model read it, the anchors no longer match, and the edit is rejected with the current anchors for that region. Because anchors only come from a read, the model cannot edit a region it was never shown.

The neighbouring lines are in the hash for a reason we measured. Over the Go standard library (2.03 million lines), 40.4% of lines have the same text as another line in the same file, and `}` and blank lines are the usual cases. Hashing the line alone would make a third of a file ambiguous. Adding one line of context on each side drops that to 12.1% of lines, and to 1.9% in the median file. Wider windows help more, but then any edit makes more nearby anchors stale, and a rejection on anchors the model read a moment ago is confusing for a weak model. So the window stops at one line and the rest is handled by refusing an ambiguous anchor.

There is one fallback. If a model cannot produce a usable anchor, a fuzzy match is allowed, and any session that used it and then failed is filed as `unattributed`, not as a model failure. That makes the harness look worse than it may be, which is the direction we chose to be wrong in.

## The syntax check and forced verification

After every edit kopicode runs the language's own checker. In `internal/syntax/registry.go` that is `gofmt -e` (then `go build` as advice) for Go, `python -m py_compile` for Python and `node --check` for JavaScript. ADR-0006 also lists `tsc --noEmit`, but we only confirmed the first three in the code. A failure straight after an edit is a clear sign the edit itself went wrong, so it is easy to spot and cheap to fix.

The second check is the one the README leads with: kopicode will not report success until the project's own tests pass. After a turn that changed things, it runs the tests and tells the model if they fail. In the first walkthrough in `docs/trying-kopicode.md` (a Go bug in `go-humanize`), the model's first attempt failed that check and it corrected itself before reporting done.

This check has a cost, and we found it in our own logs. Any turn that ran a shell command was verified, even a plain `ls`. In a repository whose tests already failed, a request to run `ls` sent the model a message saying its change was unfinished. With the opt-in `--verify-changed-only` switch off, 10 of 10 sessions went off task and edited an unrelated file. With it on, 0 of 10 did on qwen, and 3 of 10 did on `deepseek/deepseek-v3.2`. But the same switch missed a wrong file written into a git-ignored directory in 10 of 10 sessions, so it is not the default (ADR-0042 and the two runs the README links). These are small scenarios, one to three tiny repositories, and they show what a switch does, not how often.

A smaller guard sits beside these. A stall detector (ADR-0028) notices when the model repeats the same call with the same result three times, or fails three edits to one file with nothing written in between, and tells it to try something else. It is on in the REPL and has not been measured on the corpus. The ADR says so.

## How we measure

ADR-0005 starts from a sample size problem. With 20 tasks and a pass rate near 40%, the 95% confidence interval on one score is about plus or minus 21 percentage points, which is as big as the effect we want to detect. So every comparison runs two arms over the same tasks and looks only at the tasks where they disagree. An arm is a model, a harness config and a provider pin together (ADR-0007).

The pin matters as much as the pairing. OpenRouter spreads requests over providers that serve different quantizations (smaller, cheaper versions of the same weights), so "the same model" can be different weights from one request to the next. Every benchmark request names one provider with fallbacks off, for example `parasail/bf16` for qwen, and a result with a different pin is thrown away. The other rules are plain ones: pass or fail comes from unit tests and not from a model acting as judge, the corpus is our own small repositories, and every result must say what was dropped. The harness itself is tested against a mock provider that replays recorded traffic, so `make bench-smoke` costs nothing.

## What the numbers say so far

The 13-task corpus is at version 2.0.0, and we first made it harder because the earlier 10-task version gave 10 of 10 to both models. The top-level `bench-results/` folder in v0.5.0 has eight saved runs of it, counted from the files: one run each of `qwen/qwen3-coder-next` and `minimax/minimax-m2`, and three pairs of qwen with the default harness against a deliberately naive one. That is two models, and one of them is run with two harnesses.

On models: qwen passed 12 of 13 and minimax passed 12 of 13, and they failed the same task (`go-multi-file-rename-contract`, both at the turn limit). The runs cost about $0.17 and $0.29. The corpus cannot tell these two models apart. The README registers five models, and says the other three (`z-ai/glm-5.2`, `deepseek/deepseek-v3.2`, `deepseek/deepseek-v4.1-flash`) have been used on real tasks but not scored on this corpus.

On the harness, which is the thesis itself, we held qwen and its pin fixed and changed only the harness. The naive config turns off forced verification, sets the repair budget to 0 and allows only native tool calls. Here are the three pairs:

| Run | default | naive-v1 |
|---|---|---|
| 1 | 13/13 | 12/13 |
| 2 | 12/13 | 12/13 |
| 3 | 12/13 | 11/13 |

Pooled over the three runs, the default passed and naive failed on 3 tasks, the reverse happened on 1, 34 passed on both and 1 failed on both. The p-value is 0.625, which is not significant. The default was never behind in a single run (run 2 was a 1-1 tie on the tasks that flipped), and the three tasks that went its way were three different tasks. In run 1 the naive harness hit the turn limit on 5 of 13 tasks against 1 for the default. That is a pattern, not a proof.

We planned five runs and stopped at three to save money, so two are missing and the writeup says so. The naive baseline changes three things together, so even a clear result would not say which one helps. The same default config scored 13 of 13 in one run and 12 of 13 in another, which is a reminder that a fixed seed does not make a hosted model repeat itself.

So what we can say is narrow. On this corpus, with one cheap model, a tuned harness was never behind a naive one in any run and was ahead in two of three, and we cannot yet call that a win. Not measured: each of the four checks on its own, the repair rate, the syntax check, and anchored edits against the usual retype-the-text edit. There is no public benchmark result. Beyond the top-level folder, `docs/bench-results/` holds other runs (handoff and output-cap comparisons) that ask different questions.

The limits are practical too. There is no sandbox: an approved shell command runs with your privileges (ADR-0008). Most corpus tasks are Go and Python. And the corpus is already too easy to separate two good models, so we need harder tasks before it can test finer changes.

## Try it

You need an OpenRouter API key. The install command is from the README:

```bash
curl -fsSL https://raw.githubusercontent.com/leejianrong/kopicode/main/scripts/install.sh | sh
export OPENROUTER_API_KEY="..."
cd your-project
kopicode
```

The default model is `qwen/qwen3-coder-next`, and a one-line fix cost about $0.04 in our walkthroughs. Start with a small, well-described bug in a repository that has tests, and `docs/trying-kopicode.md` in the repository walks through two real ones. The code and the ADRs are at https://github.com/leejianrong/kopicode.
