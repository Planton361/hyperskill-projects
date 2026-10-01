# Hyperskill projects

Abgeschlossene Lernprojekte, nach Sprache geordnet. Jedes exportierte Projekt hat
einen eigenen Build und kann separat in IntelliJ geöffnet werden.

## Projekte

Die Projekte liegen unter `java/`, später auch unter `kotlin/` und `python/`.
Die jeweilige Projekt-README enthält Build- und Startbefehle.

## Import

Voraussetzungen: Linux, Python 3.10+, Git. Zum Bauen: ein JDK mindestens so neu
wie die Zielversion, außerdem mindestens JDK 17 für Gradle 9.6.1.

```bash
./scripts/import-hyperskill-project --dry-run --java-version 21 \
  "/path/to/Hyperskill Project" java project-name
./scripts/import-hyperskill-project --java-version 21 \
  "/path/to/Hyperskill Project" java project-name
```

`--dry-run` schreibt keine Dateien und listet jede übernommene oder ignorierte
Quelldatei auf. Das Original wird ausschließlich gelesen. Builddateien aus dem
Original werden niemals ausgeführt. `--java-version` ist nötig, wenn keine
eindeutige Zielversion erkennbar ist; die Kursversion ist nur ein Hinweis.

Version 1 unterstützt ausschließlich einfache Java-Konsolenprojekte im alten
Academy-Layout `<lesson>/task/src/<package>`. Nur `.java`-Dateien aus genau diesem
Quellordner werden kopiert. Unbekannte Buildprofile, Ressourcen, zusätzliche
Abhängigkeiten, Module, Plugins, Source Sets und Datenbankzugriffe führen zum
Abbruch. Kotlin, Python und komplexere Java-Projekte benötigen zunächst einen
eigenen geprüften Adapter. Es gibt keinen Schalter, um diese Prüfung zu umgehen.

Optionen: `--title`, `--concepts`, `--project-url`, `--main-class`,
`--java-version`, `--dry-run`, `--update`. Siehe `--help`.

Bestehende Ziele werden nur mit `--update` bearbeitet. Ein Importmanifest schützt
nachträgliche Änderungen: geänderte/zusätzliche Dateien oder im neuen Export
fehlende Dateien führen zum Abbruch. Auch Updates löschen keine Dateien. Vor
einem Update müssen lokale Buildartefakte separat entfernt/weggelegt werden.

Der Import prüft Dateipfade, Plattformcode, offensichtliche Geheimnisse,
Whitespace und Git-Status. Die Secret-Prüfung ist heuristisch und ersetzt keine
Sichtung vor Veröffentlichung. Es gibt weder automatisches Staging noch Commit
oder Push. Die Initialisierung des Repositories ist ein separater Einrichtungsschritt.

## Builds und Veröffentlichung

```bash
cd java/project-name
./gradlew build
./gradlew run
```

Jedes Projekt erhält einen eigenen geprüften Gradle-9.6.1-Wrapper. Der Download
der Distribution ist per SHA-256 abgesichert. Ein JDK wird nicht automatisch
heruntergeladen. `options.release` beschränkt Sprache, Bytecode und JDK-API auf
die gewählte Zielversion. Das Startkommando verbindet die Standardeingabe für
interaktive Konsolenprogramme.

Eigene spätere Tests können ergänzt werden. Plattformtests, Aufgabenstellungen,
Kursmetadaten und IDE-Verläufe gehören nicht in dieses Repository.
Vor Veröffentlichung `git diff --cached` prüfen. Beispiel-Commit:
`feat(java): add Simple Chatty Bot`.

## Infrastruktur prüfen

```bash
python3 -B -m unittest discover -s scripts/tests -v
```

Neue Academy-Buildprofile müssen manuell geprüft und in
`scripts/templates/academy-profile.json` freigegeben werden. Selbst eine kleine
unbekannte Änderung wird bewusst abgewiesen; Groovy/Kotlin-Buildscripts lassen
sich nicht zuverlässig mit einzelnen regulären Ausdrücken auf Sicherheit prüfen.
