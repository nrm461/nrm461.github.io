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

def cats(p):
    """A project's categories as a list (supports multi-category; falls back to the legacy single field)."""
    cs = p.get('categories')
    if not cs:
        cs = [p['category']] if p.get('category') else []
    return [c for c in cs if c]

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

def analytics_tag():
    """Umami page-view script. Emits nothing until data/site.json carries a site ID,
    so a fresh clone (and the local preview) stays untracked."""
    a = SITE.get('analytics') or {}
    wid, src = a.get('umami_id'), a.get('umami_src')
    if not (wid and src): return ''
    return f'<script defer src="{esc(src)}" data-website-id="{esc(wid)}"></script>\n'

def page(body_class, title, content, inline_vars='', depth=0):
    rel = '../' * depth
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{esc(title)}</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0, minimum-scale=1.0, maximum-scale=1.0, user-scalable=no, shrink-to-fit=no">
<link rel="stylesheet" href="{rel}css/main.css?v={VER}">
{analytics_tag()}{inline_vars}</head>
<body class="{body_class}">
{content}
<script src="{rel}js/nav-data.js?v={VER}"></script>
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
    hide = set(SITE.get('hide_groups', [])) | {'hidden', 'rolled'}
    vis = [p for p in PROJECTS if p.get('group') not in hide and not p.get('hidden')]
    vis.sort(key=lambda x: x['number'])  # preserve catalog (chronological) order
    for i, p in enumerate(vis, 1):
        p['number'] = f'W{i:03d}'
    return vis

def hidden_projects():
    """Projects moved off the public site; listed only on the unlinked /hidden/ page."""
    hid = [p for p in PROJECTS if p.get('group') == 'hidden']
    hid.sort(key=lambda x: (x.get('arch_order', 10000), -int(x['number'][1:])))
    return hid

def batch_projects():
    """Projects moved off the public site; listed only on the unlinked /hidden/ page."""
    bat = [p for p in PROJECTS if p.get('group') == 'vimeo_batch']
    bat.sort(key=lambda x: (x.get('arch_order', 10000), -int(x['number'][1:])))
    return bat

def project_by_slug(slug):
    for p in PROJECTS:
        if p['slug'] == slug:
            return p
    return None

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

def img_bust(rel_path):
    """cache-buster tied to image content so replaced thumbs show up right after a rebuild"""
    import hashlib
    fp = os.path.join(ROOT, rel_path)
    if not os.path.exists(fp):
        return rel_path
    h = hashlib.md5(open(fp, 'rb').read()).hexdigest()[:8]
    return f'{rel_path}?v={h}'

# ---------------- Works / Archive grids ----------------
def card_html(p, rel=''):
    slug = p['slug']
    t100 = img_bust(f'assets/thumbs/{slug}-100.jpg')
    t600 = img_bust(f'assets/thumbs/{slug}-600.jpg')
    has_thumb = os.path.exists(os.path.join(ROOT, f'assets/thumbs/{slug}-600.jpg'))
    car_dir = os.path.join(ROOT, 'assets', 'carousel', slug)
    car_imgs = sorted(f for f in os.listdir(car_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))) if (p.get('carousel') and os.path.isdir(car_dir)) else []
    if car_imgs:
        slides = ''.join(f'<img src="{rel}{img_bust(f"assets/carousel/{slug}/{f}")}" alt="" loading="lazy">' for f in car_imgs)
        img = f'<div class="thumb-carousel">{slides}</div>'
    elif has_thumb:
        img = f'<img class="thumb lazy" src="{rel}{t100}" data-src="{rel}{t600}" alt="{esc(SITE["site_name"])}: {esc(p.get("director") or card_first_line(p))} (Thumbnail)">'
    else:
        img = '<img class="thumb" alt="">'
    director = p.get('director') or ''
    cat = esc('|'.join(cats(p)))   # pipe-delimited so a card can match multiple archive filters
    dir_html = f'<div class="module-project_info-title">{esc(director)}</div>' if director else '<div class="module-project_info-title">&nbsp;</div>'
    return f'''\t\t<div class="module-project" data-category="{cat}">
\t\t\t<a class="module-project_link" href="{rel}{slug}/">{img}</a>
\t\t\t<div class="module-project_info">
\t\t\t\t<div>{esc(card_first_line(p))}</div>
{dir_html}
\t\t\t</div>
\t\t</div>'''

