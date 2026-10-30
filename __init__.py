# SPDX-FileCopyrightText: 2025-2026 The French Monkey
# SPDX-License-Identifier: GPL-3.0-or-later

bl_info = {
    "name": "Spline",
    "author": "The French Monkey",
    "version": (1, 0, 5),
    "blender": (4, 2, 0),
    "location": "View3D > Sidebar > Spline",
    "description": "Generate parametric spline",
    "category": "Add Spline",
    "license": "GPL-3.0-or-later",
}

import bpy
from math import sin, cos, sqrt, pi, exp, isfinite

# ----------------------------------------------------------
# Utility
# ----------------------------------------------------------

def clamp_vec3(x, y, z, limit=1000.0):
    if abs(x) > limit or abs(y) > limit or abs(z) > limit:
        x *= 0.1; y *= 0.1; z *= 0.1
    if not isfinite(x + y + z):
        return 0.0, 0.0, 0.0
    return x, y, z

def build_polyline_curve(obj, pts, closed=False):
    if obj.type != 'CURVE':
        return

    curve = obj.data
    curve.dimensions = '3D'

    while curve.splines:
        curve.splines.remove(curve.splines[0])

    if not pts:
        return

    if isinstance(pts[0][0], (int, float)):
        pts = [pts]

    for curve_pts in pts:
        if not curve_pts:
            continue
        spline = curve.splines.new('POLY')
        spline.use_cyclic_u = closed
        spline.points.add(len(curve_pts) - 1)
        for i, (x, y, z) in enumerate(curve_pts):
            spline.points[i].co = (x, y, z, 1.0)

def _downsample(points, target):
    n = len(points)
    if n <= target or target < 2:
        return points
    return [points[int(i * (n - 1) / (target - 1))] for i in range(target)]

# ----------------------------------------------------------
# Geometric Splines
# ----------------------------------------------------------

def make_spiral(seg, r, o, w, s, h):
    pts = []
    turns = 3 + int(o * 6)
    for i in range(seg):
        t = i / (seg - 1)
        a = t * turns * 2 * pi
        x = cos(a) * r * t
        y = sin(a) * r * t
        z = h * t * 0.5
        pts.append((x, y, z))
    return pts

def make_helix(seg, r, o, w, s, h):
    pts = []
    turns = 3 + int(o * 4)
    for i in range(seg):
        t = i / (seg - 1)
        a = t * turns * 2 * pi
        x = cos(a) * r
        y = sin(a) * r
        z = h * t
        pts.append((x, y, z))
    return pts

def make_wave(seg, r, o, w, s, h):
    pts = []
    amp = r * (0.5 + o)
    for i in range(seg):
        t = (i / (seg - 1)) * 2 * pi
        x = (t - pi)
        y = sin(t * s) * amp
        z = cos(t * max(1.0, w)) * h * 0.2
        pts.append((x, y, z))
    return pts

def make_zigzag(seg, r, o, w, s, h):
    pts = []
    amp = r * 0.25 * (1 + o)
    for i in range(seg):
        x = (i / (seg - 1) - 0.5) * r * 2
        y = amp if i % 2 == 0 else -amp
        z = sin(i * 0.25 * s) * h * 0.1
        pts.append((x, y, z))
    return pts

def make_golden_spiral(seg, r, o, w, s, h):
    ga = pi * (3 - sqrt(5))
    pts = []
    for i in range(seg):
        a = i * ga
        R = sqrt(i + 1) * r * 0.05 * (1 + o)
        x = cos(a) * R + sin(a * s) * w * 0.05
        y = sin(a) * R + cos(a * s) * w * 0.05
        z = sin(a * s) * h * 0.1
        pts.append((x, y, z))
    return pts

def make_spirograph(seg, r, o, w, s, h):
    pts = []
    R = r
    r2 = max(1e-4, R * (0.25 + o * 0.35))
    d = R * (0.2 + 0.6 * min(1.0, w + 0.2))
    for i in range(seg):
        t = i * 2 * pi / seg
        k = (R - r2) / r2
        x = (R - r2) * cos(t) + d * cos(k * t * s)
        y = (R - r2) * sin(t) - d * sin(k * t * s)
        x *= 0.1; y *= 0.1
        z = sin(t * s) * h * 0.2
        pts.append((x, y, z))
    return pts

def make_lissajous(seg, r, o, w, s, h):
    a = max(1, s)
    b = max(1, s - 2)
    c = s + 1
    delta = pi / 2
    pts = []
    for i in range(seg):
        t = (i / (seg - 1)) * 2 * pi
        x = r * sin(a * t + delta) * (1 + sin(t * s) * w * 0.1)
        y = r * sin(b * t) * (1 + cos(t * s) * w * 0.1)
        z = r * 0.5 * sin(c * t) * h * 0.2
        pts.append((x, y, z))
    return pts

def make_butterfly(seg, r, o, w, s, h):
    pts = []
    sc = r * 0.3 * (1 + o)
    for i in range(seg):
        t = i * 12 * pi / seg
        rr = exp(sin(t)) - 2 * cos(4 * t) + (sin((2 * t - pi) / 24))**5
        rr *= sc
        x = rr * cos(t) + sin(t * s) * w * 0.1
        y = rr * sin(t) + cos(t * s) * w * 0.1
        z = sin(t * s) * h * 0.2
        pts.append((x, y, z))
    return pts

