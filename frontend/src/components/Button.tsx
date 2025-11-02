import React from 'react';
import {
  TouchableOpacity,
  Text,
  StyleSheet,
  ActivityIndicator,
  ViewStyle,
  TextStyle,
} from 'react-native';
import { LinearGradient } from 'react-native-linear-gradient';

interface ButtonProps {
  title: string;
  onPress: () => void;
  loading?: boolean;
  disabled?: boolean;
  variant?: 'primary' | 'secondary' | 'outline' | 'danger';
  size?: 'small' | 'medium' | 'large';
  style?: ViewStyle;
  textStyle?: TextStyle;
}

export const Button: React.FC<ButtonProps> = ({
  title,
  onPress,
  loading = false,
  disabled = false,
  variant = 'primary',
  size = 'medium',
  style,
  textStyle,
}) => {
  const getButtonColors = () => {
    switch (variant) {
      case 'primary':
        return ['#667eea', '#764ba2'];
      case 'secondary':
        return ['#4facfe', '#00f2fe'];
      case 'danger':
        return ['#ff6b6b', '#ee5a6f'];
      default:
        return ['#667eea', '#764ba2'];
    }
  };

  const getButtonSize = () => {
    switch (size) {
      case 'small':
        return { height: 36, paddingHorizontal: 16 };
      case 'medium':
        return { height: 48, paddingHorizontal: 24 };
      case 'large':
        return { height: 56, paddingHorizontal: 32 };
    }
  };

  const getFontSize = () => {
    switch (size) {
      case 'small':
        return 14;
      case 'medium':
        return 16;
      case 'large':
        return 18;
    }
  };

  if (variant === 'outline') {
    return (
      <TouchableOpacity
        onPress={onPress}
        disabled={disabled || loading}
        style={[
          styles.button,
          styles.outlineButton,
          getButtonSize(),
          disabled && styles.disabledButton,
          style,
        ]}
      >
        {loading ? (
          <ActivityIndicator color="#667eea" />
        ) : (
          <Text style={[styles.outlineText, { fontSize: getFontSize() }, textStyle]}>
            {title}
          </Text>
        )}
      </TouchableOpacity>
    );
  }

  return (
    <TouchableOpacity
      onPress={onPress}
      disabled={disabled || loading}
      style={[getButtonSize(), disabled && styles.disabledButton, style]}
    >
      <LinearGradient
        colors={disabled ? ['#ccc', '#999'] : getButtonColors()}
        start={{ x: 0, y: 0 }}
        end={{ x: 1, y: 0 }}
        style={styles.gradientButton}
      >
        {loading ? (
          <ActivityIndicator color="#fff" />
        ) : (
          <Text style={[styles.buttonText, { fontSize: getFontSize() }, textStyle]}>
            {title}
          </Text>
        )}
      </LinearGradient>
    </TouchableOpacity>
  );
};

const styles = StyleSheet.create({
  button: {
    justifyContent: 'center',
    alignItems: 'center',
    borderRadius: 12,
  },
  gradientButton: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    borderRadius: 12,
    width: '100%',
  },
  outlineButton: {
    borderWidth: 2,
    borderColor: '#667eea',
    backgroundColor: 'transparent',
  },
  buttonText: {
    color: '#fff',
    fontWeight: '600',
  },
  outlineText: {
    color: '#667eea',
    fontWeight: '600',
  },
  disabledButton: {
    opacity: 0.6,
  },
});
