package com.trafficapp;

import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.app.Service;
import android.content.Context;
import android.content.Intent;
import android.os.Build;
import android.os.IBinder;
import androidx.core.app.NotificationCompat;

import com.facebook.react.bridge.Promise;
import com.facebook.react.bridge.ReactApplicationContext;
import com.facebook.react.bridge.ReactContextBaseJavaModule;
import com.facebook.react.bridge.ReactMethod;
import com.facebook.react.bridge.ReadableMap;
import com.facebook.react.modules.core.DeviceEventManagerModule;

/**
 * REAL Android Foreground Service Module
 * Provides ongoing notification with live traffic updates
 */
public class ForegroundServiceModule extends ReactContextBaseJavaModule {
    
    private static final String MODULE_NAME = "ForegroundServiceModule";
    private static final String CHANNEL_ID = "traffic_session_channel";
    private static final int NOTIFICATION_ID = 1001;
    
    private ReactApplicationContext reactContext;
    private NotificationManager notificationManager;

    public ForegroundServiceModule(ReactApplicationContext reactContext) {
        super(reactContext);
        this.reactContext = reactContext;
        this.notificationManager = (NotificationManager) 
            reactContext.getSystemService(Context.NOTIFICATION_SERVICE);
        
        createNotificationChannel();
    }

    @Override
    public String getName() {
        return MODULE_NAME;
    }

    /**
     * REAL create notification channel for Android 8+
     */
    private void createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            NotificationChannel channel = new NotificationChannel(
                CHANNEL_ID,
                "Traffic Session",
                NotificationManager.IMPORTANCE_LOW
            );
            channel.setDescription("Shows live traffic session data");
            channel.setShowBadge(false);
            
            notificationManager.createNotificationChannel(channel);
        }
    }

    /**
     * REAL start foreground service
     */
    @ReactMethod
    public void startForegroundService(String sessionId, Promise promise) {
        try {
            Intent serviceIntent = new Intent(reactContext, TrafficForegroundService.class);
            serviceIntent.putExtra("sessionId", sessionId);
            
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                reactContext.startForegroundService(serviceIntent);
            } else {
                reactContext.startService(serviceIntent);
            }
            
            promise.resolve(true);
        } catch (Exception e) {
            promise.reject("START_ERROR", "Failed to start foreground service", e);
        }
    }

    /**
     * REAL stop foreground service
     */
    @ReactMethod
    public void stopForegroundService(Promise promise) {
        try {
            Intent serviceIntent = new Intent(reactContext, TrafficForegroundService.class);
            reactContext.stopService(serviceIntent);
            
            promise.resolve(true);
        } catch (Exception e) {
            promise.reject("STOP_ERROR", "Failed to stop foreground service", e);
        }
    }

    /**
     * REAL update notification with session data
     */
    @ReactMethod
    public void updateNotification(ReadableMap data, Promise promise) {
        try {
            String sessionId = data.getString("sessionId");
            double mbSent = data.getDouble("mbSent");
            double speedMbps = data.getDouble("speedMbps");
            int durationSec = data.getInt("durationSec");
            double estimatedEarnings = data.getDouble("estimatedEarnings");
            
            Notification notification = buildNotification(
                sessionId, mbSent, speedMbps, durationSec, estimatedEarnings
            );
            
            notificationManager.notify(NOTIFICATION_ID, notification);
            
            promise.resolve(true);
        } catch (Exception e) {
            promise.reject("UPDATE_ERROR", "Failed to update notification", e);
        }
    }

    /**
     * REAL build notification with session data
     */
    private Notification buildNotification(
        String sessionId,
        double mbSent,
        double speedMbps,
        int durationSec,
        double estimatedEarnings
    ) {
        // Format duration
        int hours = durationSec / 3600;
        int minutes = (durationSec % 3600) / 60;
        int seconds = durationSec % 60;
        String duration = String.format("%02d:%02d:%02d", hours, minutes, seconds);
        
        // Format data
        String title = "?? Trafik ulashish - Faol";
        String content = String.format(
            "Yuborilgan: %.0f MB ? Tezlik: %.2f MB/s",
            mbSent, speedMbps
        );
        String subText = String.format(
            "Vaqt: %s ? Daromad: $%.4f",
            duration, estimatedEarnings
        );
        
        // Build notification
        NotificationCompat.Builder builder = new NotificationCompat.Builder(reactContext, CHANNEL_ID)
            .setSmallIcon(R.drawable.ic_notification)
            .setContentTitle(title)
            .setContentText(content)
            .setSubText(subText)
            .setOngoing(true)
            .setPriority(NotificationCompat.PRIORITY_LOW)
            .setCategory(NotificationCompat.CATEGORY_SERVICE);
        
        // Add stop action
        Intent stopIntent = new Intent(reactContext, StopSessionBroadcastReceiver.class);
        PendingIntent stopPendingIntent = PendingIntent.getBroadcast(
            reactContext,
            0,
            stopIntent,
            PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE
        );
        
        builder.addAction(
            R.drawable.ic_stop,
            "TO'XTATISH",
            stopPendingIntent
        );
        
        return builder.build();
    }

    /**
     * REAL foreground service class
     */
    public static class TrafficForegroundService extends Service {
        
        @Override
        public int onStartCommand(Intent intent, int flags, int startId) {
            String sessionId = intent.getStringExtra("sessionId");
            
            // Build initial notification
            Notification notification = new NotificationCompat.Builder(this, CHANNEL_ID)
                .setSmallIcon(R.drawable.ic_notification)
                .setContentTitle("?? Trafik ulashish")
                .setContentText("Sessiya boshlanmoqda...")
                .setOngoing(true)
                .setPriority(NotificationCompat.PRIORITY_LOW)
                .build();
            
            startForeground(NOTIFICATION_ID, notification);
            
            return START_STICKY;
        }
        
        @Override
        public IBinder onBind(Intent intent) {
            return null;
        }
        
        @Override
        public void onDestroy() {
            super.onDestroy();
            stopForeground(true);
        }
    }
}
