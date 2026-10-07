# V6.6 Global Atlas — gezielte Performance-Korrektur

Nur `app.js` wurde unter den bestehenden Global-Dateien geändert. Der vollständige SVG-Atlas und die akzeptierte Geometrie bleiben erhalten. **849 Categories, 3.106 Leaf-Slots, alle Labels und Statusmarkierungen sind identisch.** Drei identische Kamerazustände ergeben **0 unterschiedliche Pixel** bei 1440×900 und DPR 2. Die persönliche Ansicht, V6.6, Production, State und Knowledge sind unverändert.

Die Korrektur beseitigt unnötige Arbeit während Kamerabewegungen. Sie ist **keine „flüssig“-Abnahme**: Safari bleibt im gemessenen Lauf deutlich langsam; Zoom und Ast-Navigation behalten auch in Chromium einen relevanten Browser-Engpass. Die Bedienbarkeit muss der Nutzer anschließend beurteilen.

## Messung und Ursache

Gemessen wurde der aktuelle Global-Code, nicht das historische Course-V6.6. Der wiederholbare Diagnoseablauf verwendet vollständig dieselbe Szene und die echten D3-DOM-Handler: Fit All, 1,8 Sekunden Pan, 1,8 Sekunden Zoom, dann Programming languages und Topic 518. Der Eingabetreiber nimmt pro Callback den neuesten zeitbasierten Zielwert; bei verspäteten Frames entsteht keine Eingabewarteschlange. Es handelt sich um synthetische kontinuierliche Eingaben, nicht um eine aufgezeichnete menschliche Trackpad-Geste.

- **Tatsächlich geöffnetes Safari 27.0.1 auf dem Mac:** 864×913 CSS-Pixel, `devicePixelRatio = 2`, Bildschirm 1728×1117 CSS-Pixel. Native Fenstergröße und Pixeldichte wurden nicht emuliert. Je ein Vorher-/Nachher-Lauf liefert JS-Komponentenzeiten und tatsächliche `requestAnimationFrame`-Abstände.
- **Chromium for Testing 149.0.7827.55, sichtbar/headed auf demselben Mac:** ebenfalls 864×913 und natives DPR 2, ohne Device-Emulation. Kurze DevTools-Timeline-Traces trennen JS, Browser-Style/Layout und Paint/Composite; zusätzlich sind Compositor-`DrawFrame`-Abstände erfasst.
- Die visuelle Paarprüfung verwendet ausschließlich 1440×900 Dark, DPR 2. Keine historische Matrix oder Vollregression.

**Bewiesene Ursache vor der Korrektur:** Jeder Zoom-Handler schrieb Marker-Radien/Stroke-Werte, auch bei reinem Pan, und aktualisierte unveränderte UI-Werte. Danach las `updateMinimap()` die SVG-Bildschirmgeometrie. Das erzwang synchrone Browser-Style/Layout-Arbeit nach den Schreiboperationen. Zusätzlich wurden die unveränderte ausgewählte Nachkommenmenge und ihre Bounds wiederholt berechnet. Die Minimap-Grundkarte war bereits statisch und wurde nicht als Ursache behauptet.

Im Chromium-Pan-Lauf verbrauchte der Markerblock 221,6 ms; `updateMinimap` inklusive erzwungener Browser-Arbeit 626,0 ms. 60 Bildschirm-Box-Abfragen fielen an. Nachher: keine Marker-Schreiboperation bei Pan, keine Bildschirm-Box-Abfrage, Minimap-Update insgesamt 1,9 ms. Diese verschachtelten Komponentenwerte dürfen nicht addiert werden.

## Konkreter Fix

