"""Signs in the Quran #1 - Water. Procedural vertical reel renderer."""
import math, os, sys, subprocess, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
FD = os.path.join(HERE, '..', 'fonts')
W, H = 1080, 1920
BW, BH = 540, 960          # background render resolution
FPS = 30

AR = os.path.join(FD, 'fontsource-amiri-quran-5.3.0/files/amiri-quran-arabic-400-normal.woff')
ARB = os.path.join(FD, 'fontsource-amiri-5.3.0/files/amiri-arabic-700-normal.woff')
SERIF = os.path.join(FD, 'fontsource-cormorant-garamond-5.3.0/files/cormorant-garamond-latin-500-normal.woff')
SERIF_I = os.path.join(FD, 'corm500i.ttf')
CAPS = os.path.join(FD, 'cinzel400.ttf')
CAPS_B = os.path.join(FD, 'cinzel600.ttf')

GOLD = (236, 205, 140)
CREAM = (238, 232, 220)
DIM = (170, 160, 140)

_fc = {}
def font(path, size):
    k = (path, size)
    if k not in _fc:
        _fc[k] = ImageFont.truetype(path, size, layout_engine=ImageFont.Layout.RAQM)
    return _fc[k]

# ---------------------------------------------------------------- utilities
def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))

def ease(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)

def smooth(e0, e1, x):
    return ease((x - e0) / (e1 - e0)) if e1 != e0 else float(x >= e1)

rng = np.random.default_rng(7)
yy, xx = np.mgrid[0:BH, 0:BW].astype(np.float32)
NX, NY = xx / BW, yy / BH

