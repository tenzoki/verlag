#!/usr/bin/env python3
"""verlag: alle Ausgaben einer Veröffentlichung aus veroeffentlichung.yaml erzeugen und prüfen.

  bauen.py [--config veroeffentlichung.yaml] [--nur pdf,taschenbuch,ebook,website]

Ausgaben landen in <projekt>/ausgabe/ unter festen Namen:
  <slug>-a4.pdf                  PDF in DIN A4 (Ziel pdf, auch Download auf der Website)
  <slug>-<format>-innenteil.pdf  Taschenbuch-Innenteil für KDP (Ziel taschenbuch)
  <slug>-<format>-umschlag.pdf   Druckumschlag mit Rücken, CMYK (Ziel taschenbuch)
  <slug>.epub                    E-Book ohne eingebettetes Titelbild (Ziel ebook)
  <slug>-titelbild.jpg           Titelbild für KDP, 1600 x 2560 (Ziel ebook)
  <slug>-og-card.png             Vorschaukarte 1200 x 630 für Website und LinkedIn (Ziel website)
  bericht.txt                    Ergebnis aller Prüfungen
Exit-Code 0 = alles in Ordnung, 1 = mindestens eine Prüfung fehlgeschlagen.
"""
import argparse, glob, importlib.util, re, shutil, subprocess, sys, tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import voraussetzungen  # noqa: E402  (nur Standardbibliothek, prüft PyYAML/Pillow selbst)
MDPRINT = HERE / 'mdprint'
UMSCHLAG = HERE / 'umschlag.py'

report, failed = [], [False]


def say(line=''):
    print(line, flush=True)
    report.append(line)


def fail(line):
    say(f'  FEHLER: {line}')
    failed[0] = True


