# Geprüfte Vorlagen

`java-gradle/*.in` erzeugt ausschließlich ein Java-Application-Build ohne externe
Plugins oder Abhängigkeiten. Platzhalter werden vom Importer ersetzt.

Academy-Builddateien sind nicht vertrauenswürdig und werden weder geparst noch
ausgeführt, exportiert oder zur Konfiguration des Standalone-Builds verwendet.
Nur die ausgewählten Java-Quellen und die geprüfte Vorlage bestimmen den Export.

`wrapper/` wurde unabhängig mit Gradle 9.6.1 `wrapper` erzeugt. Die kleine
`settings.gradle.kts` dient nur zum erneuten Erzeugen der Vorlage und wird nicht
ins Projekt kopiert. `wrapper-sha256.json` prüft alle vier Wrapper-Dateien.

Offizielle Prüfsummen:

- Distribution: https://services.gradle.org/distributions/gradle-9.6.1-bin.zip.sha256
- Wrapper-JAR: https://services.gradle.org/distributions/gradle-9.6.1-wrapper.jar.sha256

Bei einem geplanten Upgrade Wrapper neu erzeugen, offizielle Prüfsummen
verifizieren, Manifest aktualisieren und Importtests ausführen.
