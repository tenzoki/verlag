---
description: Führt eine Veröffentlichung von Anfang bis Ende — anlegen, Begleittexte, eigenes Titelbild, alle Ausgaben bauen und prüfen, Website-Artikel vorbereiten, Freigabe-Checkliste — mit zwei Freigabepunkten (Texte, Titelbild). Verwenden, wenn der Nutzer ein fertiges Manuskript als PDF, auf der Website, als LinkedIn-Teaser, als Taschenbuch und/oder E-Book veröffentlichen will.
argument-hint: [Manuskript.md]
allowed-tools: [Read, Write, Edit, Bash, Glob, Grep, AskUserQuestion, WebSearch, Skill]
---

# /verlag:veroeffentlichen — der ganze Weg

Das Manuskript selbst ist fertig; dieser Ablauf erzeugt alles drumherum. Jeder Schritt ist ein eigener Skill und kann auch einzeln aufgerufen werden.

1. **Anlegen:** Fehlt `veroeffentlichung.yaml`, `/verlag:neu` ausführen. Sonst die Datei lesen und die aktiven Ziele nennen.
2. **Texte:** `/verlag:texte` für alle Texte, die die Ziele brauchen (Rückseite und KDP nur bei Taschenbuch/E-Book, LinkedIn nur bei linkedin, Website-Teaser nur bei website; Zusammenfassung immer).
3. **Titelbild:** Nur bei Taschenbuch, E-Book, Website oder LinkedIn. Fehlt `titelbild.svg`, `/verlag:titelbild`.
4. **Freigabe 1:** Texte und Titelbild in einer Nachricht vorlegen (Pfade, Rückseite im Wortlaut, Titelbild-Vorschau) und auf Zustimmung warten. Änderungswünsche einarbeiten.
5. **Bauen:** `/verlag:bauen`. Fehler beheben, bis alle Prüfungen bestehen. Danach in `texte/` die Seitenzahl nachtragen, wo sie erwähnt wird.
6. **Website:** bei Ziel website `/verlag:website` (bereitet vor, lädt nicht hoch).
7. **Freigabe 2:** `/verlag:freigabe` und dem Nutzer die Checkliste nennen.

Am Ende eine kurze Übersicht: was erzeugt wurde (Pfade), was geprüft ist, was der Nutzer selbst tun muss. Wird später das Manuskript geändert, reicht `/verlag:bauen` (und bei geändertem Inhalt `/verlag:texte` für die betroffenen Texte).