def run(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    out = (r.stdout + r.stderr).strip()
    return r.returncode, out


def pdf_pages(pdf):
    _, out = run(['pdfinfo', str(pdf)])
    m = re.search(r'^Pages:\s+(\d+)', out, re.M)
    return int(m.group(1)) if m else 0


def check_fonts(pdf):
    _, out = run(['pdffonts', str(pdf)])
    bad = [l for l in out.splitlines()[2:] if l.split() and l.split()[-5] != 'yes']
    if bad:
        fail(f'{len(bad)} Schrift(en) nicht eingebettet in {pdf.name}')
    else:
        say('  Schriften: alle eingebettet')


def check_margins(pdf, left_in, right_in, twoside):
    """Sucht Inhalt außerhalb des Satzspiegels (Kopfbereich ausgenommen, Fußzeile eingeschlossen)."""
    from PIL import Image
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run(['pdftoppm', '-r', '50', '-gray', str(pdf), f'{tmp}/p'], check=True)
        bad = []
        for f in sorted(glob.glob(f'{tmp}/p-*.pgm')):
            n = int(re.search(r'-(\d+)\.pgm', f).group(1))
            im = Image.open(f)
            w, h = im.size
            px = im.load()
            d = 50
            l, r = (left_in, right_in) if (not twoside or n % 2) else (right_in, left_in)
            lo, hi = int((l - 0.08) * d), int(w - (r - 0.08) * d)
            if any(px[x, y] < 200 for y in range(int(0.6 * d), h) for x in list(range(0, max(lo, 0))) + list(range(min(hi, w), w))):
                bad.append(n)
    if bad:
        fail(f'Inhalt außerhalb des Satzspiegels auf Seite(n) {", ".join(map(str, bad))}')
    else:
        say('  Satzspiegel: nichts ragt über den Rand')


def mdprint(cfg, args, outdir):
    cmd = [str(MDPRINT), '--yes', f'--outdir={outdir}', f'--lang={cfg.get("sprache", "de")}', f'--title={cfg["titel"]}']
    if 'fusszeile' in cfg:
        cmd += [f'--footer={cfg["fusszeile"]}'] if cfg['fusszeile'] else ['--no-footer']
    if cfg.get('autor'):
        cmd += [f'--author={cfg["autor"]}']
    code, out = run(cmd + args + [cfg['_manuskript'].name], cwd=cfg['_manuskript'].parent)
    if code != 0:
        fail('mdprint fehlgeschlagen:\n' + out)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--config', default='veroeffentlichung.yaml')
    ap.add_argument('--nur', default='')
    a = ap.parse_args()

    if importlib.util.find_spec('yaml') is None:
        sys.exit(f'FEHLER: Python-Bibliothek pyyaml fehlt: {sys.executable} -m pip install pyyaml')
    import yaml
    cfg_path = Path(a.config).resolve()
    cfg = yaml.safe_load(cfg_path.read_text(encoding='utf-8')) or {}
    base = cfg_path.parent
    for key in ('titel', 'manuskript', 'slug'):
        if not cfg.get(key):
            sys.exit(f'FEHLER: {key} fehlt in {cfg_path.name}')
    cfg['_manuskript'] = (base / cfg['manuskript']).resolve()
    if not cfg['_manuskript'].is_file():
        sys.exit(f'FEHLER: Manuskript nicht gefunden: {cfg["_manuskript"]}')
    ziele = {k for k, v in (cfg.get('ziele') or {}).items() if v}
    if a.nur:
        ziele &= set(a.nur.split(','))
    slug = cfg['slug']
    out = base / 'ausgabe'
    out.mkdir(exist_ok=True)
    stem = cfg['_manuskript'].stem
    py = [sys.executable, '-I', str(UMSCHLAG), '--config', str(cfg_path)]

    say(f'Veröffentlichung: {cfg["titel"]} ({cfg.get("sprache", "de")}), Ziele: {", ".join(sorted(ziele)) or "keine"}')

    say('\nVoraussetzungen')
    missing, warn = voraussetzungen.check(cfg, base, ziele, cfg['_manuskript'].read_text(encoding='utf-8', errors='replace'))
    voraussetzungen.report(missing, warn, say)
    if missing:
        say('\nErgebnis: nicht gebaut, erst das Fehlende installieren')
        (out / 'bericht.txt').write_text('\n'.join(report) + '\n', encoding='utf-8')
        sys.exit(1)

    if 'pdf' in ziele or 'website' in ziele:
        say('\nPDF (DIN A4)')
        with tempfile.TemporaryDirectory() as tmp:
            mdprint(cfg, [], tmp)
            src = Path(tmp) / f'{stem}.pdf'
            if src.is_file():
                dst = out / f'{slug}-a4.pdf'
                shutil.move(src, dst)
                say(f'  {dst.name}: {pdf_pages(dst)} Seiten')
                check_fonts(dst)
                check_margins(dst, 2.5 / 2.54, 2.5 / 2.54, False)

    if 'taschenbuch' in ziele:
        tb = cfg.get('taschenbuch') or {}
        fmt = str(tb.get('format', '6x9'))
        say(f'\nTaschenbuch ({fmt} in)')
        with tempfile.TemporaryDirectory() as tmp:
            mdprint(cfg, [f'--trim={fmt}'], tmp)
            src = Path(tmp) / f'{stem}-{fmt}.pdf'
            if src.is_file():
                inner = out / f'{slug}-{fmt}-innenteil.pdf'
                shutil.move(src, inner)
                pages = pdf_pages(inner)
                say(f'  {inner.name}: {pages} Seiten')
                check_fonts(inner)
                check_margins(inner, 0.75, 0.55, True)
                if pages < 24:
                    fail('KDP verlangt mindestens 24 Seiten für ein Taschenbuch')
                code, msg = run(py + ['druck', '--pages', str(pages), '--out', str(out / f'{slug}-{fmt}-umschlag.pdf')])
                for line in msg.splitlines():
                    say('  ' + line) if not line.startswith('FEHLER') else fail(line[8:])
                if code != 0 and 'FEHLER' not in msg:
                    fail('Umschlag fehlgeschlagen')

    if 'ebook' in ziele:
        say('\nE-Book (EPUB für KDP)')
        with tempfile.TemporaryDirectory() as tmp:
            split = (cfg.get('ebook') or {}).get('kapitel_ebene')
            log = mdprint(cfg, ['--epub'] + ([f'--split-level={split}'] if split else []), tmp)
            src = Path(tmp) / f'{stem}.epub'
            if src.is_file():
                dst = out / f'{slug}.epub'
                shutil.move(src, dst)
                errs = [l for l in log.splitlines() if l.startswith(('ERROR', 'FATAL'))]
                warns = [l for l in log.splitlines() if l.startswith('WARNING')]
                say(f'  {dst.name}: {dst.stat().st_size / 1e6:.1f} MB')
                if errs:
                    fail(f'epubcheck: {len(errs)} Fehler, z. B. {errs[0]}')
                else:
                    say(f'  epubcheck: 0 Fehler, {len(warns)} Warnungen')
        code, msg = run(py + ['ebook', '--out', str(out / f'{slug}-titelbild.jpg')])
        say('  ' + msg) if code == 0 else fail(msg)

    if 'website' in ziele or 'linkedin' in ziele:
        say('\nVorschaukarte (Website, LinkedIn)')
        code, msg = run(py + ['og', '--out', str(out / f'{slug}-og-card.png')])
        say('  ' + msg) if code == 0 else fail(msg)

    say('\nErgebnis: ' + ('FEHLER, siehe oben' if failed[0] else 'alle Prüfungen bestanden'))
    (out / 'bericht.txt').write_text('\n'.join(report) + '\n', encoding='utf-8')
    sys.exit(1 if failed[0] else 0)


if __name__ == '__main__':
    main()
