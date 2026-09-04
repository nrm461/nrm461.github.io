#!/usr/bin/env python3
"""
Incremental project ingester for Nick's portfolio site.

Scans the _MASTERS folder for project folders that are NOT yet in
data/projects.json, parses their credits file, generates thumbnails
(600px card thumb, 100px lazy placeholder, 1600px hero) and appends
new entries to data/projects.json — existing entries (and any manual
edits to them) are never touched.

Usage:
    python3 _build/add_work.py --masters /path/to/_MASTERS [--group posted]
    python3 _build/add_work.py --masters /path/to/_MASTERS --only "folder name"

After running, run:  python3 _build/build_site.py
"""
import os, json, re, subprocess, unicodedata, argparse, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, 'data', 'projects.json')
IMG = ('.jpg', '.jpeg', '.png', '.tif', '.tiff')
VID = ('.mp4', '.mov', '.m4v')

CLIENT_MAP = {'nissan':'Nissan','nike':'Nike','skims':'SKIMS','garmin':'Garmin','vanityfair':'Vanity Fair',
'lululemon':'lululemon','bensonboone':'Benson Boone','converse':'Converse','dorachan_official':'Doraemon',
'debeersgroup':'De Beers','debeersofficial':'De Beers','fujiikaze':'Fujii Kaze','070shake':'070 Shake',
'danna':'Danna Paola','lalalalisa_m':'LISA','tyla':'Tyla','mariaisabel':'María Isabel','tomsachs':'Tom Sachs',
'nikecraft':'NikeCraft','rivianofficial':'Rivian','therabody':'Therabody','functionhealth':'Function Health',
'iambeckyg':'Becky G','nigo':'NIGO','pura':'Pura'}
DIRECTOR_MAP = {'oliviadecamps':'Olivia De Camps','matteastin':'Matt Eastin','tuckerbliss':'Tucker Bliss',
'taliacollis':'Talia Collis','aerinmoreno':'Aerin Moreno','julianlamadrid':'Julian Lamadrid',
'charliemysak':'Charlie Mysak','alexfischmanc':'Alex Fischman','roosbrothers':'Roos Brothers',
'matthewpothier':'Matthew Pothier','henrydacosta':'Henry Da Costa','samcutlerkreutz':'Sam Cutler-Kreutz',
'davidcutlerkreutz':'David Cutler-Kreutz','bensonboone':'Benson Boone'}
PROD_MAP = {'smugglersite':'SMUGGLER','iconoclast':'Iconoclast','resetcontent':'Reset',
'greenpointpictures':'Greenpoint Pictures','aftrhrs':'AFTRHRS','afterhrs':'AFTRHRS',
'thegatefilms':'The Gate Films','partizan':'Partizan','casino':'Casino Productions','slmbr_prty':'SLMBR PRTY',
'fieldunit':'Field Unit','41westproductions':'41 West','apstudioinc':'AP Studio','aguitainc':'Aguita',
'lotumn_':'Lotumn','broadwaytwothousand':'Broadway 2000','echobendpictures':'Echo Bend',
'strikeanywhere':'Strike Anywhere'}
MV_HINTS = ['mv_', 'mv ', 'music_video', 'music video']
SHORT_HINTS = ['short', 'film']

def slugify(s):
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode()
    s = re.sub(r'[^a-zA-Z0-9]+', '-', s).strip('-').lower()
    return re.sub(r'-+', '-', s)

def pretty_handle(h):
    return re.sub(r'[_\.]+', ' ', h.lstrip('@')).strip()

def pretty_director(d):
    if not d: return ''
    names = []
    for h, plain in re.findall(r"@([\w\.\-]+)|([A-Za-z][A-Za-z' ]+)", d):
        if h:
            key = h.lower().rstrip('_')
            names.append(DIRECTOR_MAP.get(h.lower(), DIRECTOR_MAP.get(key, '@' + h)))
        elif plain.strip() and plain.strip().lower() not in ('&', 'and', 'x'):
            names.append(plain.strip())
    return ' & '.join(dict.fromkeys(names)) if names else d

def parse_credits(path):
    raw = open(path, encoding='utf-8', errors='replace').read().replace('⁠', '').replace('﻿', '')
    lines = [l.rstrip() for l in raw.split('\n')]
    while lines and lines[0].strip() in ('-', ''): lines.pop(0)
    head, i = [], 0
    while i < len(lines) and lines[i].strip():
        head.append(lines[i].strip()); i += 1
    body = lines[i:]
    client_line = head[0] if head else ''
    title = head[1] if len(head) > 1 else ''
    extra = ' '.join(head[2:]) if len(head) > 2 else ''
    handles = re.findall(r'@([\w\.\-]+)', client_line)
    if handles:
        names = [CLIENT_MAP.get(h.lower(), pretty_handle(h).title()) for h in handles]
        client = ' x '.join(dict.fromkeys(names))
    else:
        client = client_line.strip()
    director = production = ''
    for l in head + body:
        m = re.match(r'\s*(?:Writer\s*\+\s*)?Directors?\s*:\s*(.+)', l, re.I)
        if m and not director: director = m.group(1).strip()
        m = re.match(r'\s*Production\s*:?\s*(@.+|[A-Za-z].+)', l, re.I)
        if m and not production and not re.search(r'designer|manager|coordinator', l, re.I):
            production = m.group(1).strip()
    out = []
    for l in [*head, '', *body]:
        if l.strip() == '' and (not out or out[-1] == ''): continue
        out.append(l)
    return client, title, extra, director, production, '\n'.join(out).strip()

