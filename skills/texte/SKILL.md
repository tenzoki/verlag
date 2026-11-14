---
description: Schreibt die Begleittexte einer Veröffentlichung aus dem Manuskript — Zusammenfassung, Rückseitentext für den Druckumschlag, KDP-Beschreibung mit Schlüsselwörtern, Kategorie- und Preisvorschlag, LinkedIn-Teaser und Website-Teaser — in der Sprache des Manuskripts und im professionellen Stilprofil. Verwenden, wenn Texte für Buchrücken, Klappentext, Amazon, LinkedIn oder die Website gebraucht werden. Optionales Argument: nur bestimmte Texte (z. B. "rueckseite linkedin").
argument-hint: [zusammenfassung|rueckseite|kdp|linkedin|website]
allowed-tools: [Read, Write, Edit, Bash, Glob, Grep, WebSearch]
---

# /verlag:texte — Begleittexte

Lies `veroeffentlichung.yaml` (fehlt sie: `/verlag:neu` anbieten) und das ganze Manuskript. Schreibe jeden Text in der **Sprache des Manuskripts** (`sprache`) in die Datei, die unter `texte:` steht. Bestehende Dateien nicht stillschweigend ersetzen: Ist eine vorhanden, die neue Fassung daneben zeigen und fragen.

**Stil:** Lies das Profil `professional-voice-<sprache>.yaml` aus `flight-workbench/stilwerk/` im Projekt, sonst aus `~/.flight/stilwerk/`, und wende es an. These zuerst, ganze Sätze, Fachbegriffe beim ersten Auftreten kurz erklären. Keine Werbefloskeln, keine Superlative.

**Inhalt:** Jede Aussage muss sich im Manuskript belegen lassen. Zahlen (Seiten, Tabellen, Abbildungen) zählen, nicht schätzen: Tabellen = Trennzeilen `|---` bzw. `| :---`, Abbildungen = `![`. Seitenzahlen erst nach `/verlag:bauen` aus `ausgabe/bericht.txt`.

## Die Texte

1. **zusammenfassung.md** — eine Seite: worum es geht, für wen, Aufbau nach Teilen, was das Buch besonders macht, Stand. Grundlage für alle anderen Texte.
2. **rueckseite.md** — Rückseite des Taschenbuchs, 150 bis 180 Wörter, genau dieses Format (das Umschlag-Skript liest es):
   ```
   # Überschrift: eine Zeile, die sagt, was der Leser bekommt
   Einleitung, zwei bis drei Sätze: was, für wen.
   ## Zwischenzeile (z. B. Teil I · Grundlagen)
   Ein bis zwei Sätze.
   ...
   Schlusssatz mit dem greifbaren Nutzen (Tabellen, Abbildungen, Anleitung).
   ---
   Autor
   Herausgeber · Stand
   ```
   Danach prüfen, ob der Text passt: `python3 -I "${CLAUDE_PLUGIN_ROOT}/scripts/umschlag.py" druck --pages 120 --out /tmp/verlag-probe.pdf` (im Projektordner). Meldet es „Rückseitentext zu lang", kürzen und erneut prüfen.
3. **kdp.md** — alles, was in die KDP-Maske gehört:
   - **Beschreibung** (bis 4.000 Zeichen; KDP erlaubt `<b>`, `<i>`, `<br>`, `<p>`, `<ul><li>`): Einstieg in einem Satz, Nutzen, Aufbau als Liste, Zielgruppe, Stand.
   - **Sieben Schlüsselwörter** (je bis 50 Zeichen): Suchbegriffe, die Käufer tatsächlich eingeben; nicht den Titel wiederholen, keine Markennamen anderer Anbieter außer dem Thema selbst.
   - **Kategorien:** drei Vorschläge als Pfad im Kategorienbaum des primären Marktplatzes (Sprache de → amazon.de, en → amazon.com). Dazu der Hinweis, dass der Nutzer sie aus der Auswahlliste in KDP wählen muss und die Liste je Format (Taschenbuch/E-Book) verschieden ist.
   - **Preisvorschlag:** Taschenbuch mit Rechnung (Druckkosten amazon.de: 0,75 € + 0,012 €/Seite s/w bzw. 0,024 €/Seite Standardfarbe; Tantieme 60 % des Nettopreises ab 9,99 €, darunter 50 %; Buchpreisbindung in Deutschland). E-Book im 70-%-Band. Hinweis, dass die Druckkosten im KDP-Rechner maßgeblich sind. Wenn die Zahlen älter als ein halbes Jahr sein könnten: per WebSearch gegen die KDP-Hilfe prüfen und die Quelle nennen.
4. **linkedin.md** — Beitrag, 900 bis 1.300 Zeichen. Die ersten zwei Zeilen (rund 200 Zeichen) müssen allein tragen, weil LinkedIn danach „mehr" einblendet. Eine konkrete Beobachtung oder Frage aus dem Buch statt Ankündigung. Am Ende der Link als Platzhalter `{{LINK}}` (die Adresse ist `<website.url><slug>/`), höchstens drei Hashtags. Dazu ein Satz, dass die Vorschaukarte `ausgabe/<slug>-og-card.png` als Bild dient, falls LinkedIn den Link nicht selbst anzeigt.
5. **website-teaser.md** — zwei Sätze, höchstens 300 Zeichen, für die Artikelliste der Website (`teaser` in `articles.json`).

Am Ende in einer kurzen Liste melden: welche Dateien geschrieben wurden, Wortzahl der Rückseite und ob sie auf den Umschlag passt, was nicht geprüft werden konnte (z. B. aktuelle KDP-Kategorien).
