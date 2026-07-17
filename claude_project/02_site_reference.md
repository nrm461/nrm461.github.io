# Site Reference — add as Project Knowledge

Facts and inventory for Nick Metcalf's portfolio site. Current as of July 15, 2026.

## URLs & accounts
- Live site: https://nrm461.github.io — custom domain nickmetcalf.com purchased, DNS not yet pointed (needs A records 185.199.108–111.153 + CNAME file when Nick says go; nickmetcalf.com is already on the Vimeo embed whitelist).
- Repo: https://github.com/nrm461/nrm461.github.io (user nrm461). Token at `token/git-token` in the working copy — gitignored. Rotate it periodically.
- Admin tool: https://nrm461.github.io/admin/ (unlinked; token pasted once, stored in localStorage).
- Hidden review page: https://nrm461.github.io/hidden/ (unlinked, noindex).
- Vimeo: Pro account, ~258 videos, all embed-only/hidden/no-download, embed preset "nickmetcalf-site" (id 121484733), upload defaults whitelist nrm461.github.io + nickmetcalf.com.
- Slate: raremedium.slateapp.com (Rare Medium's reel system) — Nick logs in via Chrome.
- monday.com: "Nick's Team" account, CRM workspace, Projects board id 7600992989.

## Repo layout
```
data/projects.json        all projects (~220 entries) — single source of truth
data/site.json            nav, contact, categories, hide_groups
_build/build_site.py      generator (run: python3 _build/build_site.py)
_build/add_work.py        incremental ingester for new _MASTERS folders
css/main.css  js/main.js  theme + behavior (facades, swipe, filters, scroll memory, nav context)
js/nav-data.js            generated — ordered slug lists for prev/next arrows
assets/thumbs/            <slug>-100/600/1600.jpg
assets/carousel/<slug>/   00.jpg (hero) + 01..NN swipe/gallery stills
admin/index.html          the GUI editor
.github/workflows/build.yml  auto-build on data/asset pushes (serialized, [auto-build] guard)
hidden/  archive/  contact/  <slug>/   generated pages
_vimeo_uploads/           dated batches staged for manual Vimeo upload
token/git-token           GitHub token (gitignored)
```

## Local folders (Cowork mounts)
- ~/Desktop/to_claude/webiste — the repo working copy.
- /Volumes/Suite/rare_medium/_Personal_Folders/nick_m/_MASTERS — masters + ig_selects stills (READ-ONLY: copy, never move).
- iCloud …/color_grading/INSTAGRAM/VIDEOS/website/old — legacy masters/thumbs.
- ~/Downloads — staging.

## Conventions
- New Vimeo uploads are named by site slug, staged in `_vimeo_uploads/YYYY-MM-DD/`; after Nick uploads, harvest slug→ID from the library API and retitle to "Client | Title".
- Landing = "Selected Works": `selected: true` + `sel_order` (Benson Boone first by standing preference; Nick reorders in admin).
- Archive = delivered-date order (monday), undated legacy last.
- Campaign rollups live: ollie, homesense, rivian (Milk Run hero), oscar-mayer.
- Thumbnail replacements: admin drag-drop or EDIT modal; also syncs carousel 00.jpg.
- Credits format: "Role: Name @handle" lines; blank line separates hero block from the rest; hero roles = Director, DP, Edit, Color, Production.

## Open items (as of this snapshot)
- nickmetcalf.com DNS cutover — waiting on Nick.
- Salomon x L'Art de l'Automobile has no video file anywhere.
- ~26 legacy jobs have stills only (no video) — matches ProdCo behavior, fine.
- Unresolved hide-list names: "Reese's", "Spoiler Alert", "Course Death Map".
- Possible dup pairs left for Nick: Primary Children's Victory vs Let's Conquer; estee-laudre-estee-lauder vs other Estée spots; PNC Summer vs Today Is the Day.
- 070SHAKE master labeled "MINE" was published as "If You're Free" — confirm.
- Vimeo library still has the accidental "copy_masters" upload to delete.
- Tory Burch Jamaica credits applied to SPF26 — confirm it wasn't SPR26.
