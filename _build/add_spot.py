#!/usr/bin/env python3
"""
Add one finished spot to the site, from its masters folder.

Runs on the Mac Studio, where /Volumes/Suite is mounted. Point it at a job by
name and it does the whole job:

    python3 _build/add_spot.py Hills

  1. resolves the folder under _MASTERS (fuzzy, case-insensitive)
  2. picks the deliverable   (ProRes > mp4 > GEN, and 16x9 > FulRes)
  3. parses the credits file (or drops the blank template in and stops)
  4. builds the three thumbs (sips — no ffmpeg needed)
  5. builds the carousel stills
  6. uploads to Vimeo        (tus, token in ~/.vimeo-token)
  7. appends to data/projects.json

It never touches an existing entry. Commit and push are left to the caller so
the diff can be read first; use --commit to do them here.

Flags:
    --dry-run      report what it would do, write nothing
    --no-vimeo     skip the upload (entry gets an empty vimeo field)
    --group G      group tag for the new entry (default: hidden)
    --thumb PATH   override the thumbnail source frame
    --carousel N   how many carousel stills (default: 10, 0 to skip)
    --commit       git add/commit/push when everything succeeded
"""
import os, sys, re, json, time, argparse, subprocess, unicodedata, difflib
import urllib.request, urllib.error

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from add_work import (slugify, parse_credits, pretty_director,
                      CLIENT_MAP, PROD_MAP, MV_HINTS, SHORT_HINTS, pretty_handle)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, 'data', 'projects.json')
MASTERS = '/Volumes/Suite/rare_medium/_Personal_Folders/nick_m/_MASTERS'
TOKEN_FILE = os.path.expanduser('~/.vimeo-token')
IMG = ('.jpg', '.jpeg', '.png', '.tif', '.tiff')
VID = ('.mov', '.mp4', '.m4v')

# Thumb geometry, matching set_thumb.py.
SIZES = {'600': (600, 338), '100': (100, 56), '1600': (1600, 900)}
CAROUSEL_W = 1600


def die(msg, code=1):
    print(f'\n!! {msg}', file=sys.stderr)
    sys.exit(code)


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        die(f'command failed: {" ".join(cmd[:3])}…\n{r.stderr.strip()}')
    return r.stdout


# ---------------------------------------------------------------- resolving

def resolve_folder(name):
    """A job name, a folder name, or a full path -> the spot folder."""
    if os.path.isdir(name):
        return os.path.abspath(name)
    if not os.path.isdir(MASTERS):
        die(f'{MASTERS} is not mounted.\n'
            '   The masters live on the Studio; mount Suite or run this there.')
    entries = [d for d in os.listdir(MASTERS)
               if os.path.isdir(os.path.join(MASTERS, d)) and not d.startswith('.')]
    exact = [d for d in entries if d.lower() == name.lower()]
    if exact:
        return os.path.join(MASTERS, exact[0])
    part = [d for d in entries if name.lower() in d.lower()]
    if len(part) == 1:
        return os.path.join(MASTERS, part[0])
    if len(part) > 1:
        die(f'"{name}" matches {len(part)} folders: {", ".join(sorted(part))}')
    close = difflib.get_close_matches(name, entries, n=3, cutoff=0.5)
    hint = f'  Did you mean: {", ".join(close)}?' if close else ''
    die(f'no folder matching "{name}" under _MASTERS.{hint}')


def rank_video(path):
    """Lower sorts better. ProRes over mp4 over GEN; 16x9 over FulRes."""
    p = path.lower()
    if 'prores' in p:   src = 0
    elif '/mp4/' in p:  src = 1
    elif '/gen/' in p:  src = 2
    else:               src = 3
    fmt = 0 if '16x9' in p else (2 if 'fulres' in p else 1)
    return (fmt, src, path)


