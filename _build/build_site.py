#!/usr/bin/env python3
"""
Static site generator for Nick Metcalf's colorist portfolio (ProdCo-style).

Reads:  data/site.json, data/projects.json, assets/thumbs/, assets/stills/
Writes: index.html, contact/index.html, and one folder per project slug.

Run:    python3 _build/build_site.py
"""
import os, json, re, html, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = json.load(open(os.path.join(ROOT, 'data', 'site.json')))
PROJECTS = json.load(open(os.path.join(ROOT, 'data', 'projects.json')))

def esc(s): return html.escape(str(s or ''), quote=True)

def linkify(line):
    """Turn @handles into instagram links."""
    if not SITE.get('linkify_handles'): return esc(line)
    out, last = [], 0
    for m in re.finditer(r'@([A-Za-z0-9_\.]+)', line):
        out.append(esc(line[last:m.start()]))
        h = m.group(1).rstrip('.')
        out.append('<a href="https://instagram.com/%s" target="_blank" rel="noopener">@%s</a>' % (esc(h), esc(h)))
        last = m.start() + 1 + len(h)
    out.append(esc(line[last:]))
    return ''.join(out)

def vimeo_id(v):
    if not v: return ''
    m = re.search(r'(\d{6,})', str(v))
    return m.group(1) if m else ''

def asset_version():
    """Cache-busting stamp from the newest of css/js file mtimes."""
    t = 0
    for f in ('css/main.css', 'js/main.js'):
        p = os.path.join(ROOT, f)
        if os.path.exists(p): t = max(t, int(os.path.getmtime(p)))
    return str(t)

VER = asset_version()

