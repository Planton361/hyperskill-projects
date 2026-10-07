# V6.6 Global Overview — optical hierarchy

Der ursprüngliche Overview-Pass unten dokumentiert den akzeptierten Ausgangszustand. Die abschließende Sektion **Progress marker collision resolution** ersetzt ausschließlich dessen frühere Fortschritts-Mindestgrößen und verbleibenden Kollisionspunkt.

Die akzeptierte lokale Geometrie ist vollständig eingefroren. Dieser Pass verändert ausschließlich die Overview-Betonung, die kleine Orientierungshilfe und das Beibehalten des expliziten View-Zustands während Kameranavigation. Keine Karte, kein Tray, Teilbaum, Markerzentrum oder Verbindungssegment wurde verschoben oder skaliert.

Im Global Fit All tritt die tiefe Struktur jetzt zurück. Die oberen Verbindungen und Kategorien sind klarer von den feineren Details getrennt. Die fünf realen Roots stehen im vorhandenen Guide mit 14-px-Schrift; drei dezente Links nennen Algorithms and data structures, Programming languages und Backend. Die Guide-Höhe und sämtliche Vergleichskameras sind unverändert.

**Overview-Regeln, bestehende V6.6-Palette:**

| Strukturtiefe | Connector: Deckkraft / Bildschirmbreite | Category-Rand: Deckkraft / Bildschirmbreite |
|---|---:|---:|
| Presentation root, 0 | 0,90 / 1,10 px | 1,00 / 1,10 px |
| Reale Roots, 1 | 0,70 / 0,95 px | 1,00 / 1,10 px |
| Major Categories, 2 | 0,46 / 0,70 px | 0,90 / 0,90 px |
| Mittlere Kategorien, 3 | 0,27 / 0,55 px | 0,65 / 0,70 px |
| Tiefe Kategorien, 4 | 0,18 / 0,45 px | 0,40 / 0,60 px |
| Tiefe 5 und tiefer | 0,14 / 0,45 px | 0,28 / 0,55 px |

Tray-Rahmen sinken von 0,90 Deckkraft / 0,90 px auf 0,20 / 0,45 px. Ihr Hintergrund verwendet die vorhandene Topic-Farbe mit 0,55 Deckkraft. Topic-, Referenz- und Category-Texte bleiben exakt dieselben Raster-Commands mit unveränderter, nicht transparenter Textfarbe. Unlearned-/Unknown-/Reference-Kerne und die gestrichelte Reference-Unterscheidung bleiben erhalten.

Learned-Kerne bekommen im Overview mindestens **1,65 px Radius**, Verified-Ringe mindestens **2,80 px Radius**. Sie werden im vorhandenen Ink-Pass nach den Hintergrundstrukturen gezeichnet, ausschließlich an den ursprünglichen Topic-Positionen. Die vorhandene Mint-Farbe bleibt erhalten. Es gibt weiterhin 31 einzelne Learned-Kerne und 12 einzelne Verified-Ringe, keine zusammengefassten Fortschrittsobjekte. Subtree und Topic verwenden vollständig die bisherigen Marker-, Connector-, Karten- und Tray-Stile.

Die Optik hängt ausschließlich an `overview`, `subtree` oder `topic`. Pan, Wheel und Zoom-Buttons verändern die Kamera und behalten den View-Zustand. Explizite Fit-/Focus-Navigation bestimmt den nächsten Zustand. Keine numerische Zoomgrenze schaltet Inhalte oder Stile um. Alle 849 Kategorien, 3.106 Blattzeilen, Labels und Hierarchie-Verbindungen sind in jedem Zustand vorhanden.

**Vergleich, Dark, 1440 × 900 CSS-Pixel, DPR 2:** [Alle fünf Vorher-/Nachher-Paare](tests/overview-optics/review.html).

| Ansicht | Vorher | Nachher |
|---|---|---|
| Global Fit All | [Bild](tests/overview-optics/before/global.png) | [Bild](tests/overview-optics/after/global.png) |
| Computer science vollständig | [Bild](tests/overview-optics/before/computer-science.png) | [Bild](tests/overview-optics/after/computer-science.png) |
| Natural science vollständig | [Bild](tests/overview-optics/before/natural.png) | [Bild](tests/overview-optics/after/natural.png) |
| Bioinformatics vollständig | [Bild](tests/overview-optics/before/bio.png) | [Bild](tests/overview-optics/after/bio.png) |
| Topic Focus: Formatted output | [Bild](tests/overview-optics/before/topic.png) | [Bild](tests/overview-optics/after/topic.png) |

