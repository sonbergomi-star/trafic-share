import React from 'react';
import { View, StyleSheet, ViewStyle } from 'react-native';
import { LinearGradient } from 'react-native-linear-gradient';

interface CardProps {
  children: React.ReactNode;
  gradient?: boolean;
  gradientColors?: string[];
  style?: ViewStyle;
}

export const Card: React.FC<CardProps> = ({
  children,
  gradient = false,
  gradientColors = ['#667eea', '#764ba2'],
  style,
}) => {
  if (gradient) {
    return (
      <LinearGradient
        colors={gradientColors}
        start={{ x: 0, y: 0 }}
        end={{ x: 1, y: 1 }}
        style={[styles.card, style]}
      >
        {children}
      </LinearGradient>
    );
  }

  return <View style={[styles.card, style]}>{children}</View>;
};

const styles = StyleSheet.create({
  card: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
});
