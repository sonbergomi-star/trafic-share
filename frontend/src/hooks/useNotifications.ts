import { useEffect, useState } from 'react';
import messaging from '@react-native-firebase/messaging';
import { API } from '../api/client';

export const useNotifications = () => {
  const [fcmToken, setFcmToken] = useState<string | null>(null);
  const [hasPermission, setHasPermission] = useState(false);

  useEffect(() => {
    requestPermission();
    setupNotificationHandlers();
  }, []);

  const requestPermission = async () => {
    try {
      const authStatus = await messaging().requestPermission();
      const enabled =
        authStatus === messaging.AuthorizationStatus.AUTHORIZED ||
        authStatus === messaging.AuthorizationStatus.PROVISIONAL;

      if (enabled) {
        setHasPermission(true);
        await getToken();
      }
    } catch (error) {
      console.error('Failed to request notification permission:', error);
    }
  };

  const getToken = async () => {
    try {
      const token = await messaging().getToken();
      console.log('FCM Token:', token);
      setFcmToken(token);
      
      // Register token with backend
      await API.notifications.register({ fcm_token: token });
    } catch (error) {
      console.error('Failed to get FCM token:', error);
    }
  };

  const setupNotificationHandlers = () => {
    // Handle foreground messages
    messaging().onMessage(async (remoteMessage) => {
      console.log('Foreground notification:', remoteMessage);
      // Handle notification display
    });

    // Handle background/quit state messages
    messaging().setBackgroundMessageHandler(async (remoteMessage) => {
      console.log('Background notification:', remoteMessage);
    });

    // Handle notification opened
    messaging().onNotificationOpenedApp((remoteMessage) => {
      console.log('Notification opened app:', remoteMessage);
      // Navigate to relevant screen
    });

    // Check if app was opened from a notification
    messaging()
      .getInitialNotification()
      .then((remoteMessage) => {
        if (remoteMessage) {
          console.log('App opened from notification:', remoteMessage);
        }
      });
  };

  return {
    fcmToken,
    hasPermission,
    requestPermission,
  };
};
