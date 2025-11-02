import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  TextInput,
  ScrollView,
  StyleSheet,
  TouchableOpacity,
  Alert,
  ActivityIndicator,
} from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';
import { API } from '../api/client';

export default function SupportScreen() {
  const [loading, setLoading] = useState(false);
  const [loadingHistory, setLoadingHistory] = useState(true);
  const [subject, setSubject] = useState('');
  const [message, setMessage] = useState('');
  const [history, setHistory] = useState<any[]>([]);

  useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = async () => {
    try {
      const userData = await AsyncStorage.getItem('user_data');
      if (userData) {
        const user = JSON.parse(userData);
        const response = await API.getSupportHistory(user.telegram_id);
        setHistory(response.data.requests);
      }
    } catch (error) {
      console.error('Load history error:', error);
    } finally {
      setLoadingHistory(false);
    }
  };

  const handleSubmit = async () => {
    if (!subject.trim() || !message.trim()) {
      Alert.alert('Xato', 'Mavzu va xabar matnini kiriting');
      return;
    }

    setLoading(true);
    try {
      const userData = await AsyncStorage.getItem('user_data');
      if (userData) {
        const user = JSON.parse(userData);
        
        await API.createSupportRequest({
          telegram_id: user.telegram_id,
          subject: subject.trim(),
          message: message.trim(),
        });

        Alert.alert(
          'Muvaffaqiyat',
          'Xabaringiz yuborildi! Admin tez orada siz bilan bog\'lanadi.',
          [{ text: 'OK', onPress: () => {
            setSubject('');
            setMessage('');
            loadHistory();
          }}]
        );
      }
    } catch (error: any) {
      Alert.alert(
        'Xato',
        error.response?.data?.detail || 'Xabar yuborishda xatolik'
      );
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'new':
        return '#ffc107';
      case 'read':
        return '#007bff';
      case 'replied':
        return '#28a745';
      case 'closed':
        return '#6c757d';
      default:
        return '#999';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'new':
        return '?? Yangi';
      case 'read':
        return '?? O\'qilgan';
      case 'replied':
        return '?? Javob berilgan';
      case 'closed':
        return '? Yopilgan';
      default:
        return status;
    }
  };

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Icon name="help-circle" size={64} color="#007bff" />
        <Text style={styles.title}>Qo'llab-quvvatlash</Text>
        <Text style={styles.subtitle}>
          Savolingiz bormi? Biz sizga yordam beramiz ?????
        </Text>
      </View>

      {/* Support Form */}
      <View style={styles.formCard}>
        <Text style={styles.formTitle}>Yangi xabar</Text>

        <View style={styles.formGroup}>
          <Text style={styles.label}>Mavzu</Text>
          <TextInput
            style={styles.input}
            placeholder="Qisqa sarlavha"
            value={subject}
            onChangeText={setSubject}
            maxLength={100}
          />
        </View>

        <View style={styles.formGroup}>
          <Text style={styles.label}>Xabar matni</Text>
          <TextInput
            style={[styles.input, styles.textarea]}
            placeholder="Muammo yoki savolingizni batafsil yozing..."
            value={message}
            onChangeText={setMessage}
            multiline
            numberOfLines={6}
            maxLength={1000}
          />
        </View>

        <TouchableOpacity
          style={[styles.submitButton, loading && styles.submitButtonDisabled]}
          onPress={handleSubmit}
          disabled={loading}
        >
          {loading ? (
            <ActivityIndicator color="#fff" />
          ) : (
            <>
              <Icon name="send" size={20} color="#fff" />
              <Text style={styles.submitButtonText}>Yuborish</Text>
            </>
          )}
        </TouchableOpacity>
      </View>

      {/* Support History */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>So'rovlar tarixi</Text>

        {loadingHistory ? (
          <ActivityIndicator size="small" color="#007bff" />
        ) : history.length === 0 ? (
          <View style={styles.emptyState}>
            <Text style={styles.emptyText}>Hali so'rovlar yo'q</Text>
          </View>
        ) : (
          history.map((request) => (
            <View key={request.id} style={styles.requestCard}>
              <View style={styles.requestHeader}>
                <Text style={styles.requestSubject}>{request.subject}</Text>
                <Text style={{ color: getStatusColor(request.status) }}>
                  {getStatusText(request.status)}
                </Text>
              </View>

              <Text style={styles.requestMessage} numberOfLines={2}>
                {request.message}
              </Text>

              <Text style={styles.requestDate}>
                {new Date(request.created_at).toLocaleDateString('uz-UZ')}
              </Text>

              {request.admin_reply && (
                <View style={styles.replyBox}>
                  <Text style={styles.replyLabel}>Admin javobi:</Text>
                  <Text style={styles.replyText}>{request.admin_reply}</Text>
                </View>
              )}
            </View>
          ))
        )}
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  header: {
    backgroundColor: '#fff',
    padding: 30,
    alignItems: 'center',
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
    marginTop: 10,
  },
  subtitle: {
    fontSize: 14,
    color: '#666',
    marginTop: 5,
    textAlign: 'center',
  },
  formCard: {
    backgroundColor: '#fff',
    margin: 15,
    padding: 20,
    borderRadius: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  formTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#333',
    marginBottom: 15,
  },
  formGroup: {
    marginBottom: 15,
  },
  label: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
    marginBottom: 8,
  },
  input: {
    backgroundColor: '#f9f9f9',
    borderWidth: 1,
    borderColor: '#e0e0e0',
    borderRadius: 8,
    padding: 12,
    fontSize: 14,
  },
  textarea: {
    minHeight: 120,
    textAlignVertical: 'top',
  },
  submitButton: {
    backgroundColor: '#007bff',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 8,
    paddingVertical: 15,
    borderRadius: 8,
    marginTop: 10,
  },
  submitButtonDisabled: {
    backgroundColor: '#ccc',
  },
  submitButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  section: {
    margin: 15,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 15,
  },
  emptyState: {
    backgroundColor: '#fff',
    padding: 40,
    borderRadius: 10,
    alignItems: 'center',
  },
  emptyText: {
    color: '#999',
    fontSize: 14,
  },
  requestCard: {
    backgroundColor: '#fff',
    padding: 15,
    borderRadius: 10,
    marginBottom: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  requestHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  requestSubject: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    flex: 1,
  },
  requestMessage: {
    fontSize: 14,
    color: '#666',
    marginBottom: 8,
  },
  requestDate: {
    fontSize: 11,
    color: '#999',
  },
  replyBox: {
    backgroundColor: '#e3f2fd',
    padding: 12,
    borderRadius: 8,
    marginTop: 10,
    borderLeftWidth: 3,
    borderLeftColor: '#007bff',
  },
  replyLabel: {
    fontSize: 12,
    fontWeight: '600',
    color: '#007bff',
    marginBottom: 5,
  },
  replyText: {
    fontSize: 13,
    color: '#333',
  },
});
