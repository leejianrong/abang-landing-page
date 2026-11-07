# Brief 01b: revision pass on post 01 (semula)

This is a **revision** of an existing draft, not a new post. Edit
`blog/posts/semula-subscription-as-mock-llm.md` in place. Keep its slug, title, tags, `status: Draft`
and date. Keep everything in it that is accurate: the facts were checked against the semula source and
hold. Do not remove a verified fact unless you are replacing it with a clearer way of saying it.

The first draft is committed in git (do not run git yourself). Treat its structure and voice as the
baseline and change only what the notes below ask for.

## Notes from review

1. **Show the result.** The post shows commands but never what comes back. Add one worked example that
   follows a single request all the way through: the request is sent and held, the answer is given,
   the app receives the completion, and the same request is replayed. Show real output. Take it
   verbatim from `semula/README.md` and `semula/docs/tutorial/first-recording.md` (and the other docs
   under `semula/docs/`). If the docs do not show an output you want, describe it in a sentence and do
   not invent the text. Do not run Docker or anything that needs network or credentials.

2. **Add the dashboard screenshot.** Copy `semula/docs/assets/dashboard-pending.png` into
   `assets/blog/semula-subscription-as-mock-llm/` (use a shell `cp`) and reference it as
   `/assets/blog/semula-subscription-as-mock-llm/dashboard-pending.png` with alt text that says what the
   screen shows. Place it where it helps most, probably next to the held call. Read the image first
   so the caption and alt text describe what is actually on it.

3. **Lighten sections 3 and 4** ("A fingerprint makes the recording reusable" and "Near matches wait for
   review"). They list config names in long paragraphs and read like reference documentation. Shorten
   the paragraphs, keep one idea each, and lead with what the reader gets before the setting name. A
   compact table of the matching tiers (what each tier matches, and whether it is served or sent to
   review by default) is fine if it replaces prose. Leave the exact defaults correct.

## Keep as is

- The opening paragraph, the trade-offs section, and the provider-terms paragraph. A decision on the
  title and the subscription angle is pending with Jian, so do not soften or rewrite that caveat.
- British spelling, no em dashes, sentence-case headings, and the voice rules in `blog/AGENTS.md`.
- Length: no more than about 1,900 words including the new example.

## Also

Update the `sources` list in the metadata to include any new file you read. Finish with the three
lists that `blog/AGENTS.md` asks for, and add a short fourth list, "What changed", with one line per
note above.
