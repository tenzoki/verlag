#!/usr/bin/env python3
"""verlag: Titelbild-Ableitungen und Druckumschlag.

  umschlag.py ebook --config veroeffentlichung.yaml --out titelbild.jpg
  umschlag.py og    --config veroeffentlichung.yaml --out og-card.png
  umschlag.py druck --config veroeffentlichung.yaml --pages N --out umschlag.pdf

Das Titelbild ist ein SVG mit flachem, einfarbigem Hintergrund (titelbild.farben.hintergrund).
Alle Ableitungen setzen es unverzerrt mittig auf diesen Hintergrund, deshalb passt ein
Motiv für E-Book (1:1,6), Vorschaukarte (1200 x 630) und Taschenbuch (z. B. 2:3) zugleich.

Rückseitentext (texte.rueckseite, Markdown):
  # Überschrift
  Absatz ...
  ## Zwischenzeile        (fett, Auszeichnungsfarbe)
  Absatz ...
  ---
  Erste Zeile Impressum (fett)
  weitere Zeilen
"""
import argparse, re, subprocess, sys, tempfile
from html import escape
from pathlib import Path

import yaml
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
from voraussetzungen import cover_fonts  # noqa: E402

# Schrift für Rückseite, Rücken und Vorschaukarte: schrift.normal/fett aus der Konfiguration,
# sonst Helvetica Neue aus macOS. Gesetzt in load_config; die SVG-Schriftfamilie wird aus der
# Datei gelesen, damit rsvg-convert dieselbe Schrift setzt, mit der hier gemessen wird.
FONTS = None              # ((pfad, index) normal, (pfad, index) fett)
FONT_FAMILY = "'Helvetica Neue', Helvetica, Arial, sans-serif"
PER_PAGE_IN = {'weiss': 0.002252, 'creme': 0.0025, 'farbe': 0.002252, 'farbe-premium': 0.002347}
BLEED_IN = 0.125
TAC_LIMIT = 2.8           # höchster Farbauftrag nach eigener Umrechnung (280 %)
TAC_WARN = 300            # Warnschwelle in Prozent für die Endkontrolle

DEFAULT_COLORS = {'hintergrund': '#1f2933', 'text': '#ffffff', 'fliesstext': '#d5dbe1',
                  'auszeichnung': '#9db8d6', 'akzent': '#c98a2b'}


def die(msg, code=2):
    print(f'FEHLER: {msg}', file=sys.stderr)
    sys.exit(code)


def load_config(path):
    path = Path(path).resolve()
    cfg = yaml.safe_load(path.read_text(encoding='utf-8')) or {}
    cfg['_dir'] = path.parent
    tb = cfg.get('titelbild') or {}
    colors = dict(DEFAULT_COLORS)
    colors.update(tb.get('farben') or {})
    cfg['_colors'] = colors
    svg = tb.get('svg')
    if not svg:
        die('titelbild.svg fehlt in der Konfiguration')
    cfg['_svg'] = (cfg['_dir'] / svg).resolve()
    if not cfg['_svg'].is_file():
        die(f'Titelbild nicht gefunden: {cfg["_svg"]}')
    global FONTS, FONT_FAMILY
    try:
        FONTS = cover_fonts(cfg, cfg['_dir'])
    except ValueError as e:
        cfg['_font_error'] = str(e)
        return cfg
    family = ImageFont.truetype(FONTS[0][0], 12, index=FONTS[0][1]).getname()[0]
    if family and family != 'Helvetica Neue':
        FONT_FAMILY = f"'{family}', sans-serif"
    return cfg


def need_fonts(cfg):
    if FONTS is None:
        die(cfg.get('_font_error', 'Schrift fehlt'))


def hex_rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def font(size_px, bold=False):
    path, index = FONTS[1 if bold else 0]
    return ImageFont.truetype(path, int(size_px), index=index)


def text_width(text, size, bold=False):
    return font(1000, bold).getlength(text) / 1000 * size


def wrap(text, size, bold, maxw):
    lines, cur = [], ''
    for w in text.split():
        t = (cur + ' ' + w).strip()
        if cur and text_width(t, size, bold) > maxw:
            lines.append(cur)
            cur = w
        else:
            cur = t
    if cur:
        lines.append(cur)
    return lines


