# Brief 10: tutorial, semula

- slug: `tutorial-semula-record-and-replay`
- working title: Test an LLM app offline with semula's record and replay
- tags: tutorial, semula   product: semula   length: 900 to 1,300 words
- launch order: 10

## Angle
A hands-on walk from nothing to a test run that makes no network calls.

## Outline
1. What we are building: a tiny script that calls an OpenAI-compatible client, tested offline.
2. Start semula in record mode (Docker command from the README).
3. Point the client at it and make the first call, which is held.
4. Answer it (dashboard or CLI, whichever the docs show first) and see it recorded.
5. Switch to replay and run again, and see it served instantly.
6. What happens on a near miss, and how to review it.
7. Where to go next (the docs guide).

## Rules for this brief
Every command, flag, path and screen name is copied from `semula/README.md` and `semula/docs/guide/`.
Run nothing that needs credentials. Show expected output only where the docs show it.
