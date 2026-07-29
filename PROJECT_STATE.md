# Project State — nrm461.github.io

_Last updated 2026-07-26._

## What this is

Nick Metcalf — colorist portfolio. A static site generated from `data/site.json` and `data/projects.json`, live at https://nrm461.github.io.

## Current status

Migrated into `~/dev` and pushed to GitHub as `nrm461/nrm461.github.io` during the ~/dev + GitHub migration — see `nrm461/claude-workspace` and ADR-0001. Standardised with `CLAUDE.md` + `docs/agents/` on 2026-07-21.

## Layout — how the front end is wired (2026-07-26)

Two things to know before editing `css/main.css`:

- **`--col` is not just the thumbnail grid.** It also drives the header/footer column
  count via `--colX2`, so changing it moves the nav. Grid-only changes are scoped to
  `.page-archive .module-videos`; nav-only changes are scoped to `header`.
- **The work grid ladder skips 4-across:** 7 above 1920px, 5 from 1025-1920, then
  3 / 2 / 1 below. The header uses three equal columns inset 17.5% each side (the
  middle 65%, matching prodco.xyz's spread) from 769px up; 768px and down is flex and
  is deliberately left alone, including deck.css's FILTERS as a fourth nav item.

## Typeface — IBM Plex Mono (2026-07-26)

The site runs on **IBM Plex Mono at `--fs: 11.5px`**, self-hosted from `fonts/`
(OFL 1.1, `fonts/OFL.txt`). Nick picked it against the real work grid; issue #2.

Before this the stack was `'OCRF', Courier, monospace` — but OCRF is ProdCo's licensed
face and `fonts/ocrf.woff2` was never obtained, so every visitor since launch saw the
**Courier fallback**. The dead `@font-face` is gone; if the licence is ever bought it is
a two-line restore. Shipped weights: 300 (body) and 400/600/700 for `deck.css`'s `<b>`,
latin + latin-ext only, `font-display: swap`.

`--fs` is not just text size — `--height-text` and the rule heights derive from it, so
changing it moves the caption blocks and rules too. `--lh` stays the authored `18/13`.

**Known loose end:** `deck.css` still hard-codes `#board-title` at 13px and the admin tag
at 9px, so on the archive page they sit slightly large against the new 11.5px baseline.
Left alone pending Nick's call.

**A GitHub Action ("Rebuild site") regenerates the pages on push** and refreshes the
`?v=` cache-bust stamp that `_build/build_site.py` writes from the CSS/JS mtime. Do not
run `build_site.py` by hand — the local rebuild collides with the Action's own
`[auto-build] regenerate pages` commit. Push the CSS/JS or script edit alone and let CI
do the rest. When a change looks missing on the live site, check the served `?v=` stamp
before suspecting the deploy; it is usually browser cache.

**This repo is public** — unlike the other six, which are private. It has to be: it is the
GitHub Pages site. It also carries `.nojekyll`, so **every file in the tree is served
verbatim** at `https://nrm461.github.io/<path>`, including files that look like internal
data. Anything committed here is published.

## Known exposure — read this before adding data files

`_ig/slate_assets2.json` was **removed at HEAD on 2026-07-21** (commit `e061bbc7d`). It
contained an AWS access key ID (`AKIAWKLXWYBJAUU623BO`, 48 occurrences) inside pre-signed
Slate CDN URLs, alongside client asset titles, and — because of `.nojekyll` — was live and
publicly fetchable. Verified gone: the URL returned 200 before the push and 404 after.

Low severity: an access key *ID* is the public half of a pre-signed URL, the secret key was
never in this repo, and the signatures expired 2026-07-12. Nothing in the site referenced
the file, so removal was functionally inert.

**Published history was deliberately not rewritten** (Nick's decision, 2026-07-21).
Rewriting ~1,983 commits on a live Pages site was judged not worth the small security
delta, given the secret half is absent and the signatures have expired. The blob is still
reachable via `git show 33110d8db` by anyone who clones and digs.

Still present and still publicly served: `_ig/slate.json`, `_ig/slate_assets.json`,
`_ig/slate_dl_map.json`. **No credentials in any of them** (checked — zero
`AWSAccessKeyId`/`Signature` hits), but all three carry client asset metadata: client
names, project titles, dates, and CloudFront source URLs. Left in place — that is a
separate question from the credential one, and it is Nick's call.

## Next steps

- **#16 — deck stills re-extract (parked 2026-07-29, mid-grilling).** Two decisions
  settled, one open. **Machine-bound:** the masters live on `/Volumes/Suite/...`, which
  does not mount on the MacBook Air — the next extraction pass has to run wherever
  `Suite` mounts. Also blocked on the extraction script, which is in neither this repo
  nor `~/dev`. Full context in the issue; don't re-derive it.
- _Add as work resumes. This file is the committed cross-machine continuity record — keep it current at handoff (`/handoff-github`)._
