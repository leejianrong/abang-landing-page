<!--
title: "Approval at the round boundary: running a crew of coding agents"
description: How cuttlefish-crew runs coding agents across several repos, why it asks for your approval between rounds of work instead of cutting in mid-task, and where the three supported agents differ.
slug: cuttlefish-round-boundary-approval
author: Jian
date: 2026-11-30
status: Published
tags: [engineering, cuttlefish-crew]
product: cuttlefish-crew
sources:
  - cuttlefish-crew/README.md
  - cuttlefish-crew/AGENTS.md
  - cuttlefish-crew/agent_docs/known-gaps.md
  - cuttlefish-crew/docs-site/quickstart.md
  - cuttlefish-crew/docs-site/cli-reference.md
  - cuttlefish-crew/docs/adr/0001-satay-workflow-as-the-core-loop.md
  - cuttlefish-crew/docs/adr/0003-kopicode-delegation-is-a-wrapped-headless-invocation.md
  - cuttlefish-crew/docs/adr/0005-agent-backend-becomes-a-pluggable-protocol.md
  - cuttlefish-crew/docs/adr/0006-project-scoped-secrets-are-encrypted-at-rest-and-injected-not-brokered.md
  - cuttlefish-crew/docs/adr/0008-steering-is-a-round-boundary-redirect-not-a-mid-flight-interrupt.md
  - cuttlefish-crew/docs/adr/0016-round-boundary-approval-gate-replaces-steering-when-both-are-set.md
  - cuttlefish-crew/docs/adr/0018-codex-is-a-third-agentbackend-with-its-own-honestly-named-gaps.md
  - cuttlefish-crew/docs/adr/0019-tool-call-tracing-extends-the-existing-round-events-no-second-store.md
  - cuttlefish-crew/docs/adr/0030-a-round-that-runs-out-of-room-is-a-checkpoint.md
  - cuttlefish-crew/docs/adr/0033-a-codex-turn-in-flight-takes-a-steer-through-turn-steer.md
  - cuttlefish-crew/docs/adr/0044-the-chat-is-a-view-onto-the-agent-session-and-autopilot-keeps-a-builder-going.md
  - cuttlefish-crew/docs/adr/0045-a-one-line-install-clones-builds-the-dashboard-on-the-machine-and-never-uses-sudo.md
  - cuttlefish-crew/docs/adr/0046-approvals-are-tiered-and-a-manager-agent-answers-the-middle-tier.md
  - cuttlefish-crew/src/cuttlefish/agents/backend.py
  - cuttlefish-crew/src/cuttlefish/steering.py
  - cuttlefish-crew/src/cuttlefish/team.py
  - cuttlefish-crew/src/cuttlefish/workflow.py
-->

---

# Approval at the round boundary: running a crew of coding agents

If you run more than one coding agent, on more than one repository, you soon lose track of them. One is waiting for permission to run a command. One finished an hour ago. One is going the wrong way and you would like to tell it so. cuttlefish-crew is a small daemon and dashboard that keeps all of them in one place, and this post explains one design choice in it: when you want to change an agent's course, or approve its work, we do it between rounds of work and never in the middle of one.

We chose this because the tools we wrap give us no safe way to interrupt them. Below we show how it works, what it costs, and where the three agents we support (kopicode, Claude Code and Codex) behave differently. The project is pre-1.0 and built for one person, so read the limits section before you trust it with anything you care about.

## One crew, one dashboard

You register your repositories as projects. Each project has an agent, and you give it a goal in plain words. The dashboard puts the projects that are waiting on you at the top, with the request each one is waiting on, and the same page works on a phone.

cuttlefish-crew does not do the coding and makes no model call of its own. It hands the work to an agent CLI you already have. In the code this is a small interface called `AgentBackend` (`src/cuttlefish/agents/backend.py`). A backend wraps one tool, runs it on a checkout, reads whatever output that tool produces and turns it into one shared result type. ADR-0005 explains why: the pain we wanted to fix was running Claude Code day to day, and a tool that could only drive a different agent would not fix it. ADR-0003 and ADR-0005 also set a rule we have kept, which is that a backend uses its tool's existing headless interface as it is. We do not invent a new protocol between us and the agent.

