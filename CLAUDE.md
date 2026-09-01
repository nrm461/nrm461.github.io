# nrm461.github.io

Nick Metcalf — colorist portfolio. A static site generated from `data/site.json` and `data/projects.json`, live at https://nrm461.github.io.

## Adding a spot

`_build/add_spot.py <job>` does the whole add — credits, thumbs, stills, Vimeo, entry —
and stages it as `group: "hidden"`. It runs on the Mac Studio (SSH `studio`), where the
masters are mounted. See `docs/adding-a-spot.md`; **read its Gotchas before touching
`data/projects.json` or `/admin/`.**

## Agent skills

### Issue tracker

Issues live as GitHub issues in `nrm461/nrm461.github.io`, via the `gh` CLI. See `docs/agents/issue-tracker.md`.

### Triage labels

The five canonical roles, used verbatim as label strings. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context — `CONTEXT.md` and `docs/adr/` at the repo root. See `docs/agents/domain.md`.
