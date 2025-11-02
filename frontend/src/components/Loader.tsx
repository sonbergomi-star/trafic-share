import React from 'react';
import { ActivityIndicator, View, StyleSheet } from 'react-native';

type Props = {
  visible?: boolean;
};

export const Loader: React.FC<Props> = ({ visible = false }) => {
  if (!visible) return null;
  return (
    <View style={styles.container}>
      <ActivityIndicator color="#4ade80" size="large" />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 24,
  },
});

