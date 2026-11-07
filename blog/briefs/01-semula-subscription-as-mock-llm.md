# Brief 01: semula

- slug: `semula-subscription-as-mock-llm`
- working title: Using the AI subscription you already pay for as a mock LLM
- tags: engineering, semula   product: semula   length: 1,400 to 1,800 words
- launch order: 1 (lead post: a concrete pain with an immediate payoff)

## Angle
Developing and testing against a paid LLM API bills every call, while a coding-agent subscription
sits mostly idle. semula serves an OpenAI-compatible endpoint and lets your agent write the answers.
The lasting value is the record and replay that comes with it: answers are stored and served back
instantly, offline and free. Be straight about the limits.

## Reader
A developer with an LLM app and a test suite, who has been burnt by hand-written mocks or by a bill.

## Outline
1. The problem with testing against a paid API (cost, flaky output, mocks that break when a
   framework changes a prompt).
2. What semula is: the endpoint, record mode, a held call, the answer arriving from your agent over
   MCP or the CLI.
3. Record once, replay forever: how a request is fingerprinted and normalised (timestamps,
   reordered tool lists). ADR-0007.
4. Matching that is safe by default: tiers, and near misses going to a review queue rather than being
   served silently. ADR-0003.
5. Streaming responses and how they are stored and replayed. ADR-0008.
6. What it does not do, and the trade-offs (agent latency in record mode, what a recording cannot
   tell you about a real model).
7. Try it (the Docker command from the README).

## Read first
`semula/README.md`, `semula/docs/concepts.md`, `semula/docs/guide/answerer.md`,
`semula/docs/adr/0002-record-mode-park-and-answer-queue.md`, `0003`, `0007`, `0008`, `0013`,
`semula/CHANGELOG.md`.

## Verify in the source
The Docker command, the endpoint path, the modes and their names, the current version.

## Do not
Quote cost savings or timings you did not read. If the docs say anything about the terms of using a
subscription this way, repeat only what they say and flag it in your final message for Jian to decide.
