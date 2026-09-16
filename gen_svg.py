#!/usr/bin/env python3
"""
Generates light_mode.svg and dark_mode.svg for a GitHub profile README
in the style of Andrew6rant/Andrew6rant (neofetch-style terminal panel).

Dot padding is computed here so the static rows line up with the rows that
today.py rewrites at runtime.
"""

# ---------------------------------------------------------------- layout consts
CW = 8.1            # monospace advance width at font-size 13.5
LH = 19.0           # line height
TX = 286.0          # x origin of the text block
TOP = 92.0          # y of first body line

STATIC_COL = 24     # static rows: dots end at this column, value starts at 26
STATS_COL = 34      # dynamic rows: value RIGHT-aligns to this column

THEMES = {
    'dark_mode': {
        'panel':  '#0d1117',
        'border': '#30363d',
        'text':   '#c9d1d9',
        'label':  '#58a6ff',
        'dots':   '#3d444d',
        'dim':    '#8b949e',
        'accent': '#7ee787',
        'purple': '#d2a8ff',
        'orange': '#ffa657',
        'pink':   '#ff7b72',
        'node':   '#58a6ff',
        'edge':   '#21384f',
    },
    'light_mode': {
        'panel':  '#ffffff',
        'border': '#d0d7de',
        'text':   '#24292f',
        'label':  '#0969da',
        'dots':   '#c8d1da',
        'dim':    '#57606a',
        'accent': '#1a7f37',
        'purple': '#8250df',
        'orange': '#bc4c00',
        'pink':   '#cf222e',
        'node':   '#0969da',
        'edge':   '#cfe3fb',
    },
}

# ---------------------------------------------------------------- portrait
# Baked by photo_to_ascii.py. 52 columns wide, sparse->dense ramp " .:-=+*#%@".
# Dense glyphs sit where the photo is DARK, so on the dark panel this reads as
# a lit silhouette and on the light panel as an ink drawing. Same grid for both.
ART_ROWS = [
    '                     =++++-',
    '                 =+#%@@@%%%#*=',
    '               *%@@@%%%%%###%%#+-',
    '             +%@%%%%%%###***++##+',
    '            *%%%%%@@%%####**++=##=',
    '           -%%%@@@@@%%#####*******',
    '            %%@@@@@@%#########**+',
    '           +%%%%%%%%####***###++=--',
    '          +#%@%%##%%###########*+ =',
    '          +*%%@@%%%%%####%###+*%+ -',
    '          =*#%@@@%#%%%%%#####*+*',
    '          =*#%%@@@##%%%%%%%#####',
    '        --=*#%%@##%###%%%%%%#%#-   -',
    '        - -+%%%%+=+*######## =#=   +',
    '      ===+#%%%%#==---=***+=  *%%%+=+=',
    '     -===*#%%%%%=---- ---    #%#%#++*+---==',
    '     -=-=**%%%%%=    = -     +%%%%%*+*-==',
    '    --==++*%%*++=    -=      +%%%%%%#*+-++-',
    '    -====+*#*+=---    -      =#%%%%##**+=*=-',
    '   -====++++*+--        -      =****===++=+-',
    ' ---===++++**=-       -          =*+ -=-=-==-',
    '==-====++++**=                   -+*------ -=-',
    '==-====++++**+-         =        -=*+-= -    =',
    '++=====+++***+-                  -=+*----    -- -',
    '+*=====+++***+=                  --+*+ -      =+-',
    '+*==+==+++***+=                  --=+*=        +=',
    '**======++*+**=                  --=+**=        =',
    '**======+++***+-                --=+**##+       --',
    '**+=====+++**++=                -==**##%@*-     -+=-',
    '+*+=====++***++==-               -==+*##%%+      +*+',
]

ART_FS = 8.2        # font size; 52 cols * 0.6em = 256px, fits the art column
ART_LH = 9.84       # line height: 2x the character advance, matching CELL=0.5
ART_X = 22.0
ART_TOP = 126.0

# ---------------------------------------------------------------- content
PROMPT = 'sesha-2k3@github:~$ ./neofetch --profile'

