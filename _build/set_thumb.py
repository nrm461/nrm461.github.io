#!/usr/bin/env python3
"""
Set/replace the thumbnail for a project.

Usage:
    python3 _build/set_thumb.py <slug> <image-or-video path> [seconds]

Regenerates the 100px placeholder, 600px card thumb, and 1600px hero for that
slug. If given a video, grabs the frame at [seconds] (default: 40% duration).
Run build_site.py afterwards is NOT needed (filenames don't change) — just
publish, or hard-refresh to see it.
"""
import os, sys, subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def run(cmd): subprocess.run(cmd, check=True, capture_output=True)

def main():
    if len(sys.argv) < 3:
        print(__doc__); sys.exit(1)
    slug, src = sys.argv[1], sys.argv[2]
    tdir = os.path.join(ROOT, 'assets', 'thumbs')
    t600, t100, t1600 = (os.path.join(tdir, f'{slug}-{s}.jpg') for s in ('600', '100', '1600'))
    crop = 'scale=600:338:force_original_aspect_ratio=increase,crop=600:338'
    is_video = src.lower().endswith(('.mp4', '.mov', '.m4v'))
    if is_video:
        if len(sys.argv) > 3:
            ss = sys.argv[3]
        else:
            d = float(subprocess.check_output(['ffprobe', '-v', 'quiet', '-of', 'csv=p=0',
                  '-show_entries', 'format=duration', src]).strip() or 0)
            ss = str(max(1, d * 0.4))
        run(['ffmpeg', '-y', '-ss', ss, '-i', src, '-vf', crop, '-frames:v', '1', '-q:v', '4', t600])
        run(['ffmpeg', '-y', '-ss', ss, '-i', src, '-vf', 'scale=1600:-2', '-q:v', '4', t1600])
    else:
        run(['ffmpeg', '-y', '-i', src, '-vf', crop, '-frames:v', '1', '-q:v', '4', t600])
        run(['ffmpeg', '-y', '-i', src, '-vf', 'scale=1600:-2', '-q:v', '4', t1600])
    run(['ffmpeg', '-y', '-i', t600, '-vf', 'scale=100:56', '-q:v', '7', t100])
    print(f'thumbnail updated for {slug}')

if __name__ == '__main__':
    main()
