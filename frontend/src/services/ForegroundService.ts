import { NativeModules, NativeEventEmitter } from 'react-native';

/**
 * REAL Android Foreground Service for traffic monitoring
 * Shows ongoing notification with live updates
 */

const { ForegroundServiceModule } = NativeModules;
const foregroundServiceEmitter = new NativeEventEmitter(ForegroundServiceModule);

export interface SessionData {
  sessionId: string;
  mbSent: number;
  speedMbps: number;
  durationSec: number;
  estimatedEarnings: number;
}

class ForegroundService {
  private updateInterval: NodeJS.Timeout | null = null;

  /**
   * REAL start foreground service
   */
  async start(sessionId: string): Promise<void> {
    try {
      await ForegroundServiceModule.startForegroundService(sessionId);
      console.log('? Foreground service started');
    } catch (error) {
      console.error('? Failed to start foreground service:', error);
      throw error;
    }
  }

  /**
   * REAL stop foreground service
   */
  async stop(): Promise<void> {
    try {
      await ForegroundServiceModule.stopForegroundService();
      
      if (this.updateInterval) {
        clearInterval(this.updateInterval);
        this.updateInterval = null;
      }
      
      console.log('? Foreground service stopped');
    } catch (error) {
      console.error('? Failed to stop foreground service:', error);
      throw error;
    }
  }

  /**
   * REAL update notification with session data
   */
  async updateNotification(data: SessionData): Promise<void> {
    try {
      await ForegroundServiceModule.updateNotification({
        sessionId: data.sessionId,
        mbSent: data.mbSent,
        speedMbps: data.speedMbps,
        durationSec: data.durationSec,
        estimatedEarnings: data.estimatedEarnings,
      });
    } catch (error) {
      console.error('? Failed to update notification:', error);
    }
  }

  /**
   * REAL start automatic updates (every 3 seconds)
   */
  startAutoUpdate(getSessionData: () => SessionData): void {
    if (this.updateInterval) {
      clearInterval(this.updateInterval);
    }

    this.updateInterval = setInterval(() => {
      const data = getSessionData();
      this.updateNotification(data);
    }, 3000); // Update every 3 seconds
  }

  /**
   * REAL stop automatic updates
   */
  stopAutoUpdate(): void {
    if (this.updateInterval) {
      clearInterval(this.updateInterval);
      this.updateInterval = null;
    }
  }

  /**
   * Listen to notification action events
   */
  onNotificationAction(callback: (action: string) => void): () => void {
    const subscription = foregroundServiceEmitter.addListener(
      'onNotificationAction',
      (event) => {
        callback(event.action);
      }
    );

    return () => subscription.remove();
  }
}

export default new ForegroundService();
