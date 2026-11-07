<!--
title: "Using an AI subscription as a mock LLM for tests"
description: semula lets a coding agent answer an app's OpenAI-compatible calls, then records those answers for repeatable offline tests. This post explains how recording, matching and streaming work, and where the mock stops being useful.
slug: semula-subscription-as-mock-llm
author: Jian
date: 2026-11-07
status: Draft
tags: [engineering, semula]
product: semula
sources:
  - abang-landing-page/index.html
  - semula/README.md
  - semula/CHANGELOG.md
  - semula/pyproject.toml
  - semula/docs/concepts.md
  - semula/docs/guide/answerer.md
  - semula/docs/agents/PLAYBOOK.md
  - semula/docs/tutorial/first-recording.md
  - semula/docs/tutorial/near-misses.md
  - semula/docs/explanation/how-matching-works.md
  - semula/docs/adr/0002-record-mode-park-and-answer-queue.md
  - semula/docs/adr/0003-tiered-matching-safe-by-default.md
  - semula/docs/adr/0007-request-fingerprint-and-canonical-request.md
  - semula/docs/adr/0008-streaming-storage-and-replay.md
  - semula/docs/adr/0014-answerer-hook-runs-the-operators-command.md
  - semula/src/semula/api_openai.py
  - semula/src/semula/canonical.py
  - semula/src/semula/config.py
  - semula/src/semula/responses.py
  - semula/src/semula/streaming.py
-->

---

# Using an AI subscription as a mock LLM for tests

An LLM app can spend money just by running its test suite, and a hand-written mock often stops matching when the app's framework changes a prompt. I built semula to let a coding agent answer those calls through an OpenAI-compatible endpoint, then save each answer for later runs. The useful part is the recording. Replay gives the test the same answer without another model call, including when the agent is offline.

## A paid API is a poor default for every test run

Calling a real model is useful when we need to see how the real model behaves. It is a less useful default for tests that need a predictable answer in the right shape. Each call consumes API usage, the wording can change between runs, and a failure may tell us more about a model's latest answer than about the code under test.

Hand-written fixtures avoid those calls, but they have their own maintenance cost. If a framework adds a line to the system prompt or reorders a tool list, a fixture keyed to the full request can miss even though the application is asking the same question. Broadening the match carelessly is worse: an answer meant for one request can be returned for another, leaving a test green for the wrong reason.

semula sits at the app's OpenAI Chat Completions endpoint. We can use it while developing a feature and keep the resulting answers as test data. The coding agent writes the first answer through MCP or the CLI. Once it is stored, the agent is out of the replay path. I think that split is more useful than trying to make an agent answer every test call indefinitely.

## Record mode holds an unfamiliar call for an answer

The app points its OpenAI-compatible client at `http://127.0.0.1:8080/v1` and sends a request to `/v1/chat/completions`. This is the request in semula's README:

```bash
curl http://127.0.0.1:8080/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{"model": "gpt-4o", "messages": [{"role": "user", "content": "Name a fruit."}]}'
```

In `record` mode, an unknown request becomes a parked call. semula keeps the HTTP request open and puts the call in the pending list. A coding agent can use the MCP tools `wait_for_pending`, `get_pending` and `answer_pending`; the CLI has the same path through `semula pending`, `semula show` and `semula answer`. For a quick manual check, the README uses:

```bash
docker exec semula semula pending
docker exec semula semula answer <id> --text "Mango"
```

Here `<id>` is the id from the pending list. semula validates the answer, saves an entry and releases the waiting HTTP call. The app receives a normal chat completion with `Mango` as its message. An agent can stay in a loop waiting for the next call; the answer does not have to be typed by a person. The agent playbook tells it to read the whole request, including the system message and offered tools, before answering.

There is a real timeout to account for. The default `record_timeout` is 300 seconds; if nobody answers before then, the app gets `semula_record_timeout`, while the call remains pending and a later answer is still saved. An app's own HTTP timeout must allow for the agent's response time. Record mode is therefore useful for gathering answers during development, but I would not put it in a fast, unattended test run unless an answerer is already running.

## A fingerprint makes the recording reusable

semula turns the incoming Chat Completions body into a canonical request with messages, tools and selected parameters. `canonical.py` sorts tools by name before fingerprinting. It calculates an exact fingerprint and a normalised one; the latter collapses whitespace and scrubs timestamps, UUIDs and absolute paths. Project settings can add scrub patterns or choose how many trailing messages count.

