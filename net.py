#!/usr/bin/env python3
"""
Feed-forward network for the profile panel's art column.

Oriented top-to-bottom rather than left-to-right, because the art slot is
256 wide by 310 tall. Layers narrow as they descend, so the shape itself reads
as a network converging on an output.

Motion: pulse dots travel each transition on a 1.2s loop, with the three
transitions offset by 0.4s so signal appears to cascade down the network
continuously. Node cores flash as the wave reaches them.

Renders to SVG (for gen_svg.py) and to PNG (static, for checking geometry).
"""
W, H = 256, 310
CX = 141.0

# (y, node count, horizontal pitch, label)
LAYERS = [
    (30.0, 5, 46.0, 'input'),
    (118.0, 6, 38.0, 'hidden'),
    (206.0, 4, 50.0, 'hidden'),
    (285.0, 2, 60.0, 'output'),
]

R = 6.0            # node radius
CORE = 2.6         # activation core radius
PULSE = 2.4        # travelling dot radius
PERIOD = 2.0       # one full wave, shared by every animation in the group
HOP = 0.5          # time for a pulse to cross one transition

# how many edges per transition carry a visible pulse
PULSE_EDGES = 6


def coords():
    out = []
    for (y, n, pitch, label) in LAYERS:
        out.append([(CX + (i - (n - 1) / 2.0) * pitch, y) for i in range(n)])
    return out


def pulse_selection(a, b, k=PULSE_EDGES):
    """Spread the animated edges across the fan instead of clustering them."""
    pairs = [(i, j) for i in range(len(a)) for j in range(len(b))]
    if len(pairs) <= k:
        return pairs
    step = len(pairs) / float(k)
    return [pairs[int(i * step)] for i in range(k)]


def to_svg_body():
    L = coords()
    p = []

    # ---- edges, drawn first so nodes sit on top
    p.append('<g stroke="@@EDGE@@" stroke-width="1" fill="none">')
    for a, b in zip(L, L[1:]):
        for (x1, y1) in a:
            for (x2, y2) in b:
                p.append('<line x1="{:.1f}" y1="{:.1f}" x2="{:.1f}" y2="{:.1f}"/>'
                         .format(x1, y1, x2, y2))
    p.append('</g>')

    # ---- travelling pulses
    # Everything shares PERIOD so the wave stays in lockstep. Transition t
    # occupies the window [t*HOP, (t+1)*HOP], expressed as keyTime fractions;
    # outside that window the dot is parked and transparent.
    for t, (a, b) in enumerate(zip(L, L[1:])):
        f0 = max(t * HOP / PERIOD, 0.001)
        f1 = (t + 1) * HOP / PERIOD
        for (i, j) in pulse_selection(a, b):
            x1, y1 = a[i]
            x2, y2 = b[j]
            p.append('<circle r="{:.1f}" fill="@@ACCENT@@" opacity="0">'.format(PULSE))
            p.append('<animateMotion path="M{:.1f},{:.1f} L{:.1f},{:.1f}" '
                     'dur="{}s" keyPoints="0;0;1;1" keyTimes="0;{:.3f};{:.3f};1" '
                     'calcMode="linear" repeatCount="indefinite"/>'
                     .format(x1, y1, x2, y2, PERIOD, f0, f1))
            p.append('<animate attributeName="opacity" values="0;0;1;1;0;0" '
                     'keyTimes="0;{:.3f};{:.3f};{:.3f};{:.3f};1" dur="{}s" '
                     'repeatCount="indefinite"/>'
                     .format(f0, f0, f1, f1, PERIOD))
            p.append('</circle>')

    # ---- nodes
    for li, layer in enumerate(L):
        r = R + (1.0 if li == len(L) - 1 else 0.0)
        stroke = '@@OUT@@' if li == len(L) - 1 else '@@NODE@@'
        f = li * HOP / PERIOD          # this layer's moment in the wave
        for (x, y) in layer:
            p.append('<circle cx="{:.1f}" cy="{:.1f}" r="{:.1f}" fill="@@PANEL@@" '
                     'stroke="{}" stroke-width="1.5"/>'.format(x, y, r, stroke))
            p.append('<circle cx="{:.1f}" cy="{:.1f}" r="{:.1f}" fill="{}" opacity="0">'
                     .format(x, y, CORE, stroke))
            p.append('<animate attributeName="opacity" values="0;0;0.95;0;0" '
                     'keyTimes="0;{:.3f};{:.3f};{:.3f};1" dur="{}s" '
                     'repeatCount="indefinite"/>'
                     .format(f, min(f + 0.03, 0.99), min(f + 0.12, 0.995), PERIOD))
            p.append('</circle>')

    # ---- layer labels
    for (y, n, pitch, label) in LAYERS:
        p.append('<text x="6" y="{:.1f}" font-size="8" fill="@@DIM@@">{}</text>'
                 .format(y + 2.8, label))

    return '<g>' + ''.join(p) + '</g>'


def to_png(path, scale=2):
    from PIL import Image, ImageDraw
    L = coords()
    im = Image.new('RGB', (W * scale, H * scale), (13, 17, 23))
    d = ImageDraw.Draw(im)
    edge, node, out, accent = (33, 56, 79), (88, 166, 255), (210, 168, 255), (126, 231, 135)

    for a, b in zip(L, L[1:]):
        for (x1, y1) in a:
            for (x2, y2) in b:
                d.line([x1 * scale, y1 * scale, x2 * scale, y2 * scale], fill=edge, width=scale)
    for li, layer in enumerate(L):
        r = R + (1.0 if li == len(L) - 1 else 0.0)
        col = out if li == len(L) - 1 else node
        for (x, y) in layer:
            d.ellipse([(x - r) * scale, (y - r) * scale, (x + r) * scale, (y + r) * scale],
                      fill=(13, 17, 23), outline=col, width=max(1, round(1.5 * scale)))
    # one frame of the pulse, mid-flight on the first transition
    for (i, j) in pulse_selection(L[0], L[1]):
        x1, y1 = L[0][i]
        x2, y2 = L[1][j]
        px, py = x1 + (x2 - x1) * 0.55, y1 + (y2 - y1) * 0.55
        d.ellipse([(px - PULSE) * scale, (py - PULSE) * scale,
                   (px + PULSE) * scale, (py + PULSE) * scale], fill=accent)
    im.save(path)


def bounds():
    L = coords()
    xs = [x for layer in L for (x, y) in layer]
    ys = [y for layer in L for (x, y) in layer]
    return min(xs) - R, min(ys) - R, max(xs) + R, max(ys) + R


if __name__ == '__main__':
    to_png('net.png')
    b = bounds()
    L = coords()
    edges = sum(len(a) * len(c) for a, c in zip(L, L[1:]))
    print('edges: {}  animated: {}  period: {}s'.format(edges, PULSE_EDGES * (len(L) - 1), PERIOD))
    print('bounds x %.1f..%.1f  y %.1f..%.1f  (slot %dx%d)' % (b[0], b[2], b[1], b[3], W, H))
    print('svg body: {} chars'.format(len(to_svg_body())))
