# Brief 13: sibei-flow

- slug: `sibei-flow-never-holds-write-credentials`
- working title: Why sibei-flow never holds production write credentials
- tags: engineering, sibei-flow   product: sibei-flow   length: 1,300 to 1,700 words
- launch order: 13 (needs the most source-hunting; the ADRs live in `docs/design/` and `docs/launch/`)

## Angle
An agent that fixes broken data pipelines proposes a pull request and never merges or writes to
production itself. Explain why, and what the verification steps buy in its place.

## Outline
1. A failure at 3am: schema drift in a dbt job.
2. The bounded agent loop (read-only source access, confirm against the live schema, draft a minimal edit).
3. Verification in an ephemeral Docker sandbox, and the later fork-replay tier against a recorded
   schema snapshot.
4. Propose and approve: the rule that the system holds no production write credentials. Find where it is
   written down (it is referred to as R6.1) and quote it.
5. What is out of scope and recorded rather than attempted.
6. Try the demo (`make up && make demo`, verify in the README).

## Read first
`sibei-flow/README.md`, `sibei-flow/docs/ROADMAP.md`, everything under `sibei-flow/docs/design/` and
`sibei-flow/docs/launch/`.

## Do not
Describe features the docs mark as planned as if they exist. Mention the hosted platform idea.
