---
description: Erklärt das verlag-Plugin — was es erzeugt, die Befehle, die Datei veroeffentlichung.yaml, was automatisch geht und was manuell bleibt. Verwenden, wenn der Nutzer fragt, wie Veröffentlichen mit verlag funktioniert.
allowed-tools: [Read]
---

# /verlag:hilfe

Erkläre dem Nutzer in seiner Sprache, knapp und in ganzen Sätzen:

**Was verlag macht.** Aus einem fertigen Markdown-Manuskript entstehen wahlweise ein PDF in DIN A4, ein Artikel auf der Website mit PDF-Download, ein LinkedIn-Teaser, ein Taschenbuch für Amazon KDP (Innenteil und Umschlag) und ein E-Book für KDP. Alle Ausgaben haben die Sprache des Manuskripts.

**Die eine Datei.** `veroeffentlichung.yaml` im Projektordner hält alle Angaben: Titel, Autor, Sprache, Ziele, Buchformat, Papier, Titelbild, Farben. Alles andere wird daraus abgeleitet, auch die Rückenbreite aus der tatsächlichen Seitenzahl.

**Befehle.**
| Befehl | Zweck |
|---|---|
| `/verlag:veroeffentlichen` | der ganze Weg mit zwei Freigaben |
| `/verlag:neu` | veroeffentlichung.yaml anlegen |
| `/verlag:texte` | Zusammenfassung, Rückseite, KDP-Texte, LinkedIn, Website-Teaser |
| `/verlag:titelbild` | eigenes Motiv entwerfen |
| `/verlag:bauen` | alle Dateien erzeugen und prüfen (`ausgabe/`) |
| `/verlag:website` | Artikel auf die Website vorbereiten |
| `/verlag:freigabe` | Checkliste für die manuellen Schritte |

**Automatisch** sind Satz, Umschlag, Prüfungen und Texte. **Manuell** bleiben das Hochladen bei KDP (keine Schnittstelle), das Hochladen der Website auf den Webspace und das Posten auf LinkedIn, weil diese Schritte nach außen wirken.

**Für Fortgeschrittene:** Die Skripte liegen unter `${CLAUDE_PLUGIN_ROOT}/scripts/` (`mdprint --help`, `bauen.py --help`, `umschlag.py --help`) und laufen auch ohne Claude.
