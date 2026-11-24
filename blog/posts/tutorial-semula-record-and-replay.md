<!--
title: "Test an LLM app offline with semula's record and replay"
description: A step-by-step walk through semula 0.6.0. Record one answer to a prompt, switch to replay, and see what happens when a prompt only nearly matches.
slug: tutorial-semula-record-and-replay
author: Jian
date: 2026-12-04
status: Draft
tags: [tutorial, semula]
product: semula
sources:
  - semula/README.md
  - semula/CHANGELOG.md
  - semula/pyproject.toml
  - semula/zensical.toml
  - semula/docs/guide/install.md
  - semula/docs/tutorial/first-recording.md
  - semula/docs/tutorial/replay.md
  - semula/docs/tutorial/near-misses.md
  - semula/docs/tutorial/projects.md
  - abang-landing-page/blog/posts/semula-subscription-as-mock-llm.md
-->

---

# Test an LLM app offline with semula's record and replay

Tests that call a real model cost money and give different answers each time. In this post we use semula to answer one prompt once, save the answer, and then run the same call with no network and no model. It takes a few minutes and one Docker container. For why semula works this way, see [the earlier post](/blog/semula-subscription-as-mock-llm/). This one is only the steps.

A note on what I checked. This post follows semula 0.6.0 (the version in `pyproject.toml`, and the latest release in `CHANGELOG.md`). The commands and output below are copied from the README and the tutorial pages in the semula repo. I did not run them while writing, because the machine I used has no Docker. The output is what the docs show, not something I captured today. Your ids and timings will differ.

## What we are building

The app is one small Python script. It uses the OpenAI Python client, but points it at semula instead of at OpenAI. semula is a mock LLM server: it looks like the OpenAI API, but a person (or a coding agent) writes the answers. It saves each answer and serves it again when the same prompt comes back.

Here is the script. It is the Python example from semula's first tutorial page:

```python
from openai import OpenAI

client = OpenAI(base_url="http://127.0.0.1:8080/v1", api_key="not-needed")
reply = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Name a fruit."}],
)
print(reply.choices[0].message.content)
```

The API key can be any text, because semula does not check it unless you set `SEMULA_API_KEY`.

## Start semula in record mode

You need Docker. This is the command from the README:

```bash
docker run -d --name semula -p 127.0.0.1:8080:8080 \
  -e SEMULA_MODE=record -v semula-data:/data ghcr.io/leejianrong/semula
```

Three parts matter. `127.0.0.1:8080:8080` makes the port reachable from your machine only. `SEMULA_MODE=record` tells semula to hold any prompt it has no answer for. The `semula-data` volume keeps your recordings if you replace the container.

## Make the first call and answer it

Run the script. It does not print anything yet. semula has never seen this prompt, so it holds the call open and waits. In record mode this is called a parked call.

In a second terminal, list what is waiting:

```bash
docker exec semula semula pending
```

```text
01M5HGVZ3RCV5X9QWZKTDG9D7Z	pending	default	Name a fruit.
```

The columns are the id, the status, the project and the last message. Answer the call with its id:

```bash
docker exec semula semula answer 01M5HGVZ3RCV5X9QWZKTDG9D7Z --text "Mango"
```

```text
answered 01M5HGVZ3RCV5X9QWZKTDG9D7Z -> entry 01M5HGZ4Y2JJHS5HCTKW5E12GT
```

The script now prints `Mango`. semula saved the answer as an entry. The README says you can also open <http://127.0.0.1:8080/ui/> and answer from the Pending screen, which is the same job with buttons. In day-to-day use you would let a coding agent do the answering over MCP, as the README describes, but the CLI shows the idea with no setup.

Run the script again. This time it returns at once, with no parked call. The log shows both calls:

```bash
docker exec semula semula log --limit 5
```

```text
10:02:07.793  default      hit            exact 1.00  3ms  01M5HGZ4Y2JJHS5HCTKW5E12GT  "Name a fruit."
10:02:07.703  default      recorded       -  104305ms  01M5HGVZ3RCV5X9QWZKTDG9D7Z  "Name a fruit."
```

