# Projekt-Datenprüfungen und Systemgesundheit — Phase 5

Der Indexvertrag bleibt unverändert. Der produktive Index und der Browser-Reader
bleiben deaktiviert; diese Änderung setzt keine GitHub-Variable und deployt nichts.

## Änderungsklassen und verpflichtende Checks

| Klasse | Exakte Git-Änderungsmenge | Pflicht |
| --- | --- | --- |
| A | Nur `A`-Einträge regulärer Git-Blobs unter neuen kanonischen `projects/<ID>/`-Verzeichnissen; Schema 4; das ganze Verzeichnis fehlt im Vergleichsstand | Gesamter Archivvalidator, Index zweimal bytegleich, unabhängiger Indexvalidator, gemergter Phase-4-Browservertrag und akzeptierte Analytics mit Katalogbindung |
| B | Bestehende Archive, Löschungen, Umbenennungen, Legacy-Erweiterungen, Scripts, Actions, Workflows, Verträge, unbekannte/gemischte Änderungen oder fehlender Vergleich | A-Prüfungen plus Importer-/Publisher-/Index-Unit-Tests und alle sechs vollständigen MyAtlas-Cross-Repository-Szenarien einschließlich Chromium, WebKit, Release und Geometrie |
| C | Manueller Lauf oder wöchentlicher Gesundheitscheck | Vollständige B-Abnahme, unabhängig vom letzten Projektimport |

PRs vergleichen die Merge-Base der Event-Base-SHA mit der tatsächlich geprüften
Merge-SHA. Pushes vergleichen die Event-`before`-SHA direkt mit `github.sha`;
nicht lineare/fehlende Vergleiche bekommen B. Renames werden als Löschen/Anlegen
behandelt. Keine API-Dateiliste, Pfadfilter oder abgeschnittene Dateimenge dient
als Entscheidung. Die Policy kommt aus dem **Base-Commit**, nicht aus einem
geänderten Kandidatenscript; bei ihrer erstmaligen Installation gilt B.

Alle vier Workflows starten ohne PR-Pfadfilter. Der stabile Abschlusscheck
`Project acceptance` läuft auch bei Fehlern: Policy und Datenvertrag müssen
bestehen; nur bei A darf die Browsermatrix `skipped` sein. Bei B/C müssen alle
Matrixszenarien bestehen. GitHub-Branchschutz muss diesen Abschlusscheck und die
Archiv-/Pages-Artefaktchecks verlangen; bisher einzeln erforderliche Browserjobs
sind bei der späteren Freigabe durch den Abschlusscheck zu ersetzen. Diese Phase
ändert keine Repository-Settings. Workflow-/Actionänderungen selbst bleiben
reviewpflichtige Infrastruktur; Repositorybetreiber und GitHub-Workflowcode
bilden die CI-Vertrauensgrenze.

Es gibt weder neue Schreibrechte noch Tokens. Nur der vorhandene Pages-Deploy-Job
kann Pages schreiben; Store-/Pointer-/Main-Guards und vollständige Legacy-Redirects
bleiben erhalten. Archive werden ausschließlich als Git-Blobs gelesen; niemals
Builds oder importierter Code ausgeführt. COMPLETE, PUBLISH und Merge bleiben
persönliche Freigaben.

## Datenvertrag ohne Anwendungsbuild

`python3.12 -B scripts/test-project-data.py --myatlas-root /Pfad/myatlas --revision <vollständige SHA>`
prüft die gesamte Revision, reproduziert den Index zweimal und delegiert die
Wire-Prüfung direkt an den gemergten Phase-4-Reader. Der Mindeststand ist MyAtlas
`266c1195d5552753f3a63246ec1591ccc5c2b332`, kein alter Bootstrap-Fallback.
Die dynamische Projektion nutzt die unveränderte `ProgressAnalytics`; sie wird
gegen den bisherigen unabhängigen Git-Scanner/Serializer verglichen. Vollständige
Register ersetzen statische Evidenz, IDs zählen einmal. UNKNOWN/UNMAPPED erfinden
keine Topics; Verifikationen und Course-Daten müssen identisch bleiben.
Katalogrevision und tatsächliche Katalog-/Scope-Blob-Digests stehen im Bericht.

## Übergang, Normalbetrieb und Diagnose

**Heute deaktiviert:** Die bestehende tägliche MyAtlas-Synchronisierung bleibt
aktiv und baut geänderte statische Evidenz vollständig. Ein Archiv-PR benötigt
bereits nur Datenprüfungen; der nachgelagerte öffentliche statische Build bleibt
bis zur bewiesenen Aktivierung erforderlich.

**Später aktiviert:** Owner bestätigt COMPLETE/PUBLISH → Draft-PR → Datenchecks →
persönlicher Merge → vorhandener Index-Pages-Workflow → validierter Pointer →
Browser-Refresh. Kein neuer MyAtlas-App-Build. Erst die passende ausgelieferte,
reviewte MyAtlas-Konfiguration zusammen mit gültigem aktuellen Index berechtigt
den täglichen Sync, diesen Build zu überspringen. Flags allein genügen nicht.

**Fehler:** Archiv-/Hashfehler blockieren den Projektmerge. Ein Browser-/LeetCode-
Netzwerkfehler der B/C-Matrix ist ein Anwendungs-/Gesundheitsfehler, keine Aussage
über ungültigen Lösungscode. Bei ungültigem/nicht erreichbarem/stalem produktiven
Index stoppt die Daten-Sync-Meldung als blockiert; Browser behalten last-known-good.
Keine Meldung „aktuell“, kein leerer Fallback, kein neuer Pointer durch diese Tests.
Producer-Fehler zuerst anhand `PROJECT-INDEX.md` diagnostizieren, aktuellen Lauf
wiederholen, dann Browser erneut aktivieren. Niemals Store resetten oder Guards
abschalten. Policy- und Datenberichte nennen Commit, IDs, Digest, ausgelassene
Browserprüfung und nächsten Bedienungsschritt; vollständige Matrixartefakte
enthalten die genaue fehlgeschlagene Anwendungsprüfung.

## Übergabe an Phase 6

Beide Phase-5-PRs sind unabhängig mergebar: Projects verwendet bereits gemergtes
MyAtlas Phase 4; empfohlen zuerst Projects, anschließend MyAtlas. In Phase 6:
Branchschutz/erforderliche Checks prüfen, End-to-End mit lokalem Index abnehmen,
separat die versionierte MyAtlas-Aktivierung und ihre Release-Guards reviewen,
ersten Producer-Bootstrap manuell freigeben, Endpunkte/Digests/Storeaufbewahrung
prüfen und erst danach den dynamischen Betrieb freigeben. Diese Phase aktiviert
weder `PROJECT_INDEX_ENABLED` noch `PROJECT_INDEX_BOOTSTRAP`.

Hosting-/LeetCode-Netzwerke bleiben externe Abhängigkeiten. Eine fehlgeschlagene
Gesundheitsprüfung bleibt sichtbar und wird nicht auf einen Projektimport
umgedeutet; eine erneute Infrastrukturänderung bleibt trotzdem voll abnahmepflichtig.
