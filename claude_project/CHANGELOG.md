# CHANGELOG — where we left off

Reverse-chronological. **Top entry = current state.** At the end of each session, add what shipped and refresh the Open threads.

---

## website 2026.0017 — 2026-07-19

Shipped — deck ARCHIVE top-band alignment cleanup (deck-only: `js/deck.js` + `css/deck.css` + `_build/deck_main.html` + rebuilt `deck/index.html`).

Nick: the top area "jumps around a lot" — search bar looked low, the results count sat on its own line under the search, and turning a filter on dropped the thumbnails down. Fixed all three:

- **Results count moved to the tag line.** The `#showing` span (under the search box) was removed from `deck_main.html`; `buildChips` now renders the count as the first item on the chips row (`.chip-count`, e.g. `301 results  [ Color: Mixed × ]  clear all`). `apply()` no longer writes `#showing`.
- **Search + tag line on the same line.** `#ctrl` and `#chips` both use `padding:0 0 12px` and start at the same `#deckrow` top; each is a 29–30px `align-items:center` band, so the search underline and the chips/count baseline-align across the two columns (was: search ~14px low, count on a wrapped 2nd line).
- **Grid no longer jumps when filters toggle.** `#chips` now reserves a FIXED `min-height:30px` (border-box) always, replacing `#chips:empty{padding:0}`. The thumbnail grid top is now constant (~108px) whether 0 or N filters are active — before, adding the first filter grew the empty-height chips row and pushed every thumbnail down. Verified headless @1440 (grid top 107 unfiltered vs 108 filtered — 1px) and @390 (count on tag line, no errors).

Open threads: unchanged. Minor: at 501–760px (tablet) FILTERS sits centered at the right end of the nav row; desktop search placeholder truncates at rail width.

---

## website 2026.0016 — 2026-07-19

Shipped — two cosmetic follow-ups to 2026.0015 (deck-only: `js/deck.js` + `css/deck.css` + rebuilt `deck/index.html`).

- Detail `[ watch ]` link relabeled **`[ watch video ]`** (both the Vimeo-overlay and the no-ID fallback path).
- The `tags:` label is now the **same grey as the tags themselves** (`#ovkw .ml` → `var(--dim)`, was `--fg`) so it reads as part of the list, not a heading.

Open threads: unchanged.

---

## website 2026.0015 — 2026-07-19

Shipped — three deck detail/archive refinements (deck-only: `js/deck.js` + `css/deck.css` + `_build/deck_extras.html` + `_build/build_deck.py` + rebuilt `deck/index.html`).

- **Multi-term search.** The search box now supports stacking terms: typing still filters live, but pressing **Enter** commits the current text as its own removable `Search: …` chip (AND-combined) and clears the box so another term can be added. `state.qs[]` holds committed terms; `state.q` is the live one. Clicking a keyword `.kwtag` in the detail view now also pushes a committed chip instead of replacing the live query. `clearAll`/`exitProject`/`route` reset `qs`.
- **Detail "tags:" line — fixed height.** The keyword list (`#ovkw`, which sits above the credits) now always renders, prefixed with a `tags:` label (em-dash when empty), and is locked to a **fixed 2-line height** (`height:2.9em` + `-webkit-line-clamp:2`, verified 37.69px constant across stills) so the credits block below never jumps when stepping between stills with different tag counts.
- **`[ watch ]` → on-page Vimeo overlay.** Clicking watch no longer routes to the (hidden, `noindex`) project page — it opens a black full-screen lightbox (`#vov`) that embeds the film's Vimeo player with the same minimal-chrome params as the project pages (autoplay on desktop, muted-load on mobile). Vimeo IDs are injected at build as `window.DECK_VIMEO` (`build_deck.py` parses `data/projects.json`, keyed by `page_slug`). Esc / [ CLOSE ] / backdrop click closes it and stops playback, leaving the detail overlay open underneath. If a film has no Vimeo ID mapped, `[ watch ]` falls back to the old project-page link. Verified headless @1440 + @390: chips stack, tags line constant-height, watch opens the iframe (no nav) and Esc restores the detail.

Open threads: unchanged. Minor: at 501–760px (tablet) FILTERS sits centered at the right end of the nav row (space-between) — fine; desktop search placeholder truncates at rail width.

---