def svg_aspect(svg_path):
    head = svg_path.read_text(encoding='utf-8')[:4000]
    m = re.search(r'viewBox="\s*([-\d.]+)[\s,]+([-\d.]+)[\s,]+([\d.]+)[\s,]+([\d.]+)"', head)
    if not m:
        die('Titelbild-SVG braucht ein viewBox-Attribut')
    return float(m.group(3)), float(m.group(4))


def render_front_png(cfg, w, h):
    """Titelbild unverzerrt in w x h px einpassen, Rest mit Hintergrundfarbe."""
    vw, vh = svg_aspect(cfg['_svg'])
    scale = min(w / vw, h / vh)
    fw, fh = round(vw * scale), round(vh * scale)
    with tempfile.TemporaryDirectory() as tmp:
        png = Path(tmp) / 'front.png'
        subprocess.run(['rsvg-convert', '-w', str(fw), '-h', str(fh), '-o', str(png), str(cfg['_svg'])], check=True)
        front = Image.open(png).convert('RGBA')
        canvas = Image.new('RGBA', (w, h), hex_rgb(cfg['_colors']['hintergrund']) + (255,))
        canvas.alpha_composite(front, ((w - fw) // 2, (h - fh) // 2))
        return canvas.convert('RGB')


def cmd_ebook(cfg, out):
    img = render_front_png(cfg, 1600, 2560)
    img.save(out, 'JPEG', quality=92, optimize=True)
    print(f'E-Book-Titelbild: {out} (1600 x 2560 px, JPEG)')


def cmd_og(cfg, out):
    need_fonts(cfg)
    W, H, M = 1200, 630, 60
    c = cfg['_colors']
    vw, vh = svg_aspect(cfg['_svg'])
    fh = H - 2 * 45
    fw = round(fh * vw / vh)
    canvas = Image.new('RGB', (W, H), hex_rgb(c['hintergrund']))
    front = render_front_png(cfg, fw, fh)
    canvas.paste(front, (W - M - fw, 45))
    d = ImageDraw.Draw(canvas)
    maxw = W - 2 * M - fw - 40
    y = 90
    for size in (68, 60, 52, 46, 40):
        lines = wrap(cfg.get('titel', ''), size, True, maxw)
        if len(lines) <= 3:
            break
    for ln in lines:
        d.text((M, y), ln, font=font(size, True), fill=hex_rgb(c['text']))
        y += int(size * 1.12)
    y += 18
    d.rectangle([M, y, M + 90, y + 5], fill=hex_rgb(c['akzent']))
    y += 30
    for ln in wrap(cfg.get('untertitel', '') or '', 30, False, maxw)[:3]:
        d.text((M, y), ln, font=font(30), fill=hex_rgb(c['fliesstext']))
        y += 40
    d.text((M, H - 110), cfg.get('autor', ''), font=font(30, True), fill=hex_rgb(c['text']))
    d.text((M, H - 70), cfg.get('herausgeber', '') or '', font=font(22), fill=hex_rgb(c['auszeichnung']))
    canvas.save(out, 'PNG', optimize=True)
    print(f'Vorschaukarte: {out} (1200 x 630 px)')


def parse_back(md_text):
    """-> (headline, blocks[(kind, text)], imprint[lines])"""
    headline, blocks, imprint, in_imprint, para = '', [], [], False, []

    def flush():
        if para:
            blocks.append(('p', ' '.join(para)))
            para.clear()

    for raw in md_text.splitlines():
        line = raw.strip()
        if in_imprint:
            if line:
                imprint.append(line.strip('*'))
            continue
        if line == '---':
            flush()
            in_imprint = True
        elif line.startswith('# '):
            flush()
            headline = line[2:].strip()
        elif line.startswith('## '):
            flush()
            blocks.append(('h', line[3:].strip()))
        elif not line:
            flush()
        else:
            para.append(line.replace('**', ''))
    flush()
    return headline, blocks, imprint


def front_inner(svg_path):
    src = svg_path.read_text(encoding='utf-8')
    m = re.search(r'<svg\b([^>]*)>', src, re.S)
    if not m:
        die('Titelbild-SVG ohne <svg>-Element')
    attrs = m.group(1)
    body = src[m.end():src.rfind('</svg>')]
    body = re.sub(r'<title>.*?</title>', '', body, flags=re.S)
    keep = []
    ns = []
    for a in re.finditer(r'([\w:-]+)\s*=\s*("[^"]*"|\'[^\']*\')', attrs):
        name, val = a.group(1), a.group(2)
        if name.startswith('xmlns'):
            if name != 'xmlns':
                ns.append(f'{name}={val}')
        elif name not in ('width', 'height', 'x', 'y', 'version'):
            keep.append(f'{name}={val}')
    return ' '.join(keep), ' '.join(ns), body


def cmd_druck(cfg, pages, out):
    need_fonts(cfg)
    tb = cfg.get('taschenbuch') or {}
    fmt = str(tb.get('format', '6x9'))
    try:
        tw_in, th_in = (float(x) for x in fmt.split('x'))
    except ValueError:
        die(f'taschenbuch.format ungültig: {fmt} (erwartet z. B. 6x9)')
    papier = tb.get('papier', 'weiss')
    if papier not in PER_PAGE_IN:
        die(f'taschenbuch.papier ungültig: {papier} (erlaubt: {", ".join(PER_PAGE_IN)})')
    pages_kdp = pages + pages % 2
    mm = 25.4
    B, TW, TH = BLEED_IN * mm, tw_in * mm, th_in * mm
    SP = pages_kdp * PER_PAGE_IN[papier] * mm
    W, H = 2 * B + 2 * TW + SP, 2 * B + TH
    BACK_X0, SPINE_X0 = B, B + TW
    FRONT_X0 = SPINE_X0 + SP
    c = cfg['_colors']
    out_svg = []
    add = out_svg.append
    add(f'<rect x="0" y="0" width="{W:.3f}" height="{H:.3f}" fill="{c["hintergrund"]}"/>')

    # Vorderseite: Titelbild unverzerrt in das Endformat eingepasst
    vw, vh = svg_aspect(cfg['_svg'])
    scale = min(TW / vw, TH / vh)
    fw, fh = vw * scale, vh * scale
    attrs, ns, body = front_inner(cfg['_svg'])
    add(f'<svg x="{FRONT_X0 + (TW - fw) / 2:.3f}" y="{B + (TH - fh) / 2:.3f}" width="{fw:.3f}" height="{fh:.3f}" {attrs} overflow="visible">{body}</svg>')

    # Rücken (KDP: Beschriftung erst ab 80 Seiten, 0,0625 in Abstand zur Falz)
    spine_note = 'ohne Beschriftung'
    fs = min(3.3, SP - 2 * 1.5875 - 0.4)
    if pages_kdp >= 80 and fs >= 2.0:
        cx = SPINE_X0 + SP / 2
        bx = cx - 0.36 * fs
        add(f'<g transform="translate({bx:.3f} {B + 18:.3f}) rotate(90)"><text font-size="{fs:.3f}" font-weight="700" fill="{c["text"]}">{escape(cfg.get("titel", ""))}</text></g>')
        add(f'<g transform="translate({bx:.3f} {B + TH - 14:.3f}) rotate(90)"><text font-size="{fs:.3f}" text-anchor="end" fill="{c["auszeichnung"]}">{escape(cfg.get("autor", ""))}</text></g>')
        tlen = text_width(cfg.get('titel', ''), fs, True) + text_width(cfg.get('autor', ''), fs) + 32 + 18 + 14
        if tlen > TH:
            die('Titel und Autor sind zu lang für den Rücken')
        spine_note = f'Titel und Autor, Schrift {fs:.2f} mm'

    # Rückseite
    back_md = (cfg.get('texte') or {}).get('rueckseite')
    if not back_md or not (cfg['_dir'] / back_md).is_file():
        die('texte.rueckseite fehlt oder Datei nicht gefunden')
    headline, blocks, imprint = parse_back((cfg['_dir'] / back_md).read_text(encoding='utf-8'))
    L = BACK_X0 + 15.5
    MAXW = TW - 2 * 15.5
    y = [B + 26]

    def para(text, size, bold, color, lh=1.42, gap=0.0):
        for ln in wrap(text, size, bold, MAXW):
            y[0] += size * lh
            add(f'<text x="{L:.3f}" y="{y[0]:.3f}" font-size="{size}" font-weight="{700 if bold else 400}" fill="{color}">{escape(ln)}</text>')
        y[0] += gap

    dach = (cfg.get('umschlag') or {}).get('dachzeile')
    if dach:
        add(f'<text x="{L:.3f}" y="{y[0]:.3f}" font-size="3.0" font-weight="700" letter-spacing="0.9" fill="{c["auszeichnung"]}">{escape(dach.upper())}</text>')
        y[0] += 3
    if headline:
        para(headline, 7.0, True, c['text'], lh=1.18, gap=4.5)
        add(f'<rect x="{L:.3f}" y="{y[0]:.3f}" width="14" height="0.65" fill="{c["akzent"]}"/>')
        y[0] += 4
    BODY = 3.75
    prev = None
    for kind, text in blocks:
        if kind == 'h':
            para(text, BODY, True, c['auszeichnung'])
        else:
            para(text, BODY, False, c['fliesstext'], gap=4 if prev == 'h' else 5)
        prev = kind
    text_bottom = y[0]

    BC_W, BC_H, BC_M = 50.8, 30.48, 6.35   # KDP-Barcode 2 x 1,2 in, 0,25 in vom Rand
    bc_y = B + TH - BC_M - BC_H
    bc_x = BACK_X0 + TW - BC_M - BC_W
    if text_bottom > bc_y - 6:
        die(f'Rückseitentext zu lang: endet bei {text_bottom - B:.0f} mm, erlaubt bis {bc_y - 6 - B:.0f} mm. Bitte kürzen.', 3)
    iy = B + TH - 19
    for i, ln in enumerate(imprint[:3]):
        size = 4.2 if i == 0 else 3.0
        if L + text_width(ln, size, i == 0) > bc_x - 3:
            die(f'Impressumszeile zu lang (reicht ins Barcode-Feld): {ln}', 3)
        add(f'<text x="{L:.3f}" y="{iy:.3f}" font-size="{size}" font-weight="{700 if i == 0 else 400}" fill="{c["text"] if i == 0 else c["auszeichnung"]}">{escape(ln)}</text>')
        iy += 5.5

    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" {front_inner(cfg["_svg"])[1]} viewBox="0 0 {W:.3f} {H:.3f}" '
           f'width="{W:.3f}mm" height="{H:.3f}mm" font-family="{FONT_FAMILY}">' + ''.join(out_svg) + '</svg>')
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        (tmp / 'wrap.svg').write_text(svg, encoding='utf-8')
        subprocess.run(['rsvg-convert', '-f', 'pdf', '-o', str(tmp / 'rgb.pdf'), str(tmp / 'wrap.svg')], check=True)
        subprocess.run(['gs', '-q', '-dBATCH', '-dNOPAUSE', '-dSAFER', '-sDEVICE=pdfwrite', '-dCompressPages=false',
                        '-dNoOutputFonts', '-o', str(tmp / 'outl.pdf'), str(tmp / 'rgb.pdf')], check=True)
        note = to_cmyk(tmp / 'outl.pdf', Path(out), cfg, B / mm * 72, tmp)
    tac = measure_tac(Path(out))
    print(f'Druckumschlag: {out}')
    print(f'  Endformat {fmt} in, {pages} Seiten (KDP: {pages_kdp}), Papier {papier}, Rücken {SP:.2f} mm, gesamt {W:.2f} x {H:.2f} mm')
    print(f'  Rücken: {spine_note}; Rückseitentext endet {bc_y - 6 - text_bottom:.0f} mm über dem Barcode-Feld')
    print(f'  Farbe: {note}; höchster Farbauftrag {tac} %' + ('  WARNUNG: über 300 %' if tac > TAC_WARN else ''))


def rgb_to_cmyk(r, g, b, overrides):
    key = '#%02x%02x%02x' % (round(r * 255), round(g * 255), round(b * 255))
    if key in overrides:
        return [v / 100 for v in overrides[key]]
    # Schwarz nur zu 90 % aus K (teilweiser Unbuntaufbau): dunkle Flächen bekommen CMY-Anteile
    # und drucken satt statt grau; der Gesamtauftrag wird unten begrenzt.
    k = (1 - max(r, g, b)) * 0.9
    if max(r, g, b) <= 0.001:
        return [0.6, 0.5, 0.4, 1.0]   # Tiefschwarz: 60/50/40/100 = 250 %
    cc, mm_, yy = ((1 - x - k) / (1 - k) for x in (r, g, b))
    tac = cc + mm_ + yy + k
    if tac > TAC_LIMIT:
        f = (TAC_LIMIT - k) / (cc + mm_ + yy)
        cc, mm_, yy = cc * f, mm_ * f, yy * f
    return [round(v, 4) for v in (cc, mm_, yy, k)]


def to_cmyk(src, dst, cfg, bleed_pt, tmp):
    import pikepdf
    overrides = {k.lower(): v for k, v in ((cfg.get('umschlag') or {}).get('cmyk') or {}).items()}
    pat = re.compile(r'([\d.]+) ([\d.]+) ([\d.]+) (rg|RG)(?=\s)')

    def conv(m):
        v = rgb_to_cmyk(*map(float, m.group(1, 2, 3)), overrides)
        return ' '.join(f'{x:g}' for x in v) + (' k' if m.group(4) == 'rg' else ' K')

    pdf = pikepdf.open(src)
    leftover = False
    for page in pdf.pages:
        streams = []
        cs = page.obj.Contents
        streams += list(cs) if isinstance(cs, pikepdf.Array) else [cs]
        res = page.obj.get('/Resources', {})
        streams += [xo for _, xo in res.get('/XObject', {}).items() if xo.get('/Subtype') == '/Form']
        for s in streams:
            data = s.read_bytes().decode('latin-1')
            s.write(pat.sub(conv, data).encode('latin-1'))
        if res.get('/Shading') or any(xo.get('/Subtype') == '/Image' for _, xo in res.get('/XObject', {}).items()):
            leftover = True
        w, h = float(page.obj.MediaBox[2]), float(page.obj.MediaBox[3])
        page.obj.BleedBox = pikepdf.Array([0, 0, w, h])
        page.obj.TrimBox = pikepdf.Array([bleed_pt, bleed_pt, w - bleed_pt, h - bleed_pt])
    pdf.docinfo['/Title'] = f'Umschlag {cfg.get("titel", "")}'
    if not leftover:
        pdf.save(dst, compress_streams=True)
        return 'CMYK (eigene Umrechnung, Farbauftrag begrenzt)'
    mid = tmp / 'mid.pdf'
    pdf.save(mid)
    subprocess.run(['gs', '-q', '-dBATCH', '-dNOPAUSE', '-dSAFER', '-sDEVICE=pdfwrite', '-sColorConversionStrategy=CMYK',
                    '-sProcessColorModel=DeviceCMYK', '-o', str(dst), str(mid)], check=True)
    fix = pikepdf.open(dst, allow_overwriting_input=True)
    for page in fix.pages:
        w, h = float(page.obj.MediaBox[2]), float(page.obj.MediaBox[3])
        page.obj.BleedBox = pikepdf.Array([0, 0, w, h])
        page.obj.TrimBox = pikepdf.Array([bleed_pt, bleed_pt, w - bleed_pt, h - bleed_pt])
    fix.save(dst)
    return 'CMYK über Ghostscript (Titelbild enthält Verläufe oder Rasterbilder; Farbauftrag prüfen)'


def measure_tac(pdf):
    with tempfile.TemporaryDirectory() as tmp:
        tif = Path(tmp) / 'sep.tif'
        subprocess.run(['gs', '-q', '-dBATCH', '-dNOPAUSE', '-sDEVICE=tiff32nc', '-r100', '-o', str(tif), str(pdf)], check=True)
        im = Image.open(tif)
        return round(max(sum(p) for p in im.getdata()) / 2.55)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('was', choices=['ebook', 'og', 'druck'])
    ap.add_argument('--config', default='veroeffentlichung.yaml')
    ap.add_argument('--out', required=True)
    ap.add_argument('--pages', type=int)
    a = ap.parse_args()
    cfg = load_config(a.config)
    if a.was == 'ebook':
        cmd_ebook(cfg, a.out)
    elif a.was == 'og':
        cmd_og(cfg, a.out)
    else:
        if not a.pages:
            die('druck braucht --pages (Seitenzahl des Innenteils)')
        cmd_druck(cfg, a.pages, a.out)


if __name__ == '__main__':
    main()