def make_superformula(seg, r, o, w, s, h):
    pts = []
    a, b = 1.0, 1.0
    m = max(2, s * 2)
    n1 = 0.3 + o
    n2 = 1.3 + w
    n3 = 1.7 + o * 2
    for i in range(seg):
        th = (i / (seg - 1)) * 2 * pi
        p1 = abs(cos(m * th / 4) / a)**n2
        p2 = abs(sin(m * th / 4) / b)**n3
        rr = (p1 + p2)**(-1 / max(1e-6, n1))
        x = r * rr * cos(th)
        y = r * rr * sin(th)
        z = rr * sin(th * s) * h * 0.3
        pts.append((x, y, z))
    return pts

def make_torusknot(seg, r, o, w, s, h):
    pts = []
    p = max(2, s)
    q = max(1, s - 1)
    R = r * (1.0 + 0.2 * o)
    r2 = r * (0.3 + 0.3 * w)
    for i in range(seg):
        t = (i / (seg - 1)) * 2 * pi
        cq, sq = cos(q * t), sin(q * t)
        cp, sp = cos(p * t), sin(p * t)
        X = (R + r2 * cq) * cp
        Y = (R + r2 * cq) * sp
        Z = r2 * sq * h
        pts.append((X * 0.5, Y * 0.5, Z * 0.5))
    return pts

def make_rose(seg, r, o, w, s, h):
    pts = []
    k = max(1, s) + int(o * 2)
    for i in range(seg):
        th = (i / (seg - 1)) * 2 * pi
        rr = r * cos(k * th)
        x = rr * cos(th)
        y = rr * sin(th)
        z = sin(k * th) * h * 0.2
        pts.append((x, y, z))
    return pts

def make_vortex(seg, r, o, w, s, h):
    pts = []
    turns = 3 + s * 0.5
    decay = 1.0 + o * 0.5
    wobble = 0.5 + w * 0.2
    for i in range(seg):
        t = i / (seg - 1)
        a = t * turns * 2 * pi
        rad = r * exp(-decay * t)
        x = cos(a) * rad
        y = sin(a) * rad
        z = sin(a * wobble) * h * 0.5 - t * h * 0.3
        pts.append((x, y, z))
    return pts

def make_infinity(seg, r, o, w, s, h):
    pts = []
    freq = 1.0 + s * 0.2
    twist = 1.0 + o * 0.5
    wave = 0.3 + w * 0.1
    for i in range(seg):
        t = (i / (seg - 1)) * 2 * pi
        x = r * sin(t)
        y = r * sin(t) * cos(t * twist)
        z = sin(t * freq) * h * wave
        pts.append((x, y, z))
    return pts

def make_ripplering(seg, r, o, w, s, h):
    pts = []
    waves = max(3, int(4 + s))
    amp = r * 0.2 * (1 + o)
    freq = 1.0 + w * 0.2
    for i in range(seg):
        t = (i / (seg - 1)) * 2 * pi
        rad = r + sin(t * waves * freq) * amp
        x = cos(t) * rad
        y = sin(t) * rad
        z = sin(t * waves) * h * 0.3
        pts.append((x, y, z))
    return pts

def make_twistribbon(seg, r, o, w, s, h):
    pts = []
    turns = 2 + s
    twist = 0.5 + o
    for i in range(seg):
        t = i / (seg - 1)
        a = t * turns * 2 * pi
        offset = sin(a * twist) * r * 0.3
        x = cos(a) * (r + offset)
        y = sin(a) * (r + offset)
        z = cos(a * twist) * h * 0.4
        pts.append((x, y, z))
    return pts

# ----------------------------------------------------------
# Chaotic Attractors
# ----------------------------------------------------------

def make_lorenz(seg, r, o, w, s, h):
    sigma, rho, beta = 10 + s, 22 + 8 * (1 + o), 2.666 + 0.1 * w
    dt = 0.008
    steps = int(seg * 8)
    x, y, z = 0.1, 0.0, 0.0
    sc = r * 0.05
    pts = []
    for _ in range(steps):
        dx = sigma * (y - x)
        dy = x * (rho - z) - y
        dz = x * y - beta * z
        x += dx * dt; y += dy * dt; z += dz * dt
        pts.append((x * sc, y * sc, z * sc * h))
    return pts

def make_rossler(seg, r, o, w, s, h):
    a = 0.2 + 0.05 * w
    b = 0.2 + 0.05 * o
    c = 5.7 + 0.3 * s
    dt = 0.01
    steps = int(seg * 8)
    x, y, z = 0.1, 0.0, 0.0
    sc = r * 0.08
    pts = []
    for _ in range(steps):
        dx = -y - z
        dy = x + a * y
        dz = b + z * (x - c)
        x += dx * dt; y += dy * dt; z += dz * dt
        pts.append((x * sc, y * sc, z * sc * h))
    return pts

