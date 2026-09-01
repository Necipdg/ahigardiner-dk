#!/usr/bin/env python3
"""Henter opskalerede billeder fra upscaled.tsv og skriver dem web-optimeret ind i site/.

Format pr. linje:  sti-i-site \t url \t maxbredde
En url der starter med '@' udvides med BASE (sparer plads i manifestet).
Til sidst rettes width/height paa alle <img> saa de matcher de nye filer.
"""
import os, sys, urllib.request
from PIL import Image

BASE = 'https://d8j0ntlcm91z4.cloudfront.net/user_3I9AiIatkQ4w9kA6hDNXcFJ2ZR6/hf_2026090'
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
        if url.startswith('@'):
            url = BASE + url[1:]
        maxw = int(parts[2]) if len(parts) > 2 and parts[2].strip() else 900
        rows.append((rel, url, maxw))

# statiske brandbilleder (logo, favicon) kopieres med fra repoet.
# Binaere filer ligger som <navn>.b64 (base64-tekst) og afkodes her.
import shutil, base64, hashlib
_static = os.path.join(ROOT, 'assets', 'img')
if os.path.isdir(_static):
    for b, _d, fs in os.walk(_static):
        for fn in fs:
            s_ = os.path.join(b, fn)
            rel_ = os.path.relpath(s_, _static)
            if fn.endswith('.b64'):
                d_ = os.path.join(SITE, 'assets', 'img', rel_[:-4])
                os.makedirs(os.path.dirname(d_), exist_ok=True)
                want, data = None, []
                with open(s_, encoding='ascii') as fb:
                    for ln in fb:
                        ln = ln.strip()
                        if ln.startswith('# sha256'):
                            want = ln.split()[-1]
                        elif ln:
                            data.append(ln)
                raw = base64.b64decode(''.join(data))
                got = hashlib.sha256(raw).hexdigest()
                if want and got != want:
                    print('  FEJL %s: sha256 %s != forventet %s' % (rel_, got, want))
                    sys.exit(1)
                with open(d_, 'wb') as fo:
                    fo.write(raw)
                print('  afkodet  %-40s %d KB' % (os.path.relpath(d_, SITE), len(raw) // 1024))
            else:
                d_ = os.path.join(SITE, 'assets', 'img', rel_)
                os.makedirs(os.path.dirname(d_), exist_ok=True)
                shutil.copy2(s_, d_)
                print('  kopieret', os.path.relpath(d_, SITE))

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

# --- ret width/height paa <img> saa de matcher de nye filer -------------------
import re
_dims = {}

def _size(src, page_dir):
    key = os.path.normpath(os.path.join(page_dir, src))
    if key not in _dims:
        try:
            with Image.open(os.path.join(SITE, key)) as im:
                _dims[key] = im.size
        except Exception:
            _dims[key] = None
    return _dims[key]

_IMG = re.compile(r'<img\b[^>]*>')
_SRC = re.compile(r'src="([^"]+)"')
rettet = sider = 0
for base, _d, files in os.walk(SITE):
    for fn in files:
        if not fn.endswith('.html'):
            continue
        p = os.path.join(base, fn)
        pd = os.path.relpath(base, SITE)
        pd = '' if pd == '.' else pd
        s = open(p, encoding='utf-8').read()

        def _repl(m, pd=pd):
            global rettet
            tag = m.group(0)
            ms = _SRC.search(tag)
            if not ms:
                return tag
            wh = _size(ms.group(1), pd)
            if not wh:
                return tag
            new = re.sub(r'\swidth="\d+"', ' width="%d"' % wh[0], tag)
            new = re.sub(r'\sheight="\d+"', ' height="%d"' % wh[1], new)
            if 'width=' not in new:
                new = new[:-1] + ' width="%d" height="%d">' % wh
            if new != tag:
                rettet += 1
            return new

        ny = _IMG.sub(_repl, s)
        if ny != s:
            open(p, 'w', encoding='utf-8').write(ny)
            sider += 1
print('dimensioner rettet: %d img-tags paa %d sider' % (rettet, sider))
for k, v in sorted(_dims.items()):
    if v is None:
        print('  ADVARSEL manglende billedfil:', k)
