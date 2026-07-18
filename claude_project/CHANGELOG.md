# CHANGELOG — worklog (newest first)

Running record of every work session: what changed, why, what's live, what's still open. Append a new dated block at the TOP each session. This is the canonical "where we left off." (History before 2026-07-18 lives in the reference docs 01/02/04 and project memory; this log starts when we formalized the workflow.)

---

## Open threads (keep current — the live to-do)
- **Detail-hero sharpness** (deferred, agreed to fix "properly later"): deck frames are 480×270; the detail hero shows them at up to 1180px (desktop) / full-width (mobile) → ~2–5× upscale = soft. Proper fix = re-extract frames at ~960–1280px from `_vimeo_uploads/` and re-push via `push_deck.sh`. **Blocker/lesson:** the original extractor (`worker2.py`) was lost — it ran in a previous chat's sandbox and was never committed. Recipe is documented in project-memory `deck.md` ("Reusable extraction pipeline") — rebuild from it and **commit to `_build/` this time.** Watch: tags are keyed `slug/NNNN`; re-extraction must preserve frame numbering or `deck_tags.json` breaks (ffmpeg scene-detect is deterministic → should reproduce; verify on one film first). Nick is getting a brief from the old chat.
- **Recurrence prune:** `build_site.py` writes pages but never deletes dirs whose slug left `projects.json` → orphan "ghost" pages re-accumulate on every rename/removal. Add a prune step (remove top-level slug dirs not in projects.json, guarded by a sysdirs allowlist). Needs Nick's ok (auto-delete behavior).
- **Typo'd canonical slugs still live** (URL changes if fixed): `harley-davidson-the-linage`, `louis-vuitton-virgial-abloh-tribute`, `tiffany-co-jewlery`, `hennesy-...`. Deferred.
- **Data hygiene:** `montell-fish-who-did-you-touch` vimeo stored as a manage URL (embed works, normalize to `https://vimeo.com/1210301476`); 6 posted projects with blank credits (polo-ralph-lauren-timeless-america, lincoln-wish-list, monse-yoonmi, coke-evergreen, super-she-supershe-island, vogue-stand-on-the-word); deck detail-credits gap (105/197 films have no deck_credits entry → only Color shown); junk deck film label `wdytln-h-264-files`.
- **Confirm on phone** (couldn't self-verify — backgrounded automation tab): deck design items below — esp. the "FILTERS above search" placement interpretation, mobile soft-crop squares, swipe, blinking cursor, forced-dark overlay in white mode.
- **Longstanding** (from 02_site_reference): nickmetcalf.com DNS cutover (waiting on Nick); a few unresolved dup pairs / hide-list names.

---

## 2026-07-18 — deck perf, nav, cleanup, source-in-repo, deck design pass, docs workflow

**Deck load performance (shipped).** "Slow on fast internet" was latency + main-thread, not bandwidth (data is gzipped, ~785KB, ~168ms). Fixes in `js/deck.js`: (a) the 4 data JSON fetches now fire in parallel (`_pDATA/_pTAGS/_pFMT/_pCR`) instead of 4 serial awaits (measured 168ms→28ms); (b) `buildSidebar()` (heavy facet-count pass) deferred off the critical path via coalesced `requestIdleCallback` so the grid paints first; (c) `deck_format.json` cache-bust is now admin-only. Verified live: parallel fetch, no console errors.

**Deck source committed (was Mac-only).** `_build/build_deck.py`, `css/deck.css`, `js/deck.js`, `_build/deck_main.html`, `_build/deck_extras.html` were only on Nick's Mac — the live `deck/index.html` was an orphaned artifact. Committed all 5; verified a clean `build_deck.py` run is byte-identical to live. Deck is now reproducible from the repo. (This is the same class of problem as the lost extractor — hence the WORKFLOW rule.)

**Main nav: added DECK.** Nav is now **WORK / ARCHIVE / CONTACT / DECK** on every page. Moved the DECK entry into `data/site.json` (the single nav source; header is a centered flexbox so array order = visual order) and removed the duplicate nav hardcoded in `build_deck.py` so the deck inherits the same nav. `site.json` push triggered the Action to rebuild all pages.

**Site debug pass.** Build is clean (103 visible / 123 hidden), no console errors, all thumbs present, deck data intact. Found + **deleted 28 orphaned ghost pages** (`/<slug>/index.html` live but not in projects.json, from renamed/removed slugs; git-recoverable; no live page linked to them; confirmed 404 after). Logged the recurrence + data-hygiene items under Open threads.

**Deck design pass (3 batches, all shipped + source committed).**
- *Filters menu:* hid **Film** from the menu (kept `hide:1` in SECTIONS because `state.sets.film` drives project routing — do not delete); trimmed **Color** to red/orange/yellow/green/teal/blue/magenta/pink + warm/cool/mixed/sat/desat/bw (removed sepia/purple/neutral/white/black from the MENU only — tag data untouched); removed **Color Picker** entirely; **palette toggle** CSS-hidden (`#paltoggle{display:none}`, code kept — flip to re-enable).
- *Detail page:* reflowed to credits-hero → **filters** block (`Label: value / value`, label capitalised, values lowercase + light-grey `.mv`, empties skipped) → **[ open film page ]** at the END → **keywords** as their own section (`#ovkw`, added to deck_extras.html). Overlay **forced dark** always (even in white mode). **Swipe** left/right on `#ov` = next/prev still. Mobile detail "more stills" gallery = 3-up **soft-crop squares**.
- *Landing:* default (unfiltered) view **scoped to films on the main landing grid** — `build_deck.py` injects `window.DECK_LANDING=[selected slugs]`; deck.js seeds `landingSet`, any search/filter or Clear-all reveals the full library. As of today: 20 selected films, 15 have frames → ~736 stills default. (Committed `js/deck.js` has the DECK_LANDING line STRIPPED — build_deck re-injects it.) Added a **blinking terminal cursor** on the search field; on mobile **FILTERS moved above the search bar** (centred — interpretation of "in line with the main nav"; confirm with Nick).

**Detail-hero sharpness — diagnosed, deferred.** Measured: 480px frame shown at 1180px = ~5× upscale (desktop), ~2× (mobile). CSS unchanged today; the softness came from the earlier deck *reframe* making the detail full-bleed. Agreed to fix properly later (re-extract higher-res). → Open threads.

**Documentation workflow (this).** Added `00_START_HERE.md`, `WORKFLOW.md`, `CHANGELOG.md` to `claude_project/` (already in the repo). Established: document every session here, keep reference docs current, and **commit reusable scripts to `_build/`** so no future chat loses tooling again. Corrected the record: deck frame source is `_vimeo_uploads/`, not `_MASTERS`.