def scan(folder):
    """Find the deliverable, the stills, and the credits file."""
    out = {'videos': [], 'stills': [], 'other_imgs': [], 'credits': None}
    for base, dirs, files in os.walk(folder):
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        in_stills = 'still' in os.path.relpath(base, folder).lower()
        for f in files:
            if f.startswith('.'):
                continue
            fp, fl = os.path.join(base, f), f.lower()
            if 'credit' in fl and fl.endswith('.txt'):
                out['credits'] = out['credits'] or fp
            elif fl.endswith(IMG):
                out['stills' if in_stills else 'other_imgs'].append(fp)
            elif fl.endswith(VID):
                out['videos'].append(fp)
    out['videos'].sort(key=rank_video)
    out['stills'].sort()
    out['other_imgs'].sort()
    return out


def pick_thumb(found):
    """An explicit thumb wins; else the middle still; else any other image."""
    named = [f for f in found['stills'] + found['other_imgs']
             if re.match(r'_?thumb', os.path.basename(f), re.I)]
    if named:
        return named[0], 'explicit thumb.png'
    stills = [f for f in found['stills'] if not re.match(r'_?thumb', os.path.basename(f), re.I)]
    if stills:
        return stills[len(stills) // 2], 'middle still'
    if found['other_imgs']:
        return found['other_imgs'][0], 'first image found'
    return None, None


# ------------------------------------------------------------------ images

def sips_thumb(src, dest, w, h):
    """Scale to cover, then centre-crop to exactly w x h."""
    tmp = dest + '.tmp.png'
    sw = int(run(['sips', '-g', 'pixelWidth', src]).split(':')[-1])
    sh = int(run(['sips', '-g', 'pixelHeight', src]).split(':')[-1])
    # Scale so both dimensions cover the target, then crop the excess.
    if sw / sh > w / h:
        run(['sips', '--resampleHeight', str(h), src, '--out', tmp])
    else:
        run(['sips', '--resampleWidth', str(w), src, '--out', tmp])
    run(['sips', '-c', str(h), str(w), tmp, '--out', tmp])
    run(['sips', '-s', 'format', 'jpeg', '-s', 'formatOptions', '80', tmp, '--out', dest])
    os.remove(tmp)


def make_thumbs(slug, src, dry):
    tdir = os.path.join(ROOT, 'assets', 'thumbs')
    made = []
    for tag, (w, h) in SIZES.items():
        dest = os.path.join(tdir, f'{slug}-{tag}.jpg')
        made.append(os.path.relpath(dest, ROOT))
        if not dry:
            os.makedirs(tdir, exist_ok=True)
            sips_thumb(src, dest, w, h)
    return made


def make_carousel(slug, stills, count, dry):
    if count <= 0 or not stills:
        return []
    pool = [f for f in stills if not re.match(r'_?thumb', os.path.basename(f), re.I)]
    if not pool:
        return []
    # Spread the picks across the spot rather than taking the first N.
    if len(pool) > count:
        step = len(pool) / count
        pool = [pool[int(i * step)] for i in range(count)]
    cdir = os.path.join(ROOT, 'assets', 'carousel', slug)
    made = []
    for i, src in enumerate(pool):
        dest = os.path.join(cdir, f'{i:02d}.jpg')
        made.append(os.path.relpath(dest, ROOT))
        if not dry:
            os.makedirs(cdir, exist_ok=True)
            run(['sips', '--resampleWidth', str(CAROUSEL_W), '-s', 'format', 'jpeg',
                 '-s', 'formatOptions', '80', src, '--out', dest])
    return made


# ------------------------------------------------------------------- vimeo

def vimeo_token():
    if not os.path.exists(TOKEN_FILE):
        die(f'{TOKEN_FILE} not found — no Vimeo token. Re-run with --no-vimeo to skip.')
    tok = open(TOKEN_FILE).read().strip()
    if not tok:
        die(f'{TOKEN_FILE} is empty.')
    return tok


def vimeo_api(tok, method, path, body=None):
    req = urllib.request.Request(
        'https://api.vimeo.com' + path, method=method,
        data=json.dumps(body).encode() if body else None,
        headers={'Authorization': 'Bearer ' + tok,
                 'Content-Type': 'application/json',
                 'Accept': 'application/vnd.vimeo.*+json;version=3.4'})
    try:
        with urllib.request.urlopen(req) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        die(f'Vimeo {method} {path} -> HTTP {e.code}\n{e.read().decode()[:400]}')


def vimeo_upload(path, name, description):
    """Create the video via tus, PATCH the bytes up, return the page URL."""
    tok = vimeo_token()
    size = os.path.getsize(path)
    print(f'   uploading {size / 1e9:.2f} GB as "{name}" …')
    v = vimeo_api(tok, 'POST', '/me/videos', {
        'upload': {'approach': 'tus', 'size': str(size)},
        'name': name,
        'description': description,
        'privacy': {'view': 'unlisted', 'embed': 'public', 'download': False},
    })
    url = v['upload']['upload_link']
    offset, t0 = 0, time.time()
    with open(path, 'rb') as fh:
        while offset < size:
            chunk = fh.read(64 * 1024 * 1024)
            if not chunk:
                break
            req = urllib.request.Request(
                url, method='PATCH', data=chunk,
                headers={'Tus-Resumable': '1.0.0', 'Upload-Offset': str(offset),
                         'Content-Type': 'application/offset+octet-stream'})
            try:
                with urllib.request.urlopen(req) as r:
                    offset = int(r.headers['Upload-Offset'])
            except urllib.error.HTTPError as e:
                die(f'tus PATCH at offset {offset} -> HTTP {e.code}')
            pct = offset / size * 100
            rate = offset / max(time.time() - t0, 1) / 1e6
            print(f'\r   {pct:5.1f}%  {offset/1e9:.2f}/{size/1e9:.2f} GB  {rate:.1f} MB/s',
                  end='', flush=True)
    print()
    return 'https://vimeo.com' + v['uri'].replace('/videos', '')


# ------------------------------------------------------------------- entry

def category_for(folder_name, production):
    low = folder_name.lower()
    if any(h in low for h in MV_HINTS):
        return 'Music Video'
    if any(h in low for h in SHORT_HINTS):
        return 'Short Film'
    return 'Commercial'


def third_line_for(category, production):
    if category != 'Commercial' or not production:
        return category
    handles = re.findall(r'@([\w\.\-]+)', production)
    if not handles:
        return production
    h = handles[0].lower()
    return PROD_MAP.get(h, PROD_MAP.get(h.split('.')[0], pretty_handle(handles[0]).title()))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('job', help='job name, folder name, or full path')
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--no-vimeo', action='store_true')
    ap.add_argument('--group', default='hidden')
    ap.add_argument('--thumb', default=None)
    ap.add_argument('--client', default=None, help='override the client name')
    ap.add_argument('--title', default=None, help='override the spot title')
    ap.add_argument('--carousel', type=int, default=10,
                    help='how many carousel stills to build (0 to skip)')
    ap.add_argument('--carousel-card', action='store_true',
                    help='let the stills replace the thumbnail on the archive card')
    ap.add_argument('--commit', action='store_true')
    args = ap.parse_args()

    folder = resolve_folder(args.job)
    name = os.path.basename(folder)
    print(f'\n== {name}\n   {folder}')

    projects = json.load(open(DATA))
    if any(p.get('folder') == name for p in projects):
        die(f'"{name}" is already in projects.json — nothing to do.')

    found = scan(folder)
    if not found['videos']:
        die('no video file found in that folder.')
    video = found['videos'][0]
    print(f'   video    {os.path.relpath(video, folder)}'
          f'  ({os.path.getsize(video) / 1e9:.2f} GB)')
    if len(found['videos']) > 1:
        print(f'            (chose 1 of {len(found["videos"])}; '
              f'next best was {os.path.relpath(found["videos"][1], folder)})')

    # Credits are the one thing we cannot guess. Missing ones are not fatal:
    # the spot stages without them and gets flagged for a later pass.
    needs_review = False
    if found['credits']:
        client, title, extra, director, production, credits_text = parse_credits(found['credits'])
        if not title and client:
            title, client = client, ''
    else:
        needs_review = True
        client, title, extra, director, production, credits_text = '', '', '', '', '', ''
        template = os.path.join(MASTERS, '_credits.txt')
        dest = os.path.join(folder, '_credits.txt')
        if not args.dry_run and os.path.exists(template) and not os.path.exists(dest):
            run(['cp', template, dest])
            print(f'   NOTE     no credits file — blank template left at {dest}')
        else:
            print('   NOTE     no credits file — staging without credits')

    # --client / --title win over anything parsed, and cover the no-credits case.
    client = args.client or client
    title = args.title or title
    if not title:
        needs_review = True
        title = re.sub(r'[_\s]+', ' ', re.sub(r'^\d+[_-]?', '', name)).strip().title()
        print(f'   NOTE     no title in credits — guessed "{title}" from the folder name')
    category = category_for(name, production)
    third = third_line_for(category, production)
    slug = slugify(f'{client}-{title}')[:60] or slugify(name)
    taken = {p['slug'] for p in projects}
    n = 2
    base = slug
    while slug in taken:
        slug, n = f'{base}-{n}', n + 1

    print(f'   credits  {os.path.relpath(found["credits"], folder) if found["credits"] else "(none)"}')
    print(f'   client   {client or "(none)"}')
    print(f'   title    {title or "(none)"}')
    print(f'   director {pretty_director(director) or "(none)"}')
    print(f'   category {category}   third line: {third}')
    print(f'   slug     {slug}')

    thumb_src, why = (args.thumb, 'given on the command line') if args.thumb else pick_thumb(found)
    if not thumb_src:
        die('no image to make a thumbnail from.')
    print(f'   thumb    {os.path.relpath(thumb_src, folder)}  ({why})')

    thumbs = make_thumbs(slug, thumb_src, args.dry_run)
    carousel = make_carousel(slug, found['stills'], args.carousel, args.dry_run)
    print(f'   built    {len(thumbs)} thumbs, {len(carousel)} carousel stills')

    vimeo_url = ''
    if not args.no_vimeo and not args.dry_run:
        vimeo_url = vimeo_upload(video, f'{client} — {title}'.strip(' —'), credits_text)
        print(f'   vimeo    {vimeo_url}')

    numbers = [int(p['number'][1:]) for p in projects if re.match(r'W\d+$', p.get('number', ''))]
    entry = {
        'slug': slug, 'client': client, 'title': title, 'featuring': extra,
        'director': pretty_director(director), 'director_raw': director,
        'production': production, 'category': category, 'third_line': third,
        'vimeo': vimeo_url, 'credits': credits_text, 'group': args.group,
        'needs_review': needs_review, 'mtime': os.path.getmtime(folder),
        'folder': name, 'thumb_src': thumb_src, 'video_src': video,
        'stills': found['stills'],
        'number': f'W{max(numbers, default=0) + 1:03d}',
        'selected': False,
        # The carousel REPLACES the card thumbnail with the stills, so it is opt-in
        # (--carousel-card) even when the stills exist. The gallery is separate: it
        # hangs the stills below the credits on the spot's own page.
        'carousel': bool(carousel) and args.carousel_card,
        'gallery': bool(carousel),
        # Newest goes to the top of /archive/, which sorts on arch_order ascending.
        'arch_order': 0,
        'delivered': time.strftime('%Y-%m-%d', time.localtime(os.path.getmtime(video))),
        'categories': [category],
    }

    if args.dry_run:
        print('\n-- dry run, nothing written --')
        return

    # Make room at the top of the archive: everything already ordered slides down one.
    for p in projects:
        if isinstance(p.get('arch_order'), int):
            p['arch_order'] += 1

    projects.append(entry)
    json.dump(projects, open(DATA, 'w'), indent=1, ensure_ascii=False)
    print(f'\n   added {entry["number"]} {slug} to projects.json')

    if args.commit:
        paths = ['data/projects.json'] + thumbs + carousel
        subprocess.run(['git', '-C', ROOT, 'add'] + paths, check=True)
        subprocess.run(['git', '-C', ROOT, 'commit', '-m',
                        f'add {slug}'], check=True)
        subprocess.run(['git', '-C', ROOT, 'push'], check=True)
        print('   pushed — CI will regenerate the pages')
    else:
        print('   review the diff, then commit and push (or re-run with --commit)')


if __name__ == '__main__':
    main()