The setting is `CUTTLEFISH_AGENT_BACKEND`, with the values `kopicode` (the default), `claude-code` and `codex`. A project or a role can override it, and in a team each role can use a different agent. Any other terminal agent can run in the same tmux session, but with no live status and no approval cards (ADR-0047).

## What a round is

A round is one call to an agent. We start the agent with a task and a folder, it works until it stops, and we record what happened: the files it changed, its last words, and whether it finished, was refused or failed. Then the workflow decides what comes next.

That loop is a durable workflow built on satay, our runtime for workflows that survive a crash (ADR-0001). The daemon can restart and each project's team picks up where it was. One caution from our own docs: only the daemon resumes by itself. A one-shot `cuttlefish run` that was killed starts a new run if you simply run it again, and continues only if you pass `--resume <id>` with the same arguments.

A round can also end because it ran out of room, not because the work is done. For kopicode, a stop at the turn limit or the token limit is treated as a checkpoint. The team writes a handover and starts the next round with a fresh session, up to `CUTTLEFISH_MAX_CONTINUATIONS` times (the default is 20). So a round is a natural place to refresh context as well as a place to ask you something.

## Steering and approving between rounds

Both controls work at the same point, right after a round has been recorded.

Steering is optional. You start a run with `--steerable`, and after each round the workflow waits a short time (`DEFAULT_STEERING_GRACE_SECONDS`, 5.0 in `steering.py`) for a message from you. If none comes, the round is final. If one does, we start another round whose text is the original task, a short log of earlier rounds, and your message. From the command line:

```bash
uv run cuttlefish steer <task-id> "actually use .dockerignore instead" --role builder
```

Approval is the stricter version. With `--require-approval`, a round never finishes on its own. The workflow waits, with no timeout, until you decide. You can use the dashboard panel or the command line:

```bash
uv run cuttlefish approve <task-id> --role builder                        # finalize it
uv run cuttlefish approve <task-id> --role builder --reject "use .dockerignore instead"  # one more round
```

A rejection must carry a comment, and that comment becomes the next round's instructions. The commands above are copied from the quickstart.

When both are set, approval replaces steering for that round. ADR-0016 explains why, and it is a bug we found by running it. The fleet daemon starts every team as steerable, so the first time anyone ticked "require my approval" in the dashboard, a round was waiting for a steering message and then for an approval in turn. In satay, the identity of a wait comes from a counter that ignores the event type, so the first wait's timeout was read as the answer to the second. The team stopped, with no failure shown. We fixed it by making the two modes exclusive, since a rejection comment can say everything a steering message would. In the code this is a plain `if require_approval ... elif steerable` in `team.py` and `workflow.py`.

## Why we do not interrupt mid-flight

The obvious design is to let you cut in the moment you notice a problem. ADR-0008 explains why we did not build that.

When ADR-0008 was written, we checked the code and found that kopicode and Claude Code were both started with the task as one command-line argument, with their output read to the end and no way to send input afterwards. Sending a message to a running one would need a live two-way protocol on top of a tool that does not offer one. We would have had to invent that protocol, which goes against the rule above. The ADR also found that racing the steering wait against a running task inside satay's `gather` was never shown to work, so we kept every wait as a plain step between rounds.

The cost is delay. A message you send while a round is running waits for that round to end, and a real coding round can take minutes. The docs say this plainly (a "deliberate limit, not a missing feature").

There is one exception, and it shows why the rule was never about principle. Codex's `app-server` has its own `turn/steer` call that adds a message to a running turn. ADR-0033 uses it: a steer sent from the dashboard goes into the running Codex turn at once, and if Codex refuses, the message waits for the round boundary as before. The known-gaps file records one real case where Codex acted on a steer minutes before its round ended. It is a nudge and not an interrupt, because Codex may finish a command it had already started. The command-line `cuttlefish steer` still lands at the boundary, even for Codex.

## Three other places the agent asks you

Round-level approval is the old part of the design, and it now sits under "Advanced: run a team of roles" in the dashboard. The main path today is giving a builder a goal, and there are other ways it stops for you.