def make_aizawa(seg, r, o, w, s, h):
    a = 0.95 + 0.05 * w
    b = 0.7 + 0.05 * o
    d = 3.5 + 0.3 * s
    c, e, f = 0.6, 0.25, 0.1
    dt = 0.01
    steps = int(seg * 10)
    x, y, z = 0.1, 0.0, 0.0
    sc = r * 0.3
    pts = []
    for _ in range(steps):
        dx = (z - b) * x - d * y
        dy = d * x + (z - b) * y
        dz = c + a * z - (z**3) / 3 - (x**2 + y**2) * (1 + e * z) + f * z * (x**3)
        x += dx * dt; y += dy * dt; z += dz * dt
        pts.append((x * sc, y * sc, z * sc * h))
    return pts

def make_chen(seg, r, o, w, s, h):
    a = 40.0 + s * 0.2
    b = 3.0 + o * 0.5
    c = 28.0 + w * 2.0
    dt = 0.002
    steps = int(seg * 10)
    x, y, z = 0.1, 0.0, 0.0
    sc = r * 0.02
    pts = []
    for _ in range(steps):
        dx = a * (y - x)
        dy = (c - a) * x - x * z + c * y
        dz = x * y - b * z
        x += dx * dt; y += dy * dt; z += dz * dt
        x, y, z = clamp_vec3(x, y, z)
        pts.append((x * sc, y * sc, z * sc * h))
    return pts

def make_dadras(seg, r, o, w, s, h):
    a = 3.0 + 0.2 * w
    b = 2.7 + 0.2 * o
    c = 1.7 + 0.1 * s
    d, e = 2.0, 9.0
    dt = 0.0045
    steps = int(seg * 12)
    x, y, z = 1.0, 1.0, 0.0
    sc = r * 0.03
    pts = []
    for _ in range(steps):
        dx = y - a * x + b * y * z
        dy = c * y - x * z + z
        dz = d * x * y - e * z
        x += dx * dt; y += dy * dt; z += dz * dt
        x, y, z = clamp_vec3(x, y, z, 50.0)
        pts.append((x * sc, y * sc, z * sc * h))
    if pts:
        avgx = sum(p[0] for p in pts) / len(pts)
        avgy = sum(p[1] for p in pts) / len(pts)
        avgz = sum(p[2] for p in pts) / len(pts)
        pts = [(x - avgx, y - avgy, z - avgz) for (x, y, z) in pts]
    return pts

def make_halvorsen(seg, r, o, w, s, h):
    a = 1.4 + 0.2 * w + 0.1 * o
    dt = 0.005
    steps = int(seg * 10)
    x, y, z = 0.1, 0.0, 0.0
    sc = r * 0.08
    pts = []
    for _ in range(steps):
        dx = -a * x - 4 * y - 4 * z - y * y
        dy = -a * y - 4 * z - 4 * x - z * z
        dz = -a * z - 4 * x - 4 * y - x * x
        x += dx * dt; y += dy * dt; z += dz * dt
        x, y, z = clamp_vec3(x, y, z, 50.0)
        pts.append((x * sc, y * sc, z * sc * h))
    if len(pts) < 2:
        pts = [(0, 0, 0), (r, 0, 0)]
    return pts

def make_thomas(seg, r, o, w, s, h):
    b = 0.19 + 0.05 * w + 0.05 * o
    dt = 0.01
    steps = int(seg * 15)
    x, y, z = 0.1, -0.1, 0.1
    sc = r * 0.25
    pts = []
    for _ in range(steps):
        dx = sin(y) - b * x
        dy = sin(z) - b * y
        dz = sin(x) - b * z
        x += dx * dt; y += dy * dt; z += dz * dt
        x, y, z = clamp_vec3(x, y, z, 30.0)
        pts.append((x * sc, y * sc, z * sc * h))
    if len(pts) < 2:
        pts = [(0, 0, 0), (r, 0, 0)]
    return pts

def make_rikitake(seg, r, o, w, s, h):
    a = 2.0 + 0.5 * o
    mu = 5.0 + 0.2 * s
    dt = 0.01
    steps = int(seg * 10)
    x, y, z = 0.1, 0.1, 0.1
    sc = r * 0.1
    pts = []
    for _ in range(steps):
        dx = -mu * x + y * z
        dy = -mu * y + (z - a) * x
        dz = 1.0 - x * y
        x += dx * dt; y += dy * dt; z += dz * dt
        pts.append((x * sc, y * sc, z * sc * h))
    return pts

def make_chua(seg, r, o, w, s, h):
    alpha = 15.6 + 2.0 * o
    beta = 28.0 + 1.0 * s
    m0 = -1.143 + 0.1 * w
    m1 = -0.714 + 0.1 * o
    dt = 0.005
    steps = int(seg * 12)
    x, y, z = 0.1, 0.0, 0.0
    sc = r * 0.05
    pts = []
    for _ in range(steps):
        f = m1 * x + 0.5 * (m0 - m1) * (abs(x + 1) - abs(x - 1))
        dx = alpha * (y - x - f)
        dy = x - y + z
        dz = -beta * y
        x += dx * dt; y += dy * dt; z += dz * dt
        pts.append((x * sc, y * sc, z * sc * h))
    return pts

