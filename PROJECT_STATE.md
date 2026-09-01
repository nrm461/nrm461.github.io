# Project State — nrm461.github.io

_Last updated 2026-09-01._

## What this is

Nick Metcalf — colorist portfolio. A static site generated from `data/site.json` and `data/projects.json`, live at **https://nicholasmetcalf.com**.

## Domains (live 2026-07-27)

`nicholasmetcalf.com` is the canonical address — bare domain, registered at DreamHost,
DreamHost nameservers, four apex A records to GitHub Pages. `nickmetcalf.xyz` and
`nickmetcalf.io` are DreamHost **Redirect** domains → the apex, each with its own free
Let's Encrypt cert. `nrm461.github.io` redirects to the apex. GitHub Pages serves exactly
one custom domain, which is why the extras redirect rather than serve.

**Don't touch the MX records** — seven Google Workspace MX plus a `mail` CNAME to
`ghs.googlehosted.com`. Mail is live on this domain.

**Known limitation: `www.nicholasmetcalf.com` has no TLS certificate**, so `https://www`
does not connect. DNS is correct (`www` CNAME → `nrm461.github.io`); GitHub simply issued
an apex-only cert and will not re-issue. Two fixes were tried and ruled out on 2026-07-29:
removing and re-adding the Pages custom domain returns the *identical* cert (it matches an
existing valid one rather than requesting a new one), and DreamHost rejects
`www.nicholasmetcalf.com` as a Redirect website with `INVALID_DOMAIN` because it treats
`www` as part of the parent domain.

A GitHub **support ticket is not available** — `nrm461` is a personal Standard plan
("Technical support not included"), and the Pages HTTPS-certificate form dead-ends in a
product picker with no Pages option and a required sub-category that has no honest answer.
Asked publicly instead: **https://github.com/orgs/community/discussions/203414**
(2026-07-29, unanswered). If that goes nowhere, the remaining fix is fronting the site with
Cloudflare — covers apex and `www` on one cert, but moves nameservers off DreamHost.

**Do not set the Pages custom domain to `www.…`** to force issuance — the apex would 301 to
a `www` with no cert and take the whole site down.

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

## Adding a spot (2026-09-01)

`_build/add_spot.py <job>` is the whole add: it resolves the folder under the Studio's
`_MASTERS`, picks the deliverable (**ProRes > mp4 > GEN**, **16x9 > FulRes**), builds the
three thumbs and every carousel still with `sips` (**no ffmpeg or Homebrew needed**),
uploads to Vimeo over tus, and appends to `data/projects.json`.

**It runs on the Mac Studio** — `/Volumes/Suite` doesn't mount on the Air, but the Studio
is reachable over SSH as `studio`, so an Air session drives it remotely. A clone lives at
`~/dev/nrm461.github.io` there.

**The Studio has no GitHub credentials, deliberately, as of 2026-09-01** (Nick's call —
not yet worth doing). So `--commit` uploads and commits fine and then fails on the push
with `could not read Username for 'https://github.com'`. **That failure is expected and
nothing is lost** — the commit is local on the Studio and gets relayed:
`git fetch ssh://studio/Users/nicholasmetcalf/dev/nrm461.github.io main && git merge
--ff-only FETCH_HEAD && git push` from the Air. Don't re-diagnose it; the runbook has the
sequence. One `gh auth login` on the Studio removes the step whenever he wants it gone.

New spots land in **`group: "hidden"`** — the page builds at `/<slug>/` and is listed only
on the unlinked `/hidden/` index, until UNHIDE in admin.

**Vimeo:** token in `~/.vimeo-token` on the Studio (Pro account, ~4.3 TB free). Uploads must
use **`privacy.view: "disable"`**, never `unlisted` — unlisted URLs carry a secret hash and
`vimeo_id()` embeds by bare id, so the link and the player both break.

