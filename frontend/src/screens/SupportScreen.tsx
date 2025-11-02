import React, { useEffect, useState } from 'react';
import { View, StyleSheet, Text, TextInput, TouchableOpacity, FlatList } from 'react-native';
import Toast from 'react-native-toast-message';

import { SupportApi } from '../api/endpoints';
import { useAuth } from '../context/AuthContext';
import { SupportRequest } from '../types/api';
import { utcToLocal } from '../utils/format';

const SupportScreen = () => {
  const { user } = useAuth();
  const [subject, setSubject] = useState('');
  const [message, setMessage] = useState('');
  const [history, setHistory] = useState<SupportRequest[]>([]);
  const [loading, setLoading] = useState(false);

  const loadHistory = async () => {
    try {
      const response = await SupportApi.history();
      setHistory(response.data.items);
    } catch (error) {
      Toast.show({ type: 'error', text1: 'Tarix olinmadi' });
    }
  };

  useEffect(() => {
    loadHistory();
  }, []);

  const submit = async () => {
    if (!user) return;
    if (!subject || !message) {
      Toast.show({ type: 'error', text1: 'Mavzu va xabar to?ldirilsin' });
      return;
    }
    try {
      setLoading(true);
      await SupportApi.send({ telegram_id: user.telegram_id, subject, message });
      Toast.show({ type: 'success', text1: 'Xabar yuborildi' });
      setSubject('');
      setMessage('');
      loadHistory();
    } catch (error) {
      Toast.show({ type: 'error', text1: 'Yuborilmadi' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>?? Qo?llab-quvvatlash</Text>
      <Text style={styles.caption}>Savolingizni yozing, biz tez orada javob beramiz.</Text>
      <TextInput
        style={styles.input}
        placeholder="Mavzu"
        placeholderTextColor="#64748b"
        value={subject}
        onChangeText={setSubject}
      />
      <TextInput
        style={[styles.input, { height: 120, textAlignVertical: 'top' }]}
        placeholder="Xabar matni"
        placeholderTextColor="#64748b"
        multiline
        value={message}
        onChangeText={setMessage}
      />
      <TouchableOpacity style={[styles.button, loading && { opacity: 0.6 }]} disabled={loading} onPress={submit}>
        <Text style={styles.buttonLabel}>{loading ? 'Yuborilmoqda...' : 'Yuborish'}</Text>
      </TouchableOpacity>

      <FlatList
        data={history}
        keyExtractor={item => item.id.toString()}
        renderItem={({ item }) => <HistoryRow request={item} />}
        style={{ marginTop: 24 }}
        ItemSeparatorComponent={() => <View style={styles.separator} />}
      />
    </View>
  );
};

const HistoryRow: React.FC<{ request: SupportRequest }> = ({ request }) => (
  <View>
    <Text style={styles.historyTitle}>{request.subject}</Text>
    <Text style={styles.historyStatus}>Holat: {request.status}</Text>
    <Text style={styles.historyBody}>{request.message}</Text>
    <Text style={styles.historyDate}>{utcToLocal(request.created_at)}</Text>
    {request.admin_reply && (
      <Text style={styles.historyReply}>Admin: {request.admin_reply}</Text>
    )}
  </View>
);

export default SupportScreen;

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#050912',
    padding: 20,
  },
  title: {
    fontSize: 24,
    fontWeight: '700',
    color: '#f8fafc',
  },
  caption: {
    color: '#94a3b8',
    marginBottom: 16,
  },
  input: {
    backgroundColor: '#101727',
    borderRadius: 14,
    padding: 14,
    color: '#f8fafc',
    marginBottom: 12,
  },
  button: {
    backgroundColor: '#1d4ed8',
    borderRadius: 14,
    paddingVertical: 14,
    alignItems: 'center',
  },
  buttonLabel: {
    color: '#dbeafe',
    fontWeight: '700',
  },
  separator: {
    height: 1,
    backgroundColor: '#1e293b',
    marginVertical: 12,
  },
  historyTitle: {
    color: '#f8fafc',
    fontWeight: '600',
    marginBottom: 4,
  },
  historyStatus: {
    color: '#38bdf8',
    marginBottom: 4,
  },
  historyBody: {
    color: '#94a3b8',
    marginBottom: 4,
  },
  historyDate: {
    color: '#64748b',
    fontSize: 12,
  },
  historyReply: {
    marginTop: 6,
    color: '#c4b5fd',
  },
});

