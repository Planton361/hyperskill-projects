# V6.6 – lokale Geometrie

Ausgewählt: `atlas-v66-global-4-local-contours`, Schema 2, ausschließlich in diesem bestehenden Prototyp. Ausgangspunkt sind die beim Arbeitsbeginn kopierten aktuellen [layout.js](tests/local-geometry/before/layout.js) und [routing.js](tests/local-geometry/before/routing.js), kein historischer V6.6-Screenshot.

**Ursachen.** `DEPTH_SCALE=[64,64,16,4]` skalierte Karten und Schriften. `card.height=depthHeights.get(depth)` ersetzte anschließend individuelle Texthöhen durch weltweite Maxima. `depthTrays` reservierte den größten Tray einer Ebene auch für unabhängige Äste. Der halbe aufgeblasene Context-Root, 2.017,28 Einheiten, wurde mit Tiefenfaktoren 1,3–2,84 multipliziert: zusätzliche Abstände von 2.622–5.729 Einheiten bei maximal 441 Einheiten tatsächlicher Trayhöhe. Rechteckige Gesamtumschläge verhinderten zusätzlich das Ineinandergreifen freier Konturen. Kartenbox und Teilbaumumschlag waren konzeptionell vorhanden, aber die Kartenbox selbst bereits künstlich vergrößert.

**Gewählte Regeln.** V6.6-Textvermessung, tatsächliche Metadatenzeile und begrenztes Padding bestimmen die Karten. `cardBounds` und `subtreeBounds` sind jetzt explizit getrennt. Fünf Roots teilen ihre Oberkante; darunter gelten lokale Geschwister-/Modulreihen. Es gibt keine globalen `depthHeights`, `depthTrays`, `depthY` oder vertikalen Streckungsfaktoren mehr.

Der normale Abstand zur nächsten lokalen Reihe beträgt 58 Einheiten: 28 bis zur Verbindungsachse plus 30 bis zur Karte bzw. zum Tray. Konturen enthalten echte Karten, vollständige Trays und Routingkorridore. 24 Einheiten trennen benachbarte Konturen, 64 die Roots. 38 benachbarte Teilbaumpaare nutzen überlappende Bounding Boxes ohne Inhaltskollision.

Ab acht Trayzeilen werden ein bis drei Spalten verglichen; ausgewählt wurden 633 einspaltige und 92 zweispaltige Trays. Erst bei mehr als 6.000 Einheiten Breite und Verhältnis Breite/Höhe > 2,4 werden Modulreihen geprüft. Die Bewertung `Breite + 1,8 × Gesamthöhe` berücksichtigt vollständige Teilbäume und 64 Einheiten Reihenabstand; 12 Kategorien verwenden mehrere Reihen. Reihen erhalten fortlaufende Geschwistergruppen in kanonischer Reihenfolge. Reservierte seitliche Korridore verbinden sie mit ihrem echten Parent. Gemeinsame orthogonale Segmente werden vereinigt.

Alle folgenden Maße sind Weltkoordinaten, unabhängig vom Kamera-Zoom:

| Messung | Vorher | Nachher |
|---|---:|---:|
| Natural-science-Karte, B × H; Schrift | 19.200 × 3.505,92; 1.344 | 193 × 54,78; 21 |
| Bioinformatics-Karte; Schrift | 3.040 × 1.041,92; 272 | 160 × 45,06; 17 |
| Data-and-Tools-Karte; Schrift | 760 × 340,72; 68 | 162 × 45,06; 17 |
| Biochemistry-Karte; Schrift | 190 × 85,18; 17 | 150 × 45,06; 17 |
| Natural science → direkte Kinder, freier Y-Abstand | 3.154,78 | 58 |
| Bioinformatics → direkte Kinder, freier Y-Abstand | 4.841,02 | 58 |
| Natural science, vollständiger Teilbaum | 19.216 × 24.337 | 4.189 × 721 |
| Bioinformatics, vollständiger Teilbaum | 3.821 × 12.032 | 2.146 × 608 |
| Programming languages, vollständiger Teilbaum | 58.325 × 30.287 | 11.019 × 4.514 |
| Gesamte Welt | 254.297 × 49.580 | 30.703 × 9.879 |
| Topic 518, B × H; Schrift | 220 × 29; 14 | 220 × 29; 14 |

Teilbaum-/Weltmaße enthalten Fit-Padding und relevante Verbindungen. Natural sciences Karten-Seitenverhältnis sinkt von 5,48 auf 3,52; Bioinformatics steigt von 2,92 auf 3,55. Biochemistry behält Schriftgröße 17 und verliert die von fremden Kategorien reservierte Höhe. Topic Focus bleibt bei Schriftgröße 16 auf dem Bildschirm.

