#!/bin/bash
# Deck v3 deploy — run from repo root: bash push_deck.sh
set -e
cd "$(dirname "$0")"
echo "→ clearing stale git lock + transfer temp files"
rm -f .git/index.lock
rm -f _build/deck2_sheets.* _build/deck2_meta.tgz _build/deck_sheets.tar _build/deck_sheets.part.* \
      _build/deck_meta.tgz _build/deck_sample.tgz _build/shotcounts.* _build/070-shake-*.json 2>/dev/null || true

echo "→ dropping junk + unreferenced frames (keeping only what deck.json uses)"
find assets/deck2 -name '*.junk' -delete 2>/dev/null || true
python3 - << 'PY'
import json, os
ref=set(F['slug']+'/'+fr[0]+'.jpg' for F in json.load(open('data/deck.json'))['films'] for fr in F['frames'])
removed=0
for sl in os.listdir('assets/deck2'):
    d='assets/deck2/'+sl
    if not os.path.isdir(d): continue
    for f in os.listdir(d):
        if f.endswith('.jpg') and sl+'/'+f not in ref:
            os.remove(os.path.join(d,f)); removed+=1
    if not os.listdir(d): os.rmdir(d)
print("  removed", removed, "unreferenced frames")
PY

echo "→ removing v1 frames (assets/deck — no longer used)"
git rm -r --quiet --cached assets/deck 2>/dev/null || true
rm -rf assets/deck

echo "→ pull + stage"
git pull --no-edit
git add -A assets/deck2 data/deck.json data/deck_tags.json deck/index.html
git commit -q -m "deck v3: mid-shot regrab (6297 frames), full AI tags + keywords, ShotDeck layout"

echo "→ push"
git push "https://nrm461:$(cat token/git-token)@github.com/nrm461/nrm461.github.io.git" main
echo "✓ done — live at https://nrm461.github.io/deck/ in ~1 min"
