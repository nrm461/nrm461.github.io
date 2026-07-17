# Starter Prompts — copy/paste into the new project

## Kickoff / context check
> Read data/projects.json and data/site.json in my website folder, confirm you understand the build pipeline (build_site.py → GitHub Pages via the auto-build Action), and give me a one-paragraph status of the site. Don't change anything yet.

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