def make_rabinovich(seg, r, o, w, s, h):
    a = 0.14 + 0.05 * o
    b = 0.10 + 0.05 * w
    dt = 0.01
    steps = int(seg * 10)
    x, y, z = 0.1, 0.1, 0.1
    sc = r * 0.3
    pts = []
    for _ in range(steps):
        dx = y * (z - 1 + x * x) + b * x
        dy = x * (3 * z + 1 - x * x) + b * y
        dz = -2 * z * (a + x * y)
        x += dx * dt; y += dy * dt; z += dz * dt
        pts.append((x * sc, y * sc, z * sc * h))
    return pts

def make_rossler_mod(seg, r, o, w, s, h):
    a = 0.2 + 0.1 * o
    b = 0.2 + 0.05 * w
    c = 9.0 + 0.3 * s
    dt = 0.01
    steps = int(seg * 12)
    x, y, z = 0.1, 0.0, 0.0
    sc = r * 0.1
    pts = []
    for _ in range(steps):
        dx = -y - z
        dy = x + a * y
        dz = b + z * (x - c)
        x += dx * dt; y += dy * dt; z += dz * dt
        pts.append((x * sc, y * sc, z * sc * h))
    return pts

def make_dequanli(seg, r, o, w, s, h):
    a = 40.0 + 2.0 * o
    b = 1.833 + 0.05 * w
    c = 0.16 + 0.02 * s
    d = 0.65
    e = 20.0   
    f = 5.0   

    dt = 0.0008   
    steps = int(seg * 20)
    x, y, z = 0.1, 0.1, 0.1
    sc = r * 0.01  
    pts = []

    for _ in range(steps):
        dx = a * (y - x) + d * x * z
        dy = e * x + f * y - x * z
        dz = b * z + x * y - c * x * x
        x += dx * dt
        y += dy * dt
        z += dz * dt
        pts.append((x * sc, y * sc, z * sc * h))

    return pts

def make_hadley(seg, r, o, w, s, h):
    a = 0.2 + 0.05 * w   
    mu = 4.0 + 0.5 * o    
    nu = 1.0 + 0.2 * s    
    dt = 0.01
    steps = int(seg * 20)
    x, y, z = 0.1, 0.1, 0.1
    sc = r * 0.2
    pts = []

    for _ in range(steps):
        dx = -y**2 - z**2 - mu * x + mu * nu
        dy = x * y - a * z - y + 0.1
        dz = a * y + x * z - z
        x += dx * dt
        y += dy * dt
        z += dz * dt
        pts.append((x * sc, y * sc, z * sc * h))

    return pts

def make_burkeshaw(seg, r, o, w, s, h):
    a = 10.0 + s
    b = 4.272 + 0.1 * o
    dt = 0.002
    steps = int(seg * 12)
    x, y, z = 1.0, 0.0, 0.0
    sc = r * 0.05
    pts = []
    for _ in range(steps):
        dx = -a * (x + y)
        dy = -y - a * x * z
        dz = a * x * y + b
        x += dx * dt; y += dy * dt; z += dz * dt
        pts.append((x * sc, y * sc, z * sc * h))
    return pts

def make_luchensys(seg, r, o, w, s, h):
    a = 36.0 + 3.0 * o
    b = 3.0 + 0.2 * w
    c = 20.0 + 1.0 * s
    dt = 0.001  
    steps = int(seg * 25)
    x, y, z = 0.1, 0.1, 0.1
    sc = r * 0.01 
    pts = []

    for _ in range(steps):
        dx = a * (y - x)
        dy = c * x - x * z + c * y
        dz = x * y - b * z
        x += dx * dt
        y += dy * dt
        z += dz * dt
        pts.append((x * sc, y * sc, z * sc * h))

    return pts

def make_blackhole(seg, r, o, w, s, h):
    import random
    random.seed(42)

    steps = int(max(64, seg * 40))
    revs = max(3, 6 + int(0.7 * s))
    decay = 2.0 + 1.5 * max(0.0, o)
    spin = revs * 2.0 * pi
    ripple = 0.03 + 0.03 * min(5.0, w)
    wobble = 0.02 + 0.02 * min(5.0, w)
    depth = 0.8 + 0.6 * h
    R0 = 1.2 + 0.6 * o

    pts = []
    angle = 0.0
    for i in range(steps):
        t = i / (steps - 1)
        rad = R0 * exp(-decay * t) * (1.0 + ripple * sin(12.0 * pi * t))
        angle = spin * t + 0.5 * (rad * rad)
        x = rad * cos(angle)
        y = rad * sin(angle)
        z_fall = -(1.0 - exp(-2.5 * t)) * depth * 0.5
        z_bowl = 0.25 * (rad * rad) * h
        z_wobble = wobble * sin(10.0 * pi * t + 0.7 * s)
        z = z_fall + z_bowl + z_wobble
        pts.append((x, y, z))

    max_xy = max(sqrt(x * x + y * y) for x, y, _ in pts)
    target = r
    sc = target / max_xy
    out = [(x * sc, y * sc, z * sc * 0.6) for (x, y, z) in pts]
    return out

