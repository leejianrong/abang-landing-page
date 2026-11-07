# Brief 09: fraktal

- slug: `fraktal-does-synthetic-imagery-help`
- working title: Does synthetic satellite imagery help a real model? How fraktal plans to find out
- tags: engineering, fraktal   product: fraktal   length: 1,300 to 1,700 words
- launch order: 9

## Angle
fraktal generates labelled synthetic satellite worlds. The honest position is that it is early and the
one question that matters (does training on it help a real model?) is not answered yet. Write about the
design and the test, not about a result.

## Reader
An engineer working with earth-observation data or synthetic data in general.

## Outline
1. The shortage of labelled imagery, and why tropical South-East Asia is poorly covered.
2. Worlds built from real geography and filled in procedurally. ADR-0002.
3. Deterministic worlds with stable IDs, so a scene can be regenerated exactly. ADR-0003.
4. Rendering with a sensor model. ADR-0004.
5. The benchmark that decides success, and the dataset chosen for it. ADR-0006 and ADR-0008.
6. What exists today versus what is planned (read `README.md` and `docs/STATUS`-style files).
7. What we will do if it does not help.

## Read first
`fraktal/README.md`, `fraktal/docs/PLAN.md`, `fraktal/docs/adr/0002`, `0003`, `0004`, `0006`, `0008`.

## Do not
Write about selling datasets, keeping the engine private, a data-generation studio, or generative-model
licensing (ADR-0007, 0011, 0013). Those are business decisions, so skip them and mention it in your
final message. Do not state any result as measured unless a file shows it.
