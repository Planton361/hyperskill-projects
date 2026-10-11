# Revisionsgebundener Projektindex — Phase 3

## Vertragsauslegung vor der Implementierung

Grundlage ist der unveränderte [MyAtlas-Indexvertrag 1.0](https://github.com/Planton361/myatlas/blob/dc5870ebdd240f022292a8050a8600e6a661a67d/docs/contracts/hyperskill-project-index-v1.md).
Er definiert alle äußeren Felder, lässt jedoch die inneren Namen von `validator`
und die Identifizierung der README-Attestation für 113 offen. Hier werden diese
als `validator.version`, `validator.implementation_revision` und optionales
`manifest.attestation` (ebenfalls `path/git_blob/sha256`) konkretisiert.
Dateipfade sind repository-relative POSIX-Pfade; `archive_path` ist das
Archivverzeichnis. Keine zusätzlichen Fortschritts- oder Katalogfelder.

Pages-Artefakte sind vollständige Website-Snapshots, keine dauerhafte
append-only Datenbank. Allein das Hochladen des neuesten Payloads beweist daher
keine Aufbewahrung alter URLs. Die einfache Alternative nutzt ausschließlich
dieses Repository: ein append-only Git-Branch `portfolio-index-store` enthält
`portfolio/revisions/<Quell-SHA>/index.json`. Jeder neue Store-Commit übernimmt
alle vorherigen Payloads bytegleich. Normale Fast-forward-Pushes dienen als
Compare-and-swap; kein Force-Push. Frühere Store-Commits bleiben erreichbar.

Der Pointer hat exakt `schema`, `repository`, `revision`, `index_url`,
`index_sha256`. `index_url` ist
`https://raw.githubusercontent.com/Planton361/hyperskill-projects/<Store-Commit>/portfolio/revisions/<Quell-SHA>/index.json`.
Die zwei SHA-Werte haben unterschiedliche Aufgaben: Der geprüfte Quell-Commit
identifiziert die Archive, der immutable Store-Commit deren erzeugten Payload.
Der Quell-SHA ist auch im URL-Pfad und Payload enthalten. Dies konkretisiert die
vertragliche revisionsspezifische Hosting-URL; Code-URLs verwenden ausschließlich
den Quell-SHA. Es gibt keine branchbasierten URLs. Pages spiegelt alle bisherigen
Payloads zusätzlich unter denselben `portfolio/revisions/...`-Pfaden, während
der Pointer direkt auf den vorab geprüften Git-Payload zeigt.

Es wird keine atomare Verteilung über alle Pages/CDN-Knoten behauptet. Ein alter
oder neuer Pointer ist jeweils ein vollständiges JSON-Dokument mit Digest und
immutable Ziel; ein Leser muss das Paar prüfen und bei Fehlern last-known-good
behalten. Der bestehende Pages-Deployment-Job bleibt der einzige Pages-Schreiber.
Sein GitHub-Token erhält zusätzlich nur `contents: write` für den Store-Branch
im selben Repository. Kein persönlicher Token, kein Cross-Repository-Schreiben.

Produktiver Index, Pointer-Wechsel und Deployment werden in diesem Auftrag
nicht ausgelöst. Die spätere Aktivierung benötigt die Repositoryvariable
`PROJECT_INDEX_ENABLED=true`; das erste Anlegen zusätzlich die ausdrückliche
Bootstrap-Freigabe. Fehlender/beschädigter Pointer bei normalem Betrieb stoppt.

## Daten und Betrieb

Generator und unabhängiger Validator benötigen eine explizite vollständige
40-stellige Commit-SHA, keinen Branch und kein implizites `GITHUB_SHA`:

```bash
revision=$(git rev-parse HEAD)
python3.12 -B scripts/build-project-index.py --revision "$revision" > /tmp/index.json
python3.12 -B scripts/validate-project-index.py /tmp/index.json --revision "$revision"
```

Der Generator liest ausschließlich Git-Blobs. Er validiert zuerst die gesamte
Revision mit dem bestehenden Archivvalidator und prüft, dass seine ausführende
Validatorimplementierung bytegleich zu deren committeter Provenienz ist.
`implementation_revision` ist der letzte Commit der drei Implementierungsdateien
`project_index.py`, `validate-project-exports.py`, `export_metadata.py` innerhalb
der gewählten Quellrevision. Validatorversion ist `1.0`. Ein kompatibler späterer
Validator darf alte Payloads erneut prüfen, aber nicht umschreiben. Eine andere
Implementierung für dieselbe gespeicherte Revision erzeugt keinen Ersatz:
abweichende Bytes werden abgewiesen und benötigen eine neue überprüfte Revision.

Der Payload enthält exakt:

```text
schema: 1
kind: hyperskill-project-index
repository: Planton361/hyperskill-projects
revision: <Quell-SHA>
validator: {version: "1.0", implementation_revision: <Implementierungs-SHA>}
projects: [aufsteigend nach exakter ID]
```

Ein Projekteintrag enthält `project_id`, `project_url`, `title`, optional
`languages`, `archive_schema`, `archive_path`, `manifest`, `completion`, `files`
und `evidence_id: hyperskill:<ID>`. `manifest` referenziert den vollständigen
repository-relativen Manifestpfad, Git-Blob-ID und SHA-256. Nur bei der bekannten
README-Attestation von 113 enthält es zusätzlich `attestation` mit denselben
drei Feldern für README. Die bereits akzeptierte Beobachtung
`2026-10-08T00:00:00Z` bleibt eine Beobachtung, kein tatsächliches Abschlussdatum.
Schema 2/3 bewahren `observed_at`; Schema 4 bewahrt `confirmed_at` und nur das
tatsächlich vorhandene optionale `completed_at`.

`files` inventarisiert **alle** Archivblobs einschließlich README und Manifest.
Jeder Eintrag enthält `path`, `git_blob`, `sha256`, `role`; nur `solution`-Einträge
haben `code_url`. Das Manifest ist `metadata`, README ist `resource`. Schema-4-
Rollen kommen aus dem validierten Manifest; Legacy-Quellpfade werden gemäß ihrem
bestehenden Sprachvertrag eingeordnet, Build-/Wrapper-Dateien bleiben Ressourcen.
Keine Builddatei wird interpretiert. Alle Code-URLs entstehen aus dem festen
GitHub-Repository, Quell-SHA und pro Segment percent-encodiertem Pfad.

Serialisierung: UTF-8, sortierte JSON-Schlüssel, kompakte Separatoren, ein
abschließendes LF, keine Erzeugungszeit. Dieselbe Revision mit ihrer committeten
Implementierung ergibt exakt dieselben Bytes. Der zweite, separate Validator
prüft gegen die vollständige Git-Inventarliste, die validierten originalen
Metadaten, Blob-IDs, SHA-256, Rollen und URLs; er ruft nicht den Generator auf.
Ein Projektindex enthält keinerlei Topic-, Stage-, Verifikations- oder
Course-Abschlussfelder und kennt den Atlas-Katalog nicht.

## Automatischer Ablauf nach gesonderter Freigabe

Der bestehende Workflow `pages-redirects.yml` testet auch Pull Requests, dort
immer read-only und ohne Deploy-Job. Nach Merge validiert der Build-Job die
ausgewählte Revision zweimal und vergleicht die Bytes; archiviert wird ein
prüfbarer CI-Kandidat. Der bestehende Deploy-Job fixiert dieselbe SHA und prüft
live `origin/main`. Alle Pages-Läufe teilen eine Concurrency-Gruppe mit
`cancel-in-progress: false`; ältere wartende Läufe scheitern am Main-SHA-Check.
[GitHub dokumentiert](https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments/control-deployments)
die Serialisierung über Concurrency; Reihenfolge wird zusätzlich durch die
expliziten SHA-, Ancestry- und Pointer-Prüfungen gesichert.

Nach Aktivierung werden nacheinander ausgeführt:

1. Archive und neuer Payload vollständig prüfen; bisherigen öffentlichen
   Pointer samt Digest und Ziel prüfen. Fehlender Pointer ist ein Fehler.
2. Alle Store-Payloads prüfen; alle Quellrevisionen müssen Vorfahren der neuen
   Main-Revision sein. Alte Bytes vollständig in den neuen Store-Commit übernehmen.
3. Store-Commit normal fast-forward pushen. Ein konkurrierender Branch-Update
   scheitert am Compare-and-swap beziehungsweise am normalen Git-Push.
4. Payload an seiner **commitgebundenen Raw-GitHub-URL** tatsächlich per HTTPS
   abrufen; exakte Bytes, SHA-256 und vollständigen Index nochmals prüfen.
   HTTP-Fehler, Weiterleitungen oder falsche Bytes verhindern jeden Pointer-Wechsel.
5. Alten Pointer erneut vergleichen. Erst dann den Kandidatenpointer zuletzt
   mittels Rename im frischen lokalen Staging-Verzeichnis schreiben.
6. Vollständiges Pages-Artefakt aus allen alten/neuen Payloads, Pointer und den
   sieben bytegleichen Legacy-Redirects bauen und erneut vollständig prüfen.
7. Unmittelbar vor dem vorhandenen `deploy-pages` Main-SHA, alten Pointer,
   Kandidatendigest und erreichbares immutable Ziel nochmals prüfen.

Keine CI-Artifacts mit zeitlich begrenzter Aufbewahrung dienen als dauerhafte
Quelle. Auch nach vollständigem Ersatz eines Pages-Artefakts enthält dessen
Nachfolger alle bisherigen revisionsgebundenen Pfade. Zusätzlich bleibt jeder
alte Raw-GitHub-Link durch unveränderte, im Store-Branch verankerte Git-Historie
erreichbar. Es gibt keine automatische Bereinigung dieser Historie.
Aufbewahrung gilt innerhalb des vertrauenswürdigen Repositorybetriebs; ein
Administrator kann Repository/Branch löschen oder Git-Historie beschädigen.
Die Freigabe sollte Force-Push und Löschen des Store-Branches verbieten.

Pages ist kein verteilter Compare-and-swap-Datendienst. Der einzelne CI-Prozess
serialisiert Updates und liefert vollständige Snapshots; CDN-Verfügbarkeit und
weltweit gleichzeitige Sichtbarkeit bleiben Hosting-Grenzen. Ein gültiger alter
Pointer bleibt sicher lesbar, da sein Ziel nicht von der Pages-Ersetzung abhängt.
Diese Grenzen werden nicht als stärkere Atomizitätsgarantie ausgegeben.
Nur der bereits vorhandene Deploy-Job erhält `pages: write`/`id-token: write`.
Die [GitHub-Pages-Dokumentation](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)
beschreibt diesen Artifact-/Deploy-Mechanismus. Kein zweiter Workflow deployt.

## Fehler, Bootstrap und Wiederherstellung

Ohne Aktivierung bleiben die bisherigen Redirects erhalten; der Build erzeugt
nur den CI-Indexkandidaten. Sollte bereits Git-Store-Historie oder ein öffentlicher Pointer vorhanden
sein, verweigert auch dieser Modus ein Redirect-only-Deployment, damit ein
versehentliches Deaktivieren niemals alte Indexdateien entfernt.

Für die spätere erste Freigabe setzt der Eigentümer `PROJECT_INDEX_ENABLED=true`
und einmalig `PROJECT_INDEX_BOOTSTRAP=true`. Bootstrap erlaubt ausschließlich
einen fehlenden ersten Pointer mit leerem Store oder derselben einzigen
Revision nach unterbrochener Erstbereitstellung. Danach Bootstrap deaktivieren.
Ein beschädigter Pointer wird nie als leerer Erststand interpretiert.

Bei Abbruch vor dem Store-Push bleibt alles unverändert. Bei Abbruch nach dem
Push ist nur ein neuer immutable Payload gespeichert; der öffentliche Pointer
bleibt alt. Wiederholen desselben Laufs verwendet denselben Store-Commit und
dieselben Bytes, ohne zweite Revision oder Force-Push. Bei neuerem Main muss
stattdessen der aktuelle Main-Lauf starten. Ein fehlgeschlagener HTTP-/Hash-Check
stoppt vor `deploy-pages`. Ein Pages-Ausfall bleibt ein Hosting-Ausfall, kein
gültiger leerer Index.

Bei fehlendem/beschädigtem Pointer im laufenden Betrieb stoppt der Workflow.
Der Eigentümer startet nach Prüfung **denselben** Pages-Workflow per
`workflow_dispatch` auf aktuellem `main`, mit dem optionalen Eingabefeld
`recovery_pointer`: JSON des letzten gültigen Pointers aus bekanntem Artefakt
oder Cache. Der Workflow normalisiert es mit derselben kanonischen Serialisierung
(doppelte Schlüssel werden abgewiesen). Dieser wird
vollständig gegen seine tatsächlich erreichbare immutable URL, Hash und den
validierten Git-Store geprüft. Erst diese ausdrückliche Freigabe erlaubt das
Ersetzen eines fehlenden/beschädigten Live-Pointers. Die letzten Guards pinnen
auch dessen tatsächlich vorgefundene beschädigte Bytes; parallele Änderungen
stoppen weiterhin. Veröffentlicht wird ein komplett geprüftes aktuelles
Main-Artefakt mit sämtlicher Historie, kein leerer oder teilweise alter Stand.
Lokaler vorbereitender CLI-Vertrag ist `--recovery-pointer <regular-file>`;
diesen niemals ohne persönliche Review automatisieren. Kein automatischer Reset
auf null Projekte und keine automatische Umdeutung eines kaputten Zustands.
Ist der Store beschädigt oder
fehlt Historie, zunächst aus der bekannten Git-Historie wiederherstellen und
alle alten Payloads unabhängig prüfen; niemals dessen Branch force-pushen.
Nach einer fehlgeschlagenen Plattformverteilung kann ein gültiger alter oder
neuer Pointer sichtbar sein; beide müssen gegen ihr immutable Ziel geprüft werden.

## Tests und Übergabe an Phase 4

```bash
python3.12 -B -m unittest scripts.tests.test_project_index
```

Alle neuen Archivfixtures sind synthetisch und versioniert in temporären
Git-Repositories. Store-Pushes gehen ausschließlich an lokale Bare-Repositories;
HTTP-Publikation wird synthetisch modelliert. Ein zusätzlicher lokaler HTTP-Server
prüft die alte Payload-URL nach drei vollständig ersetzten Pages-Snapshots.
Tests decken Legacy 113/229/380, universelle und katalogfremde IDs, gemischte
Sprachen, unbekannte/endungslose Dateien, Hash-/Blob-Reproduzierbarkeit,
Manifest/README-Inventare, manipulierte Evidenz, Symlinks, falsche Origins und
Git-Objekte, unterbrochene Builds, konkurrierende Git-Pushes, stale Läufe,
kaputte Pointer/Store/Hashes, Redirects und letzte Deployment-Guards ab.
Die echten Archive werden separat read-only gegen die 22 Baseline-Hashes geprüft.
Die bestehende vollständige Cross-Repository-Akzeptanz bleibt unverändert aktiv.

Phase 4 liest ausschließlich den erlaubten HTTPS-Pointer-Endpunkt, validiert
alle fünf Pointerfelder, lädt nur dessen erlaubte immutable URL und prüft Digest,
Schema, Revision, komplette Identitäten/Inventare und commitgebundene Code-URLs.
Erst danach wird ein kompletter Snapshot installiert. Bei jeder Störung bleibt
last-known-good; ohne Cache bleibt der akzeptierte statische Stand erhalten.

Abschlüsse werden mit `hyperskill:<ID>` dedupliziert und ersetzen die bisherige
externe Evidenz als einen vollständigen Snapshot. Statische und dynamische
Evidenz dürfen niemals addiert werden. Topic-Zuordnung entsteht ausschließlich
aus dem vertrauenswürdigen MyAtlas-Katalog mit dessen Revision/Digest; nur
kataloggebundene Zeilen gehen in die akzeptierte Analytics. Katalogfremde IDs
bleiben im separaten Abschlussregister. Verifikationen und Course-Abschlüsse
bleiben unabhängige Quellen. Phase 3 ändert weder Loader noch Frontend.