**Commands.** When an agent wants to run a command nothing has approved, it stops and a card appears in the Needs you tab. You choose Allow once, Always allow or Deny. If you do nothing, the request is denied after `CUTTLEFISH_REQUEST_WINDOW` seconds (600 by default). A short list of commands (`sudo`, a forced `git push`, a download piped into a shell, writes outside the project) is refused in every mode, whatever you answer (ADR-0046 calls this tier 0).

**Autopilot.** For a builder given a goal from the dashboard, Autopilot is on by default (ADR-0044). The builder writes a plan to `.cuttlefish/artifacts/plan.md`, you approve the plan once, and from then on the daemon sends "continue" whenever the builder stops with steps left. It stops nudging at a limit (24 hours, 5 million tokens or 200 nudges by default), or when it is stuck (three nudges in a row with no step ticked). This replaces the per-round question with one question up front. It also uses a different loop from the round workflow above, so approval at a round boundary does not apply to it.

**Decisions and notices.** If the builder needs a choice only you can make, it writes a `decision.json` file and stops, and a Decision card appears. By default that card waits as long as it takes. If you set a wait on the project's Permissions tab, the recommended option is taken when the time runs out, except for options that delete or overwrite work. To hear about a card when the dashboard is closed, set `CUTTLEFISH_NOTIFY_URL` to a webhook or an ntfy topic. It gets one POST with the project name and the card title, and nothing else. Autopilot reaching a limit or getting stuck sends one too. Push to a phone through the relay is not built.

## From a phone, and one readable journal

The dashboard is a web app with no native app. From a phone you can reach it over Tailscale https or through a relay. Pairing needs an https page, and the README notes it has only been checked in Chromium. A newly paired device can read, answer Needs you, steer a running team, and start and stop. Terminal and admin rights are something you grant under Devices.

Everything the crew does goes into one journal per project, and nothing is kept in a second transcript. ADR-0019 added tool-call records to it: each tool an agent called, a short detail and whether it was ok, denied or an error, written just before the round's own result. `cuttlefish show <task-id>` prints a task's whole record, including every tool call.

Secrets are kept per project, encrypted on disk, and handed to an agent only when it starts (ADR-0006). You turn the store on by setting `CUTTLEFISH_SECRETS_KEY` to a key made with `cuttlefish secrets generate-key`. There is also an optional credential broker (`CUTTLEFISH_CREDENTIAL_BROKER=1`) that keeps an agent's model key in the daemon so the agent only sees a short-lived token.

## Limits and differences between agents

The three agents are not equal, and we would rather you knew before you picked one.

- **Steering.** For kopicode and Claude Code it always lands at a round boundary. For Codex it can land mid-turn, from the dashboard only.
- **Stop.** On kopicode and Claude Code, Stop takes effect when the current round ends, which can be minutes. On Codex's default transport the daemon interrupts the turn.
- **Codex permissions are coarse.** Codex has three sandbox levels and no per-command filter, so any allowed command moves it from `read-only` to `workspace-write` (ADR-0018). A command Codex is allowed to run is not sandboxed. A refusal also has no structured signal on the one-shot `codex exec` path, so we read a log line, which could change in a Codex release.
- **Codex cost.** Codex reports no cost, so only a token limit can stop it.
- **Read-only roles.** On Claude Code and Codex a reviewer cannot edit files. On kopicode it can, and only the role's prompt holds it back.
- **Claude Code in a sandbox** works only if you use `ANTHROPIC_API_KEY`, not Claude Code's own login.
- **Usage limits.** Devices shows each tool's usage windows and a warning at 80% for Claude Code and Codex. kopicode does not report them.

The project as a whole is pre-1.0, with one shared password and no per-user accounts. It runs on Linux and WSL2 only. CI uses Ubuntu and macOS is untested.

## Try it

The install is one line, and the script is short enough to read first (ADR-0045). It needs `git` and `curl`, and it never uses sudo.

```bash
curl -fsSL https://raw.githubusercontent.com/leejianrong/cuttlefish-crew/main/scripts/install.sh | sh
cuttlefish serve
```

`cuttlefish serve` prints a URL and a token to paste in. The [quickstart](https://leejianrong.github.io/cuttlefish-crew/docs/quickstart/) covers adding a project, and its fourth section covers steering and approval. The code and ADRs are at [github.com/leejianrong/cuttlefish-crew](https://github.com/leejianrong/cuttlefish-crew).
