# Brief 11: tutorial, satay

- slug: `tutorial-satay-durable-agent`
- working title: A durable agent loop on satay, step by step
- tags: tutorial, satay   product: satay   length: 1,000 to 1,400 words
- launch order: 11

## Angle
Take `examples/durable_agent_demo.py` and `crash_recovery_demo.py` and walk through them: write the
workflow, kill it mid-run, resume, open the debugger, fork.

## Outline
1. The workflow and its tasks (quote the example).
2. Run it and interrupt it.
3. Resume and see which steps re-ran and which were reused.
4. Open Satay Studio and read the timeline.
5. Fork with a changed input and compare.
6. Limits to know before using it for real.

## Rules for this brief
Use only the example files and README commands. Run the examples yourself if you can do so offline and
report what you ran. ADR-0043 describes the durable agent loop on-ramp. Do not mention hosted plans.
