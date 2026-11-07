# Brief 06: kampong-agents

- slug: `kampong-one-yaml-file`
- working title: One YAML file you can commit, diff and eject
- tags: engineering, kampong-agents   product: kampong-agents   length: 1,300 to 1,700 words
- launch order: 6

## Angle
Visual agent builders tend to trap you in the tool. kampong-agents treats a YAML file as the source of
truth and the canvas as one editor among several (Cursor and Claude Code are others). Export is one-way
and produces a standalone TypeScript project.

## Reader
A developer who wants a visual editor for agent workflows but refuses to lose the file.

## Outline
1. The lock-in problem with visual builders.
2. AgentSpec YAML as the source of truth, with one-way export. ADR-0002.
3. External-edit-first, and the sidecar layout file that keeps canvas positions out of the spec.
   ADR-0008 and ADR-0006.
4. Running locally against any model, including offline Ollama. ADR-0003 and ADR-0004.
5. Eject: a standalone project that depends on nothing from this tool, vendored not re-templated.
   ADR-0010 and ADR-0033.
6. What the canvas cannot do yet.
7. Try it.

## Read first
`kampong-agents/README.md`, `kampong-agents/docs/adr/0002`, `0003`, `0004`, `0006`, `0008`, `0010`, `0033`.

## Do not
Cover hosting, accounts, monetisation or enterprise governance ADRs (0013 to 0024).
