# Brief 14: release post template (use for each release)

- slug: `<product>-<version>` for example `semula-0-6`
- tags: release, `<product>`   length: 400 to 700 words
- launch order: recurring, one per notable release

## Pattern
Release posts are short and factual. Candidates today: semula 0.6, indah 0.13, kopicode 0.5.

1. One opening paragraph: what changed in this version in plain words, for the person who already uses it.
2. What is new, grouped by what a user would call it (not by commit). Each item says what you can do now.
3. Behaviour changes and upgrade notes, with the exact command or setting if there is one.
4. What is next, only if the repository already says so.
5. A link to the changelog and the release.

## Rules for this brief
Everything comes from `CHANGELOG.md` (semula, indah) or the git tags and release notes (kopicode).
Read the actual diff of user-facing files when a changelog line is vague. Never list a change you did
not find. No adjectives like "powerful" or "exciting".
