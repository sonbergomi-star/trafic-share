import React, { useEffect, useRef, useState } from 'react';
import { View, Text, StyleSheet, Animated } from 'react-native';
import LinearGradient from 'react-native-linear-gradient';

interface AnimatedBalanceProps {
  balance: number;
  previousBalance?: number;
  currency?: string;
}

/**
 * REAL animated balance component with smooth transitions
 */
export const AnimatedBalance: React.FC<AnimatedBalanceProps> = ({
  balance,
  previousBalance,
  currency = '$'
}) => {
  const animatedValue = useRef(new Animated.Value(previousBalance || balance)).current;
  const scaleAnim = useRef(new Animated.Value(1)).current;
  const deltaAnim = useRef(new Animated.Value(0)).current;
  
  const [displayBalance, setDisplayBalance] = useState(balance);
  const [delta, setDelta] = useState(0);

  useEffect(() => {
    if (previousBalance !== undefined && previousBalance !== balance) {
      const difference = balance - previousBalance;
      setDelta(difference);
      
      // Animate balance number
      Animated.timing(animatedValue, {
        toValue: balance,
        duration: 1000,
        useNativeDriver: false,
      }).start();
      
      // Pulse animation on change
      Animated.sequence([
        Animated.timing(scaleAnim, {
          toValue: 1.1,
          duration: 200,
          useNativeDriver: true,
        }),
        Animated.timing(scaleAnim, {
          toValue: 1,
          duration: 200,
          useNativeDriver: true,
        }),
      ]).start();
      
      // Show delta animation
      if (difference > 0) {
        Animated.sequence([
          Animated.timing(deltaAnim, {
            toValue: 1,
            duration: 300,
            useNativeDriver: true,
          }),
          Animated.delay(2000),
          Animated.timing(deltaAnim, {
            toValue: 0,
            duration: 300,
            useNativeDriver: true,
          }),
        ]).start();
      }
    }
  }, [balance, previousBalance]);

  useEffect(() => {
    const listener = animatedValue.addListener(({ value }) => {
      setDisplayBalance(value);
    });
    
    return () => animatedValue.removeListener(listener);
  }, []);

  return (
    <View style={styles.container}>
      <LinearGradient
        colors={['#FFD700', '#FFA500', '#FF8C00']}
        start={{ x: 0, y: 0 }}
        end={{ x: 1, y: 1 }}
        style={styles.gradient}
      >
        <Animated.View style={[styles.balanceContainer, { transform: [{ scale: scaleAnim }] }]}>
          <Text style={styles.label}>?? Balans</Text>
          <Text style={styles.balance}>
            {currency}{displayBalance.toFixed(2)}
          </Text>
        </Animated.View>
        
        {delta > 0 && (
          <Animated.View
            style={[
              styles.deltaContainer,
              {
                opacity: deltaAnim,
                transform: [
                  {
                    translateY: deltaAnim.interpolate({
                      inputRange: [0, 1],
                      outputRange: [0, -20],
                    }),
                  },
                ],
              },
            ]}
          >
            <Text style={styles.deltaText}>
              +{currency}{delta.toFixed(2)} ?
            </Text>
          </Animated.View>
        )}
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
    shadowColor: '#FFD700',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
  },
  gradient: {
    padding: 24,
    minHeight: 120,
  },
  balanceContainer: {
    alignItems: 'center',
  },
  label: {
    fontSize: 16,
    color: '#FFF',
    fontWeight: '600',
    marginBottom: 8,
  },
  balance: {
    fontSize: 36,
    color: '#FFF',
    fontWeight: 'bold',
    textShadowColor: 'rgba(0, 0, 0, 0.3)',
    textShadowOffset: { width: 0, height: 2 },
    textShadowRadius: 4,
  },
  deltaContainer: {
    position: 'absolute',
    top: 20,
    right: 20,
  },
  deltaText: {
    fontSize: 18,
    color: '#FFF',
    fontWeight: 'bold',
  },
});
