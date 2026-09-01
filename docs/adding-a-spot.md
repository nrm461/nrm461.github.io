# Adding a spot

The short version: **ask Claude.** "We got the master for Hills, have a look and let's
add it to the site." Everything below is what that does, and how to run it yourself.

## Where it runs

The masters live on the **Mac Studio** at
`/Volumes/Suite/rare_medium/_Personal_Folders/nick_m/_MASTERS/`. That volume does not
mount on the MacBook Air, so the script runs on the Studio — reachable over SSH as
`studio`, with a clone at `~/dev/nrm461.github.io`.

From the Air:

```
ssh studio 'cd ~/dev/nrm461.github.io && git pull -q && python3 _build/add_spot.py Hills'
```

On the Studio itself, just the inner half.

### Getting the result onto GitHub

**The Studio has no GitHub credentials.** It can commit but not push, so `--commit` ends
in `fatal: could not read Username for 'https://github.com'` **after** the Vimeo upload
and the commit have both succeeded. Nothing is lost when that happens — the work is
sitting in a local commit on the Studio.

The reliable sequence is to let the Studio commit, then push from the Air over SSH:

```
# on the Studio — everything except the push
ssh studio 'cd ~/dev/nrm461.github.io && python3 _build/add_spot.py Hills --commit'   # push step fails, fine

# from the Air — collect that commit and push it
cd ~/dev/nrm461.github.io
git fetch ssh://studio/Users/nicholasmetcalf/dev/nrm461.github.io main
git merge --ff-only FETCH_HEAD
git push
```

If the push is rejected as non-fast-forward, the Action's `[auto-build]` commit landed
first: `git fetch origin main && git rebase origin/main`, then push again. **Never resolve
a `data/projects.json` conflict with `-X theirs`** — it drops admin edits.

**To remove this step entirely, run `gh auth login` on the Studio once.** Then `--commit`
finishes on its own and none of the above is needed. Deliberately not done yet.

## What it does

1. **Finds the folder** — fuzzy, case-insensitive match against `_MASTERS`. A full path
   works too. Ambiguous names list the candidates and stop.
2. **Picks the deliverable** — prefers `ProRes/` over `mp4/` over `GEN/`, and `16x9` over
   `FulRes`. It prints what it chose and what came second.
3. **Reads the credits** — see below.
4. **Builds the images** — 600/100/1600 thumbs plus the gallery stills, using `sips`. An
   explicit `stills/thumb.png` wins for the thumbnail; otherwise it takes the middle still.
   **The gallery comes from `ig_selects/` when the folder has one** — those are the frames
   that were posted, already curated and in order — and falls back to `stills/` when it
   doesn't. `--all-stills` forces the raw stills instead.
5. **Uploads to Vimeo** — resumable, with a progress readout. Token in `~/.vimeo-token`.
6. **Appends to `data/projects.json`** — never touching an existing entry.

New spots land in **`group: "hidden"`**: the page builds at `/<slug>/` but is listed only
on the unlinked `/hidden/` index. Promote it with **UNHIDE** in `/admin/` when you're ready.

## Credits

Three sources, in order:

1. **A credits file in the folder** — `credits.txt` or `_credits.txt`. The blank template
   is at `_MASTERS/_credits.txt`; if there isn't one, the script drops a copy in for you.
2. **Instagram** — if the director or DP has posted the spot, their caption is usually the
   full credit block in the site's own format. Ask Claude to go and read it.
3. **The CRM** — a partial block from C41, which knows director, DP and editor:

```
cd ~/dev/CRM/c41-app
node --env-file=.env.local ~/dev/nrm461.github.io/_build/crm_credits.mjs "Hills" \
     --client "Hill's Pet Nutrition" --title "Try Again" > /tmp/credits.txt
```

Then `add_spot.py Hills --credits-file /tmp/credits.txt`.

**Missing credits are not fatal.** The spot stages without them and carries
`needs_review: true` for a later pass.

## Useful flags

| Flag | What it does |
|---|---|
| `--dry-run` | report only, write nothing — always worth doing first |
| `--client` / `--title` | override what the credits parse produced |
| `--credits-file PATH` | use a credits file from somewhere else |
| `--no-vimeo` | skip the upload |
| `--carousel N` | cap the stills built (default: all; `0` skips) |
| `--all-stills` | build the gallery from `stills/`, ignoring `ig_selects/` |
| `--category C` | override the guessed category; must be one of `site.json`'s |
| `--carousel-card` | let the stills replace the thumbnail on the grid card |
| `--thumb PATH` | pick the thumbnail frame yourself |
| `--commit` | commit and push when everything worked — the push half fails on the Studio until `gh auth login` is run there; see above |

## Gotchas

- **The category is a guess from the folder name, and it is often wrong.** A short film in
  a folder that doesn't say so lands as *Commercial*, with the production company as its
  third line. Check the dry run and pass `--category` — it is validated against
  `site.json`, so a category no page filters on can't slip through.
- **Reload `/admin/` after this runs.** The edit modal seeds from the copy of
  `projects.json` fetched at page load; a stale tab will try to write old values back. The
  save now refuses when it detects drift, but a reload avoids the interruption.
- **Don't run `build_site.py` by hand.** A GitHub Action regenerates the pages on push and
  a local rebuild collides with it.
- **Pages deploys lag.** A successful build often takes several more minutes to go live,
  and each new push cancels the in-flight deploy. If a change looks missing, check the
  served `?v=` stamp before suspecting anything is broken.
- **Vimeo privacy must be `disable`, not `unlisted`.** Unlisted URLs carry a secret hash;
  the site embeds by bare id, so both the link and the player break. The script gets this
  right — worth knowing if you upload by hand.
- **The Studio cannot push.** `--commit` fails at the last step; the commit is safe locally
  and gets relayed from the Air. See *Getting the result onto GitHub* above. This is a
  known, accepted state — not a bug to re-diagnose.

## Afterwards, in `/admin/`

- **UNHIDE** to move it from staged to live.
- **On landing** to put it on the front grid (the archive shows everything posted).
- **Carousel panel** to reorder or delete stills. The page shows `gallery_max` of them
  (12, set in `data/site.json`); the rest stay in the repo as your picking pool.
- **Card carousel** to let the stills replace the thumbnail on the grid card.
