# Eigene Hyperskill-Lösungen veröffentlichen

Verbindlicher Publisher-Vertrag: Schema 4.0 aus
[`myatlas/main`](https://github.com/Planton361/myatlas/blob/dc5870ebdd240f022292a8050a8600e6a661a67d/docs/contracts/hyperskill-code-archive-v4.md).
Der vorhandene Befehl archiviert eigenen Code. Er kompiliert, installiert und
führt weder Lösungen noch Academy-Builds aus. Neue Projekte benötigen keinen
Sprachadapter und keine Änderung an MyAtlas.

## Normalfall und Dry-Run

Im aktuellen offiziellen Repository mit Python 3.12:

```bash
python3.12 scripts/publish-hyperskill-project "/Pfad/zum/Academy-Projekt"
python3.12 scripts/publish-hyperskill-project "/Pfad/zum/Academy-Projekt" --dry-run
```

Die eindeutige Academy-Identität liefert die exakte positive ID. Die URL muss
exakt `https://hyperskill.org/projects/<ID>` sein: keine führenden Nullen,
Abschluss-Slashes, Querys oder Fragmente. Bei fehlender Identität beziehungsweise
fehlendem Titel fragt der Publisher interaktiv nach; widersprüchliche oder
manipulierte Metadaten werden abgewiesen. Titel und Code liefern niemals IDs.

Die Standardauswahl schlägt Dateien der eindeutig finalen `<Aufgabe>/task/src`
beziehungsweise `<Aufgabe>/task` vor. Bei mehreren Aufgaben wird nur ein eindeutig
zum Academy-Titel gehörender Ordner bevorzugt; andernfalls ist persönliche
Dateiauswahl erforderlich. Sichere UTF-8-Dateien werden unabhängig von ihrer
Endung als **Vorschlag mit Rolle `solution`** angezeigt. Der Eigentümer prüft
Pfade, Inhalte und Rollen vor der Veröffentlichung. Es gibt keine Erkennung von
Ressourcen anhand von Quellcode-Imports oder Literalen. Für Ressourcen oder eine
unpassende Aufgabenstruktur verwendet man die explizite Auswahl unten.

Frühere Aufgaben, bekannte Academy-Plattformtests, Aufgabenbeschreibungen,
IDE-/Git-/Build-/Abhängigkeitsdaten und generierte Dateien werden mit ihrem
genauen Pfad und Ausschlussgrund angezeigt. Binärdateien werden niemals
automatisch zu Code; sie erfordern eine explizite Ressourcenrolle. Unbekannte
Framework-Dateien sind kein Nachweis eigener Urheberschaft: bei Zweifeln die
explizite Auswahl verwenden. Die persönliche Prüfung bleibt erforderlich.

## Explizite universelle Auswahl mit `--files-from`

Eine reguläre UTF-8-JSON-Datei deklariert genaue POSIX-Pfade relativ zum **exakt
angegebenen Workspace-Verzeichnis**, ohne automatische Suche in übergeordneten
Academy-Verzeichnissen. Das Format hat genau `schema` und `files`; doppelte
JSON-Schlüssel werden abgewiesen. Mindestens eine Datei hat Rolle `solution`.

```json
{
  "schema": 1,
  "files": {
    "final/src/Main.kt": "solution",
    "helpers/process.py": "solution",
    "script.future": "solution",
    "program": "solution",
    "data/input.json": "resource",
    "assets/image.bin": "resource"
  }
}
```

Beispiel für ein Projekt ohne Academy-Metadaten; die beispielhafte ID 12345 ist
durch die eigene **exakte** Hyperskill-ID zu ersetzen:

```bash
python3.12 scripts/publish-hyperskill-project "/Pfad/zu/meinen/Dateien" \
  --files-from "/Pfad/zur/owner-selection.json" \
  --project-url "https://hyperskill.org/projects/12345" \
  --title "Mein Hyperskill-Projekt" --language kotlin --language python --dry-run
```

Nach erfolgreicher Prüfung denselben Aufruf ohne `--dry-run` ausführen.
`--language` ist optionale, wiederholbare beschreibende Metadaten; jede sichere
öffentliche Sprachbezeichnung ist zulässig, und das Feld darf ganz fehlen.
Es werden weder Syntax noch Ausführbarkeit überprüft. Die Auswahl enthält
Dateien, keine Globs, Verzeichnisse, absoluten Pfade oder Umbenennungen. Pfade
und Bytes bleiben erhalten, beispielsweise `solution/final/src/Main.kt`.
Binärdaten sind ausschließlich mit Rolle `resource` zulässig.

## Persönliche Prüfung und Zeiten

Vor jeder Veröffentlichung erfolgt ein Read-only-Dry-Run mit allen ausgewählten
und ausgeschlossenen Pfaden, Rollen und SHA-256-Hashes. Danach wird ein sauberer
isolierter Checkout des aktuellen kanonischen `main` erstellt. Der ursprüngliche
Checkout und Workspace bleiben unverändert, auch wenn sie lokale Änderungen
enthalten. Der Eigentümer gibt in einem interaktiven Terminal ein:

1. `COMPLETE <ID>`: persönliche Bestätigung von Abschluss und Urheberschaft der
   ausgewählten Lösung. Erst **nach dieser Eingabe** wird der aktuelle UTC-Instant
   als `confirmed_at` erfasst.
2. `PUBLISH <ID>`: Freigabe nach Anzeige des tatsächlichen vollständigen Git-Diffs.

Ein bekannter tatsächlicher historischer Abschlusszeitpunkt kann optional mit
`--completed-at "2026-10-01T12:00:00Z"` angegeben werden. Er darf nicht nach der
Bestätigung liegen. Ohne Angabe wird `completed_at` weggelassen; Dateizeit,
Git-Datum und Bestätigungszeit ersetzen niemals ein unbekanntes Abschlussdatum.
Ein Dry-Run-Zeitpunkt ist ausdrücklich nur Vorschau und keine Evidenz.

Der Publisher prüft nochmals unveränderte Quellbytes, Archivbytes, Git-Filter,
Commit-Inhalt und Pfadumfang. Er pusht einen neuen Branch und erstellt einen
Draft-PR. Er führt keinen Merge, Force-Push oder produktiven Deployment aus.
Codex darf die beiden persönlichen Eingaben für eine echte Veröffentlichung
nicht erzeugen. Automatische Tests verwenden ausschließlich synthetische
Workspaces, lokale Origins und gemockte GitHub-Aufrufe.

## Sicherheitsabbrüche und Wiederaufnahme

Symlinks (auch Eltern), Sonderdateien, unsichere relative Pfade, versteckte oder
private Namen, nicht normalisiertes Unicode, Case-Aliase, Secrets, falsche
Identitäten, unvollständige Inventare und Binärdaten mit Code-Rolle stoppen den
Vorgang. Gefundene Secret-Inhalte werden nicht ausgegeben. Secret-Erkennung ist
eine konservative Heuristik; persönliche Inhalts- und Eigentumsprüfung bleibt
erforderlich. Ein bereits archiviertes Projekt in Schema 2, 3 oder 4 wird nie
erneut veröffentlicht oder automatisch überschrieben.

Nach einem unterbrochenen Push oder fehlgeschlagenem `gh pr create` bleibt der
isolierte Review-Checkout samt `.hyperskill-publication.json` erhalten. Genau
diesen Checkout wiederaufnehmen:

```bash
python3.12 scripts/publish-hyperskill-project --resume "/angezeigter/Review-Checkout"
```

Der Commit, seine ursprüngliche Bestätigungszeit und die Archivbytes bleiben
unverändert. Der Publisher validiert Archiv, Herkunft, kanonisches `main`,
ursprünglichen Parent, exakten Diff und Remote-Branch erneut. Ohne bestehenden
PR fordert er erneut persönlich `COMPLETE <ID>` und `PUBLISH <ID>`; eine
erneute Bekräftigung überschreibt den ursprünglichen Bestätigungszeitpunkt nicht.
Ein identischer vorhandener Remote-Branch wird nicht erneut gepusht. Ein bereits
bestehender PR wird nur verlinkt. Änderungen oder konkurrierende Branches/PRs
erfordern manuelle Prüfung, ohne Force-Push oder zweite Veröffentlichung.

Ein erneuter normaler Aufruf erkennt den vorhandenen Branch für dieselbe ID.
Bei identischen Auswahlbytes, Rollen, Titel, Sprachmetadaten und historischem
Zeitpunkt liefert er den bestehenden PR-/Vergleichslink und Resume-Aufruf zurück.
Bei abweichenden Daten stoppt er. Der deterministische Branch
`publish/hyperskill-<ID>` verhindert auch konkurrierende zweite Remote-Branches.
Der Journalpfad gehört nur zum lokalen Review-Checkout, nicht zum Projektarchiv.

## Archiv, MyAtlas und nächste Phase

Neue Archive enthalten nur `projects/<ID>/.hyperskill-import.json`, `README.md`
und ausgewählte `solution/`-Dateien. Das Manifest inventarisiert jede Datei außer
sich selbst mit SHA-256 und Rolle; README hat Rolle `resource`. Alte Schema-2/3-
Archive bleiben unverändert. MyAtlas leitet Topics ausschließlich aus seinem
Katalog ab. Katalogfremde IDs bleiben `UNMAPPED` im separaten Abschlussregister,
ohne Topics, Katalogknoten, unabhängige Verifikationen oder Course-Abschlüsse.

Die Cross-Repository-CI verwendet Schema-4-fähiges MyAtlas `main` und prüft
alle Archiv-/Fortschritts-/Geometrie- und Browser-Gates ohne Deployment. Die
reparierte isolierte GitHub-Umgebung bleibt erhalten. Phase 3 darf auf den
vollständigen Manifesten einen atomaren, revisionsgebundenen validierten Index
aufbauen: exakte Git-Revision, Blob-Hashes, Rollen und Identitäten; atomarer
Pointer-Wechsel erst nach vollständiger Veröffentlichung, Last-known-good bei
Fehlern und keine doppelte Zählung. Hier wird noch kein produktiver Index erstellt.