def build_index():
    """/archive/ — every visible project in one grid, newest first.

    This was the site's root until 2026-07-27; the sort accordion took the landing
    slot and this became ARCHIVE in the nav. It is still the FULL list, and still
    what a project page's arrows walk (NAV_LISTS['archive']).
    """
    vis = sorted(visible_projects(),
                 key=lambda x: (x.get('arch_order', 10000), -int(x['number'][1:])))
    cards = [card_html(p, rel='../') for p in vis]
    content = (f'<div id="content-wrapper">\n{header("/archive/", 1)}\n<main>\n\t<div class="module-videos">\n'
               + '\n'.join(cards) + f'\n\t</div>\n</main>\n{footer()}\n</div>')
    write(os.path.join('archive', 'index.html'),
          page('page-works page-index page-archive', f'{SITE["site_name"]} — Archive', content, depth=1))

def build_selects():
    # The old landing grid (curated selects, sel_order). Unlinked from nav; lives at /selects/.
    sel = [p for p in visible_projects() if p.get('selected')]
    cards = [card_html(p, rel='../') for p in sorted(sel, key=lambda x: (x.get('sel_order', 9999), -int(x['number'][1:])))]
    content = (f'<div id="content-wrapper">\n{header("/selects/", 1)}\n<main>\n\t<div class="module-videos">\n'
               + '\n'.join(cards) + f'\n\t</div>\n</main>\n{footer()}\n</div>')
    write(os.path.join('selects', 'index.html'),
          page('page-works page-index page-selects', f'{SITE["site_name"]} — Selects', content, depth=1))

def build_archive():
    """/sort/ is retired as a path — that page is the site's landing page now.

    Kept alive as a redirect because the link was shared while it was a preview.
    """
    doc = ('<!DOCTYPE html>\n<html lang="en"><head><meta charset="utf-8">\n'
           '<meta name="robots" content="noindex">\n'
           '<link rel="canonical" href="/">\n'
           '<meta http-equiv="refresh" content="0; url=/">\n'
           f'<title>{esc(SITE["site_name"])}</title>\n'
           '</head><body><a href="/">Work</a></body></html>\n')
    write(os.path.join('sort', 'index.html'), doc)

def build_hidden():
    """Archive-style page of hidden jobs. Deliberately unlinked from all navigation."""
    hid = hidden_projects()
    cards = [card_html(p, rel='../') for p in hid]
    content = (f'<div id="content-wrapper">\n{header("", 1)}\n<main>\n'
               f'\t<div class="module-videos">\n' + '\n'.join(cards) + f'\n\t</div>\n</main>\n{footer()}\n</div>')
    content = f'<meta name="robots" content="noindex">\n{content}'
    write(os.path.join('hidden', 'index.html'),
          page('page-works page-index page-archive page-hidden', f'{SITE["site_name"]} — Hidden', content, depth=1))

def build_batch():
    """Archive-style page of staged Vimeo-batch jobs. Unlinked from all navigation."""
    bat = batch_projects()
    cards = [card_html(p, rel='../') for p in bat]
    content = (f'<div id="content-wrapper">\n{header("", 1)}\n<main>\n'
               f'\t<div class="module-videos">\n' + '\n'.join(cards) + f'\n\t</div>\n</main>\n{footer()}\n</div>')
    content = f'<meta name="robots" content="noindex">\n{content}'
    write(os.path.join('vimeo-batch', 'index.html'),
          page('page-works page-index page-archive page-hidden', f'{SITE["site_name"]} — Vimeo Batch', content, depth=1))

# ---------------- Sort page (category accordion) ----------------
def cat_slug(name):
    """URL token for a category: 'Music Video' -> 'music-video' (the ?query deep link)."""
    return re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')

SORT_MAX = 5             # hard cap: a section shows five spots, no more

def sort_categories():
    """The sections /sort/ shows, in order. Its own list, NOT site.json['categories'] —
    a category can be a useful tag on a project (Fashion, Long Form) without earning a
    section on this page."""
    return [c for c in SITE.get('sort_categories', []) if c]

def sort_members(name, vis):
    """The (at most five) spots shown under one section, in the order Nick set.

    Both the picks and their ORDER live in site.json["sort_picks"] as one ordered list
    of slugs per section. That is the whole point of the shape: this page orders itself
    independently of the work page, and a spot can sit high in Car and low in
    Commercial. Storing it per-project (a flag, or a list of sections) can express
    membership but not position, which is what sent the first cut of this page out in
    work-page order.

    A pick that is hidden or deleted simply drops out; the cap is applied last.
    """
    by_slug = {p['slug']: p for p in vis}
    picks = (SITE.get('sort_picks') or {}).get(name, [])
    return [by_slug[s] for s in picks if s in by_slug][:SORT_MAX]