**Credits resolve in three tiers:** a credits file in the folder, then the director's or DP's
Instagram (post captions come out of the `og:description` meta with a plain fetch), then
`_build/crm_credits.mjs` for a partial director/DP/editor block out of the C41 CRM. Missing
credits are not fatal — the spot stages with `needs_review: true`.

## Admin traps (2026-09-01)

**Do not write `data/projects.json` while `/admin/` is open — the guard is not enough.**
It happened again the same day, worse: with a tab open, the new `father-son` row came back
holding **Benson Boone's** client, title, director, category, vimeo, credits and
`group: posted`, while Benson's own row was untouched. Restored in `a45c55e33`. The guard
only runs in the edit-modal path — the carousel reorder and the order saves write with no
staleness check at all — and it diffs five fields rather than the file's `sha`. How the two
rows crossed is **not yet explained**; that is **#25**, and it wants reproducing, not a
guessed patch. Symptom to watch for: a brand-new slug carrying another spot's metadata.

 The edit modal seeds from the
copy fetched at page load and writes it back verbatim, so a stale tab blanks anything added
since — this is how the Hill's credits were lost. The save now aborts when
`credits/director/client/title/vimeo` have drifted, but after any scripted write, reload admin.

**A "lost" carousel reorder is almost always caching.** Reordering rewrites `00.jpg..` in
place — same filenames, new bytes. The gallery tiles were emitted without `img_bust` and the
admin panel read uncached raw URLs, so both showed the pre-reorder images. Both now carry
busters. Check committed blob hashes before suspecting the drag code.

`gallery_max` in `site.json` caps the spot-page gallery (**12**); extra stills stay in the repo
as the picking pool. `carousel: true` makes stills **replace** the card thumbnail — now an
explicit checkbox, because the save handler used to derive it from "are there any files".

## What the second spot changed (2026-09-01)

Adding `father-son` (W959) turned up three things in `add_spot.py`, all fixed in `f88ae69e6`:

- **The gallery now comes from `ig_selects/`** when the folder has one — those are the
  frames that were actually posted, curated and in order — falling back to `stills/`.
  27 of the job folders carry one. `--all-stills` forces the old behaviour.
- **`--category` exists and is validated** against `site.json`. The category is guessed from
  the folder name and was wrong here (a short film staged as *Commercial*, with the
  production company as its third line) with no way to fix it but hand-editing the JSON.
- **`SHORT_HINTS` returned `Short Film`**, which is not one of `site.json`'s categories — no
  page filters on it. It returns `Long Form` now.

**The Studio can push now** (2026-09-01). It was never a credentials problem: its
`~/.ssh/id_ed25519` is already registered on the account, the clone's `origin` was just
HTTPS. Switched to `git@github.com:...`, so `--commit` finishes on its own and the
commit-on-Studio → fetch-from-the-Air → push relay is retired. `gh` is *not* installed
there and can't easily be — no Homebrew — so don't reach for it.

## Next steps

Both items below are **parked** (label `parked`, 2026-08-11) — back burner, not
awaiting anything. Left open deliberately; the context is worth keeping.

- **#16 — deck stills re-extract (parked 2026-07-29 mid-grilling, re-parked 2026-08-11).** Two decisions
  settled, one open. **Machine-bound:** the masters live on `/Volumes/Suite/...`, which
  does not mount on the MacBook Air — the next extraction pass has to run wherever
  `Suite` mounts. Also blocked on the extraction script, which is in neither this repo
  nor `~/dev`. Full context in the issue; don't re-derive it.
- **#21 — exclude own traffic from Umami on the Mac Studio (parked 2026-08-11).** Analytics went live
  2026-07-29 (page views + a `play` event per video; see README's Analytics section).
  Self-exclusion in Umami is a per-browser `localStorage` flag, not an account setting,
  so it is **machine-bound:** set on the MacBook Air's Chrome, still unset on the Studio,
  which is therefore counting Nick's own visits. One console line, on the ticket.
- _Add as work resumes. This file is the committed cross-machine continuity record — keep it current at handoff (`/handoff-github`)._
