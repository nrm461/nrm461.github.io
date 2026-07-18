# PRE-HANDOFF CHECKLIST — complete EVERY item before signing off

Hard gate. Complete items 1–4 before ending any session that pushed to origin. Items 5–6 (handoff + kickoff block) are ON DEMAND — produce them ONLY when Nick says "handoff" (changed 2026-07-18).
If the session pushed nothing to origin, only items 4–5 apply.

Key distinction that caused a miss on 2026-07-18: **session memory is NOT the repo docs.**
Updating your private memory does NOT satisfy the CHANGELOG requirement. The CHANGELOG,
VERSION, and other claude_project/ files are REPO files on origin, edited via the Contents API.

1. **VERSION bumped** — claude_project/VERSION on ORIGIN incremented +1 for this session's push (website YYYY.NNNN; new year → .0001).
2. **CHANGELOG logged** — a new entry at the TOP of claude_project/CHANGELOG.md on ORIGIN, dated today, headed `## website YYYY.NNNN — DATE`, with Shipped + Open threads.
3. **Affected repo docs updated** on origin (00_START_HERE / WORKFLOW / 02_site_reference / deck docs) if what shipped changed how they read.
4. **VERIFY from origin** — re-fetch claude_project/VERSION and the CHANGELOG top entry FROM ORIGIN via the API. Confirm the CHANGELOG top version === VERSION and is dated today. If they don't match, you skipped 1 or 2 — go fix it before continuing.
5. **Handoff printed** — first line is exactly the verified `website YYYY.NNNN`, alone; then a blank line; then a short Shipped/Open summary (so pasting it seeds the next chat's title).
6. **New-chat prompt block — ON DEMAND ONLY (changed 2026-07-18):** produce a handoff only when Nick explicitly says "handoff" — never automatically. When he does, end the handoff turn with a fenced code block he can one-click copy: lead line `website YYYY.NNNN — new session.`, a one-line role reminder, this session’s key context + open threads, and any restore-point refs.

Report each item's status explicitly in the handoff turn — never a silent "done."
