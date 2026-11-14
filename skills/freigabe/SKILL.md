---
description: Schreibt die Freigabe-Checkliste einer Veröffentlichung nach ausgabe/freigabe.md — für jedes Ziel (KDP Taschenbuch, KDP E-Book, Website, LinkedIn) die hochzuladenden Dateien und jeden Feldwert zum Abschreiben, in sinnvoller Reihenfolge. Verwenden, wenn alles gebaut ist und der Nutzer veröffentlichen will.
allowed-tools: [Read, Write, Bash, Glob]
---

# /verlag:freigabe — Checkliste für die manuellen Schritte

KDP hat keine Schnittstelle zum Hochladen, und Website und LinkedIn sind nach außen sichtbar. Diese Schritte macht der Nutzer selbst; dieser Skill nimmt ihm das Zusammensuchen ab. Nichts hochladen, nichts posten.

Lies `veroeffentlichung.yaml`, `ausgabe/bericht.txt` und alle Dateien unter `texte/`. Prüfe zuerst, ob `bericht.txt` „alle Prüfungen bestanden" meldet und jünger ist als Manuskript, Titelbild und Rückseitentext (`stat`); sonst zuerst `/verlag:bauen`.

Schreibe `ausgabe/freigabe.md` mit einem Abschnitt je aktivem Ziel, jeweils als Checkliste (`- [ ]`) mit **exakten Werten** statt Verweisen:

- **Reihenfolge:** Website zuerst (der LinkedIn-Beitrag verlinkt auf sie), dann KDP E-Book und Taschenbuch (Prüfung durch Amazon bis 72 Stunden), LinkedIn zuletzt.
- **KDP Taschenbuch:** Sprache; Titel; Untertitel; Autor; Beschreibung (HTML aus kdp.md); sieben Schlüsselwörter einzeln; primärer Marktplatz (de → amazon.de, en → amazon.com) mit dem Hinweis, dass ein Wechsel die Kategorien zurücksetzt; drei Kategorien; ISBN; Druck (Schwarzweiß/Farbe, Papier aus `taschenbuch.papier`, Format, **ohne Beschnitt** für den Innenteil, Glanz oder matt); Dateien `ausgabe/<slug>-<format>-innenteil.pdf` und `ausgabe/<slug>-<format>-umschlag.pdf` als eigenes Cover; Seitenzahl und Rückenbreite aus bericht.txt zum Abgleich mit der KDP-Vorschau; Preis.
- **KDP E-Book:** gleiche Metadaten; `ausgabe/<slug>.epub`; Titelbild `ausgabe/<slug>-titelbild.jpg`; DRM-Empfehlung; Preis im 70-%-Band; Kindle Previewer ansehen.
- **Website:** geänderte Dateien unter `site/` (aus `/verlag:website`), hochladen, danach die Adresse im Browser öffnen und den PDF-Download testen.
- **LinkedIn:** fertiger Text aus linkedin.md mit eingesetzter Adresse; Bild `ausgabe/<slug>-og-card.png` falls nötig.

Zum Schluss dem Nutzer den Pfad nennen und die zwei, drei Punkte, die er vor dem Hochladen selbst entscheiden muss (z. B. Preis, Druckart, Kategorien aus der KDP-Liste).
