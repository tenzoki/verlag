---
description: Entwirft für jede Veröffentlichung ein eigenes Titelbild als SVG, abgeleitet vom Inhalt des Manuskripts, nach festen technischen Regeln, damit daraus automatisch E-Book-Cover, Vorschaukarte und Druckumschlag entstehen. Verwenden, wenn ein Cover, Titelbild oder Umschlagmotiv gebraucht oder überarbeitet wird.
argument-hint: [Wunsch zum Motiv]
allowed-tools: [Read, Write, Edit, Bash, Glob]
---

# /verlag:titelbild — eigenes Motiv

Jede Veröffentlichung bekommt ein **eigenes Motiv**. Es soll zeigen, worum es im Text geht (ein Mechanismus, eine Struktur, ein Bild aus dem Inhalt), nicht dekorieren. Lies dazu `veroeffentlichung.yaml`, die Zusammenfassung (falls vorhanden) und das Manuskript. Gibt es Abbildungen im Projekt, nimm deren Farbwelt als Ausgangspunkt, damit Buch und Cover zusammengehören.

## Technische Regeln (zwingend, sonst scheitern die Ableitungen)

- **Format:** `viewBox="0 0 1800 2700"` (2:3 = Taschenbuch 6 × 9). Das E-Book-Cover (1:1,6) und die Vorschaukarte entstehen durch Auffüllen mit der Hintergrundfarbe.
- **Hintergrund:** eine einzige flache Farbe als erstes Element (`<rect>` über die ganze Fläche). Dieselbe Farbe in `titelbild.farben.hintergrund` eintragen.
- **Nichts berührt den Rand:** jedes Element mindestens 110 Einheiten vom Rand, Text mindestens 140. Grund: Beschnitt und Einpassen; ein randabfallendes Element endet sonst sichtbar vor dem Rand.
- **Nur flache Farben:** keine Verläufe, keine Rasterbilder, keine Transparenz (`opacity`, `fill-opacity`), keine Filter. Grund: saubere CMYK-Umrechnung im Druck.
- **Schrift:** `font-family="'Helvetica Neue', Helvetica, Arial, sans-serif"`, nur die Schnitte 400 und 700. Grund: Rückseite, Rücken und Vorschaukarte werden in derselben Schrift gesetzt, das Buch wirkt sonst uneinheitlich. Ist in `veroeffentlichung.yaml` unter `schrift:` eine andere Schrift angegeben (Rechner ohne macOS), deren Familiennamen verwenden. Meldet `/verlag:bauen` die Warnung, rsvg-convert setze eine Ersatzschrift, ist die Schrift nicht installiert; dann sehen Vorschau und Druck anders aus als gedacht.
- **Pflichtinhalt:** Titel, Untertitel, Autor; optional Herausgeber und Stand. Der Titel muss als Briefmarke lesbar sein: Versalhöhe ab etwa 180 Einheiten, höchstens drei Zeilen.
- **Kontrast:** Text gegen Hintergrund mindestens 4,5 : 1. Die Farben `text`, `fliesstext`, `auszeichnung`, `akzent` in die YAML schreiben; Rückseite und Vorschaukarte verwenden sie.

## Ablauf

1. Zwei bis drei Motividee(n) in je einem Satz vorschlagen (was es zeigt, warum es zum Text passt), mit Empfehlung. Hat der Nutzer schon einen Wunsch genannt, direkt umsetzen.
2. SVG schreiben nach `abbildungen/<prefix>-titelbild.svg` (Präfix aus `date +"${FLIGHT_FILE_PREFIX:-%Y-%m-%d_%H-%M}"`), Pfad und Farben in `veroeffentlichung.yaml` eintragen.
3. **Ansehen, nicht nur schreiben:** `rsvg-convert -w 600 abbildungen/…svg -o /tmp/titel.png` und das Bild mit Read betrachten. Dann die Ableitungen erzeugen und ebenfalls ansehen:
   `python3 -I "${CLAUDE_PLUGIN_ROOT}/scripts/umschlag.py" ebook --out /tmp/eb.jpg` und `… og --out /tmp/og.png`.
   Prüfen: Lesbarkeit als Miniatur (auf 150 px Breite verkleinern), Abstände, Überlappungen, Ausgewogenheit.
4. Das Ergebnis dem Nutzer zeigen (Pfad zur PNG-Vorschau) und um Freigabe bitten. Das Titelbild ist nach außen sichtbar; ohne Freigabe nicht weiter zu `/verlag:bauen`.