def build_sort():
    """/sort/ — a curated five spots per category, in collapsible sections.

    A port of the reference site's DIRECTORS accordion (module-section /
    module-director), grouping by category instead of by director. Same card
    component and 5-across grid as the work page, so nothing here re-creates type
    or spacing — and with the cap at five, every open section is exactly one row.

    The first section with spots (RECENT, as ordered today) starts open.

    This is the site's landing page as of 2026-07-27 (it lived at /sort/ while it was
    being judged, and that path still redirects here). Being the front door, it is
    indexable — the noindex it carried as a preview is gone.
    """
    vis = sorted(visible_projects(),
                 key=lambda x: (x.get('arch_order', 10000), -int(x['number'][1:])))

    # Every section is hand-picked, RECENT included — it leads the list rather than
    # being computed, so Nick chooses what the page opens on. The FIRST section that
    # has spots is the one that starts open: the page should say something before it
    # is touched, and that stays true if the sections are ever reordered.
    groups = []
    for name in sort_categories():
        members = sort_members(name, vis)
        if members:
            groups.append((name, cat_slug(name), members, not groups))

    blocks = []
    for name, slug, members, open_ in groups:
        cards = '\n'.join(card_html(p) for p in members)
        active = ' active' if open_ else ''
        hidden = '' if open_ else ' style="display:none"'
        blocks.append(
            f'\t\t\t<div class="module-cat" data-slug="{slug}">\n'
            f'\t\t\t\t<h2 class="module-cat--title trigger{active}">'
            f'<span>{esc(name)}</span></h2>\n'
            f'\t\t\t\t<div class="module-cat--content"{hidden}>\n'
            f'\t\t\t\t\t<div class="module-cat--block">\n'
            f'\t\t\t\t\t\t<div class="module-cat--block-content module-videos">\n{cards}\n\t\t\t\t\t\t</div>\n'
            f'\t\t\t\t\t</div>\n\t\t\t\t</div>\n\t\t\t</div>')

    main_html = ('\t<section class="module-section">\n'
                 '\t\t<div id="toggle-all" class="module-section--title trigger"><span>EXPAND ALL</span><wrap></wrap></div>\n'
                 '\t\t<div class="module-section--content">\n'
                 + '\n'.join(blocks) +
                 '\n\t\t</div>\n\t</section>')

    content = (f'<div id="content-wrapper">\n{header("/")}\n<main>\n{main_html}\n</main>\n{footer()}\n</div>\n'
               f'<script>\n{CATS_JS}\n</script>')
    write('index.html',
          page('page-works page-index page-archive page-sort',
               f'{SITE["site_name"]} — Work', content))

CATS_JS = r'''(function(){
	var cats = [].slice.call(document.querySelectorAll('.module-cat'));
	var all  = document.getElementById('toggle-all');
	function isOpen(c){ return c.querySelector('.module-cat--content').style.display !== 'none'; }
	function set(c, open){
		c.querySelector('.module-cat--content').style.display = open ? '' : 'none';
		c.querySelector('.module-cat--title').classList.toggle('active', open);
	}
	function syncAll(){
		all.classList.toggle('active', cats.length > 0 && cats.every(isOpen));
	}
	cats.forEach(function(c){
		c.querySelector('.module-cat--title').addEventListener('click', function(){
			var open = !isOpen(c);
			set(c, open);
			syncAll();
			/* deep link mirrors the reference site: /sort/?beauty */
			history.replaceState(null, '', open ? '?' + c.dataset.slug : location.pathname);
		});
	});
	all.addEventListener('click', function(){
		var open = !cats.every(isOpen);
		cats.forEach(function(c){ set(c, open); });
		syncAll();
		history.replaceState(null, '', location.pathname);
	});
	syncAll();
	/* ?beauty (or #beauty) opens that section on load and scrolls it into view.
	   RECENT is already open — a deep link opens its section as well rather than
	   replacing it, so the page always leads with something. */
	var want = decodeURIComponent((location.search.slice(1) || location.hash.slice(1)).split('=')[0] || '');
	if(want){
		cats.forEach(function(c){
			if(c.dataset.slug === want){
				set(c, true);
				syncAll();
				c.scrollIntoView({block: 'start'});
			}
		});
	}
})();'''

# ---------------- Project pages ----------------
def child_label(parent, child):
    """Label for one video inside a campaign page.

    Children are usually titled '<parent title> - <cut>', so printing the child title
    verbatim under the page heading reads as a doubled title:

        Lululemon | 24 Hours To The Fullest
        24 Hours To The Fullest - Jordan Clarkson

    A child titled that way carries no information the heading doesn't already give —
    the remainder is just a talent name — so it gets no label at all. Children with
    their own distinct titles (Ollie's 'Pillows', Oscar Mayer's 'Raft') do name their
    cut, and those print as-is.
    """
    t = (child.get('title') or '').strip()
    pt = (parent.get('title') or '').strip()
    if pt and t.lower().startswith(pt.lower()):
        return ''
    return t

