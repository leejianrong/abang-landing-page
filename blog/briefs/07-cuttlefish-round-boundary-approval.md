# Brief 07: cuttlefish-crew

- slug: `cuttlefish-round-boundary-approval`
- working title: Approval at the round boundary: running a crew of coding agents
- tags: engineering, cuttlefish-crew   product: cuttlefish-crew   length: 1,500 to 1,900 words
- launch order: 7

## Angle
Interrupting an agent mid-flight is fragile. cuttlefish-crew redirects and asks for approval at a round
boundary, and delegates the coding to whichever agent CLI you already use. Be honest about the gaps
between backends.

## Reader
A developer running more than one coding agent across more than one repository.

## Outline
1. The problem: several agents, several repos, no single view.
2. The AgentBackend protocol, and delegating to kopicode, Claude Code or Codex. ADR-0005, ADR-0003, ADR-0018.
3. What a round is, and why steering happens at its boundary. ADR-0008 and ADR-0016.
4. Approving from the dashboard or a phone. README, ADR-0011 and ADR-0013.
5. One readable journal, built on satay, with tool-call tracing. ADR-0001 and ADR-0019.
6. Secrets per project. ADR-0006.
7. Install (ADR-0045) and the limits (Linux and WSL2 only today).

## Read first
`cuttlefish-crew/README.md` and the ADRs above in `cuttlefish-crew/docs/adr/`.

## Do not
Cover the Fly.io hosting ADR or anything about paid tiers. Overstate Codex support: ADR-0018 names its gaps.
