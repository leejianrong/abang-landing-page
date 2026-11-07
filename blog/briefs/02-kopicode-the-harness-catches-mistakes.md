# Brief 02: kopicode

- slug: `kopicode-the-harness-catches-mistakes`
- working title: Cheap models can code if the harness catches their mistakes
- tags: engineering, kopicode   product: kopicode   length: 1,600 to 2,000 words
- launch order: 2

## Angle
kopicode's thesis is that the harness around a model moves measured coding ability more than the
choice of model does. Present it as a thesis under test, not a result. Describe the mechanisms
concretely and show what each one catches, using real runs. State plainly how much has been measured.

## Reader
A developer using cheap or open-weight models for coding who is tired of malformed tool calls and
edits that land in the wrong place.

## Outline
1. How a cheap model fails in a coding loop (name the failure modes you can show from real runs).
2. Tool-call repair.
3. Hash-anchored edits that reject on drift instead of guessing. ADR-0006.
4. The syntax gate on every edit.
5. Forced verification: no success report until the project's own tests pass.
6. How we measure (the benchmark method in ADR-0005) and why that method was chosen.
7. What the numbers say so far, and what they do not. Read the README status and `bench-results/`
   and state exactly how many models are measured.
8. Try it.

## Read first
`kopicode/README.md`, `kopicode/docs/adr/0005-benchmark-and-ab-methodology.md`, `0006`, `0007`, `0012`,
`0028`, `0031`, `0033`, `kopicode/docs/dogfood-runs/`, `kopicode/bench-results/`.

## Verify in the source
Which models are measured and registered, the install command, version numbers.

## Do not
Invent benchmark figures. Compare against other products' performance. Claim an A/B result unless
the files show one.