def media_block(p, label=''):
    """One video slot: facade when a Vimeo id exists, else plain hero image."""
    slug = p['slug']
    vid = vimeo_id(p.get('vimeo'))
    hero = f'assets/thumbs/{slug}-1600.jpg'
    if not os.path.exists(os.path.join(ROOT, hero)):
        hero = f'assets/thumbs/{slug}-600.jpg'
    label_html = f'<div class="video-label">{esc(label)}</div>\n' if label else ''
    if vid:
        return (f'{label_html}<div class="video-facade" data-vimeo="{vid}" title="{esc(card_first_line(p))}">'
                f'<div style="padding:56.25% 0 0 0;position:relative;">'
                f'<img src="../{img_bust(hero)}" alt="{esc(card_first_line(p))}" loading="eager">'
                f'<button class="play-btn" aria-label="Play"></button>'
                f'</div></div>')
    if os.path.exists(os.path.join(ROOT, hero)):
        return (f'{label_html}<img class="thumb lazy" src="../{img_bust(f"assets/thumbs/{slug}-100.jpg")}" data-src="../{img_bust(hero)}" alt="{esc(card_first_line(p))}">')
    return label_html

def build_projects():
    vis = sorted(visible_projects(), key=lambda x: x['number'])
    hid = hidden_projects()
    bat = batch_projects()
    for i, p in enumerate(vis + hid + bat):
        in_hidden = p.get('group') == 'hidden'
        in_batch = p.get('group') == 'vimeo_batch'
        ring = bat if in_batch else (hid if in_hidden else vis)
        j = ring.index(p)
        slug = p['slug']
        prev_p = ring[j-1] if j > 0 else ring[-1]
        next_p = ring[j+1] if j < len(ring)-1 else ring[0]
        # default is the full grid; main.js swaps it for '../' if you arrived from the landing
        close_href = '../vimeo-batch/' if in_batch else ('../hidden/' if in_hidden else '../archive/')

        # media: campaign parents stack every child video; singles get one slot
        if p.get('children'):
            kids = [k for k in (project_by_slug(k) for k in p['children']) if k]
            show_labels = len(kids) > 1
            media = '\n\t\t\t'.join(media_block(k, label=(child_label(p, k) if show_labels else '')) for k in kids)
        else:
            media = media_block(p)

        # credits (v2 everywhere: hero roles + rest, mobile shows hero only)
        credits_html = credits_v2_html(p) if p.get('credits') else ''

        # optional gallery: carousel stills below the credits
        if p.get('gallery'):
            gdir = os.path.join(ROOT, 'assets', 'carousel', slug)
            gimgs = sorted(f for f in (os.listdir(gdir) if os.path.isdir(gdir) else [])
                           if f.lower().endswith(('.jpg', '.jpeg', '.png')) and not f.startswith('00'))
            # Cap what the page shows; the rest stay in the repo as the pool the
            # admin carousel panel picks from. Complete rows of 3 only.
            gimgs = gimgs[:SITE.get('gallery_max', 9)]
            gimgs = gimgs[:(len(gimgs) // 3) * 3]
            if gimgs:
                tiles = '\n'.join(f'<img class="lazy" data-src="../assets/carousel/{slug}/{esc(f)}" alt="">' for f in gimgs)
                credits_html += f'\n<div class="project-gallery">\n{tiles}\n</div>'

        director = p.get('director') or ''
        content = f'''<main>
\t<div id="single-bar">
\t\t<a id="prev" href="../{prev_p['slug']}/">&lt;</a>
\t\t<a id="close" href="{close_href}">[ CLOSE ]</a>
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
              page('page-project' + (' mobile-gallery' if SITE.get('mobile_gallery') else ''), f'{SITE["site_name"]} — {card_first_line(p)}', content, inline_vars=inline, depth=1))

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

def build_navdata():
    """Ordered slug lists so project-page arrows can follow the grid the visitor came from."""
    vis = visible_projects()
    landing = [p['slug'] for p in sorted([p for p in vis if p.get('selected')],
               key=lambda x: (x.get('sel_order', 9999), -int(x['number'][1:])))]
    archive = [p['slug'] for p in sorted(vis,
               key=lambda x: (x.get('arch_order', 10000), -int(x['number'][1:])))]
    hidden = [p['slug'] for p in hidden_projects()]
    data = json.dumps({'landing': landing, 'archive': archive, 'hidden': hidden})
    write(os.path.join('js', 'nav-data.js'), 'window.NAV_LISTS=' + data + ';\n')

if __name__ == '__main__':
    build_index()
    build_selects()
    build_archive()
    build_hidden()
    build_batch()
    build_projects()
    build_contact()
    build_sort()
    build_navdata()
    print(f'done — {len(visible_projects())} visible, {len(hidden_projects())} hidden')