The first call was `recorded` and took as long as the person took to answer. The second was a `hit` on the `exact` tier and took 3 ms. The tutorial says the model name is not part of the match, so changing `gpt-4o` to another name still hits.

## Switch to replay

Record mode is for collecting answers. For tests you want replay mode, where semula never holds a call. It serves what it has, and it fails fast on anything else. Mode is set per project, and semula keeps it across restarts:

```bash
docker exec semula semula mode replay --project default
```

```text
default: replay (kept across restarts)
```

Now run the script again. It prints `Mango`, with no agent and no network call to a model. That is the test run we set out to build.

To see the other side, change the prompt in the script to a new one and run it. The replay tutorial does this with `Name a vegetable.` and shows this result:

```text
HTTP/1.1 424 Failed Dependency

{"nearest":{"entry_id":"01M5HGZ4Y2JJHS5HCTKW5E12GT","score":0.667,"last_message":"Name a fruit."},"error":{"message":"No recorded answer matches this request, and semula is in replay mode.","type":"semula_error","param":null,"code":"semula_no_match"}}
```

The call fails at once with status 424, and the body names the closest recorded prompt and its score. I like this default. A test that fails loudly on an unknown prompt is better than one that quietly gets a made-up answer.

## What happens on a near miss

Real prompts drift. A framework adds a word, or a path changes. semula checks the prompt in steps, called tiers, from the cheapest (an exact match) to the loosest, and stops at the first one that answers. The near-misses tutorial lists five: exact, normalised, alias, words and meaning. Its rule is that a weak guess is never served by default. A prompt that only nearly matches counts as a miss, and the pairing waits for a person to decide.

The tutorial uses a project called `support-bot` with a recorded prompt `Classify: my screen is cracked`. (The [projects tutorial](https://leejianrong.github.io/semula/tutorial/projects/) shows how to create one with `semula project create`.) The `test-match` command explains a result without changing anything. First, a prompt that differs only by trailing spaces:

```bash
docker exec semula semula test-match --project support-bot --prompt "Classify: my screen is cracked  "
```

```text
match: normalised (1.00) -> entry 01M5HH1FQC65G543SK7JAABCJV (would serve)
tiers: exact no, normalised match 1.00, alias skipped, words skipped, meaning off
```

Now a prompt with one extra word:

```bash
docker exec semula semula test-match --project support-bot --prompt "Classify: my screen is badly cracked"
```

```text
no match (would park); nearest 01M5HH1FQC65G543SK7JAABCJV score 0.909; 1 weak candidate(s) would go to review
tiers: exact no, normalised no, alias no, words candidate 0.91, meaning off
```

A `candidate` is close enough to ask a person, but not close enough to serve. If you send that prompt for real with the project in record mode, the call parks as usual and the pair shows up in the review queue:

```bash
docker exec semula semula review list
```

```text
01M5HH2EBM7AV0TKB5H9MCBNDC	open	0.91	support-bot	Classify: my screen is badly cracked  ~  Classify: my screen is cracked
```

`review show <id>` puts the two requests side by side. If the old answer is right for the new prompt, approve it:

```bash
docker exec semula semula review approve 01M5HH2EBM7AV0TKB5H9MCBNDC
```

```text
approved candidate 01M5HH2EBM7AV0TKB5H9MCBNDC
```

From then on that prompt is served through the `alias` tier. If the old answer is wrong for it, run `review reject <id>` and that pairing never comes back. One detail from the tutorial is easy to miss: approving only helps the next call. The call already waiting is still parked, and you still have to answer it.

## Limits to know about

- Everything above is copied from the docs. I did not run it for this post, so treat the exact output as an example.
- semula is 0.x. The README says a minor release may still change behaviour, and the changelog lists each change.
- The review step in the docs assumes record mode. I have not checked what a near miss does in replay mode beyond the `424` above.
- The `Name a vegetable.` score of 0.667 and the 0.909 score are from the docs' example prompts. Your prompts will score differently.

## Where to go next

The full tutorial is nine short pages, starting at [Your first recording](https://leejianrong.github.io/semula/tutorial/first-recording/). The next steps there are letting a coding agent answer over MCP, and keeping recordings in git so your tests can replay them on another machine.