Alle Kameratransformationen sind vor/nachher exakt gleich. Die vier Subtree-/Topic-Hauptkartenbereiche sind pixelidentisch; ausschließlich ihre gemeinsame Minimap übernimmt die neue Overview-Optik. Natural science und Bioinformatics behalten damit die akzeptierte visuelle Qualität.

**Fokussierte Validierung:** [30 Prüfungen bestanden](tests/overview-optics/checks.json). Geometrie-, Label-, Hierarchie-Kanten- und Marker-Hashes sind vor/nachher identisch. Geometrie-SHA256:

`b38b9c7a692c27be27db7e4500b1a5b3abec85eac2ab0bf0c07852f0f8f1a6d9`

Der Geometriehash enthält alle Node-Koordinaten und Maße, Trays, Branches, vereinigten Verbindungssegmente, Packing-Pläne, Routinggruppen und den Layout-Checkpoint. Die Category-/Leaf-/Command-Identitäten und sämtliche Label-Commands wurden zusätzlich direkt verglichen. 464 eingefrorene bzw. geschützte Dateien sind byte-identisch, einschließlich `layout.js`, `routing.js`, Daten, My Skill Tree und Original V6.6.

Die Tile-/Worker-/Ink-Architektur ist erhalten. Die Raster-Commands ändern sich nicht; Depth-Metadaten steuern lediglich den vorhandenen Ink-Pass. Die neue Optikversion `v66-overview-optics-1` trennt Cache-Schlüssel. Der bestehende Style-Invalidierungsweg baut Tiles, Worker und Minimap korrekt neu auf, ohne Scene-, Geometrie- oder Hit-Test-Neuaufbau. Der vollständige Command-Inhalt bleibt über alle Rasterauflösungen identisch.

**Kurzer nativer Safari-DPR2-Check:** [Messung](tests/overview-optics/safari.json), jeweils Overview und dichter Programming-languages-Ast mit warmem Pan/Zoom. Frame-Abstand p95 vorher/nachher: Overview **17/18 ms**, dichter Ast **18/17 ms**. Zeichenzeit p95: **5/5 ms** beziehungsweise **3/3 ms**. Keine Frame-Abstände über 50 ms, keine Layoutaufrufe, unveränderte Scene/Geometrie und Cache unter 96 MiB. Die Kadenz bleibt praktisch unverändert. Der frühere Overview→Subtree-Wechsel bei Pan/Zoom findet nicht mehr statt.

**Visuelle Beurteilung der neun Akzeptanzfragen:** Die vollständige Karte ist schneller als obere Struktur plus tiefer Detailbestand erfassbar. Die fünf Roots sind im Guide klar lesbar; Major Categories unterscheiden sich optisch von tiefen Kategorien. Alle Blattzeilen bleiben dargestellt. Fortschritt ist deutlich sichtbar, allerdings im eng besetzten Java-Bereich teilweise überlagert. Natural science und Bioinformatics bleiben unverändert gut. Pan/Zoom schaltet keine Inhalte um. Palette, Karten, Text und Lesezustände bleiben erkennbar V6.6.

**Vor dieser Korrektur verbleibender visueller Punkt:** Bei Global Fit All überlagern sich mehrere benachbarte Learned-Kerne und Verified-Ringe im engen Java-Cluster. Alle tatsächlichen Marker bleiben einzeln im Renderbestand und an ihren echten Positionen; im Subtree sind sie wieder einzeln unterscheidbar. Die höhere Sichtbarkeit wird an dieser Stelle mit geringer Trennbarkeit bezahlt. Deshalb beansprucht dieser Pass keine vollständige visuelle Abnahme.

Keine Geometrieiteration, keine neue Prototypfamilie, keine Änderung an My Skill Tree. Kein Commit, Push oder Deployment. Reproduktion: lokalen Server mit diesem Prototyp als Root auf Port 8791 verwenden; `node tests/overview-optics/capture.cjs before`, `after` und `node tests/overview-optics/validate.cjs`. Der kurze native Safari-Lauf verwendet `tests/overview-optics/server.py` auf Port 8793 und `/tests/overview-optics/safari.html`.

