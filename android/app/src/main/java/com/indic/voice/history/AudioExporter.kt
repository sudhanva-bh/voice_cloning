package com.indic.voice.history

import android.content.ContentValues
import android.content.Context
import android.os.Build
import android.os.Environment
import android.provider.MediaStore
import android.util.Log
import java.io.File
import java.io.FileInputStream
import java.io.FileOutputStream

class AudioExporter(private val context: Context) {

    companion object {
        private const val TAG = "AudioExporter"
        private const val EXPORT_FOLDER = "IndicVoice"
    }

    fun exportToDownloads(sourceFile: File, customFileName: String? = null): String? {
        if (!sourceFile.exists()) {
            Log.e(TAG, "Source file does not exist: ${sourceFile.absolutePath}")
            return null
        }

        val exportName = if (!customFileName.isNullOrEmpty()) {
            if (customFileName.endsWith(".wav")) customFileName else "$customFileName.wav"
        } else {
            sourceFile.name
        }

        try {
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
                val resolver = context.contentResolver
                val contentValues = ContentValues().apply {
                    put(MediaStore.Audio.Media.DISPLAY_NAME, exportName)
                    put(MediaStore.Audio.Media.MIME_TYPE, "audio/wav")
                    put(MediaStore.Audio.Media.RELATIVE_PATH, "${Environment.DIRECTORY_DOWNLOADS}/$EXPORT_FOLDER")
                    put(MediaStore.Audio.Media.IS_PENDING, 1)
                }

                val uri = resolver.insert(MediaStore.Audio.Media.EXTERNAL_CONTENT_URI, contentValues)
                    ?: throw IllegalStateException("Failed to create MediaStore entry")

                resolver.openOutputStream(uri)?.use { out ->
                    FileInputStream(sourceFile).use { input ->
                        input.copyTo(out)
                    }
                }

                contentValues.clear()
                contentValues.put(MediaStore.Audio.Media.IS_PENDING, 0)
                resolver.update(uri, contentValues, null, null)

                Log.i(TAG, "Exported audio to Downloads/$EXPORT_FOLDER/$exportName via MediaStore")
                return "Download/$EXPORT_FOLDER/$exportName"
            } else {
                val downloadsDir = Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOWNLOADS)
                val targetDir = File(downloadsDir, EXPORT_FOLDER)
                if (!targetDir.exists()) targetDir.mkdirs()

                val targetFile = File(targetDir, exportName)
                FileInputStream(sourceFile).use { input ->
                    FileOutputStream(targetFile).use { out ->
                        input.copyTo(out)
                    }
                }
                Log.i(TAG, "Exported audio directly to ${targetFile.absolutePath}")
                return targetFile.absolutePath
            }
        } catch (e: Exception) {
            Log.e(TAG, "Failed to export audio: ${e.message}", e)
            return null
        }
    }
}