def page(body_class, title, content, inline_vars='', depth=0):
    rel = '../' * depth
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{esc(title)}</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0, minimum-scale=1.0, maximum-scale=1.0, user-scalable=no, shrink-to-fit=no">
<link rel="stylesheet" href="{rel}css/main.css?v={VER}">
{inline_vars}</head>
<body class="{body_class}">
{content}
<script src="{rel}js/main.js?v={VER}"></script>
</body>
</html>
'''

def header(active='', depth=0):
    rel = '../' * depth
    links = []
    for n in SITE['nav']:
        cls = n['slot'] + (' link-active' if n['href'] == active else '')
        tgt = ' target="_blank" rel="noopener"' if n.get('external') else ''
        if n.get('external'):
            href = n['href']
        else:
            href = rel + n['href'].lstrip('/')
            if href == '': href = './'
        links.append(f'\t<a class="{cls}" href="{esc(href)}"{tgt}>{esc(n["label"])}</a>')
    return '<header>\n' + '\n'.join(links) + '\n</header>'

def footer():
    return ('<footer>\n\t<div id="toggle-mode"><span class="white"></span><span class="black"></span></div>\n'
            '\t<span class="first"></span>\n\t<span class="middle"></span>\n\t<span class="last"></span>\n</footer>')

def card_first_line(p):
    c, t = p.get('client',''), p.get('title','')
    return f'{c} | {t}' if c and t else (t or c)

def visible_projects():
    """Visible projects, renumbered W001.. in chronological order at build time."""
    hide = set(SITE.get('hide_groups', []))
    vis = [p for p in PROJECTS if p.get('group') not in hide and not p.get('hidden')]
    vis.sort(key=lambda x: x['number'])  # preserve catalog (chronological) order
    for i, p in enumerate(vis, 1):
        p['number'] = f'W{i:03d}'
    return vis

HERO_ROLES = [
    ('Director',   re.compile(r'^\s*(writer\s*\+\s*)?(director|directed by|dir)\b(?!.*(photography|assist))', re.I)),
    ('DP',         re.compile(r'^\s*(dp|dop|director of photography|cinematograph)', re.I)),
    ('Edit',       re.compile(r'^\s*(edit|editor)\b(?!.*house)', re.I)),
    ('Color',      re.compile(r'^\s*(colou?r|colorist|colourist)\b(?!\s*(producer|assist))', re.I)),
    ('Production', re.compile(r'^\s*(production|prod)\s*(company|co)?\s*[:\-]', re.I)),
]

def credits_v2_html(p):
    """Hero credits (Dir/DP/Edit/Color/ProdCo) + gap + the rest. Mobile shows hero only."""
    lines = [l for l in (p.get('credits') or '').split('\n')]
    hero = {}
    rest, seen_role = [], False
    for l in lines:
        s = l.strip()
        if not s:
            rest.append('')
            continue
        matched = False
        for key, pat in HERO_ROLES:
            if key not in hero and pat.search(s) and ('producer' not in s.lower() or key == 'Production'):
                # normalize the label, keep the value
                val = re.sub(r'^[^:\-]*[:\-]\s*', '', s) if (':' in s or ' - ' in s) else re.sub(pat, '', s).strip()
                hero[key] = val or s
                matched = True
                seen_role = True
                break
        if not matched:
            if not seen_role:
                continue  # drop client/title/featuring header lines
            rest.append(l)
    # trim leading/duplicate blanks in rest
    out_rest = []
    for l in rest:
        if l == '' and (not out_rest or out_rest[-1] == ''):
            continue
        out_rest.append(l)
    while out_rest and out_rest[-1] == '': out_rest.pop()
    labels = {'Director':'Dir.','DP':'DP','Edit':'Edit','Color':'Color','Production':'Prod Co.'}
    def lab(k):
        l = labels[k]
        return l + ' ' if l.endswith('.') else l + ': '
    hero_html = '\n'.join(f'<p>{lab(k)}{linkify(hero[k])}</p>' for k, _ in HERO_ROLES if k in hero)
    rest_html = '\n'.join('<p class="spacer">&nbsp;</p>' if not l.strip() else f'<p>{linkify(l)}</p>' for l in out_rest)
    return (f'<div class="project-credits credits-v2">\n<div class="credits-hero">\n{hero_html}\n</div>\n'
            + (f'<div class="credits-rest">\n<p class="spacer">&nbsp;</p>\n{rest_html}\n</div>\n' if rest_html else '')
            + '</div>')

# ---------------- Works / Archive grids ----------------
def card_html(p, rel=''):
    slug = p['slug']
    t100 = f'assets/thumbs/{slug}-100.jpg'
    t600 = f'assets/thumbs/{slug}-600.jpg'
    has_thumb = os.path.exists(os.path.join(ROOT, t600))
    car_dir = os.path.join(ROOT, 'assets', 'carousel', slug)
    car_imgs = sorted(os.listdir(car_dir)) if (p.get('carousel') and os.path.isdir(car_dir)) else []
    if car_imgs:
        slides = ''.join(f'<img src="{rel}assets/carousel/{slug}/{esc(f)}" alt="" loading="lazy">' for f in car_imgs)
        img = f'<div class="thumb-carousel">{slides}</div>'
    elif has_thumb:
        img = f'<img class="thumb lazy" src="{rel}{t100}" data-src="{rel}{t600}" alt="{esc(SITE["site_name"])}: {esc(p.get("director") or card_first_line(p))} (Thumbnail)">'
    else:
        img = '<img class="thumb" alt="">'
    director = p.get('director') or ''
    cat = esc(p.get('category') or '')
    dir_html = f'<div class="module-project_info-title">{esc(director)}</div>' if director else '<div class="module-project_info-title">&nbsp;</div>'
    return f'''\t\t<div class="module-project" data-category="{cat}">
