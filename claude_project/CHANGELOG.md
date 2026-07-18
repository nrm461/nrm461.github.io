# CHANGELOG — where we left off

Reverse-chronological. **Top entry = current state.** At the end of each session, add what shipped and refresh the Open threads.

---

## website 2026.0001 — 2026-07-18

Shipped:
- Reported nav "drift" diagnosed: the LIVE site was already consistent (WORK / ARCHIVE / CONTACT / DECK on landing and /deck); the local Mac working copy was stale. Re-synced local to origin.
- Local auto-sync: `_local/` LaunchAgent (sync.sh, PATH-hardened, fast-forward-only) pulls origin every 30 min + at login. Needs Full Disk Access on /bin/zsh (Desktop is TCC-protected). Confirmed running (exit 0).
- Version tracking: new `claude_project/VERSION` counter (`website YYYY.NNNN`), cut 2026.0001. Bump on every push; kickoff + handoff lead with it to seed the next chat's title.
- Pushed stranded local edits to origin: `.gitignore` (_backups/) and `02_site_reference.md` (deck files).

Open threads:
- Deck data hygiene: typo canonical slugs (harley `-linage`, `virgial`, `jewlery`, `hennesy`); 6 posted projects blank credits; 105/197 deck films missing deck_credits; `wdytln-h-264-files` junk label; montell-fish vimeo URL normalize.
- build_site recurrence-prune for orphaned slug dirs (needs Nick's ok on auto-delete).
- nickmetcalf.com DNS cutover (waiting on Nick).
- Confirm on phone: deck swipe, blinking cursor, mobile square gallery, filters-above-search, forced-dark overlay.

## 2026-07-18 (b) — self-loading kickoff via project memory (no Claude Project needed)

- **New workflow: no Claude Project, no Instructions field.** Project memory auto-loads into every new chat on its own, so it IS the kickoff. Memory `MEMORY.md` now opens with an imperative kickoff block that routes any fresh chat to read `00_START_HERE.md` + the top of `CHANGELOG.md` from the connected website folder, then do the task or report status.
- **To start work:** open a blank chat with the website folder connected → type the task (or "status"). Nothing to paste.
- Created `00_START_HERE.md` (entry point) + this `CHANGELOG.md`; committed `04_deck.md` to the repo (was Mac-only). All on origin/main.
- Session protocol (orient → deploy via browser Contents API → **log to CHANGELOG before signing off**) lives in memory `MEMORY.md` top and in `01_project_instructions.md`.
- Updated `03_starter_prompts.md`: new kickoff prompt + reusable handoff template.

### Open threads
- Same site/deck open threads as the entry below (deck hero re-extract, design interpretations to confirm on phone, recurrence-prune, data hygiene) — unchanged this session.

---

## 2026-07-18 (a) — deck perf, ghost cleanup, deck source committed, deck design pass

### Shipped (live)
- **Deck performance** — `js/deck.js`: the 4 data-JSON fetches now fire in parallel (were serial); `buildSidebar()` moved off the critical path via a coalesced `requestIdleCallback` so the grid paints before the heavy facet-count pass; `deck_format.json` cache-bust is now admin-only. Rebuilt via `build_deck.py`, deployed `deck/index.html` via the Contents API. No console errors.
- **Ghost cleanup** — deleted 28 orphaned `<slug>/index.html` pages not in `projects.json` (git-recoverable).
- **Deck source committed to the repo (GitHub)** — `js/deck.js`, `css/deck.css`, `_build/build_deck.py`, `_build/deck_main.html`, `_build/deck_extras.html`. Deck now rebuilds reproducibly (clean build = byte-identical to live). NOTE: these were committed to `origin/main` via the browser Contents API; Nick's LOCAL working copy still shows them untracked/modified because the device can't fetch — not a problem, just don't re-commit blindly.
- **Deck design pass** (deck-only; full detail in project memory `deck_design_20260718.md`):
  - Filters menu — Film facet hidden (kept in code: still drives routing), Color trimmed to core hues + classes, Color Picker removed, palette toggle CSS-hidden.
  - Detail overlay — restructured to credits-hero → `Label: value` filters block → `[ open film page ]` → keywords as their own section; forced-dark always; swipe left/right = prev/next still; mobile "more stills" gallery = 3-up soft-crop squares.
  - Landing — default (unfiltered) view scoped to the selected landing films (~736 stills); any search/filter reveals the full ~6,236; blinking terminal cursor on the search field; mobile FILTERS moved above the search bar (centred).

### Open threads
- **Deck detail hero low-res on mobile** — frames are 480px; needs a higher-res re-extract. DEFERRED (Nick getting a brief on the old extraction script). Don't rabbit-hole unless asked.
- **Design interpretations to confirm on a phone** — swipe gesture, mobile 3-up square gallery, FILTERS-above-search placement ("in line with the main nav" = centred row under nav, vs. literally inside the header?), forced-dark overlay in white mode. Not self-verifiable in the sandbox (Chromium blocked).
- **Recurrence-prune for build_site** — `build_site.py` writes pages but never deletes dirs whose slug left `projects.json`, so ghosts re-accumulate on every rename/removal. Add a guarded prune step? Needs Nick's ok (auto-delete behavior).
- **Data hygiene (Nick's call, not yet done):**
  - Typo'd canonical slugs still live (fixing changes the live URL): `harley-davidson-the-linage`, `louis-vuitton-virgial-abloh-tribute`, `tiffany-co-jewlery`, `hennesy-more-is-made-by-many`.
  - `montell-fish-who-did-you-touch` — vimeo stored as a `/manage/` URL; normalize to plain `https://vimeo.com/1210301476`.
  - 6 posted projects with BLANK credits: `polo-ralph-lauren-timeless-america`, `lincoln-wish-list`, `monse-yoonmi`, `coke-evergreen`, `super-she-supershe-island`, `vogue-stand-on-the-word`.
  - Deck detail-credits gap: 105/197 films have no `deck_credits` entry (detail shows only Color).
  - Deck junk film label `wdytln-h-264-files` (filename leaked into the label).
- **Standing items (from `02_site_reference.md`):** nickmetcalf.com DNS cutover (waiting on Nick); Salomon x L'Art de l'Automobile has no video file anywhere; possible dup pairs for Nick to resolve; Vimeo "copy_masters" accidental upload to delete; confirm Tory Burch SPF26 vs SPR26 credits.

---

_Older history: see git log and the dated project-memory notes (`site_debug_20260718.md`, `deck_design_20260718.md`, `deck_reframe.md`)._