## Progress marker collision resolution

**Ursache.** Im realen Java-Ast liegen verschiedene Fortschrittsanker bis auf 33 Welteinheiten zusammen. Bei unverändertem Global Fit All (`k=0,03719521380326761`) sind das nur 1,227442 CSS-Pixel. Die vorherigen festen Mindestgrößen von Learned-Kernen und Verified-Ringen belegten inklusive Strichbreite 3,95 bzw. 6,35 Pixel Durchmesser. Dadurch kollidierten 37 Paare verschiedener Topic-Glyphen.

**Finale Overview-Kodierung.** Jede der 31 Learned-Zeilen erhält als primäres Signal eine dezente Mint-Tönung mit 0,28 Deckkraft auf ihrem eigenen, unveränderten Topic-Rechteck. Diese 31 einzelnen Status-Commands werden im bestehenden Ink-Pass hinter dem unveränderten Text gezeichnet. Normale und unresolved Zeilen behalten ihre bisherige Darstellung. Der kleine Learned-Kern bleibt am bisherigen Statuszentrum. Verified ergänzt dort einen Ring; Learned + Verified desselben Topics bilden eine konzentrische Composite-Glyphe, ohne Versatz. Bei Verified bleibt der innere Kern kleiner als der Ring, damit dieser als eigene Zustandsinformation beiträgt.

**Kollisionsstrategie.** Bei Scene-Kompilierung werden einmalig die nächsten verschiedenen Fortschrittsanker ermittelt: euklidischer Abstand für den Bericht und Chebyshev-Abstand für sichere, auch diagonal getrennte äußere Bounding Boxes. Zusätzlich wird der Abstand zum Rechteck jeder anderen Learned-Zeile berücksichtigt. Die aktuelle äußere Ausdehnung ist höchstens `0,40 × nächster Chebyshev-Abstand × Kameraskala` und `0,85 × Abstand zur fremden Learned-Zeile × Kameraskala`, begrenzt durch den bisherigen gewünschten V6.6-Overview-Zielwert. Der Faktor 0,40 lässt im echten Java-Cluster 20 % des engsten Ankerabstands als Trennung zwischen zwei äußeren Glyphenboxen übrig. Es gibt keine harte Mindestgröße. Die Ring-Strichbreite schrumpft ebenfalls kontinuierlich, damit sie die Begrenzung nicht wieder überschreitet.

Verglichen werden **stroke-inklusive äußere AABBs**, je eine Composite-Box pro unterschiedlicher Topic-ID. Überlappungstiefe: `max(0, min(rA+rB−|dx|, rA+rB−|dy|))`. Learned und Verified derselben Topic-ID werden nicht gegeneinander getestet. Learned-Rechtecke sind untereinander ebenfalls disjunkt; keine Glyphenbox trifft das Learned-Rechteck eines anderen Topics. Antialiasing kann Randpixel anteilig belegen, erweitert aber nicht diese geprüften geometrischen Boxen.

| Messung, CSS-Pixel sofern nicht anders angegeben | Vorher | Nachher |
|---|---:|---:|
| Learned Topics | 31 | 31 |
| Verified Topics | 12 | 12 |
| Davon Java: Learned / Verified | 26 / 11 | 26 / 11 |
| Kleinster verschiedener Ankerabstand, Welt | 33 | 33 |
| Kleinster verschiedener Ankerabstand bei Fit All | 1,227442 | 1,227442 |
| Maximale äußere Bounding-Box-Überlappung | 4,806399 | **0** |
| Kollidierende Topic-Paare | 37 | **0** |
| Kleinster Composite-Marker-Durchmesser | 3,950000 | 0,981954 |
| Median Composite-Marker-Durchmesser | 3,950000 | 1,234881 |
| Größter Composite-Marker-Durchmesser | 6,350000 | 6,350000 |