\t\t\t<a class="module-project_link" href="{rel}{slug}/">{img}</a>
\t\t\t<div class="module-project_info">
\t\t\t\t<div>{esc(card_first_line(p))}</div>
{dir_html}
\t\t\t</div>
\t\t</div>'''

def build_index():
    sel = [p for p in visible_projects() if p.get('selected')]
    # explicit reel order when sel_order present; fall back to number desc
    cards = [card_html(p) for p in sorted(sel, key=lambda x: (x.get('sel_order', 9999), -int(x['number'][1:])))]
    content = (f'<div id="content-wrapper">\n{header("/")}\n<main>\n\t<div class="module-videos">\n'
               + '\n'.join(cards) + f'\n\t</div>\n</main>\n{footer()}\n</div>')
    write('index.html', page('page-works page-index', f'{SITE["site_name"]} — Work', content))

def build_archive():
    vis = sorted(visible_projects(), key=lambda x: x['number'], reverse=True)
    cards = [card_html(p, rel='../') for p in vis]
    cats = SITE.get('categories', [])
    filters = ['\t\t<span class="archive-filter trigger active" data-filter="all">[ ALL ]</span>']
    for c in cats:
        filters.append(f'\t\t<span class="archive-filter trigger" data-filter="{esc(c)}">{esc(c)}</span>')
    content = (f'<div id="content-wrapper">\n{header("/archive/", 1)}\n<main>\n'
               f'\t<div id="archive-filters">\n' + '\n'.join(filters) + '\n\t</div>\n'
               f'\t<div class="module-videos">\n' + '\n'.join(cards) + f'\n\t</div>\n</main>\n{footer()}\n</div>')
    write(os.path.join('archive', 'index.html'),
          page('page-works page-index page-archive', f'{SITE["site_name"]} — Archive', content, depth=1))

# ---------------- Project pages ----------------
def build_projects():
    vis = sorted(visible_projects(), key=lambda x: x['number'])
    for i, p in enumerate(vis):
        slug = p['slug']
        prev_p = vis[i-1] if i > 0 else vis[-1]
        next_p = vis[i+1] if i < len(vis)-1 else vis[0]

        # media block: facade (our thumbnail + play button) that swaps to autoplaying Vimeo on click
        vid = vimeo_id(p.get('vimeo'))
        if vid:
            hero = f'assets/thumbs/{slug}-1600.jpg'
            if not os.path.exists(os.path.join(ROOT, hero)):
                hero = f'assets/thumbs/{slug}-600.jpg'
            media = (f'<div class="video-facade" data-vimeo="{vid}" title="{esc(card_first_line(p))}">'
                     f'<div style="padding:56.25% 0 0 0;position:relative;">'
                     f'<img src="../{hero}" alt="{esc(card_first_line(p))}" loading="eager">'
                     f'<button class="play-btn" aria-label="Play"></button>'
                     f'</div></div>')
        else:
            hero = f'assets/thumbs/{slug}-1600.jpg'
            if not os.path.exists(os.path.join(ROOT, hero)):
                hero = f'assets/thumbs/{slug}-600.jpg'
            media = (f'<img class="thumb lazy" src="../assets/thumbs/{slug}-100.jpg" data-src="../{hero}" alt="{esc(card_first_line(p))}">'
                     if os.path.exists(os.path.join(ROOT, hero)) else '')

        # credits (v2 everywhere: hero roles + rest, mobile shows hero only)
        credits_html = credits_v2_html(p) if p.get('credits') else ''

        director = p.get('director') or ''
        content = f'''<main>
\t<div id="single-bar">
\t\t<a id="prev" href="../{prev_p['slug']}/">&lt;</a>
\t\t<a id="close" href="../">[ CLOSE ]</a>
\t\t<a id="next" href="../{next_p['slug']}/">&gt;</a>
\t</div>
\t<div id="project-container">
\t\t<div class="module-project_info">
\t\t\t<div>{esc(card_first_line(p))}</div>
\t\t</div>
\t\t<div id="project-videos">
\t\t\t{media}
\t\t</div>
{credits_html}
\t</div>
</main>'''
        inline = '<style>\n:root{\n\t--color-bg: black;\n\t--color-text: white;\n}\n</style>\n'
        write(os.path.join(slug, 'index.html'),
              page('page-project', f'{SITE["site_name"]} — {card_first_line(p)}', content, inline_vars=inline, depth=1))

# ---------------- Contact ----------------
def build_contact():
    c = SITE['contact']
    intro = '\n'.join(f'\t<p>{esc(l)}</p>' for l in c.get('intro', []))
    sections = []
    for s in c.get('sections', []):
        lines = '\n'.join(
            f'\t\t<p><a href="{esc(l["href"])}" target="_blank" rel="noopener">{esc(l["text"])}</a></p>'
            if l.get('href') else f'\t\t<p>{esc(l["text"])}</p>'
            for l in s.get('lines', []))
        sections.append(f'''\t<div class="contact-section">
\t\t<p class="contact-section_title">{esc(s['title'])}</p>
\t\t<div class="contact-section_content">
{lines}
\t\t</div>
\t</div>''')
    content = (f'<div id="content-wrapper">\n{header("/contact/", 1)}\n<main>\n'
               f'\t<div>\n{intro}\n\t</div>\n' + '\n'.join(sections) + f'\n</main>\n{footer()}\n</div>')
    write(os.path.join('contact', 'index.html'),
          page('page-contact', f'{SITE["site_name"]} — Contact', content, depth=1))

def write(rel, content):
    path = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True) if os.path.dirname(rel) else None
    open(path, 'w', encoding='utf-8').write(content)
    print('wrote', rel)

if __name__ == '__main__':
    build_index()
    build_archive()
    build_projects()
    build_contact()
    print(f'done — {len(visible_projects())} projects')