This matters when the prompt includes a fresh timestamp on every run. A raw string comparison would miss each time, while a normalised fingerprint can find the existing entry. By default, `model`, `temperature`, `top_p`, `max_tokens`, `stream`, `user` and `seed` do not affect the fingerprint. A project can add selected parameters back with `include_params` when they matter to its answer. The model name in the example request is consequently a client detail rather than a separate fixture key.

Normalisation is a decision about which differences we consider harmless. If a path or timestamp actually changes the answer, scrubbing it can merge two requests that should stay separate. I would start with the defaults, inspect misses with `semula test-match`, and add a project rule only for noise we have seen. Stored requests have built-in credential redaction and can have project-specific redaction patterns, but recorded answers are not redacted. An agent should not put secrets in an answer.

## Near matches wait for review

The lookup goes through exact, normalised and approved alias matches before trying word overlap. The optional embedding tier can find paraphrases. Exact and normalised hits can be served directly, and an alias means a person has already approved that link. For the word tier, the default serve threshold is `1`, while a candidate above the review threshold can be shown for a decision. Embedding matches go to review by default unless the project explicitly opts in to serving them.

That conservative default costs some hit rate. It also avoids a particularly awkward test failure: a plausible answer returned for the wrong prompt. A near match still counts as a miss. In record mode the new call parks, and in replay mode it fails; a candidate above the review threshold appears separately in the review queue. The reviewer sees the two requests and the stored answer, then approves an alias or rejects the pairing. Approval affects later calls, so the already parked call still needs an answer.

The word tier also checks the request's shape before it serves a close match: roles in order, offered tools and any parameters the project chose to include. An answer containing a tool call is no good if the new request did not offer that tool. This is why I would keep the serve threshold strict until the review queue shows which variations are genuinely safe for a particular app.

## One entry can answer streamed and ordinary calls

Many clients request `stream: true`, while an agent usually writes a complete answer. semula stores the assembled assistant message, finish reason and usage. If an answer arrived as a stream, it also keeps its chunk boundaries. A later streamed call replays those chunks; if the entry has only a complete message, semula splits it into chunks (24 characters by default). The stream finishes with `data: [DONE]`, as an OpenAI-style stream does.

The reverse works too: a non-stream request can use an entry captured from a stream. Since `stream` is ignored by the default fingerprint, one recorded answer can serve both forms. That is convenient for tests that exercise the same app flow through different clients, but it is not a model of real token timing. Re-chunked boundaries differ from a provider's, and replay is immediate by default. An app that depends on the exact timing or boundaries of live generation needs a real-provider test as well.

## Know what the recording proves

A semula hit shows that the app can handle the stored answer for a matched request. It does not show that a real model would choose those words today, obey a new prompt, or make the same tool call. I would use recordings for application logic, parsing and repeatability, then keep a smaller set of calls against the real model for behaviour that depends on the model itself.

The current release is `0.6.1`, and semula is still in the `0.x` series, where a minor release may change behaviour. Its OpenAI-compatible surface covers Chat Completions, including tool calls and streams; clients using the Responses API or Anthropic Messages cannot point at that endpoint yet. Replay mode fails with HTTP `424` and `semula_no_match` on an unknown request. That failure is useful in CI because it identifies a missing fixture instead of asking an agent to improvise during a test.

There is also an operational distinction between an agent that answers pending calls over MCP or the CLI and the optional answerer hook that launches a command per call. The hook is off by default. ADR-0002 says automated headless use of a subscription has not been checked against provider terms; I would check the terms that apply to my own setup before using that path. The ordinary agent-driven queue remains the basic record workflow.

## Try one recording, then switch to replay

The README starts a local container in record mode with a named volume:

```bash
docker run -d --name semula -p 127.0.0.1:8080:8080 \
  -e SEMULA_MODE=record -v semula-data:/data ghcr.io/leejianrong/semula
```

Send the `Name a fruit.` request above, answer its pending id, and send it again to use the stored entry; when the entries cover the test, switch the default project with `docker exec semula semula mode replay --project default`. The [semula documentation](https://semula.abangai.dev/docs/) has the recording tutorial and the matching guide for the next step.
