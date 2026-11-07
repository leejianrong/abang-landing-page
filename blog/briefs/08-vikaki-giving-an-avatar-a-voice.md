# Brief 08: vikaki

- slug: `vikaki-giving-an-avatar-a-voice`
- working title: Giving a cartoon avatar a voice: lip-sync, local TTS and a worker thread
- tags: engineering, vikaki   product: vikaki   length: 1,400 to 1,800 words
- launch order: 8

## Angle
vikaki is cartoon-first on purpose (ADR-0005), and the interesting engineering is in making speech look
right with cheap parts: audio-driven lip-sync, a local voice, and keeping synthesis off the render thread.

## Reader
A developer curious about avatars, TTS or driving a character from an LLM over MCP.

## Outline
1. Why a cartoon and not a realistic face. ADR-0005.
2. A VRM avatar rendered with three.js. ADR-0002.
3. Lip-sync from audio, and the spike that chose wLipSync. ADR-0007.
4. A local voice with Kokoro, kept optional because of its size, and run in a worker thread.
   ADR-0010, ADR-0013, ADR-0011 and `docs/tts.md`.
5. Emotions as a pose plus manga symbols. ADR-0015.
6. Driving the avatar from an LLM over MCP. `docs/mcp.md`.
7. What is not tested yet. `docs/STATUS.md` says the meeting extension was only tested against a
   stand-in page; say so.

## Read first
`vikaki/README.md`, `vikaki/docs/STATUS.md`, `vikaki/docs/architecture.md`, the ADRs above, `docs/tts.md`, `docs/mcp.md`.

## Do not
Describe the poker-table scenes in depth, and do not claim the meeting integration works on a real call.