# ----------------------------------------------------------
# Fractal Splines
# ----------------------------------------------------------

def make_koch(seg, r, o, w, s, h, depth=3):
    pts = [(0.0, 0.0, 0.0), (r, 0.0, 0.0)]
    for _ in range(max(0, min(8, depth))):
        new_pts = []
        for i in range(len(pts) - 1):
            x1, y1, _ = pts[i]
            x2, y2, _ = pts[i + 1]
            dx, dy = x2 - x1, y2 - y1
            p1 = (x1, y1, 0)
            p2 = (x1 + dx / 3.0, y1 + dy / 3.0, 0)
            px = x1 + dx / 2.0 - sqrt(3.0) * dy / 6.0
            py = y1 + dy / 2.0 + sqrt(3.0) * dx / 6.0
            p3 = (px, py, 0)
            p4 = (x1 + 2.0 * dx / 3.0, y1 + 2.0 * dy / 3.0, 0)
            p5 = (x2, y2, 0)
            if i == 0: new_pts.append(p1)
            new_pts += [p2, p3, p4, p5]
        pts = new_pts
    pts = [(x * (1 + o), y * (1 + o), sin((x + y) * 0.2) * h * 0.2) for (x, y, _) in pts]
    return _downsample(pts, seg)

def make_dragon(seg, r, o, w, s, h, depth=12):
    depth = max(1, min(16, depth))
    pts2d = [(0.0, 0.0), (1.0, 0.0)]
    for _ in range(depth):
        pivot = pts2d[-1]
        new_pts = pts2d[:-1]
        for p in reversed(pts2d):
            x, y = p[0] - pivot[0], p[1] - pivot[1]
            xr, yr = -y, x
            new_pts.append((xr + pivot[0], yr + pivot[1]))
        pts2d = new_pts
    xs, ys = zip(*pts2d)
    minx, maxx, miny, maxy = min(xs), max(xs), min(ys), max(ys)
    sc = r / max(1e-6, max(maxx - minx, maxy - miny))
    pts = []
    for i, (x, y) in enumerate(pts2d):
        t = i / max(1, len(pts2d) - 1)
        X = (x - (minx + maxx) / 2.0) * sc * (1.0 + 0.3 * o)
        Y = (y - (miny + maxy) / 2.0) * sc * (1.0 + 0.3 * o)
        Z = sin(t * 4 * pi * (1 + w)) * h * 0.15
        pts.append((X, Y, Z))
    return _downsample(pts, seg)

def _hilbert_recursive(pts, x, y, xi, xj, yi, yj, n):
    if n <= 0:
        pts.append((x + (xi + yi) / 2.0, y + (xj + yj) / 2.0))
    else:
        _hilbert_recursive(pts, x, y, yi/2, yj/2, xi/2, xj/2, n-1)
        _hilbert_recursive(pts, x+xi/2, y+xj/2, xi/2, xj/2, yi/2, yj/2, n-1)
        _hilbert_recursive(pts, x+xi/2+yi/2, y+xj/2+yj/2, xi/2, xj/2, yi/2, yj/2, n-1)
        _hilbert_recursive(pts, x+xi/2+yi, y+xj/2+yj, -yi/2, -yj/2, -xi/2, -xj/2, n-1)

def make_hilbert(seg, r, o, w, s, h, depth=3):
    order = max(1, min(6, depth))
    pts2d = []
    _hilbert_recursive(pts2d, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, order)
    xs, ys = zip(*pts2d)
    minx, maxx, miny, maxy = min(xs), max(xs), min(ys), max(ys)
    sc = r / max(1e-6, max(maxx - minx, maxy - miny))
    pts = []
    for i, (x, y) in enumerate(pts2d):
        t = i / max(1, len(pts2d) - 1)
        X = (x - (minx + maxx)/2.0) * sc * (1.0 + o * 0.3)
        Y = (y - (miny + maxy)/2.0) * sc * (1.0 + o * 0.3)
        Z = sin(t * 2 * pi * (1 + s * 0.1)) * h * 0.2
        pts.append((X, Y, Z))
    return _downsample(pts, seg)

def make_levy(seg, r, o, w, s, h, depth=10):
    pts2d = [(0.0, 0.0), (r, 0.0)]
    for _ in range(max(1, min(16, depth))):
        new_pts = []
        for i in range(len(pts2d) - 1):
            x1, y1 = pts2d[i]
            x2, y2 = pts2d[i + 1]
            mx, my = (x1 + x2) / 2.0, (y1 + y2) / 2.0
            dx, dy = x2 - x1, y2 - y1
            nx, ny = -dy / sqrt(2), dx / sqrt(2)
            px, py = mx + nx / 2.0, my + ny / 2.0
            if i == 0: new_pts.append((x1, y1))
            new_pts.append((px, py))
            new_pts.append((x2, y2))
        pts2d = new_pts
    sc = 1.0 + o
    pts = [(x * sc, y * sc, sin((x + y) * 0.2) * h * 0.2) for (x, y) in pts2d]
    return _downsample(pts, seg)

