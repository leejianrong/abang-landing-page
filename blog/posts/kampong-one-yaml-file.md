<!--
title: "One YAML file you can commit, diff and eject"
description: How kampong-agents keeps an agent workflow in one plain YAML file, lets the canvas and your editor share it, and ejects to a standalone TypeScript project when you want to leave.
slug: kampong-one-yaml-file
author: Jian
date: 2026-11-28
status: Published
tags: [engineering, kampong-agents]
product: kampong-agents
sources:
  - kampong-agents/README.md
  - kampong-agents/docs/concepts.md
  - kampong-agents/docs/tutorial/external-editing.md
  - kampong-agents/docs/tutorial/exporting.md
  - kampong-agents/docs/tutorial/offline.md
  - kampong-agents/docs/reference/cli.md
  - kampong-agents/docs/reference/agentspec.md
  - kampong-agents/docs/index.md
  - kampong-agents/SLICES.md
  - kampong-agents/examples/agent.yaml
  - kampong-agents/packages/cli/templates/market-etl/agent.yaml
  - kampong-agents/docs/adr/0002-yaml-source-of-truth-oneway-export.md
  - kampong-agents/docs/adr/0003-mastra-typescript-runtime.md
  - kampong-agents/docs/adr/0004-no-llm-gateway-for-mvp.md
  - kampong-agents/docs/adr/0006-sidecar-layout-file.md
  - kampong-agents/docs/adr/0008-external-edit-first-workflow.md
  - kampong-agents/docs/adr/0010-exported-runtime-is-vendored-not-retemplated.md
  - kampong-agents/docs/adr/0033-export-verifies-its-components.md
  - kampong-agents/docs/adr/0052-yaml-serialisation-style.md
  - kampong-agents/docs/adr/0054-spec-is-internal-yaml-is-interchange.md
-->

---

# One YAML file you can commit, diff and eject

Most visual agent builders keep your workflow inside the tool. You draw boxes, and the real thing lives in their database, in a format you cannot read. If you stop paying, or the tool changes, you start again. We built kampong-agents to avoid that. A workflow is one YAML file, and the canvas is just one way to edit it.

This post shows how that works: what is in the file, how the canvas and your editor share it, how you run it with any model, and how you leave. It also lists what the canvas cannot do yet.

## The problem with visual builders

A visual builder is good for seeing a workflow. It is bad when the picture is the only copy. You cannot review a change in a pull request, you cannot ask a coding agent to edit it, and you cannot move it to another tool.

The fix is simple to state. Keep a plain text file as the main copy, and let the canvas read and write that file. Then the canvas never holds anything you cannot get out.

## The file is the workflow

kampong-agents calls the file an AgentSpec. This is the starter example from the repository, `examples/agent.yaml`, without its comments:

```yaml
version: "1.0"
agent:
  id: hello_agent
  name: "Hello Agent"
  role: "Friendly assistant"
  goal: "Greet the user warmly and answer one question in a concise, helpful tone."
  model:
    provider: openrouter
    name: liquid/lfm-2.5-2.6b:free
    api_key: ${OPENROUTER_API_KEY}
  workflow:
    - step: greet
      action: generate_text
      inputs: [input]
```

Secrets never go in the file. The `api_key` is a `${OPENROUTER_API_KEY}` placeholder, and the real value comes from `.env` or the environment.

The canvas parses this file, draws it, and writes it back when you change something. The round trip is built to give you the same file back, comments included (ADR-0002). That took some work. The YAML library we use first re-wrapped long lines and changed `{ a: 1 }` to `{a: 1}`, so a hand-written file was reformatted on its first canvas save. ADR-0052 fixes both: long expressions are not re-wrapped, and the canvas copies the spacing style it finds in your file.

One thing is still not kept. A folded `>-` block is saved with each paragraph on one line. The value is the same, but the line breaks are gone. Use a literal `|` block where the breaks matter.

## Your editor is a first-class editor

We expect many people to write these files in Cursor or Claude Code, because those tools are better at editing text than anything we would build. So the canvas does not have an import step. Point `kampong dev` at a folder, and every valid spec in it shows up:

```sh
kampong dev ./my-specs --spec support-bot.yaml
```

If the canvas is open while you edit, it reloads on its own. It only asks you a question in one case: your editor saved a change at the moment you had an unsaved change on the canvas, and one of them has to lose (ADR-0008).

You also get checking in your editor for free. The spec has a published JSON Schema, and one comment on the first line makes any editor that uses the YAML language server validate the file and suggest fields:

