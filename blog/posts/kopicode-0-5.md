<!--
title: "kopicode 0.5: handoff, a socket for serve, and a Codex provider"
description: What changed in kopicode 0.5.0. You can hand a session off to a fresh one, keep a serve process running after its client leaves, use a Codex login or a custom endpoint, and load AGENTS.md files from every directory.
slug: kopicode-0-5
author: Jian
date: 2026-12-12
status: Draft
tags: [release, kopicode]
product: kopicode
sources:
  - kopicode/README.md
  - kopicode/docs/RELEASING.md
  - kopicode/docs/kopicode-serve-protocol.md
  - kopicode/cmd/kopicode/main.go
  - kopicode (git log and git diff, v0.4.0 to v0.5.0)
  - kopicode (GitHub release notes for v0.5.0, read with gh release view)
-->

---

# kopicode 0.5: handoff, a socket for serve, and a Codex provider

kopicode 0.5.0 adds a way to continue work in a fresh session, a `serve` mode that keeps running after its client goes away, two new ways to pick a model provider, and a change in how `AGENTS.md` files load. It adds to the `serve` wire and the journal and removes nothing, but one change can alter what the model sees (see upgrade notes).

## Handoff

In the terminal, `/handoff [goal]` drafts a handoff document with one model call and leaves the session as it is. If `$VISUAL` or `$EDITOR` is set, it opens the draft there so you can edit it. If you answer `y`, it ends the session and starts a new one from the document, with verification reset to "not run".

The same exists on the wire. `session.handoff` returns a draft and a `handoff` field on `session.start` begins from one. kopicode never hands off by itself. (ADR-0026). The release notes say no benchmark claim is made for handoff yet.

## serve that outlives its client

`kopicode serve --listen <socket>` serves the same wire on a unix socket. The process and its sessions stay up when a client disconnects, so a client that restarts can reconnect and find them. The socket has mode `0600`. Unix only: on other platforms `--listen` is a usage error.

Three new methods help a client catch up: `server.sessions` lists each session and what it is doing, `session.events` replays the events after a sequence number, and `server.shutdown` closes every session and exits. `--idle-timeout` ends a socket process that has no client and no open session (default `30m`,). A load test with many concurrent sessions found two bugs, now fixed (ADR-0030).

## Providers

`--provider-url` sends requests to any OpenAI-compatible endpoint instead of OpenRouter. These two lines are from the README:

```bash
kopicode --provider-url http://localhost:11434/v1 --model qwen2.5-coder:7b     # Ollama, no key needed
KOPICODE_PROVIDER_API_KEY=... kopicode --provider-url https://llm.example.com/v1 --model my-model
```

Your OpenRouter key is never sent to that host, and `serve` and `mcp` take the flag too (ADR-0027).

`--provider codex` (or `provider = "codex"` in the user config) uses the login Codex CLI already made, read from `~/.codex/auth.json`. kopicode only reads that file and does not refresh it, so if the token expires, run Codex CLI once. A 401, 403 or 429 now says what to do. The release notes say it is for personal development use and reports no cost. They also say no real quota or expiry response has been recorded, so those messages come from the documented shapes (ADR-0035).

## Instructions, long runs and caching

`AGENTS.md` files are now loaded from the repository root down to the directory you start in, nearest last, up to 32 KiB in total. A file over the cap is dropped whole, furthest first, and the session start lists each file and says which were dropped (ADR-0032).

Two checks help long runs. If the model repeats the same call with the same result three times, or fails three edits to one file, the REPL tells it and suggests a change. `--stall-threshold N` changes the count and `0` turns it off (ADR-0028). A `run_shell` or `grep` result over 32 KiB is shown to the model as its start and end, with a note on what was left out, and the journal keeps all of it. `--output-cap N` changes the limit and `0` shows everything (ADR-0033). Both are off for every registered benchmark arm.

## Upgrade notes

With `run --print`, `serve` and `mcp`, a new session is now told which skills the repository ships, and all the `AGENTS.md` files in the chain load, where only the nearest loaded before. A repository with one `AGENTS.md` behaves as before. The model sees more context, so it may act differently on the same task. Both are recorded as `project_instructions_loaded` events, which gain `dropped` and `bytes`, and there is a new `HandoffWritten` event.

## Next

The release notes say ADR-0031 (observation masking), ADR-0034 (reminders and a todo list) and ADR-0036 (minimal hooks) are written down. ADR-0036 is a design that is not built.

The full change list is at https://github.com/leejianrong/kopicode/compare/v0.4.0...v0.5.0, and the release is `v0.5.0` at https://github.com/leejianrong/kopicode/releases/tag/v0.5.0.
