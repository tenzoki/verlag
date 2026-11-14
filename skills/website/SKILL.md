---
description: Stellt eine Veröffentlichung als Artikel auf die eigene statische Website (website.pfad) — Volltext, PDF-Download, Vorschaukarte, Teaser — nach den Regeln im README und CLAUDE.md der Website, baut die Seiten und prüft sie lokal. Lädt nichts hoch; das Hochladen auf den Webspace macht der Nutzer. Verwenden, wenn ein Text auf die Website soll.
allowed-tools: [Read, Write, Edit, Bash, Glob, Grep]
---

# /verlag:website — Artikel auf die Website

Voraussetzungen: `veroeffentlichung.yaml` mit `website.pfad`, ein Lauf von `/verlag:bauen` (liefert `ausgabe/<slug>-a4.pdf` und `ausgabe/<slug>-og-card.png`), `texte/website-teaser.md` (sonst `/verlag:texte website`).

1. **Regeln der Website lesen:** `<website.pfad>/CLAUDE.md` und `README.md`. Sie gehen vor; die Schritte 2 bis 5 beschreiben den Weg für eine Website mit `articles/`, `tools/articles.json` und `tools/build.py`. Ist die Website anders gebaut, dem README folgen. Generierte Seiten nie von Hand bearbeiten.
2. **Artikelordner** `<website.pfad>/articles/<slug>/` anlegen bzw. aktualisieren: das Manuskript (Dateiname beibehalten), alle im Manuskript verwendeten Bilder mit gleichem relativem Pfad, `ausgabe/<slug>-a4.pdf`, `ausgabe/<slug>-og-card.png` als `og-card.png`. Existiert der Ordner schon, vorher zeigen, was sich ändert.
3. **Eintrag in `tools/articles.json`** anhängen bzw. aktualisieren: `slug`, `title`, `date` (aus `datum`), `lang` (aus `sprache`), `file` (Manuskriptname), `pdf` (`<slug>-a4.pdf`), `toc` (true ab etwa 3.000 Wörtern), `og_image` (`og-card.png`), `teaser` (aus website-teaser.md), `origin` null, `cover` null. Format und Reihenfolge der bestehenden Einträge beibehalten.
4. **Bauen:** `python3 tools/build.py` im Website-Ordner.
5. **Handgepflegte Stellen** laut README: die Liste „Writing" in `site/index.html` und `site/de/index.html` (neuer Eintrag oben, `counter-reset:p` am `<ol>` um eins erhöhen, beide Seiten synchron) und `site/sitemap.xml`.
6. **Prüfen** wie im CLAUDE.md der Website beschrieben: lokaler Server in `site/`, Headless-Chrome-Bildschirmfoto der Artikelseite (Desktop und 500 px) ansehen, interne Linkprüfung (jedes `href`/`src` ohne `http`/`mailto:` muss unter `site/` existieren), PDF-Download-Link vorhanden.
7. **Nicht hochladen.** Dem Nutzer sagen, welche Dateien unter `site/` neu oder geändert sind, und dass er `site/` wie gewohnt auf den Webspace kopiert. Die öffentliche Adresse für LinkedIn: `<website.url><slug>/`. In `texte/linkedin.md` den Platzhalter `{{LINK}}` erst ersetzen, wenn der Nutzer das Hochladen bestätigt hat.
