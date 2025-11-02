package com.trafficsharing.app

import android.app.Application
import com.trafficsharing.app.data.preferences.PreferencesManager

class TrafficApplication : Application() {
    
    companion object {
        lateinit var instance: TrafficApplication
            private set
    }
    
    lateinit var preferencesManager: PreferencesManager
    
    override fun onCreate() {
        super.onCreate()
        instance = this
        preferencesManager = PreferencesManager(this)
    }
}