**Screenshots.** [Direkter Vorher-/Nachher-Vergleich aller neun Bildpaare](tests/local-geometry/review.html), jeweils 1440 × 900 CSS-Pixel, DPR 2:

| Ansicht | Vorher | Nachher |
|---|---|---|
| Global Fit All | [Bild](tests/local-geometry/before/global.png) | [Bild](tests/local-geometry/after/global.png) |
| Natural science vollständig | [Bild](tests/local-geometry/before/natural.png) | [Bild](tests/local-geometry/after/natural.png) |
| Bioinformatics vollständig | [Bild](tests/local-geometry/before/bio.png) | [Bild](tests/local-geometry/after/bio.png) |
| Dichter CS-Ast: Programming languages | [Bild](tests/local-geometry/before/dense.png) | [Bild](tests/local-geometry/after/dense.png) |
| Topic Focus | [Bild](tests/local-geometry/before/topic.png) | [Bild](tests/local-geometry/after/topic.png) |

Die Vergleichsseite ergänzt feste Maßstäbe: Natural science 5 %, Bioinformatics 15 %, Biochemistry und Topic jeweils 100 %, mit identischer Ankerposition. Die automatischen Fits verbessern sich von 0,45 % auf 3,72 % global, von 2,65 % auf 27,26 % bei Natural science und von 5,37 % auf 53,23 % bei Bioinformatics. Diese Zoomwerte sind Folge der kleineren Welt; der Nachweis der Geometrieänderung steht in den Weltmaßen und den Bildern mit identischem Maßstab.

**Validierung.** [31 fokussierte Prüfungen bestanden](tests/local-geometry/checks.json): 849 Kategorien und 3.106 Blattzeilen mit eindeutiger Identität, Reihenfolge, Elternports, lokale Ausrichtung, vollständige Umschläge, keine Karten-/Text-/Tray-/Routingkollisionen, keine doppelt gezeichneten Segmente, korrekte Hit-Tests und vollständiger Command-Index. Ein ausschließlich im Speicher vergrößerter Bioinformatics-Tray verschiebt keine Y-Koordinate im unabhängigen Biology-Ast und vergrößert die Natural-science-Karte nicht. Die alten globalen Y- und eingefrorenen X-/Größenassertionen wurden in `tests/focused.cjs` ausdrücklich durch diesen lokalen Vertrag ersetzt; die vertikale Metrik meldet Verteilungen statt falscher globaler Baselines.

Die Tile-Architektur, Worker, Rasterstufen, Navigation und Design-CSS bleiben bestehen. Beim Laden entstehen Scene, Command-/Ink-/Hit-Indizes, Minimap und Tile-Cache aus der neuen Geometrie; Scene und Cache-Schlüssel tragen deren Version. Die Textbounds behandeln gemessene Nullwerte korrekt, statt sie durch künstliche Ersatzhöhen zu überschreiben. Pan/Zoom erhält dieselbe Scene und Geometrie.

[Kurzer nativer Safari-Check](tests/local-geometry/safari.json), 1440 × 900, DPR 2, warmes Pan/Zoom auf dem dichten CS-Ast: vorher/nachher Frame-Abstand p95 **17/17 ms**, Zeichenzeit p95 **3/3 ms**, keine Frame-Abstände über 50 ms, keine Layoutaufrufe, Cache jeweils unter 96 MiB. Das ist ein kurzer Schutzcheck, kein umfassender Benchmark.

[Integrität](tests/local-geometry/integrity.json): aktuelle Catalog-Projektion; 462 geschützte Dateien und ihr Inventar unverändert, einschließlich Original V6.6, persönlicher Ansicht, Knowledge, State, Docs/Production und gemeinsamem Runtime-Code. Kein Ingesting, keine Migration, kein Commit, Push oder Deployment.

**Grenzen.** Fit All und der Ast mit 1.127 Programming-language-Blattzeilen bleiben Orientierungsansichten; alle Zeilen sind vorhanden, aber dort nicht einzeln lesbar. Modulreihen haben längere seitliche Parent-Verbindungen und reservieren die reale Höhe der jeweils vorherigen vollständigen Reihe. Die begrenzte Packing-Suche garantiert kein globales Flächenoptimum. Die visuelle Gewichtung der nun normalen Parent-Karten benötigt menschliche Freigabe.

Reproduktion: lokalen HTTP-Server auf Port 8791 mit diesem Verzeichnis als Root starten; `node tests/focused.cjs`, `python3 tests/integrity.py`, `node tests/local-geometry/capture.cjs before` und `after`. Für Safari: `python3 tests/local-geometry/server.py`, dann lokal Port 8792 unter `/tests/local-geometry/safari.html` öffnen.

TECHNISCH VALIDIERT — VISUELLE FREIGABE AUSSTEHEND.