- Kameraereignisse setzen den aktuellen Transform synchron und planen höchstens ein `requestAnimationFrame`-Update. Der Renderjob verwendet ausschließlich den neuesten Zustand.
- Wiederverwendete Marker-Selektionen; Radius und Stroke werden nur geschrieben, wenn der berechnete Wert wirklich anders ist. Reines Pan schreibt keine Markerattribute. Die bisherigen Zahlen/Formeln bleiben unverändert.
- Status, Zoomtext, Guide-Sichtbarkeit und Minimap-Attribute werden nur bei Änderungen gesetzt.
- Nachkommen, Subtree-Mengen, Subtree-Bounds und Welt-Bounds werden für die unveränderliche Geometrie wiederverwendet. Minimap-Auswahlbounds werden nur bei neuer Auswahl gesetzt.
- Bildschirmmaße und beide bestehenden Fit-Bereiche werden beim Start und tatsächlichem Container-Resize gemessen. Während Pan/Zoom lesen diese App-Pfade keine DOM-Geometrie. Resize-Äquivalenz wurde gezielt geprüft.
- Minimap-Grundkarte und Graph-Nodes werden bei Kameraeingaben nicht neu aufgebaut. Shared Hierarchy Segments bleiben einmal gezeichnet.
- Navigation bleibt bei 220 ms; der letzte Kamerazustand wird am Ende geschrieben. Reduced Motion und nicht animierte Fits werden weiterhin synchron dargestellt.

Ein Burst aus **60 Pan-Ereignissen erzeugt ein Renderupdate statt 60**, mit null Marker-Mutationen. Keine Nodes, Labels oder Leaf-Slots werden hierfür entfernt, ausgeblendet, zusammengefasst oder unscharf gerendert.

## Vorher / nachher: Frame-Abstände

Werte in ms, je Median / p95. Die Phasen enthalten die kurze bestehende Abschluss-/Settling-Zeit. Kleine Navigations-Stichproben und andere laufende Mac-Anwendungen können Spitzen beeinflussen. RAF misst tatsächliche Callback-Abstände, nicht physische Bildschirm-Scanouts; `DrawFrame` misst Compositor-Ereignisse, nicht bestätigte Monitor-Präsentationen.

| Phase | Safari RAF vorher | Safari RAF nachher | Chromium RAF vorher | Chromium RAF nachher |
|---|---:|---:|---:|---:|
| Fit All inkl. Rückkehr aus Computer science | 166.0 / 183.0 | 71.0 / 202.0 | 57.5 / 91.7 | 41.7 / 50.1 |
| Kontinuierliches Pan | 154.0 / 182.0 | 124.0 / 143.0 | 33.3 / 34.3 | 8.4 / 17.5 |
| Kontinuierlicher Zoom | 136.0 / 144.0 | 126.0 / 134.0 | 57.5 / 67.6 | 41.7 / 58.1 |
| Programming languages → Topic 518 | 122.0 / 143.0 | 119.0 / 288.0 | 58.5 / 65.7 | 40.8 / 50.9 |

Safari-Pan verbessert sich im Median von 154 auf 124 ms, Zoom von 136 auf 126 ms. Das bleibt weit von einer flüssigen Navigation entfernt. Der Safari-p95 bei Ast/Topic-Navigation wird in diesem kleinen Lauf schlechter (143 → 288 ms); diese Verschlechterung wird nicht verschwiegen.

| Phase | Chromium DrawFrame vorher, Median / p95 | Nachher, Median / p95 |
|---|---:|---:|
| Fit All inkl. Rückkehr aus Computer science | 62.2 / 75.3 | 50.2 / 59.7 |
| Kontinuierliches Pan | 30.9 / 32.5 | 11.6 / 17.5 |
| Kontinuierlicher Zoom | 64.0 / 73.3 | 47.9 / 58.7 |
| Programming languages → Topic 518 | 62.6 / 64.3 | 47.9 / 53.9 |

Die zusätzliche SVG-Leseprobe wiederholt denselben Chromium-Ablauf. Sie bestätigt den Unterschied: Pan-RAF-Median 33,3 → 8,4 ms, Zoom 58,2 → 41,8 ms. Einzelne schnelle Pan-Werte rechtfertigen keine pauschale Aussage über Zoom oder Safari.

## JS, Style/Layout und Zeichnen getrennt

Chromium-Trace, kumulierte ms je Phase; vorher → nachher. JS ist die Vereinigungsdauer der Timer/Event/Function-Spannen abzüglich darin enthaltenem Style/Layout, keine reine V8-CPU-Stichprobe. Browserphasen und Worker-Rasterzeiten können sich überschneiden und dürfen nicht summiert werden. Raster ist die Vereinigungsdauer über Worker-Zeitintervalle, keine aufsummierte Multi-Core-CPU-Zeit.

