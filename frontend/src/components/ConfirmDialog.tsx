import React from 'react';
import {
  Modal,
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  Animated,
} from 'react-native';
import LinearGradient from 'react-native-linear-gradient';

interface ConfirmDialogProps {
  visible: boolean;
  title: string;
  message: string;
  confirmText?: string;
  cancelText?: string;
  onConfirm: () => void;
  onCancel: () => void;
  type?: 'info' | 'warning' | 'danger' | 'success';
}

/**
 * REAL confirmation dialog with animations
 */
export const ConfirmDialog: React.FC<ConfirmDialogProps> = ({
  visible,
  title,
  message,
  confirmText = 'Tasdiqlash',
  cancelText = 'Bekor qilish',
  onConfirm,
  onCancel,
  type = 'info',
}) => {
  const scaleAnim = React.useRef(new Animated.Value(0)).current;

  React.useEffect(() => {
    if (visible) {
      Animated.spring(scaleAnim, {
        toValue: 1,
        friction: 6,
        useNativeDriver: true,
      }).start();
    } else {
      scaleAnim.setValue(0);
    }
  }, [visible]);

  const getColors = () => {
    switch (type) {
      case 'warning': return ['#FFA726', '#FF9800'];
      case 'danger': return ['#EF5350', '#E53935'];
      case 'success': return ['#66BB6A', '#4CAF50'];
      default: return ['#42A5F5', '#2196F3'];
    }
  };

  const getIcon = () => {
    switch (type) {
      case 'warning': return '??';
      case 'danger': return '?';
      case 'success': return '?';
      default: return '??';
    }
  };

  return (
    <Modal
      visible={visible}
      transparent
      animationType="fade"
      onRequestClose={onCancel}
    >
      <View style={styles.overlay}>
        <Animated.View
          style={[
            styles.dialog,
            {
              transform: [{ scale: scaleAnim }],
            },
          ]}
        >
          <LinearGradient
            colors={getColors()}
            start={{ x: 0, y: 0 }}
            end={{ x: 1, y: 1 }}
            style={styles.header}
          >
            <Text style={styles.icon}>{getIcon()}</Text>
            <Text style={styles.title}>{title}</Text>
          </LinearGradient>

          <View style={styles.body}>
            <Text style={styles.message}>{message}</Text>
          </View>

          <View style={styles.footer}>
            <TouchableOpacity
              style={[styles.button, styles.cancelButton]}
              onPress={onCancel}
              activeOpacity={0.8}
            >
              <Text style={styles.cancelButtonText}>{cancelText}</Text>
            </TouchableOpacity>

            <TouchableOpacity
              style={styles.button}
              onPress={onConfirm}
              activeOpacity={0.8}
            >
              <LinearGradient
                colors={getColors()}
                start={{ x: 0, y: 0 }}
                end={{ x: 1, y: 0 }}
                style={styles.confirmButtonGradient}
              >
                <Text style={styles.confirmButtonText}>{confirmText}</Text>
              </LinearGradient>
            </TouchableOpacity>
          </View>
        </Animated.View>
      </View>
    </Modal>
  );
};

const styles = StyleSheet.create({
  overlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.7)',
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  dialog: {
    backgroundColor: '#1E1E1E',
    borderRadius: 20,
    width: '100%',
    maxWidth: 400,
    overflow: 'hidden',
    elevation: 10,
  },
  header: {
    padding: 20,
    alignItems: 'center',
  },
  icon: {
    fontSize: 48,
    marginBottom: 8,
  },
  title: {
    fontSize: 22,
    color: '#FFF',
    fontWeight: 'bold',
  },
  body: {
    padding: 20,
  },
  message: {
    fontSize: 16,
    color: '#CCC',
    lineHeight: 24,
    textAlign: 'center',
  },
  footer: {
    flexDirection: 'row',
    padding: 12,
    gap: 12,
  },
  button: {
    flex: 1,
    borderRadius: 12,
    overflow: 'hidden',
  },
  cancelButton: {
    backgroundColor: '#2A2A2A',
  },
  cancelButtonText: {
    fontSize: 16,
    color: '#AAA',
    fontWeight: '600',
    textAlign: 'center',
    paddingVertical: 14,
  },
  confirmButtonGradient: {
    paddingVertical: 14,
    alignItems: 'center',
  },
  confirmButtonText: {
    fontSize: 16,
    color: '#FFF',
    fontWeight: 'bold',
  },
});
