# Deck Reference — add as Project Knowledge

The `/deck/` frame library. Current as of July 18, 2026.

## What it is
`https://nrm461.github.io/deck/` — a ShotDeck-style searchable library of stills from Nick's graded work (~197 films, ~6,236 tagged frames). As of the 2026-07-18 reorder the deck IS the **ARCHIVE** nav item (`/deck/` unchanged); still `noindex` for now (flagged — revisit if it should be indexable now that it's linked). **Identity: an advanced search area**, not a curated reel — the point is that a client can find "aerial food shots on a beach that Nick colored." So it stays a *tool* (dense grid, deep filters, per-still metadata) but must look/feel like a native part of the portfolio.

Admin mode: append `?admin=1` (needs `localStorage.ghtoken` on an nrm461.github.io tab — same token as `/admin/`). Adds the FORMAT bulk-editor panel + per-still format override.

## Architecture — the deck is GENERATED, single-source
The recurring "it doesn't match the site" churn had one root cause: the deck's shell (head / nav / footer) was **hand-authored separately from `_build/build_site.py`**, the generator that produces that markup for every other page. Two sources of the same markup → drift. The fix eliminates the second source:

- **`_build/build_deck.py`** `import build_site` and calls its **`page()`, `header()`, `footer()`** to build the deck's shell. So the deck's `<head>`, nav, and footer are *byte-identical* to every other page, by construction (verified: `build_site.footer()`/`header()` strings appear verbatim in the output). `build_site.py` itself is **untouched** — zero risk to the live pages.
- The **detail view** (the still overlay) reuses the real project-page components verbatim: `#single-bar` nav (`<a id=prev>&lt;</a><a id=close>[ CLOSE ]</a><a id=next>&gt;</a>` — brackets/arrows come from `main.css`; never add literal brackets or they double), `.module-project_info` title (uppercased by main.css), `.project-credits.credits-v2 > .credits-hero` + `.credits-rest`, and `.project-gallery`. Canonical template: any project page, e.g. `benson-boone-the-time-of-my-life/index.html`.
- **`main.css` is LINKED** (not copied), so colour, type, spacing, and the light/dark toggle track the site automatically.