def make_tree(seg, r, o, w, s, h, depth=5):
    lines = [(0.0, 0.0, 0.0, 0.0, r)]
    for _ in range(max(1, min(8, depth))):
        new_lines = []
        for x1, y1, z1, x2, y2 in lines:
            dx, dy = x2 - x1, y2 - y1
            length = sqrt(dx*dx + dy*dy) * (0.65 + 0.05 * o)
            ang = pi/6 * (1 + 0.2 * w)
            for a in (-ang, ang):
                nx = x2 + length * sin(a)
                ny = y2 + length * cos(a)
                new_lines.append((x2, y2, 0.0, nx, ny))
        lines += new_lines
    pts = []
    for x1, y1, _, x2, y2 in lines:
        pts.append((x1, y1, sin(x1 + y1) * h * 0.05))
        pts.append((x2, y2, sin(x2 + y2) * h * 0.05))
    return _downsample(pts, seg)

def make_peano(seg, r, o, w, s, h, depth=3):
    pts2d = [(0, 0)]
    for _ in range(max(1, min(6, depth))):
        new = []
        for (x, y) in pts2d:
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    new.append((x + dx, y + dy))
        pts2d = new
    sc = r / max(1, (3 ** depth))
    pts = [(x * sc, y * sc, sin((x + y) * 0.5) * h * 0.1) for x, y in pts2d]
    return _downsample(pts, seg)

def make_spiralfractal(seg, r, o, w, s, h, depth=6):
    pts = []
    angle = 0.0
    rad = r
    steps = max(2, seg * max(1, depth))
    for i in range(steps):
        angle += pi / 12 * (1 + w)
        rad *= 0.995 - 0.01 * o
        x = cos(angle) * rad
        y = sin(angle) * rad
        z = sin(angle * s) * h * 0.05
        pts.append((x, y, z))
    return _downsample(pts, seg)

def make_sierpinski(seg, r, o, w, s, h, depth=6):
    depth = max(1, min(10, depth))
    pts = [(0.0, 0.0), (r, 0.0), (r/2.0, r * sqrt(3)/2.0)]
    triangles = [pts]
    for _ in range(depth):
        new_tris = []
        for tri in triangles:
            (x1, y1), (x2, y2), (x3, y3) = tri
            m12 = ((x1 + x2)/2, (y1 + y2)/2)
            m23 = ((x2 + x3)/2, (y2 + y3)/2)
            m31 = ((x3 + x1)/2, (y3 + y1)/2)
            new_tris += [[(x1, y1), m12, m31],
                         [(x2, y2), m23, m12],
                         [(x3, y3), m31, m23]]
        triangles = new_tris

    pts = []
    for tri in triangles:
        for x, y in tri:
            z = sin((x + y) * 0.3) * h * 0.05
            pts.append((x - r/2, y - r/3, z))
    return _downsample(pts, seg)

def make_fractalvine(seg, r, o, w, s, h, depth=6):
    pts = []
    turns = 3 + s * 0.3
    branches = max(2, int(3 + o * 2))
    height_scale = r * (0.6 + 0.4 * h)
    amp = r * 0.1 * (1 + w * 0.3)
    freq = 2.5 + w * 0.5

    for i in range(seg):
        t = i / (seg - 1)
        angle = t * turns * 2 * pi
        base_r = r * (1 - t * 0.9)
        x = cos(angle) * base_r
        y = sin(angle) * base_r
        z = t * height_scale + sin(angle * freq) * amp

        for b in range(branches):
            off_angle = angle + (b / branches) * 2 * pi
            bx = cos(off_angle) * base_r * 0.3
            by = sin(off_angle) * base_r * 0.3
            bz = sin(t * pi * b) * amp * 0.3
            pts.append((x + bx, y + by, z + bz))

    return _downsample(pts, seg)

def make_cantor3d(seg, r, o, w, s, h, depth=5):
    pts = []
    depth = max(1, min(8, depth))
    gap = 0.33 + o * 0.1     
    turns = 2 + s * 0.5        
    wobble = 0.1 + 0.05 * w      
    height_scale = h * 0.2         
    sc = r * 0.5                   

    lines = [(0.0, 1.0)]
    for _ in range(depth):
        new_lines = []
        for a, b in lines:
            d = b - a
            new_lines.append((a, a + d * gap))
            new_lines.append((b - d * gap, b))
        lines = new_lines

    for (a, b) in lines:
        for t in (a, (a + b) / 2.0, b):
            u = t * turns * 2 * pi
            rad = sc * (1.0 - t * 0.8)
            x = cos(u) * rad + sin(u * 2.0) * wobble
            y = sin(u) * rad + cos(u * 3.0) * wobble
            z = sin(u * 1.5) * height_scale * (1.0 - t)
            pts.append((x, y, z))

    return _downsample(pts, seg)

def make_binarytree(seg, r, o, w, s, h, depth=6):
    lines = [(0.0, 0.0, pi/2, r * 0.5)]
    for _ in range(depth):
        new_lines = []
        for x, y, ang, length in lines:
            nx, ny = x + cos(ang) * length, y + sin(ang) * length
            new_lines.append((nx, ny, ang + o * 0.3, length * 0.7))
            new_lines.append((nx, ny, ang - o * 0.3, length * 0.7))
        lines += new_lines

    pts = []
    for x, y, _, _ in lines:
        z = sin(x + y) * h * 0.1
        pts.append((x, y, z))
    return _downsample(pts, seg)