Die minimale Trennung der äußeren Boxen beträgt jetzt 0,245488 CSS-Pixel. Die Durchmesser umfassen den äußeren Ring einschließlich Strichbreite, sofern vorhanden, sonst den Learned-Kern. Kleine dichte Glyphen werden durch die gut erkennbare individuelle Zeilentönung unterstützt. Sechs dünn besetzte Topics behalten die vorherige äußere Zielgröße unverändert: IDs 259, 260, 348, 1476, 1761 und 3538. Jeder der zwölf Verified-Ringe trägt bei seiner tatsächlichen Subpixelposition im DPR2-Test messbar eigene Pixel bei. Es gibt keine zusammengeführte Fortschrittsglyphe.

**Screenshots:** [Direkter Vergleich](tests/progress-collisions/review.html). [Fit All vorher](tests/progress-collisions/before/global.png), [Fit All nachher](tests/progress-collisions/after/global.png), [Java vorher](tests/progress-collisions/before/java-cluster.png), [Java nachher](tests/progress-collisions/after/java-cluster.png), [normaler Natural-science-Subtree nachher](tests/progress-collisions/after/natural.png). Java wurde aus derselben 1440×900-Dark-Aufnahme mit identischem Crop ausgeschnitten; die Vergleichsseite vergrößert nur die gespeicherten Crop-Bilder. Die Karte selbst wurde für diesen Vergleich nicht anders gezoomt.

**Validierung und Erhaltung:** [28 fokussierte Prüfungen bestanden](tests/progress-collisions/checks.json). Unveränderter Geometriehash `b38b9c7a692c27be27db7e4500b1a5b3abec85eac2ab0bf0c07852f0f8f1a6d9`; 849 Kategorien, 3.106 Blattzeilen, 5.250 Text-Commands, Learned-/Verified-IDs, Anker und Connector-Inventar unverändert. Die akzeptierten vier Leseansichten Computer science, Natural science, Bioinformatics und Topic Focus bleiben im Hauptkartenbereich pixelidentisch. Nur die gemeinsame Overview-Minimap übernimmt die korrigierten Statusglyphen.

Die Größenfunktion bleibt ausschließlich im expliziten Overview aktiv. An sechs geprüften Kameraskalen von 0,001 bis 4 bleiben alle Fortschrittsglyphen positiv groß und kollisionsfrei; keine Topic-/Label-/Status-Sichtbarkeit wird umgeschaltet. Subtree-/Topic-Glyphen benutzen exakt die normalen V6.6-Radien. Die Nachbarbeziehungen bleiben in der Scene erhalten; es gibt keine Distanzsuche während Pan/Zoom. Tile-Commands bleiben unverändert, 31 ergänzte Ink-Commands tragen die einzelnen Zeilenakzente. Die Optikversion `v66-overview-progress-2` nutzt den bestehenden Cache-/Worker-/Minimap-Aufbau. [20 Renderer-/Cache-/Worker-/Navigationsmethoden](tests/progress-collisions/architecture.json) sind gegenüber dem Ausgangszustand unverändert. Die Architektur ist erhalten.

466 eingefrorene bzw. geschützte Dateien sind byte-identisch, darunter Layout, lokale Konturen, Tray-/Card-Geometrie, Routing, komplette Hierarchie-Optik, Guide, CSS, App-Navigation, Tile-Painter, Worker, Original V6.6, My Skill Tree, Knowledge, State und geschützter gemeinsamer Code. Nur `tiled-renderer.js` und die angeforderten Prüf-/Berichtsartefakte wurden in diesem Schritt geändert.

**Ein kurzer nativer Safari-DPR2-Check:** [Messung](tests/progress-collisions/safari.json), 1440×900, warmes Pan/Zoom in Overview und dichtem CS-Ast. Frame-Abstand p95 vorher/nachher jeweils **17/17 ms**. Overview-Zeichenzeit p95 **4/5 ms**, dichter Ast **3/3 ms**. Keine Abstände über 50 ms, keine Layoutaufrufe, unveränderte Scene/Geometrie; Cache bleibt unter 96 MiB. Browser-Kadenz bleibt erhalten.

Die Java-Kollisionen sind gelöst; Fortschritt bleibt verteilt und ohne falsch zusammengeführte Marker sichtbar. Es waren keine Positionsverschiebungen, Leader Lines oder Spiderification erforderlich. HARD STOP: keine weitere visuelle, Layout- oder Performanceiteration; kein Commit, Push oder Deployment.

C — GLOBAL V6.6 VISUAL DESIGN ACCEPTED
