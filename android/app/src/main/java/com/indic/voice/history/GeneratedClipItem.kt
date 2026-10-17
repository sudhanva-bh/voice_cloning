package com.indic.voice.history

import java.io.File

data class GeneratedClipItem(
    val file: File,
    val displayTitle: String,
    val rtf: String?,
    val rssMB: String?,
    val timestampMs: Long
)
