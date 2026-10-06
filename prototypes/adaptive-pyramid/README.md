# Adaptive Pyramid · isolierter Vergleich

Vom Repository-Root starten:

```sh
python -B -m http.server 8765 --bind 127.0.0.1 --directory .
```

URL: http://127.0.0.1:8765/prototypes/adaptive-pyramid/

Die Seite liest `../global-pyramid/generated/catalog.json`, dessen unveränderte
A2-Geometrie und die vorhandenen normalisierten Beziehungskanten. Sie enthält
keinen zweiten Katalog, keine Fortschrittsänderung und keine Datenakquisition.
Auswahl, Stage, „nur gelernt“ und Astfilter werden erst über eine der drei
Ansichtsaktionen übernommen. Suche/Hover ändern das Layout nicht; das explizite
Öffnen zusammengefasster Details kann ein Layout auslösen.

„Im Atlas hervorheben“ bettet die vorhandene globale Referenz ein. Eine getrennte
Canvas-Schicht markiert IDs/Pfade in deren globalen Koordinaten. Ihre Kamera bleibt
bei Auswahländerungen erhalten. „In globaler Pyramide zeigen“ übergibt die gewählte
ID an deren bestehende Fokusfunktion. Es gibt keine gemeinsame lokale/globale
Viewport-Minimap. In der kompakten Ansicht zeigen Root-Markierungen den Kontext.

Fixtures sind ausschließlich Auswahlfunktionen über bekannte Struktur-Slots;
Titel sind `Fixture Slot #<id>`, persönlicher Fortschritt bleibt unbelegt.
„Große Auswahl zusammenfassen“ ist eine explizite Aktion: bis 299 Slots auf Tiefe 2,
ab 300 auf Tiefe 1, über 1.000 auf Root-Ebene. Suche öffnet versteckte Details.

Fokussierte Prüfungen:

```sh
node prototypes/adaptive-pyramid/tests/core.cjs
python -B prototypes/adaptive-pyramid/tests/integrity.py
PLAYWRIGHT_MODULE=/home/anton/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright \
CHROMIUM_EXECUTABLE=/home/anton/.cache/ms-playwright/chromium-1228/chrome-linux64/chrome \
node prototypes/adaptive-pyramid/tests/browser.cjs
# Gezielter Fokus-/Filter-/Motion-Check
PLAYWRIGHT_MODULE=/home/anton/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright \
CHROMIUM_EXECUTABLE=/home/anton/.cache/ms-playwright/chromium-1228/chrome-linux64/chrome \
node prototypes/adaptive-pyramid/tests/navigation.cjs
```

Browserprüfung setzt den oben genannten lokalen Server voraus, nutzt ausschließlich
1440×900 und schreibt nur in dieses Prototyp-Verzeichnis. Die externen Browserpfade
sind die bei dieser Validierung tatsächlich vorhandenen Installationen.

[Entscheidung und Messergebnisse](DESIGN-VALIDATION.md) ·
[Layout-Abhängigkeit und Lizenzen](vendor/README.md)
