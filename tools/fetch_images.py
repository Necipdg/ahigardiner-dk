#!/usr/bin/env python3
"""Henter opskalerede billeder fra upscaled.tsv og skriver dem web-optimeret ind i site/."""
import os, sys, urllib.request
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST = os.path.join(ROOT, 'upscaled.tsv')
SITE = os.path.join(ROOT, 'site')

if not os.path.exists(MANIFEST):
    print('ingen upscaled.tsv - springer over')
    sys.exit(0)

rows = []
with open(MANIFEST, encoding='utf-8') as fh:
    for line in fh:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        parts = line.split('\t')
        if len(parts) < 2:
            print('springer ugyldig linje over:', line[:60]); continue
        rel, url = parts[0], parts[1]
        maxw = int(parts[2]) if len(parts) > 2 and parts[2].strip() else 900
        rows.append((rel, url, maxw))

print('billeder i manifest:', len(rows))
fejl = 0
for rel, url, maxw in rows:
    dest = os.path.join(SITE, rel)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    tmp = dest + '.download'
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'ahigardiner-build'})
        with urllib.request.urlopen(req, timeout=120) as r, open(tmp, 'wb') as out:
            out.write(r.read())
        im = Image.open(tmp)
        im = im.convert('RGB')
        if im.width > maxw:
            im = im.resize((maxw, round(im.height * maxw / im.width)), Image.LANCZOS)
        im.save(dest, 'JPEG', quality=82, optimize=True, progressive=True)
        print('  ok  %-44s %sx%s  %d KB' % (rel, im.width, im.height, os.path.getsize(dest) // 1024))
    except Exception as e:
        fejl += 1
        print('  FEJL %-44s %s' % (rel, e))
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)

if fejl:
    print('%d billeder fejlede' % fejl)
    sys.exit(1)
print('alle billeder hentet')