### Files
| File | Role |
|---|---|
| `_build/build_deck.py` | Imports build_site; deck nav is inherited from site.json (WORK/CONTACT/ARCHIVE — the deck itself is the ARCHIVE item, `link-active`); wraps the body partials with page/header/footer; **inlines** deck.css + deck.js into one self-contained `deck/index.html`. |
| `css/deck.css` | Deck-only styles (derived tokens `--panel/--field/--dim/--line`, controls, filter rail, deck grid, detail overrides). References main.css vars. |
| `js/deck.js` | The grid/filter/modal engine + light/dark toggle that **FOLLOWS THE SITE** (shares the site's `mode` key — no forced default; was `deckmode`/defaults-dark, changed 2026-07-18) + device-class + sticky-pin snippets. Fetches `../data/deck*.json`. |
| `_build/deck_main.html` | The deck's `<main>` inner: controls row + filter rail + grid column. |
| `_build/deck_extras.html` | The filter scrim, admin panel, and detail-overlay skeleton (built from the site's project-page classes). |

To change the deck's **chrome** → edit `build_site.py` (whole site stays consistent). To change **deck-only** behaviour → edit `deck.css`/`deck.js` and re-run `build_deck.py`. No more hand-matching.

Build: `python3 _build/build_deck.py` → writes `deck/index.html`.

## Shared design vocabulary (use these names)
Inherited from the main site: **site nav** (WORK/ARCHIVE/DECK/CONTACT); **single-bar** (`[ < ] [ CLOSE ] [ > ]` detail nav — desktop = arrows at the screen edges, mobile = sticky top bar); **credits-hero** (Dir./DP/Edit/Color block); **project-credits** (2-column `label - value` list); **project-gallery** (3-column still grid); **card** (a WORK/ARCHIVE tile = thumb + `CLIENT | TITLE`).
Deck-specific: **controls** (search + `[ FILTERS ]`, under the nav — **Sort/Random removed 2026-07-18**; on desktop the FILTERS toggle is hidden and the rail is always shown, and the search box width = rail width so its right edge lines up with the rail; on mobile FILTERS is `position:fixed` in the top-right corner, in line with the nav — it lives OUTSIDE `#ctrl` in the DOM so `#ctrl`'s sticky stacking context doesn't bury it under the header, and the search then sits at the same top spacing as the Work page); **filter rail** (left credits-style facet list; always shown on desktop, full-screen takeover on mobile — **no "Filters" title, no Clear all in the rail as of 2026-07-19**; the rail head holds only the mobile close ×); **deck grid** (the justified masonry thumbnail wall — no labels; mobile = 3-up soft-crop squares); **detail view** (the still overlay); **shot data** (the technical fields, rendered as part of the credits); **chips** (active-filter `[ … ]` row above the grid — **Clear all now renders here, as a `.chip-clear`, only when ≥1 filter is active**).

## Design decisions
- Titles: `CLIENT | TITLE` (pipe, no dash/quotes), UPPERCASE (via `.module-project_info`).
- Deck grid: dense justified masonry, **no labels**; mobile = 3-up soft-crop squares.
- Filters: full facets kept, but styled as a **credits-style list** (plain text, no divider lines, an active pick shows as `[ bracket ]`). A search field is always visible up top so the page reads as "search area."
- Detail view: the big still (`#ovimg`) is **locked to a 16:9 frame** (`aspect-ratio:16/9` + `object-fit:contain` over black) so every big view is the same height — non-16:9 stills pillar/letter-box inside it (2026-07-19). Order under the image: **keyword tags first (`#ovkw`), then credits (`#ovcredits`), then the shot-data/filters list (`#ovmeta`)** — tags moved above credits 2026-07-19. Shot-data fields are still a `.credits-rest` `label - value` block (no separate "shot data" header). The film-page link reads **`[ watch ]`** (was "open film page"). The film's other stills show below via `.project-gallery`. No separate "deck project page".
- Landing shows **all** ~6,236 stills (removed the "N featured / explore all" text).

## Data model
- **`assets/deck2/<slug>/NNNN.jpg`** — the frames (480px, ~100 MB). Mid-shot two-pass extraction, SAR-normalized, junk auto-dropped.
- **`data/deck.json`** (~1.1 MB) — `films[{slug, label, cats, ar, dar, page, page_slug, dur, frames[[file, pal12, weights12, hue, h, s, lum, classes[]]]}]`.
- **`data/deck_tags.json`** (~1.85 MB) — `"slug/NNNN" → {fs, tod, ie, pp, loc, kw[], st[], cmp[], lt[], lty[], fl[]}` (AI-tagged; 10–15 keywords/frame).
- **`data/deck_credits.json`** — `slug → {d, dp, e}` (director / DP / editor handles for the detail credits; Color is always @nick__metcalf).
- **`data/deck_format.json`** — `{films:{slug:fmt}, frames:{"slug/NNNN":fmt}}`; filled by Nick via `?admin=1`. Formats: f35/f16/s8/f65/imax/tape/dig/dlf/anim.

Facets shown in the rail: Genre, Color (12 hues + 7 classes), Color Picker, Brightness, Format, Frame Size, Shot Type, Composition, Lighting, Lighting Type, Time of Day, Int/Ext, Commercial Flags. **Aspect Ratio and Number of People are hidden from the rail (`hide:1`) as of 2026-07-18** — data kept (still shown in the detail view and used by similarity scoring), just not offered as filters. Film is `hide:1` too (drives project routing, not a menu facet). Section headers no longer show the ▼ caret glyph. Top search box matches film label + keywords.

## Deploy
`deck/` is **not** an Action trigger path, so the deck deploys as a single self-contained file via the browser GitHub Contents API (upload the file into an injected file input on an nrm461.github.io tab → PUT with `localStorage.ghtoken`). See `deploy.md` / `03_starter_prompts.md` for the exact steps. The frames + multi-MB data files exceed the browser API and are pushed from Nick's Mac (`push_deck.sh`).

## Status (2026-07-18)
- The generated deck is live at **`deck/preview3.html`** (unlinked preview); renders identically to the hand-authored `preview2.html`. Earlier iterations: `preview.html`, `preview2.html`.
- **To promote:** PUT the generated file to `deck/index.html`, and commit the five source files above so the build is reproducible (`css/`+`js/` are Action trigger paths → a harmless `[auto-build]` runs).
- Backups of the pre-refactor state: repo `_backups/pre-deck-refactor-20260718-042035/` + git tag of the same name.
- Not self-verifiable in the cloud sandbox (Chromium is blocked): the mobile 3-up squares and the detail title clearing the nav — confirm on a phone.