def make_logspiral(seg, r, o, w, s, h, depth=8):
    pts = []
    a = 1.0
    b = 0.15 + 0.05 * o
    spins = 4 + s
    for i in range(seg * depth):
        t = i / (seg - 1) * spins * 2 * pi
        radius = a * exp(b * t)
        x = cos(t) * radius
        y = sin(t) * radius
        z = sin(t * w) * h * 0.1
        pts.append((x, y, z))
    sc = r / (abs(pts[-1][0]) + abs(pts[-1][1]) + 1e-6)
    pts = [(x * sc, y * sc, z * sc) for (x, y, z) in pts]
    return pts

FRACTAL_SET = {
    "KOCH", "HILBERT", "DRAGON", "LEVY", "TREE", "PEANO", "SPIRALFRACTAL",
    "SIERPINSKI", "FRACTALVINE", "CANTOR3D", "BINARYTREE", "LOGSPIRAL"
}

# ----------------------------------------------------------
# Rebuild Shape
# ----------------------------------------------------------

def rebuild_shape(obj):
    if not obj or obj.type != 'CURVE':
        return

    st = obj.get("shape_type", "")
    seg = int(obj.get("segments", 300))
    r   = float(obj.get("size", 1.0))
    o   = float(obj.get("offset", 0.2))
    w   = float(obj.get("wave_intensity", 0.0))
    s   = int(obj.get("symmetry", 6))
    h   = float(obj.get("height", 1.0))
    depth = int(obj.get("fractal_depth", 3))

    fn = globals().get(f"make_{st.lower()}")
    if not fn:
        build_polyline_curve(obj, [(0, 0, 0), (0, 1, 0)], False)
        return

    if st in FRACTAL_SET:
        pts = fn(seg, r, o, w, s, h, depth)
    else:
        pts = fn(seg, r, o, w, s, h)

    build_polyline_curve(obj, pts, False)

# ----------------------------------------------------------
# Operator / UI
# ----------------------------------------------------------

class SPLINEGEN_OT_generate(bpy.types.Operator):
    bl_idname = "mesh.spline_generator"
    bl_label = "Generate Spline"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        p = context.scene.splinegen_props

        curve = bpy.data.curves.new(f"{p.shape_type}_Shape", type='CURVE')
        curve.dimensions = '3D'

        obj = bpy.data.objects.new(curve.name, curve)
        context.collection.objects.link(obj)
        context.view_layer.objects.active = obj
        obj.select_set(True)

        for k in ("shape_type","segments","size","offset","wave_intensity","symmetry","height","fractal_depth"):
            obj[k] = getattr(p, k)

        rebuild_shape(obj)
        return {'FINISHED'}

def update_shape(self, context):
    obj = context.active_object

    if (
        not obj or
        obj.type != 'CURVE' or
        not obj.select_get() or
        "shape_type" not in obj
    ):
        return

    for k in ("shape_type", "segments", "size", "offset", "wave_intensity", "symmetry", "height", "fractal_depth"):
        obj[k] = getattr(self, k)

    rebuild_shape(obj)

    new_name = f"{self.shape_type}_Shape"
    if obj.name != new_name:
        obj.name = new_name
        obj.data.name = new_name

SHAPES_SIMPLE = [
    ("SPIRAL", "Simple - Spiral", ""),
    ("HELIX", "Simple - Helix", ""),
    ("WAVE", "Simple - Wave", ""),
    ("ZIGZAG", "Simple - Zigzag", ""),
    ("LISSAJOUS", "Simple - Lissajous", ""),
    ("SPIROGRAPH", "Simple - Spirograph", ""),
    ("ROSE", "Simple - Rose / Rhodonea", ""),
    ("SUPERFORMULA", "Simple - Superformula", ""),
    ("TORUSKNOT", "Simple - Torus Knot", ""),
    ("BUTTERFLY", "Simple - Butterfly", ""),
    ("GOLDEN_SPIRAL", "Simple - Golden Spiral", ""),
    ("VORTEX", "Simple - Vortex Spiral", ""),
    ("INFINITY", "Simple - Infinity Curve", ""),
    ("RIPPLERING", "Simple - Ripple Ring", ""),
    ("TWISTRIBBON", "Simple - Twisted Ribbon", ""),
]

SHAPES_FRACTAL = [
    ("KOCH", "Fractal - Koch Curve", ""),
    ("DRAGON", "Fractal - Dragon Curve", ""),
    ("HILBERT", "Fractal - Hilbert Curve", ""),
    ("LEVY", "Fractal - Lévy C Curve", ""),
    ("TREE", "Fractal - Tree Branch", ""),
    ("PEANO", "Fractal - Peano Curve", ""),
    ("SPIRALFRACTAL", "Fractal - Spiral Fractal", ""),
    ("FRACTALVINE", "Fractal - Vine Spiral", ""),
    ("CANTOR3D", "Fractal - 3D Cantor Spiral", ""),
    ("SIERPINSKI", "Fractal - Sierpiński Triangle", ""),
    ("LOGSPIRAL", "Fractal - Logarithmic Spiral", ""),
]