| Phase | JS ohne verschachteltes Style/Layout | Style/Layout | Paint | PrePaint | Layerize/Composite | Raster |
|---|---:|---:|---:|---:|---:|---:|
| Fit All inkl. Rückkehr aus Computer science | 82.4 → 10.3 | 355.7 → 284.4 | 117.8 → 109.5 | 65.2 → 64.7 | 50.4 → 52.6 | 123.8 → 128.7 |
| Kontinuierliches Pan | 442.6 → 22.6 | 518.5 → 93.1 | 400.5 → 71.8 | 140.5 → 211.3 | 260.2 → 685.9 | 446.4 → 1693.9 |
| Kontinuierlicher Zoom | 221.3 → 17.5 | 938.6 → 1029.1 | 329.6 → 411.5 | 172.6 → 225.8 | 116.0 → 146.8 | 389.2 → 481.3 |
| Programming languages → Topic 518 | 67.8 → 14.6 | 365.3 → 301.0 | 126.5 → 125.2 | 65.1 → 69.7 | 44.6 → 46.9 | 87.8 → 102.3 |

Beim Pan zeichnet Chromium nachher wesentlich mehr Frames in derselben Zeit; deshalb steigen einige kumulierte Composite-/Rasterwerte. Auch die höhere kumulierte Zoom-Layout-Zeit entsteht bei mehr gezeichneten Frames. Die Frame-Abstände und vollständigen Rohdaten sind für die Bewertung entscheidend. Safari hat keine separat aufgezeichnete Web-Inspector-Rendering-Timeline; die Chromium-Phasenwerte werden nicht als Safari-Paint-Messung ausgegeben.

## Verbleibender Engpass und nächster technischer Schritt

Die App-Hotpath-Arbeit ist weitgehend entfernt. Chromium benötigt beim Zoom weiterhin etwa 48 ms zwischen Compositor-Frames. Im Trace laufen weiterhin globale SVG-Layout/PrePaint/Paint- und Stroke-Verarbeitungen für die große Szene.

Eine Zusatzprobe lokalisiert einen weiteren synchronen Leser **innerhalb von D3**: `getScreenCTM()` für die Zeigerprojektion. Nachher braucht dieser native Read bei Zoom insgesamt **1.001,5 ms / 40 Aufrufe** (ca. 25 ms/Aufruf). Vorher war dieser Read billig, weil das teure Flush bereits in `updateMinimap/getBoundingClientRect` erfolgt war. Die Eliminierung der App-Abfrage beseitigt also nicht das weiterhin erforderliche SVG-Browserlayout.

Der kleinste nächste technische Versuch ist, **D3s Zeigerprojektion auf die unveränderliche Root-SVG-Bildschirmmatrix zu entkoppeln**, mit exakter Invalidierung bei Resize, Scroll und Browser-Viewport-Änderung. Er muss Rad-/Pinch-Anker und die bestehende Gestenlogik vor/nach exakt prüfen. Das wurde hier nur gemessen und dokumentiert; kein natives SVG-Verfahren wurde eigenmächtig überschrieben. Der Versuch kann den synchronen Input-Flush vermeiden, garantiert aber nicht, den vollständigen SVG-Paint-Aufwand zu beseitigen. Für Safari bleibt eine native Rendering-Timeline nötig, bevor sein Restengpass genauer als „außerhalb der gemessenen App-Callbacks“ zugeordnet wird.

Kein Canvas/WebGL/OffscreenCanvas/Tile-Renderer wurde eingeführt. Ein späterer Renderer-Schritt müsste weiterhin sämtliche V6.6-Zeilen, Texte, Referenz-IDs und Marker darstellen.

## Graue Überblicksdichte

**2.715 physische Hierarchiesegmente, null identische doppelt gezeichnete Segmente.** Es gibt keine versehentlich doppelte Zeichenoperation zu entfernen.