# (label, value, dynamic_id or None)
STATIC_ROWS = [
    ('OS',        'Windows 11',                          None),
    ('Editor',    'VS Code, Jupyter, Colab',             None),
    ('Shell',     'Windows Terminal',                    None),
    ('Uptime',    '0 years, 0 months, 0 days',           'age_data'),
    ('Focus',     'Data Science, AI, Machine Learning',  None),
    ('Languages', 'C, C++, Python',                      None),
    ('ML',        'NumPy, Pandas, scikit-learn',         None),
    ('Frontend',  'HTML, CSS, Bootstrap',                None),
    ('Backend',   'FastAPI, Streamlit',                  None),
    ('Databases', 'MySQL, PostgreSQL, MongoDB',          None),
    ('Email',     'seshadrivv28@gmail.com',              None),
    ('LinkedIn',  'in/seshadrivv28',                     None),
]

# (label, element_id, placeholder, suffix_parts)
STAT_ROWS = [
    ('Repositories',  'repo_data',     '24',      'contrib'),
    ('Commits',       'commit_data',   '1,284',   None),
    ('Stars',         'star_data',     '37',      None),
    ('Followers',     'follower_data', '19',      None),
    ('Lines of Code', 'loc_data',      '128,430', None),
]


def esc(s):
    return (s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'))


def static_dots(label):
    """Dots so every static value starts at the same column."""
    n = STATIC_COL - len(label) - 1
    return ' ' + ('.' * max(n, 1)) + ' '


def stat_dots(label, value):
    """Mirror today.py's justify_format: dot_string = ' ' + dots + ' '."""
    width = STATS_COL - len(label) - 2
    just = max(0, width - len(value))
    if just <= 2:
        return {0: '', 1: ' ', 2: '. '}[just]
    return ' ' + ('.' * just) + ' '


def stat_width(label):
    return STATS_COL - len(label) - 2


def typing_values(n_chars, px_total):
    """Discrete stepped reveal widths for the typewriter clip."""
    steps = [str(round(px_total * i / n_chars, 1)) for i in range(n_chars + 1)]
    return ';'.join(steps)


def build(theme_name):
    c = THEMES[theme_name]
    out = []
    W = 880
    # H is computed at the end from wherever the content actually finishes,
    # so adding rows can never clip the bottom of the panel.
    out.append('@@OPEN@@')

    # ---- typewriter clip
    prompt_px = len(PROMPT) * CW
    out.append('<defs><clipPath id="typeclip"><rect x="24" y="50" width="0" height="24">')
    out.append('<animate attributeName="width" values="{}" dur="2.4s" '
               'calcMode="discrete" fill="freeze"/>'.format(
                   typing_values(len(PROMPT), prompt_px + 4)))
    out.append('</rect></clipPath></defs>')

    # ---- panel
    out.append('@@PANEL@@')

    # ---- window dots
    for i, col in enumerate([c['pink'], c['orange'], c['accent']]):
        out.append('<circle cx="{}" cy="24" r="4.5" fill="{}" opacity="0.85"/>'
                   .format(28 + i * 16, col))
    out.append('<line x1="0" y1="42" x2="{}" y2="42" stroke="{}"/>'
               .format(W, c['border']))

    # ---- typed prompt line
    out.append('<g clip-path="url(#typeclip)">')
    out.append('<text x="24" y="66" fill="{}">{}</text>'.format(c['accent'], esc(PROMPT)))
    out.append('</g>')
    # cursor rides the typing edge, then blinks
    out.append('<rect y="55" width="8" height="14" fill="{}" x="24">'.format(c['label']))
    out.append('<animate attributeName="x" values="{}" dur="2.4s" '
               'calcMode="discrete" fill="freeze"/>'.format(
                   ';'.join(str(round(24 + prompt_px * i / len(PROMPT), 1))
                            for i in range(len(PROMPT) + 1))))
    out.append('<animate attributeName="opacity" values="1;1;0;0;1" dur="1.1s" '
               'begin="2.4s" repeatCount="indefinite"/>')
    out.append('</rect>')

    # ---- left graphic: ASCII portrait
    for i, line in enumerate(ART_ROWS):
        if not line.strip():
            continue
        out.append('<text x="{:.1f}" y="{:.2f}" font-size="{}" fill="{}" '
                   'xml:space="preserve">{}</text>'
                   .format(ART_X, ART_TOP + i * ART_LH, ART_FS, c['text'], esc(line)))

    # ---- header inside the text block
    y = TOP
    out.append('<text x="{}" y="{}" fill="{}" font-weight="bold">sesha-2k3</text>'
               .format(TX, y, c['orange']))
    out.append('<text x="{}" y="{}" fill="{}">@</text>'
               .format(TX + 9 * CW, y, c['dim']))
    out.append('<text x="{}" y="{}" fill="{}" font-weight="bold">github</text>'
               .format(TX + 10 * CW, y, c['orange']))
    y += LH
    out.append('<text x="{}" y="{}" fill="{}">{}</text>'
               .format(TX, y, c['border'], '-' * 42))
    y += LH * 1.35

    # ---- static rows
    for label, value, dyn in STATIC_ROWS:
        out.append('<text x="{}" y="{:.1f}">'.format(TX, y))
        out.append('<tspan fill="{}">{}</tspan>'.format(c['label'], esc(label)))
        out.append('<tspan fill="{}" xml:space="preserve">{}</tspan>'
                   .format(c['dots'], static_dots(label)))
        if dyn:
            out.append('<tspan id="{}" fill="{}">{}</tspan>'
                       .format(dyn, c['text'], esc(value)))
        else:
            out.append('<tspan fill="{}">{}</tspan>'.format(c['text'], esc(value)))
        out.append('</text>')
        y += LH

    # ---- github block
    y += LH * 0.55
    out.append('<text x="{}" y="{:.1f}" fill="{}">{}</text>'
               .format(TX, y, c['dim'], 'github ' + '-' * 35))
    y += LH * 1.35

    for label, eid, placeholder, extra in STAT_ROWS:
        out.append('<text x="{}" y="{:.1f}">'.format(TX, y))
        out.append('<tspan fill="{}">{}</tspan>'.format(c['label'], esc(label)))
        out.append('<tspan id="{}_dots" fill="{}" xml:space="preserve">{}</tspan>'
                   .format(eid, c['dots'], stat_dots(label, placeholder)))
        out.append('<tspan id="{}" fill="{}" font-weight="bold">{}</tspan>'
                   .format(eid, c['text'], placeholder))
        if extra == 'contrib':
            out.append('<tspan fill="{}" xml:space="preserve">  (</tspan>'.format(c['dim']))
            out.append('<tspan id="contrib_data" fill="{}">36</tspan>'.format(c['dim']))
            out.append('<tspan fill="{}"> contributed)</tspan>'.format(c['dim']))
        out.append('</text>')
        y += LH

    # ---- loc breakdown, indented under Lines of Code
    out.append('<text x="{:.1f}" y="{:.1f}" xml:space="preserve">'
               .format(TX + 16 * CW, y))
    out.append('<tspan id="loc_add" fill="{}">262,918</tspan>'.format(c['accent']))
    out.append('<tspan fill="{}"> added   </tspan>'.format(c['dim']))
    out.append('<tspan id="loc_del" fill="{}">134,488</tspan>'.format(c['pink']))
    out.append('<tspan fill="{}"> removed</tspan>'.format(c['dim']))
    out.append('</text>')
    y += LH * 1.6

    # ---- palette strip
    strip = [c['pink'], c['orange'], c['accent'], c['label'],
             c['purple'], c['dim'], c['text'], c['border']]
    for i, col in enumerate(strip):
        out.append('<rect x="{:.1f}" y="{:.1f}" width="18" height="10" rx="2" '
                   'fill="{}"/>'.format(TX + i * 22, y - 9, col))

    # ---- close: size the canvas around the real content extent
    art_bottom = ART_TOP + (len(ART_ROWS) - 1) * ART_LH
    H = round(max(y + 6, art_bottom) + 24)

    svg_open = (
        '<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        'viewBox="0 0 {w} {h}" font-family="\'JetBrains Mono\',\'Cascadia Code\','
        '\'Fira Code\',\'DejaVu Sans Mono\',Consolas,\'Courier New\',monospace" '
        'font-size="13.5">'.format(w=W, h=H))
    panel = ('<rect x="0.5" y="0.5" width="{}" height="{}" rx="10" fill="{}" '
             'stroke="{}"/>'.format(W - 1, H - 1, c['panel'], c['border']))

    out.append('</svg>')
    return ''.join(out).replace('@@OPEN@@', svg_open).replace('@@PANEL@@', panel)


if __name__ == '__main__':
    for name in THEMES:
        path = '{}.svg'.format(name)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(build(name))
        print('wrote', path)

    print('\nfield widths for svg_overwrite():')
    for label, eid, _, _ in STAT_ROWS:
        print('  {:<14} {}'.format(eid, stat_width(label)))
