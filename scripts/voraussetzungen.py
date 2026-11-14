#!/usr/bin/env python3
"""verlag: prüft vor dem Bau, ob alles vorhanden ist, was die gewählten Ziele brauchen.

  voraussetzungen.py [--config veroeffentlichung.yaml] [--nur pdf,taschenbuch,ebook,website]

Geprüft werden Programme, Python-Bibliotheken, LaTeX-Pakete, die Schriften für den Satz
(DejaVu) und für Umschlag und Vorschaukarte (Standard: Helvetica Neue aus macOS, sonst
schrift.normal / schrift.fett in veroeffentlichung.yaml) sowie das Titelbild-SVG.
Für alles Fehlende wird der Installationsbefehl genannt.
Exit-Code 0 = vollständig, 1 = etwas fehlt.

Nur Standardbibliothek: das Skript muss auch laufen, wenn PyYAML oder Pillow fehlen.
"""
import argparse, importlib.util, os, re, shutil, subprocess, sys
from pathlib import Path

MAC = sys.platform == 'darwin'
MAC_FONT = '/System/Library/Fonts/HelveticaNeue.ttc'

# Installationshinweise: (macOS, Linux/Debian)
HINT = {
    'pandoc': ('brew install pandoc', 'Paket pandoc, besser aktuell von https://pandoc.org/installing.html'),
    'xelatex': ('brew install --cask basictex, danach: sudo tlmgr install collection-fontsrecommended xurl', 'sudo apt install texlive-xetex texlive-fonts-recommended texlive-latex-extra'),
    'kpsewhich': ('kommt mit xelatex', 'kommt mit xelatex'),
    'pdfinfo': ('brew install poppler', 'sudo apt install poppler-utils'),
    'pdffonts': ('brew install poppler', 'sudo apt install poppler-utils'),
    'pdftoppm': ('brew install poppler', 'sudo apt install poppler-utils'),
    'rsvg-convert': ('brew install librsvg', 'sudo apt install librsvg2-bin'),
    'gs': ('brew install ghostscript', 'sudo apt install ghostscript'),
    'epubcheck': ('brew install epubcheck', 'sudo apt install epubcheck'),
    'mmdc': ('npm install -g @mermaid-js/mermaid-cli', 'npm install -g @mermaid-js/mermaid-cli'),
    'dejavu': ('brew install --cask font-dejavu', 'sudo apt install fonts-dejavu'),
}
PYMOD = {'yaml': 'pyyaml', 'PIL': 'pillow', 'pikepdf': 'pikepdf'}

# LaTeX-Pakete, die pandoc (xelatex) und mdprint laden; Wert = TeX-Live-Paketname, falls abweichend
LATEX = {'amsmath': '', 'amssymb': 'amsfonts', 'array': 'tools', 'babel': '', 'bookmark': '', 'booktabs': '',
         'calc': 'tools', 'etoolbox': '', 'fancyhdr': '', 'fancyvrb': '', 'fontspec': '',
         'geometry': '', 'graphicx': 'graphics', 'hyperref': '', 'iftex': '', 'longtable': 'tools',
         'unicode-math': '', 'xcolor': ''}
# pandoc lädt diese nur, wenn vorhanden; ohne sie geht es, aber schlechter
LATEX_OPTIONAL = {'xurl': 'lange Links werden nicht umbrochen und können über den Rand ragen',
                  'microtype': 'etwas gröberer Blocksatz', 'footnotehyper': 'Fußnoten in Tabellen eingeschränkt',
                  'upquote': 'gerade Anführungszeichen im Code werden typografisch', 'parskip': ''}
BABEL = {'de': ('ngerman.ldf', 'babel-german'), 'en': ('english.ldf', 'babel-english'),
         'fr': ('french.ldf', 'babel-french'), 'es': ('spanish.ldf', 'babel-spanish'),
         'it': ('italian.ldf', 'babel-italian'), 'nl': ('dutch.ldf', 'babel-dutch')}

FONT_DIRS = ['~/Library/Fonts', '/Library/Fonts', '/System/Library/Fonts', '/usr/share/fonts',
             '/usr/local/share/fonts', '~/.local/share/fonts', '~/.fonts']