Bei 1440×900 Fit All beträgt der Maßstab ca. 0,00449081. Eine 29-Unit-Zeile projiziert auf nur 0,13 CSS-Pixel, während die vorhandenen non-scaling Hierarchiestriche ungefähr 0,7 px und Tray-Outlines 0,9 px behalten. Das erklärt einen wesentlichen Anteil der grauen Dichte: Einzelne mikroskopische Silhouetten/Slot-Cues liegen dichter als ihre Bildschirmstriche. Diese optische Eigenschaft wurde **nicht geändert**; alle Abstände, Stroke-Werte und Farben bleiben erhalten.

## Absicherung und Artefakte

**24 fokussierte Vergleichschecks bestanden**: vollständige identische IDs/Labels/Statuszuordnungen, exakt identische Node-/Tray-/Connector-Geometrie und Textmaße, gleicher Inspector und Endkamera, Search, Topic-/Referenz-Focus, Reduced Motion, gezielter Resize und Wiederherstellung, keine Layoutaufrufe oder DOM-Neuerzeugung bei Navigation, keine Zoom-Ausblendung, ein Burst-Renderjob, keine Markerwrites bei Pan und keine Minimap-Neuerzeugung.

Die 3 Paarbilder (Fit All, Programming languages, Topic 518) ergeben bei 2880×1800 physischen Pixeln jeweils **0 unterschiedliche Pixel**. Es wurde keine Vollregression gefahren.

- [Vergleich und Checks](tests/performance/comparison.json), [Pixelvergleich](tests/performance/pixel-comparison.json)
- [Safari vorher](tests/performance/safari-before.json), [Safari nachher](tests/performance/safari-after.json)
- [Chromium-Trace vorher](tests/performance/trace-before.json.gz), [nachher](tests/performance/trace-after.json.gz), [Trace-Zusammenfassung vorher](tests/performance/trace-before-summary.json), [nachher](tests/performance/trace-after-summary.json)
- [SVG-Leseprobe](tests/performance/svg-geometry-reads.json)
- [Fit All vorher](tests/performance/before-fit-all.png), [nachher](tests/performance/after-fit-all.png)
- [Ast vorher](tests/performance/before-dense-branch.png), [nachher](tests/performance/after-dense-branch.png)
- [Topic vorher](tests/performance/before-topic.png), [nachher](tests/performance/after-topic.png)

Alle **455 geschützten Dateien** haben identische Bytes und Inventare, einschließlich persönlichem Skill Tree, Original-V6.6, sämtlichen Docs/Production, State, Knowledge und Shared Runtime. Unter den bestehenden Global-Dateien änderte sich ausschließlich `app.js`; `layout.js`, `routing.js`, `model.js`, `model.json`, `style.css` und `index.html` sind byte-identisch. Nachweis: [preservation.json](tests/performance/preservation.json) und die `protected-before/after.json`-Manifeste. Kein Commit, Push oder Deployment.

## Lokal starten / wiederholen

Vom Repository-Root:

```sh
python3 -m http.server 8777 --bind 127.0.0.1 --directory prototypes/knowledge-atlas-v6-global
```

Atlas: <http://127.0.0.1:8777/>

Der separate Loopback-Diagnoseserver lädt Messinstrumentierung nur bei `?probe=1`; der normale Atlas enthält sie nicht:

```sh
python3 -B prototypes/knowledge-atlas-v6-global/tests/performance/server.py
node prototypes/knowledge-atlas-v6-global/tests/performance/trace.cjs before
node prototypes/knowledge-atlas-v6-global/tests/performance/trace.cjs after
node prototypes/knowledge-atlas-v6-global/tests/performance/compare.cjs
node prototypes/knowledge-atlas-v6-global/tests/performance/pixels.cjs
```

Native Safari-Probe: <http://127.0.0.1:8782/tests/performance/run.html?phase=before&label=safari> und entsprechend `phase=after`. Der Testserver archiviert die Antworten ausschließlich unter `tests/performance/`. Browserfenster während der Messung sichtbar lassen. Die CLI verwendet die bereits vorhandene Playwright-Installation und Chromium-Cache-Pfade; es wurden keine Pakete installiert.

Die Verbesserung ist gemessen; eine menschliche Abnahme der kontinuierlichen Navigation steht aus.
