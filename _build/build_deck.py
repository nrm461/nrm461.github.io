#!/usr/bin/env python3
"""
Generate deck/index.html by REUSING build_site.py's shell (page/header/footer).
The deck's chrome (head, nav, footer) is therefore produced by the exact same
code as every other page — nothing to hand-match. Only the deck-specific parts
live in css/deck.css, js/deck.js, and _build/deck_main.html / deck_extras.html.

Run: python3 _build/build_deck.py
"""
import os, re, build_site as B

ROOT = B.ROOT
VER = B.VER

# Nav (incl. DECK) now lives in data/site.json — inherited verbatim, no override.
main_inner = open(os.path.join(ROOT, '_build', 'deck_main.html'), encoding='utf-8').read().rstrip()
extras     = open(os.path.join(ROOT, '_build', 'deck_extras.html'), encoding='utf-8').read().rstrip()

content = (f'<div id="content-wrapper">\n{B.header("/deck/", 1)}\n<main>\n{main_inner}\n</main>\n{B.footer()}\n</div>\n'
           + extras)

# deck.css is LINKED (not inlined), but the link carries a CONTENT-HASH cache-buster
# (?v=<md5>) so browsers actually re-fetch it when it changes. => a deck.css tweak now
# REQUIRES rebuilding + committing deck/index.html (the link's hash changes); it is NOT a
# push-css-alone one-shot (that silently served stale CSS from cache — the 2026.0012 bug).
# deck.js stays inlined because it carries per-build data (window.DECK_LANDING below).
import hashlib
_deck_css_bytes = open(os.path.join(ROOT, 'css', 'deck.css'), 'rb').read()
DECK_CSS_VER = hashlib.md5(_deck_css_bytes).hexdigest()[:10]
deck_js  = open(os.path.join(ROOT, 'js',  'deck.js'),  encoding='utf-8').read().rstrip()

# the deck's default (unfiltered) view is scoped to films currently on the main landing grid
import json as _json
_landing = [p['slug'] for p in B.visible_projects() if p.get('selected')]
deck_js = 'window.DECK_LANDING=' + _json.dumps(_landing) + ';\n' + deck_js

inline = (f'<meta name="robots" content="noindex">\n'
          f'<link rel="stylesheet" href="../css/deck.css?v={DECK_CSS_VER}">\n')

doc = B.page('page-deck', f'{B.SITE["site_name"]} — Archive', content, inline_vars=inline, depth=1)

# swap the site's default scripts (nav-data + main.js) for the deck's own inline JS
doc = re.sub(
    r'<script src="\.\./js/nav-data\.js\?v=\d*"></script>\n<script src="\.\./js/main\.js\?v=\d*"></script>',
    lambda m: f'<script>\n{deck_js}\n</script>',   # function repl → no backslash interpretation
    doc, count=1)

B.write(os.path.join('deck', 'index.html'), doc)
print('deck built via build_site shell; VER=', VER)