SHAPES_CHAOTIC = [
    ("LORENZ", "Chaotic - Lorenz Attractor", ""),
    ("ROSSLER", "Chaotic - Rössler Attractor", ""),
    ("AIZAWA", "Chaotic - Aizawa Attractor", ""),
    ("CHEN", "Chaotic - Chen Attractor", ""),
    ("DADRAS", "Chaotic - Dadras Attractor", ""),
    ("HALVORSEN", "Chaotic - Halvorsen Attractor", ""),
    ("THOMAS", "Chaotic - Thomas Attractor", ""),
    ("RIKITAKE", "Chaotic - Rikitake Dynamo", ""),
    ("CHUA", "Chaotic - Chua Circuit", ""),
    ("RABINOVICH", "Chaotic - Rabinovich–Fabrikant", ""),
    ("DEQUANLI", "Chaotic - Dequan–Li", ""),
    ("HADLEY", "Chaotic - Hadley Circulation", ""),
    ("BURKESHAW", "Chaotic - Burke–Shaw", ""),
    ("LUCHENSYS", "Chaotic - Lü–Chen", ""),
    ("BLACKHOLE", "Chaotic - Black Hole Vortex", ""),
]

def update_category(self, context):
    p = context.scene.splinegen_props
    if p.category == 'SIMPLE':
        p.shape_type = SHAPES_SIMPLE[0][0]
    elif p.category == 'FRACTAL':
        p.shape_type = SHAPES_FRACTAL[0][0]
    else:
        p.shape_type = SHAPES_CHAOTIC[0][0]

class SplineGenProperties(bpy.types.PropertyGroup):
    category: bpy.props.EnumProperty(
        name="Category",
        items=[
            ("SIMPLE", "Simple", ""),
            ("FRACTAL", "Fractal", ""),
            ("CHAOTIC", "Chaotic", "")
        ],
        default="SIMPLE",
        update=update_category
    )

    def shape_items(self, context):
        if self.category == "SIMPLE":
            return SHAPES_SIMPLE
        elif self.category == "FRACTAL":
            return SHAPES_FRACTAL
        else:
            return SHAPES_CHAOTIC

    shape_type: bpy.props.EnumProperty(
        name="Shape Type",
        items=shape_items,
        update=update_shape
    )

    segments: bpy.props.IntProperty(name="Segments", default=300, min=16, max=10000, subtype='FACTOR', update=update_shape)
    size: bpy.props.FloatProperty(name="Size", default=1.0, min=0.01, max=100.0, subtype='FACTOR', update=update_shape)
    offset: bpy.props.FloatProperty(name="Offset", default=0.2, min=0.0, max=100.0, subtype='FACTOR', update=update_shape)
    wave_intensity: bpy.props.FloatProperty(name="Wave", default=0.0, min=0.0, max=100.0, subtype='FACTOR', update=update_shape)
    symmetry: bpy.props.IntProperty(name="Symmetry", default=6, min=1, max=256, subtype='FACTOR', update=update_shape)
    height: bpy.props.FloatProperty(name="Height", default=1.0, min=0.0, max=100.0, subtype='FACTOR', update=update_shape)
    fractal_depth: bpy.props.IntProperty(name="Fractal Depth", default=3, min=1, max=20, subtype='FACTOR', update=update_shape)

# ----------------------------------------------------------
# UI
# ----------------------------------------------------------

class VIEW3D_PT_spline_generator(bpy.types.Panel):
    bl_label = "Spline"
    bl_idname = "VIEW3D_PT_spline_generator"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Spline"

    def draw(self, context):
        layout = self.layout
        p = context.scene.splinegen_props
        o = context.object

        layout.operator("mesh.spline_generator", text="Generate Spline", icon="OUTLINER_OB_CURVE")

        layout.separator(factor=0.5)

        layout.prop(p, "category", expand=True)
        layout.prop(p, "shape_type")

        layout.separator(factor=0.5)

        layout.prop(p, "segments")
        layout.prop(p, "size")
        layout.prop(p, "offset")
        layout.prop(p, "wave_intensity")
        layout.prop(p, "symmetry")
        layout.prop(p, "height")

        if p.category == "FRACTAL":
            layout.prop(p, "fractal_depth")

        layout.separator(factor=0.5)

        if o and o.type == "CURVE" and "shape_type" in o and o.select_get():
            layout.label(text=f"Editing: {o['shape_type']}", icon="OUTLINER_OB_CURVE")
        else:
            layout.label(text="No spline selected", icon="INFO")

# ----------------------------------------------------------
# Register
# ----------------------------------------------------------

classes = (
    SplineGenProperties,
    SPLINEGEN_OT_generate,
    VIEW3D_PT_spline_generator,
)

def register():
    for c in classes:
        bpy.utils.register_class(c)
    bpy.types.Scene.splinegen_props = bpy.props.PointerProperty(type=SplineGenProperties)

def unregister():
    for c in reversed(classes):
        bpy.utils.unregister_class(c)
    del bpy.types.Scene.splinegen_props

if __name__ == "__main__":
    register()