```yaml
# yaml-language-server: $schema=../packages/spec/schemas/agent-spec.v1.0.schema.json
```

There is one gap, and the docs say so. The schema marks `model.api_key` as optional for every provider. The real rule (needed for cloud models, left out for Ollama) is checked when `kampong` loads the file, so a missing key shows up at run time and not as a red line in your editor.

### Canvas positions stay out of the file

The canvas has to remember where each box sits. If it wrote those numbers into the spec, every small drag would add noise to your diffs. So positions go in a second file, `.kampong/layout.json`, keyed by step and tool name (ADR-0006).

The spec has no layout data in it at all. If you add a step by hand, the canvas places it automatically. If you delete the layout file, you lose the arrangement and nothing else. The cost is that two files travel together. If your team does not commit `.kampong/`, each person gets their own layout. We think that is the right trade, since a diff of the spec then shows only changes in behaviour.

A card you drag onto empty canvas stays where you put it. Cards you have not touched keep their automatic place (ADR-0061).

## Run it on any model, including offline

The model is a setting in the spec: `openrouter`, `openai`, `anthropic` or a local `ollama`. There is no gateway service in between (ADR-0004), so the engine calls the provider directly, and a failed call fails in plain view. If Ollama is not running, you get an error. You do not get a quiet switch to a paid API.

For a run with no network at all, use a local model and replay recorded tool calls. The `--tools` flag has three modes: `live`, `record` and `replay`. A replay never touches the network, and a missing recording is an error, not a live call (`docs/tutorial/offline.md`):

```sh
kampong run agent.yaml --input "order 1234" --tools record
kampong run agent.yaml --input "order 1234" --tools replay
```

The `market-etl` template shows the same idea on a bigger workflow. It is a scheduled price pipeline that loads daily prices, checks them, saves them to Supabase and posts to Slack when a price moves more than a set amount. It uses `provider: ollama` and ships recorded data, so you can replay it with no keys. The engine is TypeScript on Mastra (ADR-0003), so the whole tool is one Node program with no Python to install.

## Eject: a project that needs nothing from us

When a workflow is settled, you can leave:

```sh
kampong export agent.yaml ./my-agent
cd ./my-agent && npm install && npm start
```

The result is an ordinary Node project on Mastra and its own declared packages. It does not import anything from kampong-agents. The CLI reference and tutorial both say it behaves the same as running the spec on the canvas or with `kampong run`.

We got there by copying, not by writing a second engine. The exporter copies the real engine source files into the new project's `src/runtime/` folder (ADR-0010). The code that runs your exported agent is the same code our tests run, not a parallel version that could drift. Only a small entry point is generated. The cost, which the ADR states plainly, is that the copy is frozen at export time. A later fix to our engine does not reach a project you already exported.

If your workflow uses components (the pinned connectors and your own), the export copies their exact bytes. The project re-checks them at startup and refuses to run if a file changed. It also writes a `kampong.lock` file and an `sbom.json`, and `npm run verify` checks the components against the second one (ADR-0033). We added this because an exported project can no longer be checked from our side.

Export goes one way. The canvas and CLI never read your generated code, and edits you make there do not flow back to the spec. We chose this over two-way sync because syncing a canvas with arbitrary hand-written TypeScript means parsing any code back into boxes, which is a much bigger and riskier build (ADR-0002). `kampong export` also refuses to write into a directory that has files in it, unless you pass `--force`, so a re-export cannot wipe your changes.

## What it cannot do yet

- One agent per spec. Multi-agent workflows are on the roadmap, not built.
- No RAG (search over your own documents), no parallel steps and no dark mode on the canvas. The README lists all three as still coming.
- The YAML may become less central in the hosted product. ADR-0054 says the validated spec is the truth, and YAML is its text form. In local mode nothing changes, and you still edit `agent.yaml`. A hosted server exists in the repository but is not deployed, so we do not cover it here.
- The exported project is yours to maintain. There is no path back, and engine fixes do not reach it.
- The schema gap for `api_key` described above.

The project is early. The canvas, local engine, CLI and export are merged and tested in the repository, but we have not measured how well the exported project matches the canvas run beyond our own tests.

## Try it

You need Node 22 or newer. `make try-demo` in the repository opens the canvas on the `market-etl` template, ready to replay, with no keys and no Docker. The tutorials in `docs/` cover editing in your IDE and ejecting step by step. The code is at https://github.com/leejianrong/kampong-agents.
