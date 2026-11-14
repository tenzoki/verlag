---
description: Erzeugt alle Ausgaben einer Veröffentlichung aus veroeffentlichung.yaml — DIN-A4-PDF, Taschenbuch-Innenteil und CMYK-Druckumschlag für KDP, EPUB mit Titelbild, Vorschaukarte — und prüft sie (Schriften eingebettet, Satzspiegel, Rückenbreite aus der echten Seitenzahl, Farbauftrag, epubcheck). Verwenden, wenn PDF, Buch, E-Book oder Umschlag erzeugt oder nach einer Textänderung neu gebaut werden sollen.
argument-hint: [pdf,taschenbuch,ebook,website]
allowed-tools: [Read, Bash, Edit, Glob]
---

# /verlag:bauen — Ausgaben erzeugen und prüfen

1. Im Projektordner (dort, wo `veroeffentlichung.yaml` liegt) ausführen, Zeitlimit 10 Minuten:
   ```
   python3 -I "${CLAUDE_PLUGIN_ROOT}/scripts/bauen.py" [--nur pdf,taschenbuch,ebook,website]
   ```
   Das Skript schreibt nach `ausgabe/` und legt den Prüfbericht in `ausgabe/bericht.txt` ab. Exit 0 = alle Prüfungen bestanden.
   Zuerst prüft es die Voraussetzungen für die gewählten Ziele (Programme, Python-Bibliotheken, LaTeX-Pakete, Schriften, Titelbild). Fehlt etwas, baut es nichts und nennt je Punkt den Installationsbefehl. **Nichts selbst installieren**: dem Nutzer die Liste zeigen und die Befehle zum Ausführen mit `! <befehl>` vorschlagen (`sudo` fragt nach dem Passwort). Warnungen (z. B. ein fehlendes optionales LaTeX-Paket) nennen, der Bau läuft trotzdem.
2. **Ergebnis ansehen, nicht nur den Exit-Code lesen.** Umschlag und Titelbild rendern und betrachten:
   `pdftocairo -png -r 40 -singlefile ausgabe/<slug>-<format>-umschlag.pdf /tmp/umschlag` und mit Read ansehen. Bei neuen Tabellen oder Abbildungen zwei, drei Seiten des Innenteils stichprobenartig rendern (`pdftoppm -r 70 -png -f N -l N …`).
3. **Fehler beheben, wo die Ursache liegt:**
   - *Rückseitentext zu lang* → `texte/rueckseite.md` kürzen (Regeln in `/verlag:texte`), neu bauen.
   - *Inhalt außerhalb des Satzspiegels* → betroffene Seite rendern. Meist eine Tabelle mit sehr langem Wort, eine Codezeile oder ein zu breites Bild; im Manuskript beheben (Zeilenumbruch im Code, Bildbreite `{width=100%}`), nicht im Skript.
   - *Schrift nicht eingebettet* oder *mdprint fehlgeschlagen* → Meldung zeigen, Ursache suchen (fehlende Schrift, LaTeX-Fehler im Manuskript).
   - *epubcheck-Fehler* → Meldung lesen; häufig ein Bildpfad oder ungültiges HTML im Manuskript.
4. Kurz melden: erzeugte Dateien mit Seitenzahl, Rückenbreite, Farbauftrag, epubcheck-Ergebnis, und was nicht geprüft wurde (Darstellung im Kindle Previewer, Annahme durch KDP). **Ändert sich die Seitenzahl des Innenteils, wird der Umschlag automatisch mit neu gebaut** — nie einen alten Umschlag mit neuem Innenteil hochladen.

Die Skripte im Einzelnen (für Sonderfälle): `${CLAUDE_PLUGIN_ROOT}/scripts/mdprint --help` und `python3 -I "${CLAUDE_PLUGIN_ROOT}/scripts/umschlag.py" --help`.
