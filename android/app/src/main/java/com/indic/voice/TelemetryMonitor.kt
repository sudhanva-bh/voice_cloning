package com.indic.voice

import java.io.File

object TelemetryMonitor {

    /**
     * Reads current resident memory (VmRSS) from Linux /proc/self/status.
     * Returns memory usage in Megabytes (MB).
     */
    fun getResidentMemoryMB(): Int {
        try {
            val statusFile = File("/proc/self/status")
            if (!statusFile.exists()) return 0

            statusFile.useLines { lines ->
                for (line in lines) {
                    if (line.startsWith("VmRSS:")) {
                        val parts = line.split("\\s+".toRegex())
                        if (parts.size >= 2) {
                            val kb = parts[1].toIntOrNull() ?: 0
                            return kb / 1024
                        }
                    }
                }
            }
        } catch (ignored: Exception) {}
        return 0
    }
}
