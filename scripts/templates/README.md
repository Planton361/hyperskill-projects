# Geprüfte Vorlagen

`java-gradle/*.in` erzeugt ausschließlich ein Java-Application-Build ohne externe
Plugins oder Abhängigkeiten. Platzhalter werden vom Importer ersetzt.

`academy-profile.json` enthält SHA-256-Werte der manuell geprüften Academy-
Builddateien. Diese Original-Builddateien werden gelesen, aber niemals ausgeführt
oder exportiert. Unbekannte Varianten müssen vor Freigabe separat geprüft werden.

`wrapper/` wurde unabhängig mit Gradle 9.6.1 `wrapper` erzeugt. Die kleine
`settings.gradle.kts` dient nur zum erneuten Erzeugen der Vorlage und wird nicht
ins Projekt kopiert. `wrapper-sha256.json` prüft alle vier Wrapper-Dateien.

Offizielle Prüfsummen:

- Distribution: https://services.gradle.org/distributions/gradle-9.6.1-bin.zip.sha256
- Wrapper-JAR: https://services.gradle.org/distributions/gradle-9.6.1-wrapper.jar.sha256

Bei einem geplanten Upgrade Wrapper neu erzeugen, offizielle Prüfsummen
verifizieren, Manifest aktualisieren und Importtests ausführen.
