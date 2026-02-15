/**
 * Doc Agent - Gradle Build Configuration
 *
 * Custom tasks for running the Python agent with structured logging.
 * Usage:
 *   ./gradlew runWorker    - Start the agent worker (streams logs)
 *   ./gradlew runSession   - Start a documentation recording session
 */

// Detect the Python executable (prefer venv)
val pythonExe: String = if (file("venv/bin/python").exists()) {
    "venv/bin/python"
} else {
    "python3"
}

tasks.register<Exec>("runWorker") {
    group = "application"
    description = "Start the Doc Agent worker — streams logs to terminal"

    workingDir = projectDir
    commandLine(pythonExe, "worker.py")

    // Stream output to terminal in real-time
    standardOutput = System.out
    errorOutput = System.err
}

tasks.register<Exec>("runSession") {
    group = "application"
    description = "Start a documentation recording session"

    workingDir = projectDir
    commandLine(pythonExe, "session.py")

    standardOutput = System.out
    errorOutput = System.err
}
