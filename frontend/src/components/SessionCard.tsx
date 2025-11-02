import React, { useEffect, useRef } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Animated } from 'react-native';
import LinearGradient from 'react-native-linear-gradient';

interface SessionCardProps {
  isActive: boolean;
  sessionId?: string;
  duration?: string;
  mbSent?: number;
  speedMbps?: number;
  estimatedEarnings?: number;
  onStart?: () => void;
  onStop?: () => void;
}

/**
 * REAL animated session control card
 */
export const SessionCard: React.FC<SessionCardProps> = ({
  isActive,
  sessionId,
  duration = '00:00:00',
  mbSent = 0,
  speedMbps = 0,
  estimatedEarnings = 0,
  onStart,
  onStop,
}) => {
  const pulseAnim = useRef(new Animated.Value(1)).current;
  const rotateAnim = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    if (isActive) {
      // Pulse animation when active
      Animated.loop(
        Animated.sequence([
          Animated.timing(pulseAnim, {
            toValue: 1.05,
            duration: 1500,
            useNativeDriver: true,
          }),
          Animated.timing(pulseAnim, {
            toValue: 1,
            duration: 1500,
            useNativeDriver: true,
          }),
        ])
      ).start();

      // Rotate animation
      Animated.loop(
        Animated.timing(rotateAnim, {
          toValue: 1,
          duration: 3000,
          useNativeDriver: true,
        })
      ).start();
    } else {
      pulseAnim.setValue(1);
      rotateAnim.setValue(0);
    }
  }, [isActive]);

  const rotate = rotateAnim.interpolate({
    inputRange: [0, 1],
    outputRange: ['0deg', '360deg'],
  });

  return (
    <View style={styles.container}>
      <LinearGradient
        colors={isActive ? ['#4CAF50', '#45A049'] : ['#2A2A2A', '#1E1E1E']}
        start={{ x: 0, y: 0 }}
        end={{ x: 1, y: 1 }}
        style={styles.gradient}
      >
        <View style={styles.statusContainer}>
          <Animated.View
            style={[
              styles.statusIndicator,
              {
                backgroundColor: isActive ? '#4CAF50' : '#666',
                transform: [{ scale: pulseAnim }],
              },
            ]}
          />
          <Text style={styles.statusText}>
            {isActive ? '?? Faol sessiya' : '? Sessiya yo\'q'}
          </Text>
        </View>

        {isActive && (
          <View style={styles.statsContainer}>
            <Animated.View style={[styles.statBox, { transform: [{ rotate }] }]}>
              <Text style={styles.statIcon}>??</Text>
            </Animated.View>

            <View style={styles.statsGrid}>
              <View style={styles.statItem}>
                <Text style={styles.statLabel}>?? Davomiyligi</Text>
                <Text style={styles.statValue}>{duration}</Text>
              </View>

              <View style={styles.statItem}>
                <Text style={styles.statLabel}>?? Yuborilgan</Text>
                <Text style={styles.statValue}>{mbSent.toFixed(0)} MB</Text>
              </View>

              <View style={styles.statItem}>
                <Text style={styles.statLabel}>? Tezlik</Text>
                <Text style={styles.statValue}>{speedMbps.toFixed(2)} MB/s</Text>
              </View>

              <View style={styles.statItem}>
                <Text style={styles.statLabel}>?? Daromad</Text>
                <Text style={[styles.statValue, styles.earnings]}>
                  ${estimatedEarnings.toFixed(4)}
                </Text>
              </View>
            </View>
          </View>
        )}

        <TouchableOpacity
          style={[styles.button, isActive ? styles.stopButton : styles.startButton]}
          onPress={isActive ? onStop : onStart}
          activeOpacity={0.8}
        >
          <LinearGradient
            colors={isActive ? ['#EF5350', '#E53935'] : ['#4CAF50', '#45A049']}
            start={{ x: 0, y: 0 }}
            end={{ x: 1, y: 0 }}
            style={styles.buttonGradient}
          >
            <Text style={styles.buttonText}>
              {isActive ? '?? TO\'XTATISH' : '?? BOSHLASH'}
            </Text>
          </LinearGradient>
        </TouchableOpacity>
      </LinearGradient>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    marginVertical: 16,
    borderRadius: 20,
    overflow: 'hidden',
    elevation: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
  },
  gradient: {
    padding: 20,
  },
  statusContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16,
  },
  statusIndicator: {
    width: 12,
    height: 12,
    borderRadius: 6,
    marginRight: 8,
  },
  statusText: {
    fontSize: 16,
    color: '#FFF',
    fontWeight: '600',
  },
  statsContainer: {
    marginBottom: 20,
  },
  statBox: {
    alignItems: 'center',
    marginBottom: 16,
  },
  statIcon: {
    fontSize: 48,
  },
  statsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  statItem: {
    width: '48%',
    backgroundColor: 'rgba(0, 0, 0, 0.3)',
    borderRadius: 12,
    padding: 12,
    marginBottom: 8,
  },
  statLabel: {
    fontSize: 12,
    color: '#BBB',
    marginBottom: 4,
  },
  statValue: {
    fontSize: 18,
    color: '#FFF',
    fontWeight: 'bold',
  },
  earnings: {
    color: '#FFD700',
  },
  button: {
    borderRadius: 12,
    overflow: 'hidden',
  },
  startButton: {
    elevation: 4,
  },
  stopButton: {
    elevation: 4,
  },
  buttonGradient: {
    paddingVertical: 16,
    alignItems: 'center',
  },
  buttonText: {
    fontSize: 18,
    color: '#FFF',
    fontWeight: 'bold',
  },
});
