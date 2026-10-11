# Phase 5 — Daten-CI-Abnahme

Kanonische Basis: Projects `5795c668c639e001fcef80c45f36794d0ca2a39b`,
MyAtlas `266c1195d5552753f3a63246ec1591ccc5c2b332`. PR #12 und MyAtlas #8
waren gemergt, Main-CI und MyAtlas Pages grün. Indexvariablen nicht gesetzt.

Tatsächlich lokal ausgeführt (Python 3.12):

| Prüfung | Ergebnis |
| --- | --- |
| Import, Publish, Adapter, isolierter GitHub-Kontext, Schema-4-/Reader-Parität, Index/Retention/Pages | 99 Tests grün |
| Git-Änderungsklassen einschließlich PR-Merge-Base, Push-before, bestehender Evidenz, gemischter Scripts/Workflows, Symlink/Gitlink und Workflow-Gates | 7 Tests grün |
| Nicht reproduzierbare/zu große Indexbytes und manipuliertes committetes Archiv im Datenpfad | 2 Tests grün |
| 30 nacheinander versionierte synthetische Importer-Archive, Java/Python/Kotlin/JS/gemischt/unbekannte/endungslose Quellen und binäre Ressourcen | Jeder Commit A für PR und Push, volle Datenabnahme grün, genau 3 → 33 Projekte |
| MyAtlas Readervertrag | Alle 45 Tests grün, zusätzlich alle 45 mit erweitertem synthetischem Archivstand |
| MyAtlas Sync/Indexgesundheit | 41 Tests grün |

Der Dreißiger-Test läuft ohne Browserinstallation, Anwendungsbuild, Compiler,
Academy-Build oder Ausführung von Lösungscode. Pro Commit werden sämtliche Archive,
Index zweimal und unabhängiger Indexvalidator geprüft. Der echte Phase-4-Reader
und die unveränderte Analytics stimmen mit der unabhängigen bisherigen Git-
Projektion überein. Nur der bekannte Katalogeintrag kann Topics beitragen; alle
weiteren UNKNOWN/UNMAPPED-Archive ändern diese nicht. Verifikationen bleiben zwölf,
Course-Records leer, keine echten weiteren Abschlüsse in diesem Repository.

Beispiel dieses temporären Testlaufs (keine öffentliche Evidenz): letzte Quell-SHA
`806df34d2e06c5a0fe2dc4918339e1a13e1f9a6b`, reproduzierbare Index-SHA-256
`7fbd3f467f355010176be48536f9080d845951101e033e2527493f8fbb6fe1fd`.
Git-Fixture-Commits sind zeitabhängig; reproduzierbar sind die Indexbytes derselben
exakt ausgewählten Revision, nicht Git-SHAs verschiedener Fixtureläufe.

## Unveränderte Baseline

Alle 22 Archivdateien stimmen bytegenau mit MyAtlas
`docs/contracts/hyperskill-baseline-v1.json` überein. SHA-256 der sortierten
kompakten Hashmap plus LF:
`6045f7b64cb92af554f575bde4a346adeadbe5f7b384d7a2ab38a09f7c1e9bf2`.
Semantische Projektion ohne `source`, kompakte sortierte JSON-Darstellung ohne LF:
`1a86243ba9c3581c709417281cd18498bb72b5b0bfc23a91baa6bcffa0086878`.
Reale IDs 113/229/380, 32 gelernt, zwölf unabhängig verifiziert, Course-Records leer.
Alle fünf akzeptierten Geometrie-Fingerprints bleiben verpflichtende unveränderte
Assertions der vollständigen Browsermatrix. Keine Änderungen an echten Archiven.

## Vollständige CI und Diagnose

Der erste PR-Lauf `38183102218` führte konservativ B aus. Der Datenpfad einschließlich
30 Importen war grün; fünf vollständige Szenarien scheiterten an einem bestehenden
Phase-4-Reader-Fixturefehler (`4 !== 3`, `33 !== 32`), nicht an Archivdaten. MyAtlas
Draft-PR #9 behebt die Eingabetrennung unter Erhaltung aller Sicherheits- und
Baseline-Assertions. Der Growth-Runner gibt fehlgeschlagene Anwendungsausgaben
jetzt vollständig aus statt nur die letzten 800 Zeichen.

Der versionierte `review_commit` pinnt den MyAtlas-Draft exakt für die vollständige
PR-Reviewmatrix. Produktive/Health-Läufe verlangen seinen Merge; kein stiller
Fallback auf altes MyAtlas. **Merge-Reihenfolge: MyAtlas #9, dann Projects #13.**
Die endgültigen Lauf-SHAs und alle sechs Szenarien werden im Draft-PR #13 verlinkt.
Unvollständige oder fehlgeschlagene Abnahmen gelten nicht als bestanden.

Keine Pages-Schreibrechte außerhalb des bestehenden Deploymentjobs, keine Tokens,
keine Indexaktivierung, kein produktiver Pointer-Wechsel, kein Deployment/Merge.
Normalablauf, Blocker, Branchschutz-Review und Phase-6-Übergabe:
[PROJECT-DATA-CI.md](PROJECT-DATA-CI.md).

Weitere Fälle desselben Fixturefehlers wurden separat diagnostiziert und korrigiert:
Baseline-Semantik muss an ihrer unveränderlichen Archivrevision geprüft werden,
nicht am um UNKNOWN/UNMAPPED erweiterten Kandidaten. Die 22 aktuellen Hashes und
unabhängigen Verifikations-/Course-Nachweise bleiben zusätzliche Pflichtassertions.
Der Browser-Offline-Fallback prüft das ganze Universalregister einschließlich
UNMAPPED. Der Review-Pin enthält alle drei hierfür relevanten Fixturedateien und
erkennt bytegleiche Squash-/Rebase-Merges, ohne alten inkompatiblen Fallback.
Überholte Matrixläufe mit dem bereits diagnostizierten alten Fixturestand wurden
abgebrochen; die neueste Revision muss wieder alle sechs Szenarien bestehen.

Read-only GitHub-Prüfung: Projects `main` besitzt derzeit weder klassischen
Branchschutz noch wirksame Rulesets. Vor normalen Projektmerges sind die stabilen
Abschluss-/Archiv-/Artefaktchecks daher als Required Checks einzurichten; solange
sie nicht technisch erzwungen werden, muss der Eigentümer alle grünen Checks
persönlich prüfen. Diese Phase ändert keine Repository-Settings.
