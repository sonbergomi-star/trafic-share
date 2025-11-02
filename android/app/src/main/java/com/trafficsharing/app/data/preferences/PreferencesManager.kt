package com.trafficsharing.app.data.preferences

import android.content.Context
import android.content.SharedPreferences

class PreferencesManager(context: Context) {
    
    companion object {
        private const val PREFS_NAME = "traffic_sharing_prefs"
        private const val KEY_JWT_TOKEN = "jwt_token"
        private const val KEY_TELEGRAM_ID = "telegram_id"
        private const val KEY_USERNAME = "username"
        private const val KEY_FIRST_NAME = "first_name"
        private const val KEY_LANGUAGE = "language"
        private const val KEY_NOTIFICATIONS_ENABLED = "notifications_enabled"
        
        @Volatile
        private var INSTANCE: PreferencesManager? = null
        
        fun getInstance(context: Context): PreferencesManager {
            return INSTANCE ?: synchronized(this) {
                val instance = PreferencesManager(context.applicationContext)
                INSTANCE = instance
                instance
            }
        }
    }
    
    private val prefs: SharedPreferences = 
        context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
    
    fun saveJwtToken(token: String) {
        prefs.edit().putString(KEY_JWT_TOKEN, token).apply()
    }
    
    fun getJwtToken(): String? {
        return prefs.getString(KEY_JWT_TOKEN, null)
    }
    
    fun saveTelegramId(id: Long) {
        prefs.edit().putLong(KEY_TELEGRAM_ID, id).apply()
    }
    
    fun getTelegramId(): Long {
        return prefs.getLong(KEY_TELEGRAM_ID, 0L)
    }
    
    fun saveUserInfo(username: String, firstName: String) {
        prefs.edit()
            .putString(KEY_USERNAME, username)
            .putString(KEY_FIRST_NAME, firstName)
            .apply()
    }
    
    fun getUsername(): String? {
        return prefs.getString(KEY_USERNAME, null)
    }
    
    fun getFirstName(): String? {
        return prefs.getString(KEY_FIRST_NAME, null)
    }
    
    fun saveLanguage(language: String) {
        prefs.edit().putString(KEY_LANGUAGE, language).apply()
    }
    
    fun getLanguage(): String {
        return prefs.getString(KEY_LANGUAGE, "uz") ?: "uz"
    }
    
    fun setNotificationsEnabled(enabled: Boolean) {
        prefs.edit().putBoolean(KEY_NOTIFICATIONS_ENABLED, enabled).apply()
    }
    
    fun isNotificationsEnabled(): Boolean {
        return prefs.getBoolean(KEY_NOTIFICATIONS_ENABLED, true)
    }
    
    fun clearAll() {
        prefs.edit().clear().apply()
    }
}
