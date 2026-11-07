# Brief 03: satay

- slug: `satay-replay-is-the-debugger`
- working title: Replay is the debugger: what a journal buys you in an agent run
- tags: engineering, satay   product: satay   length: 1,600 to 2,000 words
- launch order: 3

## Angle
Durable execution is a crowded idea. satay's bet (ADR-0025) is that for agents the valuable part is
being able to fork a run, change an input and compare, and the journal is what makes that possible.
Lead with the debugging problem, and treat durability as the means.

## Reader
A developer running multi-step LLM or agent workflows in Python who has had a run fail at step seven
of ten.

## Outline
1. What goes wrong when a long agent run fails late (cost, non-reproducibility).
2. The journal: append-only, event-sourced. ADR-0001 and ADR-0004.
3. Replay from the top, reusing recorded results, and how a durable call is identified. ADR-0002.
4. Catching non-determinism instead of silently diverging. ADR-0003 and ADR-0022.
5. Fork from a code or input override, then a structural diff of the two runs. ADR-0028 and ADR-0034.
6. What it costs to run: one process over SQLite, no extra infrastructure, and the limits of that.
7. Try it with `examples/fork_and_compare_demo.py`.

## Read first
`satay-runtime/README.md`, `satay-runtime/docs/adr/0001`, `0002`, `0003`, `0004`, `0022`, `0025`, `0028`,
`0034`, `satay-runtime/examples/fork_and_compare_demo.py`, `crash_recovery_demo.py`.

## Verify in the source
Decorator and API names, the install command, what Satay Studio shows today.

## Do not
Write comparisons with other durable-execution products beyond what ADR-0025 itself says. Mention
hosted or paid plans. Describe features that the ADRs mark as proposed or not built.
