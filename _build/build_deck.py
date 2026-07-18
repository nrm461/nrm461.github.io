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

# The deck's nav = the site nav + a DECK entry (WORK / ARCHIVE / DECK / CONTACT).
# Reuses build_site.header() verbatim so the markup matches all other pages.
B.SITE['nav'] = [
    {'label': 'WORK',    'href': '/',         'slot': 'first'},
    {'label': 'ARCHIVE', 'href': '/archive/', 'slot': 'middle'},
    {'label': 'DECK',    'href': '/deck/',    'slot': 'middle'},
    {'label': 'CONTACT', 'href': '/contact/', 'slot': 'last'},
]

main_inner = open(os.path.join(ROOT, '_build', 'deck_main.html'), encoding='utf-8').read().rstrip()
extras     = open(os.path.join(ROOT, '_build', 'deck_extras.html'), encoding='utf-8').read().rstrip()

content = (f'<div id="content-wrapper">\n{B.header("/deck/", 1)}\n<main>\n{main_inner}\n</main>\n{B.footer()}\n</div>\n'
           + extras)

# deck-specific CSS/JS are INLINED so the page stays one self-contained file
# (existing deploy model). main.css stays LINKED (inherited), so the shell tracks the site.
deck_css = open(os.path.join(ROOT, 'css', 'deck.css'), encoding='utf-8').read().rstrip()
deck_js  = open(os.path.join(ROOT, 'js',  'deck.js'),  encoding='utf-8').read().rstrip()

inline = (f'<meta name="robots" content="noindex">\n'
          f'<style>\n{deck_css}\n</style>\n')

doc = B.page('page-deck dark-mode', f'{B.SITE["site_name"]} — Deck', content, inline_vars=inline, depth=1)

# swap the site's default scripts (nav-data + main.js) for the deck's own inline JS
doc = re.sub(
    r'<script src="\.\./js/nav-data\.js\?v=\d*"></script>\n<script src="\.\./js/main\.js\?v=\d*"></script>',
    lambda m: f'<script>\n{deck_js}\n</script>',   # function repl → no backslash interpretation
    doc, count=1)

B.write(os.path.join('deck', 'index.html'), doc)
print('deck built via build_site shell; VER=', VER)