def tlmgr(pkgs):
    """Installationsbefehl für LaTeX-Pakete. Ist die lokale TeX-Live-Installation älter als das
    laufende Jahr, lehnt tlmgr den aktuellen Server ab; dann aus dem Archiv des eigenen Jahrgangs."""
    cmd = f'sudo tlmgr install {pkgs}'
    if shutil.which('kpsewhich'):
        root = subprocess.run(['kpsewhich', '-var-value', 'SELFAUTOPARENT'], capture_output=True, text=True).stdout
        m = re.search(r'texlive/(\d{4})', root)
        if m:
            import datetime
            year = int(m.group(1))
            # Ob der Server schon auf dem neuen Jahrgang ist, hängt vom Release (meist März) ab;
            # deshalb den Archivweg nur als Ausweichbefehl nennen.
            if year < datetime.date.today().year:
                cmd += (f' — meldet tlmgr „older than remote repository“: sudo tlmgr --repository '
                        f'https://ftp.math.utah.edu/pub/tex/historic/systems/texlive/{year}/tlnet-final install {pkgs}')
    return cmd


def hint(key):
    h = HINT.get(key)
    return (h[0] if MAC else h[1]) if h else ''


def split_index(spec):
    """'datei.ttc#1' -> ('datei.ttc', 1)"""
    path, _, idx = spec.partition('#') if re.search(r'#\d+$', spec) else (spec, '', '')
    return path, int(idx or 0)


def cover_fonts(cfg, base):
    """Schriftdateien für Umschlag und Vorschaukarte: ((pfad, index) normal, (pfad, index) fett).
    Reihenfolge: schrift.normal/schrift.fett aus der Konfiguration, sonst Helvetica Neue aus macOS.
    Löst ValueError mit verständlicher Meldung aus, wenn nichts Brauchbares gefunden wird."""
    s = (cfg or {}).get('schrift') or {}
    if s.get('normal') or s.get('fett'):
        out = []
        for key in ('normal', 'fett'):
            if not s.get(key):
                raise ValueError(f'schrift.{key} fehlt in veroeffentlichung.yaml (beide angeben: normal und fett)')
            p, i = split_index(str(s[key]))
            path = (Path(base) / os.path.expanduser(p)).resolve()
            if not path.is_file():
                raise ValueError(f'Schriftdatei schrift.{key} nicht gefunden: {path}')
            out.append((str(path), i))
        return tuple(out)
    if Path(MAC_FONT).is_file():
        return (MAC_FONT, 0), (MAC_FONT, 1)
    raise ValueError('Schrift für Umschlag und Vorschaukarte fehlt: Helvetica Neue gibt es nur unter macOS. '
                     'In veroeffentlichung.yaml eine andere angeben, z. B. schrift: {normal: "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", fett: "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"}')


def font_installed(filename):
    for d in FONT_DIRS:
        d = Path(os.path.expanduser(d))
        if d.is_dir() and any(d.rglob(filename)):
            return True
    if shutil.which('kpsewhich'):
        r = subprocess.run(['kpsewhich', filename], capture_output=True, text=True)
        if r.stdout.strip():
            return True
    return False


def svg_family_warnings(svg):
    """Prüft mit fc-match, ob die im SVG verlangte Schrift vorhanden ist (rsvg-convert ersetzt sie sonst stillschweigend)."""
    if not shutil.which('fc-match'):
        return []
    fams = set()
    for m in re.finditer(r'font-family\s*[=:]\s*["\']?([^"\';>]+)', svg.read_text(encoding='utf-8', errors='replace')):
        first = m.group(1).split(',')[0].strip().strip('\'"')
        if first and first.lower() not in ('sans-serif', 'serif', 'monospace'):
            fams.add(first)
    return [w for w in (family_warning(f, 'Das Titelbild') for f in sorted(fams)) if w]


def family_warning(family, wer):
    """Warnung, wenn fontconfig (und damit rsvg-convert) die Schriftfamilie durch eine andere ersetzt."""
    if not shutil.which('fc-match'):
        return ''
    got = subprocess.run(['fc-match', '-f', '%{family}', family], capture_output=True, text=True).stdout
    if family.lower() in got.lower():
        return ''
    return (f'{wer} verlangt die Schrift „{family}“, rsvg-convert setzt auf diesem Rechner stattdessen '
            f'„{got.split(",")[0]}“. Die Schrift installieren, damit Bild und Maße stimmen.')