## website 2026.0014 — 2026-07-19

Shipped — mobile FILTERS is now a REAL nav item (deck-only: `js/deck.js` + `css/deck.css` + rebuilt `deck/index.html`).

- The 2026.0011–0013 mobile FILTERS used `position:fixed` with a per-breakpoint `top: calc(margin-top + 3*(height-text+gap-small))`. That calc assumed a nav line-pitch that didn't match real devices — on Nick's phone FILTERS landed on the CONTACT/ARCHIVE lines and "moved independently." Root cause: hardcoding a position instead of tracking the actual nav.
- Fix: `deck.js` moves `#fbtn` INTO the `<header>` on load (before the sticky positioner), so FILTERS stacks as a genuine 4th nav item using the nav's own flex layout/spacing — perfectly aligned under WORK/CONTACT/ARCHIVE, rides with the sticky nav, robust across fonts/devices. Desktop keeps `#fbtn{display:none}` (rail always shown).
- Removed all the fragile mobile hacks: `#fbtn` fixed/`top` calcs, `#ctrl` padding-top, `#deckrow` negative margin. The search now simply pins below the FULL header (which includes FILTERS) via the existing JS sticky-top — thumbnails scroll behind the whole opaque nav+search band, no overlap, no image bleed. Verified headless @390 (4-item stack, drawer opens, pinned search + thumbs behind on scroll) and @1440 (FILTERS hidden, desktop unchanged).

Open threads: unchanged. Minor: at 501–760px (tablet) FILTERS sits centered at the right end of the nav row (space-between) — fine; desktop search placeholder truncates at rail width.

---

## website 2026.0013 — 2026-07-18