def scan(path):
    e = {'credits': None, 'stills': [], 'other_imgs': [], 'videos': []}
    if os.path.isfile(path):
        e['videos'] = [path]; return e
    for base, dirs, files in os.walk(path):
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        rel = os.path.relpath(base, path).lower()
        for f in files:
            if f.startswith('.'): continue
            fp, fl = os.path.join(base, f), f.lower()
            if 'credit' in fl and fl.endswith('.txt'): e['credits'] = fp
            elif fl.endswith(IMG): (e['stills'] if 'still' in rel else e['other_imgs']).append(fp)
            elif fl.endswith(VID): e['videos'].append(fp)
    for k in ('stills', 'other_imgs', 'videos'): e[k].sort()
    return e

def run(cmd): subprocess.run(cmd, check=True, capture_output=True)

def make_thumbs(slug, thumb_src, video_src):
    tdir = os.path.join(ROOT, 'assets', 'thumbs')
    os.makedirs(tdir, exist_ok=True)
    t600, t100, t1600 = (os.path.join(tdir, f'{slug}-{s}.jpg') for s in ('600', '100', '1600'))
    crop = 'scale=600:338:force_original_aspect_ratio=increase,crop=600:338'
    if thumb_src:
        run(['ffmpeg', '-y', '-i', thumb_src, '-vf', crop, '-frames:v', '1', '-q:v', '4', t600])
        run(['ffmpeg', '-y', '-i', thumb_src, '-vf', 'scale=1600:-2', '-q:v', '4', t1600])
    elif video_src:
        d = float(subprocess.check_output(['ffprobe', '-v', 'quiet', '-of', 'csv=p=0',
              '-show_entries', 'format=duration', video_src]).strip() or 0)
        ss = str(max(1, d * 0.4))
        run(['ffmpeg', '-y', '-ss', ss, '-i', video_src, '-vf', crop, '-frames:v', '1', '-q:v', '4', t600])
        run(['ffmpeg', '-y', '-ss', ss, '-i', video_src, '-vf', 'scale=1600:-2', '-q:v', '4', t1600])
    else:
        return False
    run(['ffmpeg', '-y', '-i', t600, '-vf', 'scale=100:56', '-q:v', '7', t100])
    return True

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--masters', required=True, help='Path to the _MASTERS folder')
    ap.add_argument('--group', default='posted', help='Group tag for new entries (default: posted)')
    ap.add_argument('--only', default=None, help='Only ingest this folder name')
    args = ap.parse_args()

    projects = json.load(open(DATA))
    known = {p['folder'] for p in projects}
    numbers = [int(p['number'][1:]) for p in projects if re.match(r'W\d+', p.get('number', ''))]
    next_n = max(numbers, default=0) + 1
    slugs = {p['slug'] for p in projects}

    candidates = []
    for d in sorted(os.listdir(args.masters)):
        if d.startswith('_') or d.startswith('.'): continue
        if args.only and d != args.only: continue
        if d in known: continue
        candidates.append(d)

    if not candidates:
        print('No new project folders found.'); return

    for name in candidates:
        path = os.path.join(args.masters, name)
        e = scan(path)
        client = title = extra = director = production = credits_text = ''
        needs_review = True
        if e['credits']:
            client, title, extra, director, production, credits_text = parse_credits(e['credits'])
            needs_review = False
        if not title and client: title, client = client, ''
        low = name.lower()
        if any(h in low for h in MV_HINTS): category = 'Music Video'
        elif any(h in low for h in SHORT_HINTS): category = 'Short Film'
        else: category = 'Commercial'
        third = category
        if category == 'Commercial' and production:
            ph = re.findall(r'@([\w\.\-]+)', production)
            if ph:
                k = ph[0].lower().split('.')[0]
                third = PROD_MAP.get(ph[0].lower(), PROD_MAP.get(k, pretty_handle(ph[0]).title()))
            else:
                third = production
        slug = slugify(f'{client}-{title}')[:60] or slugify(name)
        n = 2
        while slug in slugs: slug = f'{slug}-{n}'; n += 1
        slugs.add(slug)
        # A file named _thumb.* anywhere in the project folder always wins
        explicit = [f for f in e['stills'] + e['other_imgs']
                    if os.path.basename(f).lower().startswith('_thumb')]
        thumb_src = (explicit[0] if explicit else
                     e['stills'][len(e['stills'])//2] if e['stills'] else
                     (e['other_imgs'][0] if e['other_imgs'] else ''))
        video_src = e['videos'][0] if e['videos'] else ''
        ok = make_thumbs(slug, thumb_src, video_src)
        entry = {
            'slug': slug, 'client': client, 'title': title, 'featuring': extra,
            'director': pretty_director(director), 'director_raw': director,
            'production': production, 'category': category, 'third_line': third,
            'vimeo': '', 'credits': credits_text, 'group': args.group,
            'needs_review': needs_review, 'mtime': os.path.getmtime(path),
            'folder': name, 'thumb_src': thumb_src, 'video_src': video_src,
            'number': f'W{next_n:03d}',
        }
        next_n += 1
        projects.append(entry)
        print(f"added {entry['number']} {slug}  (thumb: {'ok' if ok else 'MISSING'}, credits: {'ok' if not needs_review else 'MISSING - needs review'})")

    json.dump(projects, open(DATA, 'w'), indent=1, ensure_ascii=False)
    print(f'\n{len(candidates)} project(s) added. Now run: python3 _build/build_site.py')

if __name__ == '__main__':
    main()
