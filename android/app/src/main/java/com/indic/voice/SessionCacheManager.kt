package com.indic.voice

import android.content.Context
import android.content.SharedPreferences

class SessionCacheManager(context: Context) {

    companion object {
        private const val PREF_NAME = "indic_voice_session"
        private const val KEY_REF_PATH = "ref_clip_path"
        private const val KEY_REF_NAME = "ref_file_name"
        private const val KEY_REF_TEXT = "ref_text"
        private const val KEY_TARGET_TEXT = "target_text"
        private const val KEY_CFM_STEPS = "cfm_steps"
    }

    private val prefs: SharedPreferences =
        context.getSharedPreferences(PREF_NAME, Context.MODE_PRIVATE)

    var refClipPath: String?
        get() = prefs.getString(KEY_REF_PATH, null)
        set(value) = prefs.edit().putString(KEY_REF_PATH, value).apply()

    var refFileName: String?
        get() = prefs.getString(KEY_REF_NAME, null)
        set(value) = prefs.edit().putString(KEY_REF_NAME, value).apply()

    var refText: String
        get() = prefs.getString(KEY_REF_TEXT, "Some call me nature.") ?: "Some call me nature."
        set(value) = prefs.edit().putString(KEY_REF_TEXT, value).apply()

    var targetText: String
        get() = prefs.getString(KEY_TARGET_TEXT, "Hey there! Hope you are having a wonderful day.") ?: "Hey there! Hope you are having a wonderful day."
        set(value) = prefs.edit().putString(KEY_TARGET_TEXT, value).apply()

    var cfmSteps: Int
        get() = prefs.getInt(KEY_CFM_STEPS, 16)
        set(value) = prefs.edit().putInt(KEY_CFM_STEPS, value).apply()

    fun clearReference() {
        prefs.edit().remove(KEY_REF_PATH).remove(KEY_REF_NAME).apply()
    }
}
