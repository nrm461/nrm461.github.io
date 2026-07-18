# Deck Reference — the frame-library sub-site

Add as Project Knowledge. Covers `https://nrm461.github.io/deck/`, which the main-site docs do **not** describe.

## What it is
- A ShotDeck-style, searchable **still-frame library** built from Nick's graded work: ~6,236 frames across 197 films/projects, filterable by film, keyword, color/hue/brightness, shot type, composition, lighting, aspect, format, etc.
- Lives as a sub-page of the portfolio. It should feel like a **native part of nrm461.github.io**, not a bolted-on tool. (That integration is in progress and **not yet "right"** — see "Open design problem" at the bottom.)

## CRITICAL — how the deck differs from the main site
- The main site is Python-generated (`_build/build_site.py` → HTML), and the rule there is "never edit generated HTML."
- **The deck is the opposite.** `deck/index.html` is a single, **hand-authored**, self-contained ~40 KB file (inline CSS + JS). **Edit it directly.** `build_site.py` does not touch it. There is no generator and no auto-build Action for the deck.

## Files
- `deck/index.html` — the whole app: virtualized justified-grid (windowed rows + binary search on scroll), filter drawer, detail overlay, hash routing (`#/movie/<slug>~<Name>`), admin format-tagging. **This is the source. Edit here.**
- Runtime data (fetched from `../data/`):
  - `data/deck.json` — the frames (minified): film list + per-frame metadata.
  - `data/deck_tags.json` — extra tags.
  - `data/deck_format.json` — per-film / per-still capture-format overrides (written by admin mode).
  - `data/deck_credits.json` — per-film Director / DP / Editor.
- Frame images: `assets/deck2/*.jpg` (~6,297 on disk). **Never crop the source images** — the mobile "square" look is CSS `object-fit:cover` only.
- **Landing scope**: on load the deck fetches the main index (`../`), scrapes the featured project slugs, and defaults the view to only those stills (~736 of 6,236) so the first screen looks curated. Any filter/search/pick — or the "explore all 6,236" link — expands to the full set. This stays in sync with the portfolio landing automatically.
- **Admin**: `?admin=1` unlocks per-film / per-still format tagging; it saves `deck_format.json` via the GitHub API using `localStorage.ghtoken`.

## Design system — must mirror the main site (`css/main.css`)
- **Font**: `--font:'OCRF',Courier,monospace`, weight 300, `liga` off, antialiased. OCRF isn't hosted (`fonts/` doesn't exist), so both the site and the deck render **Courier** — that's the match, not Helvetica.
- **Color**: two-tone, driven by `--color-bg` / `--color-text`. `:root` = white/black (light); `.dark-mode` = black/white. **The deck defaults to dark.**
  - Dark default uses the deck's **own** `localStorage` key `deckmode` (NOT the site's shared `mode`), so a "light" choice on the portfolio can't force the deck light.
  - **CSS gotcha that bit us twice**: the derived tokens (`--bg, --fg, --dim, --dim2, --line, --panel, --field, --accent`) must be declared on **both** `:root` **and** `.dark-mode` — currently `:root,.dark-mode{ … }`. If declared only on `:root`, they bake in the light values and get inherited, so dark mode only half-flips (background stays white even with the class on). Keep both scopes.
- **Toggle**: the site's exact two-circle control (`#toggle-mode` > `.white`/`.black`), same click behavior as `js/main.js`. Currently top-right of the deck's control bar.
- **Nav**: WORK / ARCHIVE / DECK / CONTACT, centered, uppercase, same clamp spacing as the site header, all links equal weight.
- **Vocabulary**: uses the site's `[ ]` bracket treatment for the Filters trigger.

## Deploying the deck — READ THIS, it saves hours
From a **Cloud** Cowork session the deck cannot ship the normal way:
- `git push` is blocked (auth wall) and the sandbox can't reliably reach `api.github.com`. The auto-build Action doesn't apply (nothing to generate).
- Deploy path = **Claude in Chrome + GitHub Contents API PUT**, from a tab already on `nrm461.github.io` (that origin has the admin token in `localStorage.ghtoken`):
  1. Edit `deck/index.html`; syntax-check the script (`new Function(scriptBody)`); compute the git-blob-SHA locally: `sha1('blob ' + byteLength + '\0' + bytes)`.
  2. Copy the file into `/mnt/user-data/outputs/` (the `file_upload` tool only accepts the session's upload/output folders).
  3. In the page, inject an `<input type=file>`; use the **`file_upload`** tool to load the local file into it. **Never hand-paste the file's base64 through a tool** — it corrupts (homoglyph / generation errors on long random strings). `file_upload` is a clean binary channel.
  4. In-page: FileReader → `arrayBuffer` → bytes → base64; **recompute the git-blob-SHA in the browser and assert it equals the local one**. This gate catches any corruption before writing.
  5. GET the live file's `sha`, then PUT to `https://api.github.com/repos/nrm461/nrm461.github.io/contents/deck/index.html` with `{message, content:<base64>, sha:<current sha>, branch:'main'}` and `Authorization: token <localStorage.ghtoken>`.
  6. Re-sync the local clone: `git fetch origin main && git reset --hard origin/main`.
- **Pages CDN is slow** (~30–90 s to propagate). Verify with a cache-busted URL (`?cb=…`) and re-check `getComputedStyle`; the first reload often still serves the old file — wait and reload.
- **Shortcut**: if the task runs **"On your computer"** instead of the cloud, normal `git push` / publish works and none of this browser dance is needed.

## Open design problem — the reason for the July 2026 handoff
Type + color + dark-default + toggle now match the site, but Nick's read is "**better but still not right**," and he can't fully name why. Leading hypothesis: the remaining mismatch is **structural, not surface**.
- The deck still reads as a dense **database tool**: tight justified-masonry rows (5 px gaps, edge-to-edge), a checkbox/slider filter **drawer**, hover-only labels, a metadata-table **modal**.
- The portfolio reads as an airy **gallery**: 4-column fixed grid, generous margins/row-gaps, uniform ~1.7:1 cards with "CLIENT | TITLE" labels **under each**, full-page projects, inline `[ ]` bracket filters.
- So we matched the paint but not the architecture. The open decision (needs Nick): how far to push the deck toward the gallery layout — grid geometry, spacing, filter UI, per-card labels, detail view — vs. keeping tool-grade density for browsing 6 k frames. Diagnose and agree on direction **before** restyling again.
