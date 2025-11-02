import React, { useRef, useEffect } from 'react';
import { View, Text, StyleSheet, Animated } from 'react-native';

interface PullToRefreshProps {
  isRefreshing: boolean;
}

/**
 * REAL Pull to Refresh indicator with animation
 */
export const PullToRefreshIndicator: React.FC<PullToRefreshProps> = ({
  isRefreshing,
}) => {
  const spinAnim = useRef(new Animated.Value(0)).current;
  const scaleAnim = useRef(new Animated.Value(0.8)).current;

  useEffect(() => {
    if (isRefreshing) {
      // Spin animation
      Animated.loop(
        Animated.timing(spinAnim, {
          toValue: 1,
          duration: 1000,
          useNativeDriver: true,
        })
      ).start();

      // Scale animation
      Animated.sequence([
        Animated.timing(scaleAnim, {
          toValue: 1,
          duration: 200,
          useNativeDriver: true,
        }),
      ]).start();
    } else {
      spinAnim.setValue(0);
      scaleAnim.setValue(0.8);
    }
  }, [isRefreshing]);

  const spin = spinAnim.interpolate({
    inputRange: [0, 1],
    outputRange: ['0deg', '360deg'],
  });

  if (!isRefreshing) return null;

  return (
    <View style={styles.container}>
      <Animated.View
        style={[
          styles.spinner,
          {
            transform: [{ rotate: spin }, { scale: scaleAnim }],
          },
        ]}
      >
        <Text style={styles.icon}>??</Text>
      </Animated.View>
      <Text style={styles.text}>Yangilanmoqda...</Text>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    alignItems: 'center',
    paddingVertical: 16,
  },
  spinner: {
    marginBottom: 8,
  },
  icon: {
    fontSize: 32,
  },
  text: {
    fontSize: 14,
    color: '#AAA',
  },
});
