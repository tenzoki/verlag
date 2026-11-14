# verlag

Veröffentlichungs-Pipeline für Markdown-Manuskripte in Claude Code. Eine Datei `veroeffentlichung.yaml` je Veröffentlichung steuert alle Ausgaben. Sie haben immer die Sprache des Manuskripts.

| Ziel | Ausgabe in `ausgabe/` |
|---|---|
| PDF | `<slug>-a4.pdf` (DIN A4) |
| Website | Artikel mit Volltext, PDF-Download und Vorschaukarte `<slug>-og-card.png` (vorbereitet, nicht hochgeladen) |
| LinkedIn | Teaser-Text in `texte/linkedin.md`, Vorschaukarte |
| Taschenbuch (KDP) | `<slug>-6x9-innenteil.pdf`, `<slug>-6x9-umschlag.pdf` (CMYK, Rücken aus der echten Seitenzahl) |
| E-Book (KDP) | `<slug>.epub`, `<slug>-titelbild.jpg` |

## Benutzung

`/verlag:veroeffentlichen` führt durch den ganzen Weg: anlegen, Texte, eigenes Titelbild, bauen, Website, Freigabe-Checkliste. Unterwegs gibt es zwei Freigaben, für Texte und Titelbild. Einzelschritte: `/verlag:neu`, `/verlag:texte`, `/verlag:titelbild`, `/verlag:bauen`, `/verlag:website`, `/verlag:freigabe`, `/verlag:hilfe`.

Manuell bleiben das Hochladen bei KDP (es gibt keine Schnittstelle), das Hochladen der Website auf den Webspace und das Posten auf LinkedIn.

## Skripte (laufen auch ohne Claude)

- `scripts/mdprint`: Markdown zu PDF (A4 oder `--trim=6x9`) und EPUB, über pandoc und xelatex. Siehe `mdprint --help`.
- `scripts/mdprint-tables.lua`: Tabellen im PDF mit Spaltenbreiten nach Inhalt.
- `scripts/bauen.py`: erzeugt alle Ziele aus `veroeffentlichung.yaml` und prüft sie. Geprüft werden eingebettete Schriften, der Satzspiegel, die Rückenbreite, der Farbauftrag und das EPUB mit epubcheck.
- `scripts/umschlag.py`: aus dem Titelbild-SVG das E-Book-Cover, die Vorschaukarte und den Druckumschlag.

## Voraussetzungen

Das Plugin bringt seine Skripte mit, aber keine Programme. Auf dem Rechner müssen vorhanden sein:

- pandoc, xelatex (BasicTeX mit collection-fontsrecommended und xurl: `sudo tlmgr install collection-fontsrecommended xurl`; BasicTeX enthält xurl nicht, ohne das Paket werden lange Links nicht umbrochen und können über den Rand ragen. Meldet tlmgr „Local TeX Live (JAHR) is older than remote repository“, aus dem Archiv des eigenen Jahrgangs installieren: `sudo tlmgr --repository https://ftp.math.utah.edu/pub/tex/historic/systems/texlive/JAHR/tlnet-final install xurl`), librsvg (`rsvg-convert`), ghostscript, poppler (`pdfinfo`, `pdffonts`, `pdftoppm`), epubcheck; mermaid-cli (`mmdc`) nur, wenn das Manuskript Mermaid-Diagramme enthält
- Python 3 mit PyYAML, Pillow, pikepdf
- Schrift DejaVu (Serif, Sans, Mono) für den Satz
- für Rückseite, Rücken und Vorschaukarte: Helvetica Neue (unter macOS vorhanden); auf anderen Systemen eine eigene Schrift unter `schrift:` in `veroeffentlichung.yaml` angeben

`scripts/voraussetzungen.py` prüft das für die gewählten Ziele und nennt für alles Fehlende den Installationsbefehl. `bauen.py` ruft die Prüfung vor jedem Bau auf und baut nichts, solange etwas fehlt.