Shipped — **cache-buster on the deck stylesheet link** (the real reason today's deck CSS changes "looked the same" for Nick).

- `deck/index.html` linked `../css/deck.css` with NO version query, while `main.css` had `?v=<VER>`. So browsers cached deck.css indefinitely and never re-fetched it — every deck.css-only push (2026.0010–0012) silently served stale CSS to anyone with a warm cache. The "one-shot: push css/deck.css alone" model in the docs was WRONG.
- Fix: `build_deck.py` now stamps a **content-hash** buster onto the link — `../css/deck.css?v=<md5(deck.css)[:10]>`. The hash changes iff deck.css changes, so the browser re-fetches exactly when needed. **Consequence: a deck.css edit now REQUIRES rebuilding + committing `deck/index.html`** (not a push-css-alone one-shot). Docs updated (`04_deck.md`); build_deck comment corrected.
- This deploy carries the current deck.css (hash `f630d43adc`) which already includes all of today's work: desktop grid at Work-top, mobile FILTERS as 4th nav item, filter accordion, detail nav consistent at all widths, and the pinned-with-thumbnails-behind mobile search (2026.0012). A normal reload now picks them all up.

Open threads: unchanged. Minor: desktop search placeholder truncates at rail width.

---

## website 2026.0012 — 2026-07-18

Shipped — deck mobile search: keep it PINNED, thumbnails scroll behind (deck-only, `css/deck.css` only). Supersedes 2026.0011's non-sticky approach — Nick wanted the search bar pinned in place with the grid hiding behind it, not scrolling away.

- Mobile `#ctrl` is back to sticky (JS pins `top` = header height). Added `padding-top: (height-text + gap-small)` — the padding is opaque (`#ctrl` bg), so when stuck the search field drops one nav-line BELOW the fixed FILTERS line and the search bg runs flush from the header down (no gap → no image bleed; thumbnails scroll behind the whole nav+FILTERS+search band).
- `#deckrow{margin-top: -(height-text + gap-small)}` on mobile cancels that padding at REST so the resting gap under the nav is unchanged (negative margin on the parent doesn't move the child's sticky pin). Verified headless @390/600: rest input at 139/78 (same as before), scrolled input pins at 117/71, `#ctrl` box top === header bottom (no bleed), input below FILTERS.
- `#fbtn{background:var(--color-bg)}` kept so FILTERS stays legible over the band.

Open threads: unchanged. Minor: desktop search placeholder truncates at rail width.

---

## website 2026.0011 — 2026-07-18

Shipped — deck mobile top-chrome fix (deck-only, `css/deck.css` only — linked file, one-shot):

- **Mobile search no longer rides up under the nav on scroll.** In 2026.0010 the search was `position:sticky` pinned at header height (~94px), but the fixed FILTERS 4th-nav line sits at ~84–102px, so scrolling let the search touch/overlap FILTERS (Nick: "search bar can get too close to top nav"). Fix: on mobile `#ctrl{position:static}` — the search scrolls WITH the grid instead of pinning, so it can't collide with the nav. Resting spacing under the nav is unchanged (search still at the same Y at scroll-top). Desktop search stays sticky in the left column (unaffected — the `position:static` override is inside the ≤760px block).
- **`#fbtn{background:var(--color-bg)}` on mobile** so the fixed FILTERS label reads cleanly when it floats over the grid on scroll (was transparent → images showed through). Verified headless light + dark, at 390 and 600px: search scrolls away, nav+FILTERS stay, no image bleed, no overlap.
- Tried first (reverted): pinning the search below FILTERS with a JS offset, then a padding/negative-margin trick — both just relocated the image-bleed gap. Non-sticky is the clean fix.

Open threads: unchanged. Minor: on mobile the FILTERS label makes a small opaque tab over the first grid row when scrolled (it's a fixed nav affordance — acceptable); desktop search placeholder truncates at rail width.

---

## website 2026.0010 — 2026-07-18

Shipped — deck (ARCHIVE) design pass #3 (all deck-only):

- **Grid now starts at the same Y as the Work-page thumbnails (desktop).** Restructured `_build/deck_main.html`: `#ctrl` (search) now lives INSIDE a new `#leftcol` ABOVE the rail `#side`, so the grid column rises to the top of `#deckrow`. `#leftcol` = `flex:0 0 210px` on desktop (`#deckrow` `align-items:stretch` so the stretched column keeps the sticky search + rail pinned the whole scroll) and `display:contents` on mobile (search stays a full-width sticky bar, `#side` still the off-canvas drawer). `#chips:empty{padding:0}` + grid layout `top:0` remove the last reserved space. Verified headless: deck cell top === Work thumb top (78px @1440, both at mainTop).
- **Mobile FILTERS → left, as a 4th nav item** (Nick's call). `#fbtn` `position:fixed; left`; `top` per breakpoint (4th line below WORK/CONTACT/ARCHIVE at ≤500px; one line under the single-row nav 501–760px). Bracket pseudo `content:none` on mobile so the label aligns to the nav margin. (Mobile nav is a hard `flex-direction:column` stack at ≤500px in main.css — that's why top-left couldn't be a bare corner pin.)
- **Filter rail is now an accordion** — opening one section auto-collapses the others (`deck.js buildSidebar`), keeping the rail short.
- **Detail overlay keeps the compact `[ < ] [ CLOSE ] [ > ]` top bar at ALL widths.** `deck.css` overrides main.css's `>=1367px` `#single-bar` rule (which flipped it to a fixed full-viewport grid with screen-edge sans-serif arrows) back to the sticky bracketed top row, scoped to `#ov`.
- Edited: `_build/deck_main.html`, `css/deck.css`, `js/deck.js`, regenerated `deck/index.html`. Doc `04_deck.md` updated. Deploy: deck-only, pushed `[auto-build]` (skips the site rebuild); `deck/index.html` committed directly (Action doesn't run build_deck).

Open threads: unchanged (deck noindex decision; cosmetic URL≠label; project-from-/selects/ closes to Work; deck data hygiene; recurrence-prune; nickmetcalf.com DNS). Minor: mobile grid still sits below the search (search is full-width above it — inherent; only desktop aligns to Work); desktop search placeholder truncates at rail width.

---

## website 2026.0009 — 2026-07-18

Shipped — deck (ARCHIVE) design pass #2 (all deck-only):

Main grid page:
- **Mobile FILTERS now sits top-right, in line with the nav.** Moved `#fbtn` OUT of `#ctrl` in the DOM (it was `position:fixed` but trapped under the header because `#ctrl` is `position:sticky;z-index:8` = its own stacking context, so the header at z:9 painted over it). Now `#fbtn` is a direct child of `<main>`; mobile CSS pins it `position:fixed; top/right = margins; z:10`.
- **Content top spacing matches the Work page** on mobile: with FILTERS out of the control-row flow (+ `#ctrl` padding-top zeroed on mobile), the search now starts at the same top offset as the Work grid.
- **Removed the "Filters" title AND "Clear all" from the left rail.** Rail head now holds only the mobile close ×; hidden entirely on desktop. Clear all moved next to the active-filter chips — renders as a `.chip-clear` ("clear all") only when ≥1 filter is set (`clearAll()` refactored out of the old `#clearall` binding).

Detail overlay:
- **Big view locked to a consistent 16:9 height** (`#ovimg` → `aspect-ratio:16/9; object-fit:contain; background:#000`). Non-16:9 stills pillar/letter-box inside the frame (verified 1.26 → pillarbox, 2.40 → letterbox, both boxed to 1180×664).
- **Metadata keyword tags moved above credits** (DOM reorder in `deck_extras.html`: `#ovkw` now precedes the `.project-credits` block → tags, then credits, then the shot-data/filters list).
- **"open film page" link → "[ watch ]".**

- Edited: `_build/deck_main.html`, `_build/deck_extras.html`, `css/deck.css`, `js/deck.js`, regenerated `deck/index.html`. Docs `04_deck.md` updated. Verified headless: desktop rail (no title/clearall) + chip clear-all + mobile FILTERS top-right in line with nav + search at Work top spacing + detail 16:9 pillar/letterbox + tags-above-credits + [ watch ].
- Deploy: deck-only, pushed `[auto-build]` (skips the site rebuild); `deck/index.html` committed directly (Action doesn't run build_deck).

Open threads: unchanged from 2026.0005 (deck noindex decision; cosmetic URL≠label; project-from-/selects/ closes to Work; deck data hygiene; recurrence-prune; nickmetcalf.com DNS).

---

## website 2026.0008 — 2026-07-18

Shipped — deck (ARCHIVE) design pass:
- **Sort/Random control removed** from the controls row (`deck_main.html`; `$('sort')` refs guarded in `deck.js`; `#sortwrap` CSS dropped). Grid still defaults to a shuffled order internally.
- **Filter toggle is context-aware:** on desktop (≥761px) the `[ FILTERS ]` button is hidden and the filter rail is always shown (page is wide enough — no toggle needed). On mobile the FILTERS toggle now sits on its own line **below the nav, aligned top-right** (was centered above search).
- **Search box width = rail width** on desktop (`#searchwrap` flex:0 0 210px) so its right edge lines up with the filter rail's right edge.
- **Theme now FOLLOWS THE SITE.** Deck no longer force-dark: body class dropped `dark-mode` (`build_deck.py`), and `deck.js` uses the shared `mode` localStorage key (same as `main.js`) instead of its own `deckmode`/dark default. The detail overlay (`#ov`) is still forced black in CSS.
- **Removed the ▼ caret glyphs** from filter section headers (`.car` span dropped in `deck.js`; `.sec-h .car` CSS removed).
- **Hid Aspect Ratio and Number of People** from the filter rail (`hide:1` on the `arb` + `pp` SECTIONS) — data kept (still in detail view + similarity scoring), just not offered as filters.
- Edited: `_build/deck_main.html`, `_build/build_deck.py`, `css/deck.css`, `js/deck.js`, regenerated `deck/index.html`. Docs `04_deck.md` updated. Verified headless at 1280px (desktop: no sort, no toggle, rail always shown, search ends at rail edge, light theme, no carets, no ratio/people) + 390px (mobile: FILTERS below nav top-right) + detail overlay forced black over a light page.
- Deploy: deck-only change (doesn't affect `build_site.py` output), so pushed with `[auto-build]` to skip a needless site rebuild; `deck/index.html` committed directly since the Action doesn't run `build_deck.py`.

Open threads: unchanged from 2026.0005 (deck noindex decision — still noindex; cosmetic URL≠label; project-from-/selects/ closes to Work; deck data hygiene; recurrence-prune; nickmetcalf.com DNS).

---

## website 2026.0007 — 2026-07-18

Shipped:
- **Direct `git push` deploy path enabled from the cloud container.** Verified an authenticated push works (auth was the only old blocker; `github.com` HTTPS git is reachable for push, not just fetch). Recipe: clone → `device_stage_files` the token from the connected website folder (`token/git-token`) → push with an inline credential helper (`git -c credential.helper='!f(){ echo username=x-access-token; echo "password=$TOKEN"; }; f' push`), token read from the staged file into `$TOKEN`, never printed/committed.
- This is now the PRIMARY deploy channel (faster: one commit for many files, no browser, no per-file sha, no forced 90s wait). Browser Contents API is the FALLBACK (used only if the token can't be staged). `api.github.com` stays proxy-blocked, so the browser remains the backup.
- This changelog entry + VERSION 0007 + `00_START_HERE.md` deploy section were themselves pushed via the new `git push` path (dogfooded). Docs are non-trigger paths, so no Action fired.

Open threads: unchanged from 2026.0005 (deck noindex decision, cosmetic URL≠label, project-from-/selects/ closes to Work, deck data hygiene, recurrence-prune, nickmetcalf.com DNS).

---

## website 2026.0006 — 2026-07-18

Shipped:
- Workflow change: the handoff / copy-paste kickoff prompt is now ON DEMAND — produced only when Nick says "handoff", not automatically every turn. Updated HANDOFF_CHECKLIST item 6 (+ intro) and project memory.

Open threads: unchanged from 2026.0005 (deck noindex decision, cosmetic URL≠label, project-from-/selects/ closes to Work, deck data hygiene, recurrence-prune, nickmetcalf.com DNS).

---

## website 2026.0005 — 2026-07-18

Shipped — site nav reorder (root = Work):
- Homepage `/` is now the **WORK** grid: all visible projects in `arch_order` (old archive content), category filters (ALL/Commercial/Music Video/Beauty/Long Form/Car) REMOVED. Body `page-archive`; nav-data ctx `archive`.
- Old landing grid ("Selected Works") renamed **Selects**, moved to `/selects/`, UNLINKED from nav (still reachable, indexable).
- `/archive/` page retired → redirect stub to `/` (old bookmarks resolve).
- Deck relabeled **ARCHIVE** in nav; `/deck/` path unchanged; deck `<title>` → "Archive". Deck still `noindex`.
- Nav is now `WORK`→`/` · `CONTACT`→`/contact/` · `ARCHIVE`→`/deck/` (labels decoupled from URLs).
- `js/main.js`: project `[CLOSE]` returns to `/` (root Work) for archive/landing ctx (was `/archive/`).
- Admin tabs relabeled **Selects** / **Work** (internal data-view keys `landing`/`archive` unchanged).
- Edited: `data/site.json`, `_build/build_site.py` (build_index→Work root, new build_selects, build_archive→redirect), `_build/build_deck.py` (title), `js/main.js`, `admin/index.html`. Docs `02_site_reference.md` + `04_deck.md` updated.
- Deploy: 5 source files pushed via Contents API, git-blob-sha verified byte-exact vs local; `deck/index.html` patched directly (Action doesn't run build_deck). Build Action `485ca11` succeeded; live-verified (root 103 cards/0 filters, /selects/ 20, /archive/ redirect, /deck/ title Archive, project close → /).
- Backup before this work: tag `backup-2026.0003` + branch `backup/2026-07-18-pre-bigchanges` at `587617f` (roll back = reset main to either).

Open threads:
- Deck (ARCHIVE) is now a linked nav item but still `noindex` — decide whether to make it indexable.
- Cosmetic URL≠label: ARCHIVE nav → `/deck/`; old `/archive/` shows a redirect.
- Closing a project opened from `/selects/` returns to the Work grid, not Selects (no `selects` navctx) — refine if wanted.
- Prior, still open: deck data hygiene (canonical slug typos, 6 blank credits, 105/197 films missing deck credits, junk film label, Vimeo URL normalization); `build_site` recurrence-prune for orphaned dirs (awaiting approval); nickmetcalf.com DNS cutover (pending).

---

## website 2026.0004 — 2026-07-18

Shipped:
- Workflow doc updated: Nick no longer uses a Claude Project — each new chat is a fresh, standalone conversation seeded by the copy-paste kickoff prompt + auto-loaded project memory. Noted at the top of claude_project/00_START_HERE.md.
- Standing preference recorded: every handoff must END with a fenced code block Nick can one-click-copy — a ready-to-paste kickoff prompt for the next conversation (lead line `website YYYY.NNNN — new session.`, role reminder, this session's context/open threads, restore-point refs). Added as item 6 in claude_project/HANDOFF_CHECKLIST.md so it can't be skipped.

Open threads:
- Big changes incoming — restore point is origin branch `backup/2026-07-18-pre-bigchanges` + tag `backup-2026.0003` at HEAD 587617f.
- Deck data hygiene: typo canonical slugs (harley -linage, virgial, jewlery, hennesy); 6 posted projects blank credits; 105/197 deck films missing deck_credits; wdytln-h-264-files junk label; montell-fish vimeo URL normalize.
- build_site recurrence-prune for orphaned slug dirs (needs Nick's ok on auto-delete).
- nickmetcalf.com DNS cutover (waiting on Nick).
- Confirm on phone: deck swipe, blinking cursor, mobile square gallery, filters-above-search, forced-dark overlay.

---

## website 2026.0003 — 2026-07-18

Shipped:
- Structural fix so deck CSS tweaks are ONE-SHOT: deck/index.html now LINKS css/deck.css (<link rel=stylesheet href=../css/deck.css>) instead of inlining it in a <style> block. Editing deck.css + pushing that one file now updates the live deck with no deck/index.html rebuild. build_deck.py updated to emit the link; deck.js stays inlined (carries per-build window.DECK_LANDING data). Deck page shrank 43KB→32KB.
- This removes the mechanism behind the recurring nav/deck drift (see 2026.0002): there's no longer a second, inlined copy of deck styling to fall out of sync. Verified headless parity (landing vs deck) still 1:1 at 2560/1440/1100/900/700/420px after the relink.

Open threads:
- Deck data hygiene: typo canonical slugs (harley -linage, virgial, jewlery, hennesy); 6 posted projects blank credits; 105/197 deck films missing deck_credits; wdytln-h-264-files junk label; montell-fish vimeo URL normalize.
- build_site recurrence-prune for orphaned slug dirs (needs Nick's ok on auto-delete).
- nickmetcalf.com DNS cutover (waiting on Nick).
- Confirm on phone: deck swipe, blinking cursor, mobile square gallery, filters-above-search, forced-dark overlay.

- SAFETY BACKUP taken before big changes: origin branch `backup/2026-07-18-pre-bigchanges` + tag `backup-2026.0003`, both pinned to HEAD 587617f (complete, incl. all assets). Roll back by resetting main to either ref. Portable source-only zip also saved to Nick's Mac.
- ⚠️ Nick is about to make BIG CHANGES next session — the backup above is the restore point.
---

## website 2026.0002 — 2026-07-18

Shipped:
- CORE FIX for the recurring landing-vs-deck nav drift — and this time it WAS live (prior 2026.0001 "stale local copy" diagnosis was wrong). Root cause: the deck page carried its OWN copy of the nav column-gap/wrap rules in css/deck.css (inlined into deck/index.html), so it never tracked css/main.css. Landing used a 3-item-tuned desktop gap clamp(6rem,31vw,48rem) with flex-wrap:wrap → the 4th item (DECK) wrapped to a 2nd line at wide widths; deck used a tighter gap → all 4 on one centered row. Two sources = perpetual divergence.
- Made css/main.css the SINGLE SOURCE OF TRUTH: desktop gap clamp(2.5rem,10vw,9rem), tablet/default clamp(1.5rem,7vw,5rem), + flex-wrap:nowrap at min-width:769px so DECK can NEVER drop to a 2nd line. Deleted the duplicate header column-gap/wrap overrides from css/deck.css; rebuilt deck/index.html to drop the inlined override; cache-bust'd main.css (?v=2026000200) on landing + deck so visitors pull the new CSS.
- Verified headless (Chromium) at 2560/1440/1100/900/700/420px: landing and deck nav row-count matches at every width — 1 centered row on all desktop widths, identical wrap on phone.

Open threads:
- Deck data hygiene: typo canonical slugs (harley -linage, virgial, jewlery, hennesy); 6 posted projects blank credits; 105/197 deck films missing deck_credits; wdytln-h-264-files junk label; montell-fish vimeo URL normalize.
- build_site recurrence-prune for orphaned slug dirs (needs Nick's ok on auto-delete).
- nickmetcalf.com DNS cutover (waiting on Nick).
- Confirm on phone: deck swipe, blinking cursor, mobile square gallery, filters-above-search, forced-dark overlay.

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
