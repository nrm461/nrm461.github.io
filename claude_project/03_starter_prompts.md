# Starter Prompts — copy/paste into the new project

## Kickoff / context check (start every new chat with this)
> You're picking up work on my colorist portfolio site (nrm461.github.io) and its /deck/ frame library. Orient first: read `claude_project/00_START_HERE.md`, then the TOP of `claude_project/CHANGELOG.md`, and glance at project memory. Give me a 4–5 line status — what shipped last session + current Open threads. Don't change anything yet; I'll give you the task next.

## New-task handoff template (paste at the top of any task)
> Orient from `claude_project/00_START_HERE.md` + the top of `CHANGELOG.md` first (don't re-derive what's in the docs). Then do this: **<the task>**. Deploy via the browser Contents API. When done, log it as a new CHANGELOG entry and refresh Open threads.

## Add a new job (the most common task)
> New job to add: [CLIENT] "[TITLE]", directed by [@handle]. Master is in _MASTERS/[folder]. Category: [Commercial/Music Video/Beauty/Long Form]. Use the _thumb file in the folder (or the Slate poster) for the thumbnail. Stage an H.264 named by slug in a dated _vimeo_uploads folder for me to upload; wire the Vimeo link once I say it's uploaded. Credits are in this IG post: [link].

## Credits pass
> Do a credits pass: scrape every project flagged needs_credits (their ig_url links), parse the captions into our credits format, apply, rebuild, publish. List anything you couldn't parse.

## Refresh from Slate
> Check Slate for new deliveries since [date]. List anything new that's shareable (skip DO NOT SHARE), with client/title/date. After I approve, add them: Slate poster thumbs, slug-named videos staged for Vimeo upload, delivered dates from monday.

## Refresh archive order
> Re-pull delivered dates from my monday Projects board and re-sort the archive, newest first. Unmatched stay last.

## Landing page changes
> Put [job] on the landing page after [job]. / Take [job] off the landing but keep it in the archive. / Hide [job] entirely.

## Campaign rollup
> Roll the [brand] spots into one campaign card like Rivian: hero thumb from [spot], videos stacked on the page in this order: [list].

## Go live on nickmetcalf.com
> Time to point nickmetcalf.com at the site. Walk me through the DNS records at my registrar, add the CNAME file to the repo, enable HTTPS in Pages settings, and verify Vimeo embeds still play on the new domain.

## Vimeo hygiene
> Audit Vimeo: every video should be hidden from Vimeo, embed-whitelisted, downloads off, titled "Client | Title". Fix any that drifted and report.

## Monthly maintenance
> Monthly pass: new Slate jobs → propose additions; credits pass on anything queued; re-sort archive by delivered dates; check for broken thumbs/videos on the live site; report in five bullets or fewer.
