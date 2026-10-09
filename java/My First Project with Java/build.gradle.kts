plugins {
    application
}

tasks.withType<JavaCompile>().configureEach {
    options.encoding = "UTF-8"
    options.release.set(23)
}

application {
    mainClass.set("calculator.Main")
}

tasks.named<JavaExec>("run") {
    standardInput = System.`in`
}
