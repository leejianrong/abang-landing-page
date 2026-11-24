<!--
title: "Giving a cartoon avatar a voice"
description: How vikaki makes a cartoon avatar speak with cheap parts - lip-sync from audio, a local voice kept off the main thread, and an LLM driving it over MCP - and what we have not tested yet.
slug: vikaki-giving-an-avatar-a-voice
author: Jian
date: 2026-12-02
status: Draft
tags: [engineering, vikaki]
product: vikaki
sources:
  - vikaki/README.md
  - vikaki/CLAUDE.md
  - vikaki/docs/STATUS.md
  - vikaki/docs/architecture.md
  - vikaki/docs/tts.md
  - vikaki/docs/mcp.md
  - vikaki/docs/observability.md
  - vikaki/docs/spikes/lipsync.md
  - vikaki/docs/adr/0002-stylised-vrm-avatar-rendered-with-threejs.md
  - vikaki/docs/adr/0005-cartoon-first-avatars-no-human-mimicry.md
  - vikaki/docs/adr/0007-wlipsync-for-lip-sync.md
  - vikaki/docs/adr/0010-kokoro-for-local-tts.md
  - vikaki/docs/adr/0013-tts-engines-run-in-a-worker-thread.md
  - vikaki/docs/adr/0015-emotions-as-pose-and-manga-symbols.md
  - vikaki/docs/adr/0048-the-default-mouth-is-hybrid-and-falls-back-to-the-audio.md
  - vikaki/docs/adr/0050-kokoro-stays-the-default-voice-others-are-opt-in-and-chosen-by-ear.md
  - vikaki/packages/cli/src/index.ts
-->

---

# Giving a cartoon avatar a voice

vikaki is a small open-source tool that makes a cartoon character talk. You give it text (or a microphone) and the character speaks it, moves its mouth and shows a feeling. This post covers the parts that took the most work: making the mouth match the sound, making the voice run on a laptop without freezing the server, and letting an LLM drive it. It also says plainly what we have not tested.

## Why a cartoon

We chose a cartoon on purpose (ADR-0005). A realistic face has to be exactly right or it looks creepy, and exact is expensive: it needs a lot of art, a lot of rendering and often a GPU for every stream. A cartoon only has to be readable. The ADR says expression should come from big, clear emotion, mouth shapes and idle movement, not from fidelity.

The cost is that we give up the "digital copy of me" use, and we accept that.

## A VRM model in the browser

The avatar is a VRM model (a standard file format for 3D characters), drawn in a web page with three.js and three-vrm (ADR-0002). Any browser can show it, and drawing it is cheap.

The catch is in the same ADR. VRM's built-in mouth shapes are five vowels (`aa`, `ih`, `ou`, `ee`, `oh`), so the lip-sync is coarser than a face with dozens of shape controls. The default avatar, Cookieman, has no brows either. ADR-0015 records that we checked all 16 of its morph targets (the sliders that bend its face) by showing each one in turn.

## Choosing a lip-sync library with a spike

We started from audio, not text: a library listens to sound and turns it into weights for those five mouth shapes. We ran a spike (a short test to decide) on two candidates, wLipSync and wawa-lipsync, using 12 clips in headless Chromium (`docs/spikes/lipsync.md`).

Both reacted inside our 100 ms budget. The differences were elsewhere:

- On quiet pink noise, wLipSync opened slightly (largest weight 0.12). wawa-lipsync reported a consonant in 93% of frames and moved its mouth fully, so it would chew along with room noise.
- On the word "you", wLipSync gave `ou` as its top shape 42% of the time. wawa-lipsync never produced `ou`.
- wawa-lipsync does report consonants, which wLipSync does not. We judged that a polish item for a five-shape mouth.

So ADR-0007 picked wLipSync, with wawa-lipsync as a fallback in case a page blocks the AudioWorklet or WASM it needs. The spike has limits we wrote down at the time: 12 clips, English only, synthetic voices, and a profile calibrated by someone else that we cannot remake without Unity.

Since then we found the next weakness by measuring. A mouth driven only by sound does not know which vowel was said. On our scorecard (`make lipsync-scorecard`, eight lines, a report and not a pass or fail test) it made the right vowel shape about a quarter of the time. ADR-0048 added a "hybrid" mouth: shapes come from the phonemes (the sounds of the words), and how far the mouth opens follows the loudness of the audio. If the hub sends no phonemes, it falls back to the audio mouth exactly. That mouth is now the default. The score of 90% against 23% for vowel shapes needs a caution: it measures agreement with the phoneme track, so it is high for the phoneme mouths by design. It shows how far the audio-only mouth is from the spoken vowels, and nothing more. wLipSync stays for the microphone, where there is no text.

## A local voice, kept optional

For speech we use Kokoro through `kokoro-js` (ADR-0010). It runs on the CPU, the licences are Apache-2.0, and no text leaves the machine. It is also large: about 410 MB with its runtime, then a model download of about 330 MB on first use. So it is not a dependency of the workspace. You install it when you want it:

```bash
make install-voice     # installs into .vikaki/voice and downloads the model; safe to run again
make doctor            # checks that everything the demos need is in place
```

Without it, the demos play a steady test tone and the page says so in a banner.

We measured speed on a laptop CPU in ADR-0010: about 0.75x real time at first, with 8-bit weights. In ADR-0013 we found that those 8-bit weights were about three times slower on our CPU than full precision, so full precision is now the default. For the same audio, "Check." took 1.4 s with 8-bit and 0.46 s with full precision. At the hub, a 44-character line now reaches first audio in 0.98 s, against 2.4 s before. The price was a bigger download (about 330 MB, not 90 MB) and a model load of 4 to 10 s instead of 1 to 2 s.

## Keeping synthesis off the server's main thread

Our timeline view showed the page reporting `speech_started` at 1.6 s, but the driver (the program sending the lines) was told at 3.0 s. Kokoro holds its thread for up to 1.8 s while it makes a sentence, and the hub relays every message on that same thread. So messages waited, and a `cancel` would have waited too. Our cancel tests used a fake voice that does not block, so they never saw it.

ADR-0013 runs the engine in a worker thread (a second thread inside the same process). `WorkerTts` wraps any engine behind the same `Tts` interface, and audio comes back chunk by chunk with the buffers moved, not copied. Measured with the real voice:

| | Server stall | Driver told "started" after the page | Cancel, page to driver |
| --- | --- | --- | --- |
| In the main thread | up to 1,681 ms | 1,227 ms later | n/a |
| In a worker | up to 17 ms | 9 ms later | 33 ms, then 11 ms |

Two details cost us time. A worker thread cannot load TypeScript here, so the engine code is plain `.mjs`. And you must not kill the worker while Kokoro is running, because the native runtime then aborts the whole process. `close()` waits for work in progress, up to 10 s.

Kokoro also cannot be stopped part-way through a call. So a long sentence is made in pieces of about 70 characters, the first one at most 40, and a cancel costs at most one piece.

A better voice exists, but it is opt-in. ADR-0050 records that Chatterbox on a rented RTX 4090 sounded more expressive by ear, but took about 4.0 s to first audio (0.77x real time), too slow for live play. Kokoro stays the default, and `vikaki serve --tts chatterbox` (with `CHATTERBOX_URL` set) is there if you run your own server. Its pace setting was chosen by ear too, as the slowest of three blind variants.

## Emotions as a pose plus a symbol

The protocol has seven emotions: `neutral`, `happy`, `smug`, `worried`, `surprised`, `sad` and `angry`. Since Cookieman has no brows or smile, ADR-0015 shows an emotion as a small pose (an eyelid squint, a head tilt or nod, a bounce or a tremble) plus one manga-style symbol beside the head, such as sparkles for happy or a sweat drop for worried. The symbols are drawn in code, so they carry no licensed art.

This has a limit that the ADR states: sad, worried and angry have similar faces, and the symbol and the head movement carry the difference.

## Driving it from an LLM

`vikaki mcp` is an MCP server (the Model Context Protocol, a standard way for an LLM client to call tools). It has four tools: `say`, `set_emotion`, `set_persona` and `cancel`. With Claude Code you add it like this (from `docs/mcp.md`):

```bash
claude mcp add vikaki -- pnpm --silent --dir /path/to/vikaki vikaki mcp --port 8787
```

The `--silent` flag matters. The server talks over stdout, and pnpm's own banner would corrupt the stream. You start the hub first with `pnpm serve --port 8787` and open the page.

A `say` call waits until the line has been spoken and returns an outcome of `completed`, `interrupted` or `failed`, with `first_audio_ms`.

The same lines work from the terminal, so you can try the avatar without an LLM:

```bash
pnpm --silent vikaki say "Oh, is that so?" --emotion smug --think 1.5
pnpm --silent vikaki cancel
```

(The first command is the README example with different words.) The hub allows one driver at a time, and `cancel` always works because it comes from a controller role (ADR-0014), not a driver.

## What is not tested yet

The README and `docs/STATUS.md` list a meeting extension that replaces your camera in Google Meet with the avatar. We tested it only against a stand-in page. We have not run it on a real call, and the steps that need a person on a real call machine are still open. We also have not tried Teams or Zoom on the web. So we make no claim that it works in a meeting.

Other limits:

- Most numbers here come from one development machine, sometimes with other work running. Treat them as a guide.
- Kokoro's runtime carries eSpeak NG (GPL-3.0). So we publish no Docker image that contains Kokoro (ADR-0051). You build that image yourself.
- We have not heard a hosted voice judged against Kokoro. ADR-0050 says that needs a person listening.

## Try it

You need Node 24 and pnpm 11. Run `pnpm install --frozen-lockfile`, then `make demo-speech`, type a line and press Speak. The code and the decision records are in the vikaki repository, under `docs/`.
