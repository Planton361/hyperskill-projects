# Kontrollierter Produktiv-Rollout — Phase 6

Stand: 12. Oktober 2026. **Keine Produktivfreigabe.** Dieser PR setzt keine
GitHub-Variablen, erstellt keinen Store und veröffentlicht keinen Pointer.
[Preflight](acceptance/phase6-preflight.json) enthält den vollständigen geprüften
Dateibestand einschließlich aller 22 SHA-256-Werte und Git-Blob-IDs.

## Geprüfte Voraussetzungen und Zustände

MyAtlas #9 wurde am `2026-10-12T11:07:04Z` als
`12377e3fac28817adcbdf2fca846828763c0dc99` gemergt. Projects #13 folgte am
`2026-10-12T11:35:11Z` als `e26dea5ff43d0f4404cbab4b25f60850b5d6cb8c`.
MyAtlas Main: [Read-only](https://github.com/Planton361/myatlas/actions/runs/38240595021),
[Pages](https://github.com/Planton361/myatlas/actions/runs/38240595010), beide grün.
Projects Main: [Publisher](https://github.com/Planton361/hyperskill-projects/actions/runs/38243602596),
[Archive](https://github.com/Planton361/hyperskill-projects/actions/runs/38243602586),
[Pages](https://github.com/Planton361/hyperskill-projects/actions/runs/38243602632),
[Integration](https://github.com/Planton361/hyperskill-projects/actions/runs/38243602969), alle grün.
Die isolierten Worktrees ändern keine bestehenden lokalen Arbeitsstände.

| Status | Nachweis |
| --- | --- |
| IMPLEMENTED | Bestehender universeller Publisher, Schema-2/3/4-Validator, deterministischer Index, append-only Store, deaktivierter Browser-Reader, Daten-CI |
| TESTED | Commitgebundener Preflight; unveränderte 113/229/380, 32 gelernt, 12 unabhängig verifiziert, Course-Records leer; synthetische Sicherheits-/Recovery-/Wachstumstests |
| PRODUCTION_VERIFIED | Obige Main-Checks; öffentlicher Pointer tatsächlich HTTP 404 aus Python und der öffentlichen MyAtlas-Origin in Chromium/WebKit |
| BLOCKED | Produktiver Payload-/Raw-GitHub-CORS-Nachweis vor Bootstrap; Branchschutz und Produktivaktivierung benötigen gesonderte Eigentümerfreigabe |

`portfolio-index-store` existiert derzeit nicht. `PROJECT_INDEX_ENABLED` und
`PROJECT_INDEX_BOOTSTRAP` sind nicht gesetzt. Fehlender Erstpointer ist ein
beobachteter Bootstrap-Zustand, kein erfolgreich validierter leerer Index.

## Branchschutz: konkrete administrative Freigabe erforderlich

Read-only REST-Prüfung: beide `main`-Branches haben `Branch not protected` (404),
keine wirksamen Branchregeln und keine Rulesets. Die vorhandene Anmeldung hat
Adminrechte; **es fehlt die ausdrückliche Erlaubnis, sie hierfür einzusetzen**.
Damit sind Required Checks derzeit CI-Konvention, keine erzwungene Merge-Sperre.

Nach separater Freigabe unter **Settings → Rules → Rulesets → New branch ruleset**:

1. Regel für `main`, Status **Active**, keine Bypass-Akteure; PR vor Merge
   verlangen. Force-Push und Löschen sperren, erforderliche Checks und aktuellen
   Branchstand verlangen. Bei einem alleinigen Eigentümer zunächst null fremde
   Approval-Reviews: ein verpflichtender PR erlaubt die persönliche Merge-Prüfung,
   eine erzwungene fremde Zustimmung benötigt tatsächlich einen zweiten Reviewer.
2. Projects: `Project acceptance`, `check`, `build` aus **GitHub Actions**.
   Oberfläche: `Hyperskill project checks / check` und
   `Legacy redirects and validated project index / build`. REST `check-runs`
   meldet die Jobkontexte **`check` und `build`**, App-ID `15368`.
   Keine einzeln übersprungenen `Full Pages compatibility (...)`-Matrixjobs als
   Required Checks eintragen. `Project acceptance` erzwingt sie vollständig für B/C.
3. MyAtlas: `check` (Read-only validation), `project-check`, `build` (vollständige
   Pages-/Release-/Browser-/Geometrieprüfung), zusätzlich `activation-check` aus
   dem kontrollierten Aktivierungs-Draft. Workflowname und Jobname in der UI
   prüfen; beim Check GitHub Actions als Herkunft auswählen.
4. Eigenes Ruleset mit exaktem Branch `portfolio-index-store`: **Restrict deletions**
   und **Block force pushes** aktivieren. Normale Brancherstellung und Fast-forward-
   Writes durch den bestehenden Deploy-Job zulassen. Keine PR-/Required-Check-
   oder Signaturpflicht auf diesen maschinellen Store legen. Kein neuer Token,
   kein pauschaler Admin-BYPASS. Regeln vor Bootstrap auch für den noch fehlenden
   Branch einrichten; nach Umsetzung REST-Wirksamkeit erneut kontrollieren.

[GitHub dokumentiert Required Checks und Herkunft](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)
sowie [Ruleset-Regeln](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets).
Administratorlöschung des gesamten Repositorys und Hosting-Ausfälle bleiben
außerhalb dieser Aufbewahrungsgarantie. Schutz konfigurieren heißt nicht testen:
seine tatsächliche Wirksamkeit muss nach autorisierter Einrichtung geprüft werden.

## Read-only Preflight und feste Identitäten

```bash
python3.12 -B scripts/preflight-project-index.py \
  --myatlas-root /isoliert/myatlas \
  --revision e26dea5ff43d0f4404cbab4b25f60850b5d6cb8c \
  --output /tmp/phase6-preflight.json
```

Der geprüfte Payload hat SHA-256
`49fa5bc1a8055c8e293bb90e6f44ddad1ccd742860fa4c8630525880812b989e`.
Validatorimplementierung: `5795c668c639e001fcef80c45f36794d0ca2a39b`, Version `1.0`.
Zwei Erzeugungen derselben Revision ergeben identische Bytes; ein unabhängiger
Validator prüft alle Archive, README/Manifest, Blob-IDs, Rollen und Code-Links.
Der Store-SHA ist **noch nicht vorhanden** und wird nicht erfunden. Nach Merge
weiterer Infrastruktur-PRs muss der Preflight mit dem dann aktuellen kanonischen
Main-SHA wiederholt werden; dieser alte Nachweis darf keinen neueren Pointer ersetzen.

Endpunkte und Schema bleiben [PROJECT-INDEX.md](PROJECT-INDEX.md):
`https://planton361.github.io/hyperskill-projects/portfolio/current.json` und
`https://raw.githubusercontent.com/Planton361/hyperskill-projects/<STORE_SHA>/portfolio/revisions/<SOURCE_SHA>/index.json`.
Source-SHA bindet Archive/Code-Links; Store-SHA bindet den gespeicherten Index.
Beide sind vollständige unterschiedliche Commits. Pointerfelder bleiben exakt
`schema`, `repository`, `revision`, `index_url`, `index_sha256`.

## Spätere Freigabereihenfolge — jetzt nicht ausführen

1. Producer-Preflight-PR prüfen und manuell mergen; Main-CI abwarten. MyAtlas-
   Aktivierungs-PR bleibt Draft. Schutzregeln nach eigener Adminfreigabe einrichten.
2. Aktuelles Projects Main fixieren, Read-only-Preflight neu ausführen und drei
   reale Abschlüsse, 22 Dateihashes, Indexdigest und fehlenden Erststore prüfen.
3. **Separate Eigentümerfreigabe für Bootstrap einholen.** Erst dann Projects-
   Repositoryvariablen `PROJECT_INDEX_ENABLED=true`, initial einmalig
   `PROJECT_INDEX_BOOTSTRAP=true` setzen und den bestehenden
   `pages-redirects.yml`-Workflow manuell auf aktuellem `main` starten.
4. Genau dieser bestehende Deploy-Job darf den Store mit normalem Fast-forward
   schreiben. Vollständige Validierung → langlebiger Store-Payload → tatsächliches
   anonymes HTTPS + Digest → atomarer lokaler Pointer → sämtliche Legacy-Redirects
   und alte Payloads → letzter Main-/Pointer-/Payload-Guard → bestehendes Pages-
   Deployment. Keine weltweit atomare CDN-Verteilung behaupten.
5. Nach erfolgreichem Erstlauf Bootstrap sofort wieder deaktivieren. Enabled
   bleibt erst nach dieser Freigabe gesetzt. Store-Commit, Source-Commit,
   Public-Pointer und Digest protokollieren.
6. Aus dem überprüften MyAtlas-Aktivierungs-Draft den echten Read-only-Smoke
   **ohne `--allow-missing`** ausführen. Python, Chromium und WebKit müssen dasselbe
   Paar bestätigen. Re-run des Aktivierungs-PRs verlangt diesen Nachweis ebenfalls.
7. Erst nach dessen Erfolg und separater Eigentümerfreigabe Aktivierungs-Draft
   reviewbereit machen und manuell mergen. Eine einmalige geprüfte MyAtlas-
   Release-Auslieferung aktiviert die Darstellung; spätere Datenimporte benötigen
   keinen erneuten Anwendungsbuild.

## Recovery, Rollback und täglicher Betrieb

Vor Aktivierung funktioniert der bisherige statische Sync weiter. Bei einem
fehlenden/ungültigen aktivierten Index bleibt der Browser beim letzten komplett
validierten Snapshot; ohne Cache beim statischen Fallback. Eine fehlgeschlagene
Gesundheitsprüfung meldet Blockierung, keinen angeblichen leeren Erfolg.

Abbruch vor Store-Push: nichts publiziert. Abbruch nach Push: immutable Daten
vorhanden, alter Pointer bleibt gültig. Aktuelles Main erneut prüfen und denselben
Workflow wiederholen; kein Force-Push. Ein beschädigter Pointer benötigt die
persönlich geprüfte `recovery_pointer`-Eingabe des bestehenden Workflows und
vollständige Prüfung gegen erhaltene Git-Historie. Ein beschädigter Store ist
kein Bootstrapfall. Niemals Store resetten oder Pointer mit null Projekten ersetzen.

Reader-Rollback: reviewter MyAtlas-PR entfernt ausschließlich die additive
Aktivierungsfreigabe, führt dieselben vollständigen Release-/Browser-/Geometrie-
Gates aus und stellt den originalen deaktivierten Fallback wieder bereit.
**Producer Enabled nicht einfach deaktivieren**: dessen Guard verweigert
Redirect-only-Deployment, sobald ein Store/Pointer existiert. Store und alte
immutable URLs bleiben erhalten; Datenkorrekturen sind neue überprüfte Commits.

Normalablauf nach Freigabe: eigene Lösung → universeller Publisher → persönlich
`COMPLETE <ID>` und `PUBLISH <ID>` → Draft-PR → manuelle Merge-Prüfung → Klasse-A-
Archiv/Index/Reader-Vertragschecks → Producerindex → Browser-Refresh.
KNOWN/KNOWN_EMPTY/UNKNOWN/UNMAPPED stammen ausschließlich aus dem Atlas-Katalog.
Projektcode erzeugt weder Verifikationen noch Course-Abschlüsse. B/C behalten
vollständige sechs Browser-/Geometrieszenarien; unabhängiger LeetCode-Netzfehler
ist Anwendungsdiagnose, keine ungültige Codeauswahl.

## Raycast-/Codex-Snippet

```text
Veröffentliche meine eigene Hyperskill-Lösung aus "<absoluter Projektpfad>"
mit dem bestehenden python3.12 scripts/publish-hyperskill-project.
Prüfe kanonisches main und mache zuerst den read-only Dry-Run.
Bei unklarer Identität/Dateiauswahl stoppe und bereite --files-from zur
persönlichen Prüfung vor. Zeige alle Pfade, Rollen, Hashes und den Git-Diff.
COMPLETE <ID> und PUBLISH <ID> gebe ausschließlich ich persönlich interaktiv ein.
Erstelle einen Draft-PR oder liefere den vorhandenen Resume-/PR-Link.
Kein Code ausführen, kein Auto-Merge, keine GitHub-Variablen ändern.
STOPP vor Merge.
```

Beispiele und Auswahlformat: [PUBLISHING.md](PUBLISHING.md).
Phase 7 übernimmt ausschließlich den separat freigegebenen echten Bootstrap,
HTTPS-/CORS-Abnahme, kontrollierte Readerfreigabe und finale öffentliche Abnahme.