def check(cfg, base, ziele, manuscript_text=''):
    """Liefert (fehlt, warnungen) als Listen von Textzeilen."""
    missing, warn = [], []
    satz = bool(ziele & {'pdf', 'website', 'taschenbuch'})
    bild = bool(ziele & {'taschenbuch', 'ebook', 'website', 'linkedin'})
    schrift = bool(ziele & {'taschenbuch', 'website', 'linkedin'})

    progs = set()
    if satz or 'ebook' in ziele:
        progs.add('pandoc')
    if satz:
        progs |= {'xelatex', 'kpsewhich', 'pdfinfo', 'pdffonts', 'pdftoppm'}
    if 'taschenbuch' in ziele:
        progs.add('gs')
    if bild:
        progs.add('rsvg-convert')
    if 'ebook' in ziele:
        progs.add('epubcheck')
    if (satz or 'ebook' in ziele) and re.search(r'^```\s*mermaid', manuscript_text, re.M):
        progs.add('mmdc')
    for p in sorted(progs):
        if not shutil.which(p):
            missing.append(f'Programm {p}: {hint(p)}')

    mods = {'yaml'}
    if satz or bild:
        mods.add('PIL')
    if 'taschenbuch' in ziele:
        mods.add('pikepdf')
    for m in sorted(mods):
        if importlib.util.find_spec(m) is None:
            missing.append(f'Python-Bibliothek {PYMOD[m]}: {sys.executable} -m pip install {PYMOD[m]}')

    if shutil.which('pandoc') and (satz or 'ebook' in ziele):
        v = subprocess.run(['pandoc', '--version'], capture_output=True, text=True).stdout
        m = re.search(r'pandoc\S*\s+(\d+)\.(\d+)', v)
        if m and int(m.group(1)) < 3:
            warn.append(f'pandoc {m.group(1)}.{m.group(2)} ist alt; getestet ist verlag mit pandoc 3.9 ({hint("pandoc")}).')

    if satz and shutil.which('kpsewhich'):
        lang = str((cfg or {}).get('sprache', 'de')).split('-')[0].lower()
        r = subprocess.run(['kpsewhich'] + [f'{n}.sty' for n in LATEX_OPTIONAL], capture_output=True, text=True)
        have = {Path(l).stem for l in r.stdout.split()}
        for n, why in LATEX_OPTIONAL.items():
            if n not in have and why:
                warn.append(f'LaTeX-Paket {n} fehlt, {why}: {tlmgr(n)}')
        files = [f'{n}.sty' for n in LATEX]
        if lang in BABEL:
            files.append(BABEL[lang][0])
        r = subprocess.run(['kpsewhich'] + files, capture_output=True, text=True)
        found = {Path(l).name for l in r.stdout.split()}
        lacking = []
        for f in files:
            if f not in found:
                name = f[:-4]
                pkg = BABEL[lang][1] if f.endswith('.ldf') else (LATEX[name] or name)
                if pkg not in lacking:
                    lacking.append(pkg)
        if lacking:
            missing.append(f'LaTeX-Paket(e) {", ".join(lacking)}: {tlmgr(" ".join(lacking))}')
    if satz:
        for f in ('DejaVuSerif.ttf', 'DejaVuSans.ttf', 'DejaVuSansMono.ttf'):
            if not font_installed(f):
                missing.append(f'Schrift DejaVu (für den Satz): {hint("dejavu")}')
                break

    if schrift:
        try:
            (path, index), _ = cover_fonts(cfg, base)
            if 'taschenbuch' in ziele and importlib.util.find_spec('PIL') is not None:
                from PIL import ImageFont
                w = family_warning(ImageFont.truetype(path, 12, index=index).getname()[0], 'Der Umschlag')
                if w:
                    warn.append(w)
        except ValueError as e:
            missing.append(str(e))

    if bild:
        svg = ((cfg or {}).get('titelbild') or {}).get('svg')
        if not svg:
            missing.append('Titelbild: titelbild.svg fehlt in veroeffentlichung.yaml (/verlag:titelbild)')
        elif not (Path(base) / svg).is_file():
            missing.append(f'Titelbild nicht gefunden: {Path(base) / svg}')
        elif shutil.which('rsvg-convert'):
            warn += svg_family_warnings(Path(base) / svg)
    return missing, warn


def report(missing, warn, out=print):
    for w in warn:
        out(f'  WARNUNG: {w}')
    if missing:
        out(f'  Es fehlt ({len(missing)}):')
        for m in missing:
            out(f'    - {m}')
    else:
        out('  Voraussetzungen: alles vorhanden')


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--config', default='veroeffentlichung.yaml')
    ap.add_argument('--nur', default='')
    a = ap.parse_args()
    if importlib.util.find_spec('yaml') is None:
        print(f'  Es fehlt: Python-Bibliothek pyyaml: {sys.executable} -m pip install pyyaml')
        sys.exit(1)
    import yaml
    path = Path(a.config).resolve()
    cfg = yaml.safe_load(path.read_text(encoding='utf-8')) or {}
    ziele = {k for k, v in (cfg.get('ziele') or {}).items() if v}
    if a.nur:
        ziele &= set(a.nur.split(','))
    ms = path.parent / str(cfg.get('manuskript', ''))
    text = ms.read_text(encoding='utf-8', errors='replace') if ms.is_file() else ''
    missing, warn = check(cfg, path.parent, ziele, text)
    report(missing, warn)
    sys.exit(1 if missing else 0)


if __name__ == '__main__':
    main()
