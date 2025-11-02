import React, { useEffect, useRef } from 'react';
import { View, Text, StyleSheet, Animated } from 'react-native';
import LinearGradient from 'react-native-linear-gradient';

interface TrafficProgressBarProps {
  sentMB: number;
  usedMB: number;
  label?: string;
  showPercentage?: boolean;
}

/**
 * REAL animated progress bar for traffic
 */
export const TrafficProgressBar: React.FC<TrafficProgressBarProps> = ({
  sentMB,
  usedMB,
  label = 'Trafik',
  showPercentage = true,
}) => {
  const progressAnim = useRef(new Animated.Value(0)).current;
  const pulseAnim = useRef(new Animated.Value(1)).current;

  const percentage = sentMB > 0 ? (usedMB / sentMB) * 100 : 0;

  useEffect(() => {
    // Animate progress bar
    Animated.spring(progressAnim, {
      toValue: percentage,
      friction: 8,
      tension: 40,
      useNativeDriver: false,
    }).start();

    // Pulse animation when active
    if (percentage > 0 && percentage < 100) {
      Animated.loop(
        Animated.sequence([
          Animated.timing(pulseAnim, {
            toValue: 1.05,
            duration: 1000,
            useNativeDriver: true,
          }),
          Animated.timing(pulseAnim, {
            toValue: 1,
            duration: 1000,
            useNativeDriver: true,
          }),
        ])
      ).start();
    }
  }, [percentage]);

  const progressWidth = progressAnim.interpolate({
    inputRange: [0, 100],
    outputRange: ['0%', '100%'],
    extrapolate: 'clamp',
  });

  const getProgressColor = () => {
    if (percentage < 50) return ['#4CAF50', '#81C784'];
    if (percentage < 80) return ['#FFA726', '#FFB74D'];
    return ['#EF5350', '#E57373'];
  };

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.label}>?? {label}</Text>
        {showPercentage && (
          <Text style={styles.percentage}>{percentage.toFixed(1)}%</Text>
        )}
      </View>

      <View style={styles.progressBarContainer}>
        <Animated.View
          style={[
            styles.progressBar,
            {
              width: progressWidth,
              transform: [{ scale: pulseAnim }],
            },
          ]}
        >
          <LinearGradient
            colors={getProgressColor()}
            start={{ x: 0, y: 0 }}
            end={{ x: 1, y: 0 }}
            style={styles.gradient}
          />
        </Animated.View>
      </View>

      <View style={styles.stats}>
        <View style={styles.statItem}>
          <Text style={styles.statLabel}>?? Yuborilgan</Text>
          <Text style={styles.statValue}>{sentMB.toFixed(0)} MB</Text>
        </View>
        <View style={styles.statItem}>
          <Text style={styles.statLabel}>?? Ishlatilgan</Text>
          <Text style={styles.statValue}>{usedMB.toFixed(0)} MB</Text>
        </View>
        <View style={styles.statItem}>
          <Text style={styles.statLabel}>? Qolgan</Text>
          <Text style={styles.statValue}>{Math.max(0, sentMB - usedMB).toFixed(0)} MB</Text>
        </View>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    backgroundColor: '#1E1E1E',
    borderRadius: 16,
    padding: 16,
    marginVertical: 12,
    elevation: 4,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.25,
    shadowRadius: 4,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  label: {
    fontSize: 16,
    color: '#FFF',
    fontWeight: '600',
  },
  percentage: {
    fontSize: 18,
    color: '#4CAF50',
    fontWeight: 'bold',
  },
  progressBarContainer: {
    height: 12,
    backgroundColor: '#2A2A2A',
    borderRadius: 6,
    overflow: 'hidden',
    marginBottom: 16,
  },
  progressBar: {
    height: '100%',
    borderRadius: 6,
  },
  gradient: {
    flex: 1,
  },
  stats: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  statItem: {
    alignItems: 'center',
  },
  statLabel: {
    fontSize: 12,
    color: '#999',
    marginBottom: 4,
  },
  statValue: {
    fontSize: 16,
    color: '#FFF',
    fontWeight: 'bold',
  },
});
