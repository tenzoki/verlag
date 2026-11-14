---
description: Legt für ein Manuskript die Datei veroeffentlichung.yaml und den Ordner texte/ an. Liest Titel, Untertitel, Autor, Datum und Sprache aus dem Manuskript und fragt nur, welche Ziele (PDF, Website, LinkedIn, Taschenbuch, E-Book) gewünscht sind. Verwenden, wenn der Nutzer eine neue Veröffentlichung vorbereiten will oder /verlag:veroeffentlichen keine veroeffentlichung.yaml findet.
argument-hint: [Manuskript.md]
allowed-tools: [Read, Write, Edit, Bash, Glob, AskUserQuestion]
---

# /verlag:neu — Veröffentlichung anlegen

1. **Manuskript bestimmen.** Argument verwenden; sonst die `.md`-Dateien im aktuellen Ordner ansehen. Gibt es genau eine plausible (die größte, kein `-stand-vor-`, keine Notiz), nimm sie; sonst fragen.
2. **Existiert `veroeffentlichung.yaml` schon,** nichts überschreiben: zeigen, was drinsteht, und fragen, was geändert werden soll.
3. **Vorlage kopieren:** `${CLAUDE_PLUGIN_ROOT}/templates/veroeffentlichung.yaml` → `./veroeffentlichung.yaml`.
4. **Felder füllen aus dem Manuskript:**
   - YAML-Kopf: `title`/erste Überschrift → `titel` (sonst Dateiname ohne `.md`), `subtitle` → `untertitel`, `author` → `autor`, `publisher` → `herausgeber`, `date` → `stand`, `lang` → `sprache`.
   - Fehlt `lang`, die Sprache am Text erkennen (de oder en). Die Sprache des Manuskripts gilt für **alle** Ausgaben.
   - `slug`: Titel klein, Umlaute ausgeschrieben (ä→ae), Leerzeichen → `-`.
   - `datum`: heutiges Datum aus `date +%Y-%m-%d` (nie aus dem eigenen Zeitgefühl).
   - `fusszeile`: aus `printdocs.sh` im Ordner übernehmen, falls dort ein `--footer=` steht.
5. **Ziele fragen** (eine AskUserQuestion, multiSelect): PDF (A4), Website, LinkedIn-Teaser, Taschenbuch (KDP), E-Book (KDP). Bei Taschenbuch zusätzlich Format (Standard 6x9) und Papier (Standard weiß) bestätigen lassen. Bei Website oder LinkedIn `website.pfad` und `website.url` aus einer früheren `veroeffentlichung.yaml` in Nachbarordnern übernehmen; gibt es keine, danach fragen.
6. **Voraussetzungen früh prüfen:** `python3 -I "${CLAUDE_PLUGIN_ROOT}/scripts/voraussetzungen.py"`. Das Fehlen des Titelbilds ist an dieser Stelle normal. Fehlt sonst etwas (Programme, Bibliotheken, Schriften), die Liste mit den Installationsbefehlen zeigen, damit der Nutzer das vor dem ersten Bau erledigen kann. Nichts selbst installieren.
7. `mkdir -p texte` und das Ergebnis kurz zeigen: welche Felder gefüllt sind, welche leer bleiben (ISBN, Preise, Titelbild) und welcher Schritt als Nächstes kommt (`/verlag:texte`, `/verlag:titelbild` oder gleich `/verlag:veroeffentlichen`).
