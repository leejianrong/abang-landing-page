# Blog plan

The blog lives at abangai.dev/blog. Posts are Markdown in `blog/posts/`, built to static HTML by
`scripts/build_blog.py` (CI runs it on every push to `main`). A Codex agent writes the prose from a
brief; a human reviews and flips `status: Draft` to `Published`.

## What the reference blogs do

I read the listings and sampled one full post from each (all three serve full text).

| Blog | What it publishes | What to borrow |
|---|---|---|
| OpenAI Developers | Practical how-tos and case studies tied to a product ("Custom Code Review rules for Codex", ~1,200 words, five sections) | Short posts with a concrete job to do, one idea each |
| Apache Airflow | Release posts, tutorials, community news, each with author, date and tags (Release, Development, Community, Tutorial) | The tag vocabulary, and tutorials that walk one real DAG end to end (~3,000 words) |
| Claude | Product announcements and agent-building guides (one post lists an 18 minute read) | Guides that state a failure mode first, then a pattern |

## Our shape

Four kinds of post, used as tags:

- `engineering`: why a design decision was made, grounded in an ADR. The core of the blog.
- `tutorial`: a hands-on walk through something that exists.
- `release`: short, factual, from the changelog.
- `behind-the-build`: how we work.

Cadence: one post a week at most. Lead with posts that have a concrete pain and an immediate payoff
(semula, then kopicode's thesis and satay's replay debugger), not the most technically
interesting one.

## The plan

Each row has a brief in `blog/briefs/` with the outline, the sources the agent must read, and what it
must not write about. Order is the suggested publishing order.

| # | Working title | Product | Type |
|---|---|---|---|
| 01 | Using the AI subscription you already pay for as a mock LLM | semula | engineering |
| 02 | Cheap models can code if the harness catches their mistakes | kopicode | engineering |
| 03 | Replay is the debugger: what a journal buys you in an agent run | satay | engineering |
| 04 | Designing a logo system for nine products with a coding agent | abang-ai | behind-the-build |
| 05 | A Python UI framework with no Node: shipping a prebuilt frontend | indah | engineering |
| 06 | One YAML file you can commit, diff and eject | kampong-agents | engineering |
| 07 | Approval at the round boundary: running a crew of coding agents | cuttlefish-crew | engineering |
| 08 | Giving a cartoon avatar a voice: lip-sync, local TTS and a worker thread | vikaki | engineering |
| 09 | Does synthetic satellite imagery help a real model? How fraktal plans to find out | fraktal | engineering |
| 10 | Test an LLM app offline with semula's record and replay | semula | tutorial |
| 11 | A durable agent loop on satay, step by step | satay | tutorial |
| 12 | Launch a Python dashboard from a Colab cell with indah | indah | tutorial |
| 13 | Why sibei-flow never holds production write credentials | sibei-flow | engineering |
| 14 | Release posts (semula 0.6, indah 0.13, kopicode 0.5) | various | release |

Brief numbers follow this order. Swap any two if news or a release makes one more timely.

## Writing a post with Codex

```bash
blog/run-codex.sh 01-semula-subscription-as-mock-llm          # one at a time
uv run scripts/build_blog.py --drafts --out /tmp/blog-preview # preview with drafts
```

Then review against the checklist below, edit by hand, and set `status: Published` and the real date.

## Review checklist

- Every command and code block matches the repository. Run the ones you can.
- Every number, version and "we measured" claim has a file behind it. Read the agent's `sources` list
  and its "Could not verify" list.
- Nothing about pricing, hosting plans or strategy (see each brief's "Do not").
- Reads like us: calm, specific, no em dashes, no hype, British spelling.
- The product's own README and the post agree on what is built and what is planned.
