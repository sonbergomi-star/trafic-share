import React from 'react';
import { View, StyleSheet, ViewStyle } from 'react-native';

type Props = {
  children: React.ReactNode;
  style?: ViewStyle;
};

export const SectionCard: React.FC<Props> = ({ children, style }) => {
  return <View style={[styles.container, style]}>{children}</View>;
};

const styles = StyleSheet.create({
  container: {
    backgroundColor: '#101727',
    borderRadius: 16,
    padding: 16,
    marginBottom: 16,
    shadowColor: '#000',
    shadowOpacity: 0.15,
    shadowRadius: 10,
    shadowOffset: { width: 0, height: 6 },
    elevation: 4,
  },
});

