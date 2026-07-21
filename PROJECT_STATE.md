# Project State — nrm461.github.io

_Last updated 2026-07-21._

## What this is

Nick Metcalf — colorist portfolio. A static site generated from `data/site.json` and `data/projects.json`, live at https://nrm461.github.io.

## Current status

Migrated into `~/dev` and pushed to GitHub as `nrm461/nrm461.github.io` during the ~/dev + GitHub migration — see `nrm461/claude-workspace` and ADR-0001. Standardised with `CLAUDE.md` + `docs/agents/` on 2026-07-21.

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

- _Add as work resumes. This file is the committed cross-machine continuity record — keep it current at handoff (`/handoff-github`)._