def value_noise(w, h, cells, seed):
    r = np.random.default_rng(seed).random((cells[1], cells[0])).astype(np.float32)
    im = Image.fromarray((r * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC)
    return np.asarray(im, np.float32) / 255.0

def fbm(w, h, seed, base=4, octaves=5):
    out = np.zeros((h, w), np.float32); amp = 1.0; tot = 0
    for o in range(octaves):
        c = base * 2 ** o
        out += amp * value_noise(w, h, (c, max(2, int(c * h / w))), seed + o)
        tot += amp; amp *= 0.5
    return out / tot

def starfield(seed, n, w=BW, h=BH):
    r = np.random.default_rng(seed)
    img = np.zeros((h, w), np.float32)
    xs = r.integers(0, w, n); ys = r.integers(0, h, n)
    b = r.random(n) ** 3
    img[ys, xs] = b
    big = r.random(n) > 0.985
    im = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8))
    glow = np.asarray(im.filter(ImageFilter.GaussianBlur(1.2)), np.float32) / 255.0
    bigimg = np.zeros_like(img); bigimg[ys[big], xs[big]] = 1
    bglow = np.asarray(Image.fromarray((bigimg * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(3)), np.float32) / 255.0
    return np.clip(img + glow * 2.5 + bglow * 6, 0, 1.5)

STARS_A = starfield(1, 2600)
STARS_B = starfield(2, 2600)
NEB = fbm(BW, BH, 11, base=3)
NEB2 = fbm(BW, BH, 21, base=2)
SEA_N = fbm(BW * 2, BH * 2, 31, base=6, octaves=5)
CLOUD = fbm(BW * 2, BH, 41, base=3, octaves=6)
EARTH = fbm(BW, BH, 51, base=24, octaves=4)

def stars(t, amt=1.0):
    tw = 0.5 + 0.5 * math.sin(t * 1.3)
    return (STARS_A * (0.6 + 0.4 * tw) + STARS_B * (1.0 - 0.4 * tw)) * amt

def space_bg(t, hue=(0.03, 0.06, 0.14), neb=0.35):
    g = (1 - NY) * 0.4 + 0.6
    base = np.stack([g * hue[0], g * hue[1], g * hue[2]], -1)
    n = np.clip(NEB * 1.6 - 0.55, 0, 1) ** 1.5 * neb
    n2 = np.clip(NEB2 * 1.8 - 0.8, 0, 1) * neb
    base += n[..., None] * np.array([0.12, 0.16, 0.35], np.float32)
    base += n2[..., None] * np.array([0.25, 0.12, 0.30], np.float32)
    s = stars(t)
    base += s[..., None] * np.array([0.9, 0.92, 1.0], np.float32)
    return base

def blob(cx, cy, r, sx=1.0, sy=1.0):
    d2 = ((xx - cx) / sx) ** 2 + ((yy - cy) / sy) ** 2
    return np.exp(-d2 / (2 * r * r))

def add(img, mask, color, k=1.0):
    img += mask[..., None] * (np.array(color, np.float32) * k)

def top_shade(img, h=0.45, k=0.75):
    m = np.clip(1 - NY / h, 0, 1) ** 1.5 * k
    img *= (1 - m)[..., None]

# ---------------------------------------------------------------- text
def ar_lines(text, f, maxw):
    words = text.split(); lines = []; cur = []
    for wd in words:
        trial = ' '.join(cur + [wd])
        if cur and f.getlength(trial, direction='rtl', language='ar') > maxw:
            lines.append(' '.join(cur)); cur = [wd]
        else:
            cur.append(wd)
    if cur: lines.append(' '.join(cur))
    return lines

def lat_lines(text, f, maxw):
    words = text.split(); lines = []; cur = []
    for wd in words:
        trial = ' '.join(cur + [wd])
        if cur and f.getlength(trial) > maxw:
            lines.append(' '.join(cur)); cur = [wd]
        else:
            cur.append(wd)
    if cur: lines.append(' '.join(cur))
    return lines

class TextEl:
    """Pre-rendered text block with glow; composited with fade + rise."""
    def __init__(self, text, path, size, color, y, t_in, t_out=None, arabic=False,
                 maxw=940, glow=0.55, spacing=1.25, tracking=0, glow_col=None):
        f = font(path, size)
        lines = (ar_lines if arabic else lat_lines)(text, f, maxw) if '\n' not in text else text.split('\n')
        lh = int(size * spacing)
        pad = 40
        bh = lh * len(lines) + pad * 2
        layer = Image.new('L', (W, bh), 0)
        d = ImageDraw.Draw(layer)
        for i, ln in enumerate(lines):
            y0 = pad + i * lh + lh // 2
            if arabic:
                d.text((W // 2, y0), ln, font=f, fill=255, anchor='mm', direction='rtl', language='ar')
            elif tracking:
                tw = sum(f.getlength(c) for c in ln) + tracking * (len(ln) - 1)
                x = W / 2 - tw / 2
                for c in ln:
                    d.text((x, y0), c, font=f, fill=255, anchor='lm'); x += f.getlength(c) + tracking
            else:
                d.text((W // 2, y0), ln, font=f, fill=255, anchor='mm')
        a = np.asarray(layer, np.float32) / 255.0
        g = np.asarray(layer.filter(ImageFilter.GaussianBlur(size * 0.28)), np.float32) / 255.0
        col = np.array(color, np.float32) / 255.0
        gcol = np.array(glow_col or color, np.float32) / 255.0
        self.alpha = a
        self.glow = g * glow
        self.col, self.gcol = col, gcol
        self.y = int(y - bh / 2)
        self.h = bh
        self.t_in, self.t_out = t_in, t_out

    def draw(self, frame, t):
        a = smooth(self.t_in, self.t_in + 0.9, t)
        if self.t_out is not None:
            a *= 1 - smooth(self.t_out, self.t_out + 0.7, t)
        if a <= 0.001:
            return
        rise = int(18 * (1 - a))
        y0 = self.y + rise
        y1 = y0 + self.h
        sy0, sy1 = max(0, y0), min(H, y1)
        if sy1 <= sy0: return
        al = self.alpha[sy0 - y0: sy1 - y0] * a
        gl = self.glow[sy0 - y0: sy1 - y0] * a
        reg = frame[sy0:sy1]
        reg += gl[..., None] * self.gcol * 0.9
        reg *= (1 - al)[..., None]
        reg += al[..., None] * self.col

def ayah_block(ar, en, ref, t0, t1, y=330, ar_size=74, en_size=44, maxw=930):
    els = []
    f = font(AR, ar_size)
    nlines = len(ar_lines(ar, f, maxw))
    ar_h = nlines * ar_size * 1.55
    ar_y = y + ar_h / 2
    els.append(TextEl(ar, AR, ar_size, GOLD, ar_y, t0, t1, arabic=True, maxw=maxw, spacing=1.55, glow=0.6))
    fe = font(SERIF_I, en_size)
    nen = len(lat_lines(en, fe, 900))
    en_y = ar_y + ar_h / 2 + 30 + nen * en_size * 1.2 / 2
    els.append(TextEl(en, SERIF_I, en_size, CREAM, en_y, t0 + 0.9, t1, maxw=900, spacing=1.2, glow=0.35))
    ref_y = en_y + nen * en_size * 1.2 / 2 + 44
    els.append(TextEl(ref, CAPS, 26, GOLD, ref_y, t0 + 1.5, t1, tracking=5, glow=0.4))
    return els

# ---------------------------------------------------------------- scenes
# each scene: (start, end, bg_fn(local_t, dur), [text elements])

def sc_intro(t, d):
    img = space_bg(t, neb=0.15) * 0.55
    hy = 0.62 * BH
    # dark water plane
    wm = np.clip((yy - hy) / 8, 0, 1)
    img *= (1 - 0.6 * wm)[..., None]
    add(img, wm * np.clip(1 - (yy - hy) / (BH - hy), 0, 1) ** 2, (0.02, 0.05, 0.10))
    ti = 1.5
    if t < ti:
        p = (t / ti) ** 2
        cy = 0.08 * BH + p * (hy - 0.08 * BH)
        add(img, blob(BW / 2, cy, 5, 1.0, 1.0 + 2.5 * p), (0.9, 0.95, 1.0), 1.6)
        add(img, blob(BW / 2, cy, 22), (0.3, 0.5, 0.8), 0.5)
    else:
        dt = t - ti
        dx = (xx - BW / 2); dy = (yy - hy) * 4.0
        dist = np.sqrt(dx * dx + dy * dy)
        for k in range(4):
            r = (dt - k * 0.45) * 150
            if r <= 0: continue
            fade = math.exp(-r / 380) * (1 if k == 0 else 0.7)
            ring = np.exp(-((dist - r) ** 2) / (2 * (3 + r * 0.02) ** 2)) * fade
            ring *= (yy > hy - 40)
            add(img, ring, (0.95, 0.82, 0.55), 1.1)
        flash = math.exp(-dt * 3)
        add(img, blob(BW / 2, hy, 30, 1.8, 0.6), (1.0, 0.85, 0.6), 1.5 * flash + 0.25)
    return img

def sc_count(t, d):
    img = space_bg(t + 20, neb=0.25) * 0.6
    n = int(clamp((t - 1.2) / 3.6) * 63)
    cx, cy = BW / 2, 0.60 * BH
    ga = math.pi * (3 - math.sqrt(5))
    lay = Image.new('L', (BW, BH), 0); dr = ImageDraw.Draw(lay)
    for i in range(63):
        r = 11 * math.sqrt(i + 0.5); th = i * ga + t * 0.08
        x = cx + r * math.cos(th); y = cy + r * math.sin(th)
        if i < n:
            dr.ellipse([x - 3.2, y - 3.2, x + 3.2, y + 3.2], fill=255)
        else:
            dr.ellipse([x - 1.2, y - 1.2, x + 1.2, y + 1.2], fill=60)
    a = np.asarray(lay, np.float32) / 255
    g = np.asarray(lay.filter(ImageFilter.GaussianBlur(5)), np.float32) / 255
    add(img, a, (0.95, 0.85, 0.6), 1.2)
    add(img, g, (0.4, 0.7, 1.0), 1.8)
    return img

def sc_throne(t, d):
    img = space_bg(t + 40, hue=(0.02, 0.05, 0.13), neb=0.45)
    hy = int(0.70 * BH)
    # light on horizon
    add(img, blob(BW / 2, hy, 60, 4.0, 0.7), (0.9, 0.75, 0.5), 0.35 + 0.1 * math.sin(t))
    # reflection
    rows = np.arange(hy, BH)
    src_rows = np.clip(2 * hy - rows, 0, BH - 1)
    depth = (rows - hy) / (BH - hy)
    refl = img[src_rows].copy()
    shift = (np.sin(rows * 0.35 + t * 2.0) * (2 + 10 * depth)).astype(int)
    cols = (np.arange(BW)[None, :] + shift[:, None]) % BW
    refl = refl[np.arange(len(rows))[:, None], cols]
    refl *= (0.55 * (1 - depth) ** 1.2)[:, None, None]
    refl += np.array([0.01, 0.03, 0.07], np.float32)
    img[hy:] = refl
    add(img, np.exp(-((yy - hy) ** 2) / 4.0), (0.7, 0.75, 0.9), 0.25)
    return img

# precompute branching growth for "every living thing"
def make_tree(seed=3):
    r = random.Random(seed); segs = []
    cx, cy = BW / 2, 0.66 * BH
    def grow(x, y, ang, ln, depth, tb):
        if depth > 6 or ln < 4: return
        nx = x + math.cos(ang) * ln; ny = y + math.sin(ang) * ln
        segs.append((x, y, nx, ny, tb, depth))
        nb = 2 if r.random() < 0.75 else 3
        for _ in range(nb):
            grow(nx, ny, ang + r.uniform(-0.75, 0.75), ln * r.uniform(0.66, 0.85), depth + 1, tb + 0.35)
    for k in range(11):
        a = -math.pi / 2 + (k - 5) * 0.52 + r.uniform(-0.1, 0.1)
        grow(cx, cy, a, r.uniform(48, 70), 0, r.uniform(0, 0.3))
    return segs
TREE = make_tree()

def sc_life(t, d):
    img = space_bg(t + 60, hue=(0.01, 0.05, 0.08), neb=0.2) * 0.6
    cx, cy = BW / 2, 0.66 * BH
    prog = (t - 0.6) * 0.95
    lay = Image.new('RGB', (BW, BH), 0); dr = ImageDraw.Draw(lay)
    for (x0, y0, x1, y1, tb, dp) in TREE:
        if prog <= tb: continue
        f = clamp((prog - tb) / 0.35)
        xe = x0 + (x1 - x0) * f; ye = y0 + (y1 - y0) * f
        c = (int(80 + 20 * dp), int(200 - 6 * dp), int(190 - 22 * dp))
        dr.line([x0, y0, xe, ye], fill=c, width=max(1, 4 - dp // 2))
        if f >= 1 and dp == 6:
            dr.ellipse([x1 - 1.5, y1 - 1.5, x1 + 1.5, y1 + 1.5], fill=(240, 220, 150))
    a = np.asarray(lay, np.float32) / 255
    g = np.asarray(lay.filter(ImageFilter.GaussianBlur(6)), np.float32) / 255
    img += a * 0.8 + g * 1.1
    pulse = 0.8 + 0.2 * math.sin(t * 3)
    add(img, blob(cx, cy, 9, 0.8, 1.1), (0.85, 0.95, 1.0), 1.5 * pulse)
    add(img, blob(cx, cy, 40), (0.2, 0.6, 0.8), 0.6 * pulse)
    return img

RAIN = [(random.Random(i).random(), random.Random(i + 999).random(), random.Random(i + 5).uniform(0.6, 1.0)) for i in range(420)]

def rain_layer(t, amt, angle=0.12):
    lay = Image.new('L', (BW, BH), 0); dr = ImageDraw.Draw(lay)
    n = int(len(RAIN) * amt)
    for i in range(n):
        x0, y0, sp = RAIN[i]
        y = ((y0 + t * 1.6 * sp) % 1.2 - 0.1) * BH
        x = (x0 * 1.2 - 0.1) * BW + y * angle
        ln = 26 * sp
        dr.line([x, y, x - ln * angle, y - ln], fill=int(170 * sp), width=1)
    return np.asarray(lay, np.float32) / 255

def sc_rain(t, d):
    img = np.zeros((BH, BW, 3), np.float32)
    off = int(t * 18)
    c = CLOUD[:, off:off + BW]
    c = np.clip(c * 1.7 - 0.45, 0, 1)
    top = np.clip(1.15 - NY * 1.3, 0, 1)
    base = 0.05 + 0.12 * c * top
    img += base[..., None] * np.array([0.65, 0.75, 1.0], np.float32)
    # lightning
    fl = 0.0
    for lt in (2.6, 2.85, 5.6):
        if t > lt: fl += math.exp(-(t - lt) * 10)
    img += (c * top * fl * 0.9)[..., None] * np.array([0.8, 0.85, 1.0], np.float32)
    r = rain_layer(t, 1.0)
    add(img, r, (0.7, 0.8, 1.0), 0.75)
    # puddle shimmer at bottom
    add(img, np.clip((NY - 0.86) * 8, 0, 1) * (0.5 + 0.5 * np.sin(xx * 0.3 + t * 5)) * 0.2, (0.5, 0.6, 0.8))
    return img

SPROUTS = []
_r = random.Random(9)
for i in range(46):
    x = _r.uniform(0.04, 0.96) * BW
    SPROUTS.append((x, _r.uniform(60, 240) * (1 - abs(x / BW - 0.5)), _r.uniform(-0.4, 0.4), _r.uniform(0, 1.6), _r.random()))

def sc_revive(t, d):
    gy = 0.80 * BH
    img = np.zeros((BH, BW, 3), np.float32)
    dawn = smooth(2.5, 7.0, t)
    sky = np.clip(1 - NY / 0.8, 0, 1)
    img += (sky * 0)[..., None]
    add(img, np.clip(NY / 0.8, 0, 1) ** 3 * (yy < gy), (0.10 + 0.35 * dawn, 0.08 + 0.18 * dawn, 0.12 + 0.05 * dawn))
    add(img, blob(BW / 2, gy, 70, 4, 1.2) * dawn, (1.0, 0.75, 0.4), 0.6)
    img += 0.03
    ground = yy >= gy
    green = smooth(3.0, 7.5, t)
    ec = (0.18 + EARTH * 0.18)
    gcol = np.stack([ec * (0.55 - 0.3 * green), ec * (0.38 + 0.12 * green), ec * 0.25], -1)
    img[ground] = gcol[ground] * (0.5 + 0.5 * dawn)
    # rain at start
    ra = 1 - smooth(2.0, 3.5, t)
    if ra > 0:
        add(img, rain_layer(t + 3, ra), (0.7, 0.8, 1.0), 0.6)
    # sprouts
    lay = Image.new('RGB', (BW, BH), 0); dr = ImageDraw.Draw(lay)
    for (x, hmax, bend, delay, k) in SPROUTS:
        g = smooth(2.6 + delay, 6.2 + delay, t)
        if g <= 0: continue
        h = hmax * g; pts = []
        for s in range(12):
            u = s / 11
            pts.append((x + bend * h * u * u + 3 * math.sin(t * 1.5 + k * 6) * u, gy - h * u))
        dr.line(pts, fill=(70, 170, 70), width=2)
        # leaves
        for u in (0.45, 0.7, 0.95):
            if g > u:
                px, py = pts[int(u * 11)]
                s = 4 * min(1, (g - u) * 4)
                dr.ellipse([px - s * 1.6, py - s * 0.6, px, py + s * 0.4], fill=(110, 200, 90))
                dr.ellipse([px, py - s * 0.6, px + s * 1.6, py + s * 0.4], fill=(110, 200, 90))
    a = np.asarray(lay, np.float32) / 255
    gl = np.asarray(lay.filter(ImageFilter.GaussianBlur(5)), np.float32) / 255
    img = img * (1 - a.max(-1, keepdims=True)) + a + gl * 0.8
    return img

def sc_seas(t, d):
    o1 = int(t * 10); o2 = int(t * 14)
    n1 = SEA_N[o1:o1 + BH, 100:100 + BW]
    n2 = SEA_N[BH - o2:2 * BH - o2, BW:2 * BW]
    edge = BW * 0.5 + 26 * np.sin(NY * 7 + t * 0.6) + 10 * np.sin(NY * 19 - t)
    m = 1 / (1 + np.exp(np.clip(-(xx - edge) / 3, -40, 40)))
    c1 = np.stack([0.01 + 0.05 * n1, 0.05 + 0.13 * n1, 0.16 + 0.28 * n1], -1)
    c2 = np.stack([0.03 + 0.10 * n2, 0.20 + 0.30 * n2, 0.24 + 0.26 * n2], -1)
    img = c1 * (1 - m[..., None]) + c2 * m[..., None]
    # caustic sparkle
    sp = np.clip((SEA_N[o2:o2 + BH, :BW] - 0.62) * 9, 0, 1) ** 2
    img += sp[..., None] * 0.18
    line = np.exp(-((xx - edge) ** 2) / 6.0) * (0.65 + 0.35 * np.sin(NY * 40 - t * 4))
    add(img, line, (1.0, 0.88, 0.62), 0.9 * smooth(1.0, 3.0, t))
    add(img, np.exp(-((xx - edge) ** 2) / 200.0), (0.9, 0.8, 0.6), 0.12 * smooth(1.0, 3.0, t))
    top_shade(img, 0.55, 0.85)
    return img

def drop_mask(cx, cy, r):
    # teardrop: circle + cone pointing up
    dx = (xx - cx) / r; dy = (yy - cy) / r
    circ = np.sqrt(dx * dx + dy * dy)
    tip = np.where(dy < 0, np.abs(dx) + (-dy) * 0.55, 9)
    sdf = np.minimum(circ - 1, np.where(dy < 0, tip - 1 + (-dy) * 0.0, 9))
    sdf = np.where((dy < 0) & (dy > -1.8), np.minimum(circ - 1, np.abs(dx) - (1 + dy / 1.8) * 0.95), circ - 1)
    return sdf, dx, dy

def sc_drink(t, d):
    img = space_bg(t + 90, hue=(0.02, 0.04, 0.09), neb=0.2) * 0.5
    cx, cy, r = BW / 2, 0.66 * BH + 6 * math.sin(t * 1.2), 95
    sdf, dx, dy = drop_mask(cx, cy, r)
    inside = np.clip(-sdf * 25, 0, 1)
    bitter = smooth(4.4, 5.2, t) * (1 - smooth(6.6, 7.6, t))
    clear = np.array([0.35, 0.65, 0.95], np.float32)
    salt = np.array([0.45, 0.42, 0.22], np.float32)
    col = clear * (1 - bitter) + salt * bitter
    shade = np.clip(0.35 + 0.6 * (dy + 1) / 2 - 0.2 * dx, 0, 1)
    body = inside * shade
    img = img * (1 - inside[..., None] * 0.85) + body[..., None] * col * 0.9
    rim = np.exp(-(sdf ** 2) / 0.0025)
    add(img, rim, (0.75, 0.88, 1.0) if bitter < 0.5 else (0.75, 0.7, 0.45), 0.7)
    add(img, blob(cx - r * 0.35, cy - r * 0.35, r * 0.12, 0.7, 1.3) * inside, (1, 1, 1), 1.0)
    add(img, blob(cx, cy + r * 0.2, r * 1.6), col, 0.25)
    return img

def sc_sink(t, d):
    img = np.zeros((BH, BW, 3), np.float32)
    # cross-section of earth
    gy = 0.42 * BH
    sky = (yy < gy)
    add(img, sky * np.clip(NY / 0.42, 0, 1), (0.04, 0.06, 0.12))
    strata = EARTH * 0.5 + 0.5 * (0.5 + 0.5 * np.sin(NY * 60 + EARTH * 6))
    ground = (~sky)
    img[ground] = (np.stack([0.10 + 0.06 * strata, 0.07 + 0.04 * strata, 0.05 + 0.03 * strata], -1))[ground]
    sink = smooth(1.5, 4.5, t); back = smooth(5.2, 7.2, t)
    level = gy + 30 + (sink * (1 - back)) * 0.48 * BH
    bright = (1 - 0.75 * sink) + 0.9 * back
    band = np.clip(1 - np.abs(yy - (level + 40)) / 45, 0, 1) ** 0.8
    flow = 0.8 + 0.2 * np.sin(xx * 0.05 - t * 3)
    add(img, band * flow * ground, (0.2, 0.55, 0.95), 0.75 * min(bright, 1.4))
    # spring stream surfacing when water returns
    if back > 0:
        sx = BW / 2
        col = np.exp(-((xx - sx) ** 2) / 30) * ((yy > gy - 4) & (yy < level + 40))
        col = col * (0.6 + 0.4 * np.sin(yy * 0.3 + t * 12)) * back
        add(img, col, (0.5, 0.8, 1.0), 1.2)
        add(img, blob(sx, gy, 28, 2.2, 0.6) * back, (0.6, 0.85, 1.0), 0.8)
    return img

def sc_favors(t, d):
    img = space_bg(t + 120, neb=0.3) * 0.75
    pts = [(0.5, 0.66, 0.0), (0.28, 0.78, 1.0), (0.74, 0.74, 1.8), (0.42, 0.88, 2.7), (0.65, 0.92, 3.4)]
    for (px, py, t0) in pts:
        cx, cy = px * BW, py * BH
        dist = np.sqrt((xx - cx) ** 2 + ((yy - cy) * 2.5) ** 2)
        for k in range(3):
            dt = t - t0 - k * 0.5
            if dt <= 0: continue
            r = dt * 70
            ring = np.exp(-((dist - r) ** 2) / 18) * math.exp(-dt * 0.5)
            add(img, ring, (0.95, 0.8, 0.5), 0.7)
        if t > t0:
            add(img, blob(cx, cy, 6, 1.5, 0.6), (1, 0.9, 0.7), 1.2 * math.exp(-(t - t0) * 2))
    return img

def star8(cx, cy, r, ang):
    pts = []
    for i in range(16):
        rr = r if i % 2 == 0 else r * 0.62
        a = ang + i * math.pi / 8
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    return pts

def sc_end(t, d):
    img = space_bg(t + 150, neb=0.25) * 0.5
    cx, cy = BW / 2, 0.44 * BH
    p = smooth(0.2, 2.2, t)
    lay = Image.new('L', (BW, BH), 0); dr = ImageDraw.Draw(lay)
    R = 120
    for k, rr in enumerate((R, R * 0.93)):
        dr.arc([cx - rr, cy - rr, cx + rr, cy + rr], -90, -90 + 360 * p, fill=255, width=2)
    pts = star8(cx, cy, R * 0.86 * p + 1, t * 0.05)
    dr.polygon(pts, outline=255)
    pts2 = star8(cx, cy, R * 0.55 * p + 1, -t * 0.08 + math.pi / 8)
    dr.polygon(pts2, outline=200)
    for i in range(8):
        a = t * 0.05 + i * math.pi / 4
        dr.line([cx, cy, cx + R * 0.86 * p * math.cos(a), cy + R * 0.86 * p * math.sin(a)], fill=90)
    a = np.asarray(lay, np.float32) / 255
    g = np.asarray(lay.filter(ImageFilter.GaussianBlur(4)), np.float32) / 255
    add(img, a, (0.95, 0.82, 0.55), 1.0)
    add(img, g, (0.95, 0.75, 0.45), 1.3)
    add(img, blob(cx, cy, 14), (1, 0.9, 0.7), 1.2 * p)
    return img

# ---------------------------------------------------------------- timeline
S = []
def scene(start, end, fn, els):
    S.append((start, end, fn, els))

scene(0, 6.5, sc_intro, [
    TextEl('SIGNS IN THE QURAN  ·  I', CAPS, 30, DIM, 330, 2.0, 5.6, tracking=6, glow=0.2),
    TextEl('مَاء', ARB, 220, GOLD, 600, 2.4, 5.6, arabic=True, glow=0.9),
    TextEl('Water', SERIF_I, 64, CREAM, 820, 3.1, 5.6),
])
scene(6.0, 13.5, sc_count, [
    TextEl('The word for water, māʾ,', SERIF_I, 52, CREAM, 300, 6.6, 12.8),
    TextEl('appears in the Quran', SERIF_I, 52, CREAM, 370, 7.0, 12.8),
    TextEl('TIMES', CAPS, 30, DIM, 1500, 8.4, 12.8, tracking=8, glow=0.2),
])
COUNT = (7.2, 3.6)     # counter start offset (scene-local 1.2s), duration
scene(13.0, 21.5, sc_throne, ayah_block('وَكَانَ عَرْشُهُ عَلَى الْمَاءِ', 'And His Throne had been upon water', 'HŪD  11:7', 13.6, 20.8))
scene(21.0, 29.5, sc_life, ayah_block('وَجَعَلْنَا مِنَ الْمَاءِ كُلَّ شَيْءٍ حَيٍّ', 'And We made from water every living thing', 'AL-ANBIYĀ’  21:30', 21.6, 28.8))
scene(29.0, 37.5, sc_rain, ayah_block('وَأَرْسَلْنَا الرِّيَاحَ لَوَاقِحَ فَأَنْزَلْنَا مِنَ السَّمَاءِ مَاءً فَأَسْقَيْنَاكُمُوهُ',
      'And We have sent the fertilizing winds and sent down water from the sky and given you drink from it', 'AL-HIJR  15:22', 29.6, 36.8))
scene(37.0, 46.5, sc_revive, ayah_block('وَمِنْ آيَاتِهِ أَنَّكَ تَرَى الْأَرْضَ خَاشِعَةً فَإِذَا أَنْزَلْنَا عَلَيْهَا الْمَاءَ اهْتَزَّتْ وَرَبَتْ',
      'And of His signs is that you see the earth stilled, but when We send down upon it rain, it quivers and grows', 'FUSSILAT  41:39', 37.6, 45.8))
scene(46.0, 55.5, sc_seas, ayah_block('مَرَجَ الْبَحْرَيْنِ يَلْتَقِيَانِ ۝ بَيْنَهُمَا بَرْزَخٌ لَا يَبْغِيَانِ',
      'He released the two seas, meeting side by side; between them is a barrier so neither of them transgresses', 'AR-RAHMĀN  55:19–20', 46.6, 54.8))
scene(55.0, 64.0, sc_drink,
      ayah_block('أَفَرَأَيْتُمُ الْمَاءَ الَّذِي تَشْرَبُونَ', 'And have you seen the water that you drink?', 'AL-WĀQI‘AH  56:68', 55.6, 59.2) +
      ayah_block('لَوْ نَشَاءُ جَعَلْنَاهُ أُجَاجًا فَلَوْلَا تَشْكُرُونَ', 'If We willed, We could make it bitter, so why are you not grateful?', 'AL-WĀQI‘AH  56:70', 59.9, 63.3))
scene(63.5, 72.5, sc_sink, ayah_block('قُلْ أَرَأَيْتُمْ إِنْ أَصْبَحَ مَاؤُكُمْ غَوْرًا فَمَنْ يَأْتِيكُمْ بِمَاءٍ مَعِينٍ',
      'Say, “Have you considered: if your water were to sink into the earth, who then could bring you flowing water?”', 'AL-MULK  67:30', 64.1, 71.8, y=250))
scene(72.0, 80.0, sc_favors, ayah_block('فَبِأَيِّ آلَاءِ رَبِّكُمَا تُكَذِّبَانِ', 'So which of the favors of your Lord would you deny?', 'AR-RAHMĀN  55:13', 72.6, 79.3, ar_size=84))
scene(79.5, 85.0, sc_end, [
    TextEl('SIGNS IN THE QURAN', CAPS_B, 50, GOLD, 1250, 80.6, None, tracking=6, glow=0.5),
    TextEl('Part I  ·  Water', SERIF_I, 44, CREAM, 1335, 81.2, None),
    TextEl('@islamevryday', SERIF_I, 58, GOLD, 1560, 81.6, None, glow=0.6),
    TextEl('Follow for the next sign', SERIF_I, 36, DIM, 1640, 82.2, None, glow=0.2),
])
TOTAL = 85.0

# counter digits cache
DIGITS = {}
def counter_el(n):
    if n not in DIGITS:
        DIGITS[n] = TextEl(str(n), CAPS_B, 150, GOLD, 1390, -10, None, glow=0.8)
    return DIGITS[n]

WATERMARK = TextEl('@islamevryday', SERIF_I, 32, (150, 140, 120), 1690, 0.6, 79.3, glow=0.0)

GRAIN = np.random.default_rng(5).normal(0, 1, (8, BH, BW)).astype(np.float32)
VIG = np.clip(1 - ((NX - 0.5) ** 2 * 1.4 + (NY - 0.5) ** 2 * 0.9), 0, 1) ** 0.8

def scene_alpha(st, en, t, xf=0.5):
    a = 1.0
    if st > 0: a *= smooth(st, st + xf, t)
    if en < TOTAL: a *= 1 - smooth(en - xf, en, t)
    return a

def render(fi):
    t = fi / FPS
    bg = np.zeros((BH, BW, 3), np.float32)
    active = []
    for (st, en, fn, els) in S:
        if st <= t < en:
            a = scene_alpha(st, en, t)
            bg += fn(t - st, en - st) * a
            active.append(els)
    if t >= TOTAL - 1.0:
        bg *= 1 - smooth(TOTAL - 1.0, TOTAL, t)
    bg *= VIG[..., None]
    bg += GRAIN[fi % 8][..., None] * 0.012
    # gentle tone map
    bg = 1 - np.exp(-np.clip(bg, 0, None) * 1.35)
    u8 = (np.clip(bg, 0, 1) * 255).astype(np.uint8)
    big = np.asarray(Image.fromarray(u8).resize((W, H), Image.BILINEAR), np.float32) / 255.0
    big = np.ascontiguousarray(big)
    for els in active:
        for e in els:
            e.draw(big, t)
    if 7.0 <= t < 13.3:
        n = int(clamp((t - COUNT[0]) / COUNT[1]) * 63)
        e = counter_el(n); e.t_in = 7.0; e.t_out = 12.8
        e.draw(big, t)
    WATERMARK.draw(big, t)
    if TOTAL - 1.0 <= t:
        big *= 1 - smooth(TOTAL - 1.0, TOTAL, t)
    return (np.clip(big, 0, 1) * 255).astype(np.uint8)

def render_chunk(a, b, out):
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}',
                          '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '18',
                          '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
    for fi in range(a, b):
        p.stdin.write(render(fi).tobytes())
    p.stdin.close(); p.wait()

if __name__ == '__main__':
    mode = sys.argv[1]
    if mode == 'still':
        for ts in sys.argv[2:]:
            Image.fromarray(render(int(float(ts) * FPS))).save(os.path.join(HERE, f'still_{ts}.png'))
    elif mode == 'chunk':
        render_chunk(int(sys.argv[2]), int(sys.argv[3]), sys.argv[4])
    elif mode == 'frames':
        print(int(TOTAL * FPS))
