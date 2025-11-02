import React, { useEffect, useState } from 'react';
import { View, StyleSheet, Text, TouchableOpacity, Linking, FlatList } from 'react-native';
import Toast from 'react-native-toast-message';

import { NewsApi } from '../api/endpoints';
import { Announcement, NewsPromoResponse, PromoCode } from '../types/api';
import { utcToLocal } from '../utils/format';
import { useAuth } from '../context/AuthContext';

const NewsScreen = () => {
  const { user } = useAuth();
  const [data, setData] = useState<NewsPromoResponse | null>(null);

  const load = async () => {
    try {
      const response = await NewsApi.list();
      setData(response.data);
    } catch (error) {
      Toast.show({ type: 'error', text1: 'Yangiliklar olinmadi' });
    }
  };

  useEffect(() => {
    load();
  }, []);

  const activatePromo = async (code: string) => {
    try {
      await NewsApi.activatePromo({ user_id: user?.id ?? 0, code });
      Toast.show({ type: 'success', text1: `Promo ${code} ishga tushirildi` });
    } catch (error) {
      Toast.show({ type: 'error', text1: 'Promo faollashtirilmadi' });
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.header}>?? Rasmiy kanallar</Text>
      {data?.telegram_links && (
        Object.entries(data.telegram_links).map(([key, url]) => (
          <TouchableOpacity key={key} style={styles.linkBtn} onPress={() => Linking.openURL(url)}>
            <Text style={styles.linkLabel}>{key.toUpperCase()}</Text>
            <Text style={styles.linkUrl}>{url}</Text>
          </TouchableOpacity>
        ))
      )}

      <Text style={[styles.header, { marginTop: 24 }]}>?? Yangiliklar</Text>
      <FlatList
        data={data?.announcements || []}
        keyExtractor={item => item.id.toString()}
        renderItem={({ item }) => <NewsCard announcement={item} />}
        ListEmptyComponent={<Text style={styles.empty}>Hozircha e?lonlar yo?q</Text>}
      />

      <Text style={[styles.header, { marginTop: 24 }]}>?? Promo kodlar</Text>
      <FlatList
        data={data?.promo || []}
        keyExtractor={item => item.id.toString()}
        renderItem={({ item }) => <PromoCard promo={item} onActivate={activatePromo} />}
        ListEmptyComponent={<Text style={styles.empty}>Aktiv promo kodlar yo?q</Text>}
      />
    </View>
  );
};

const NewsCard: React.FC<{ announcement: Announcement }> = ({ announcement }) => (
  <View style={styles.newsCard}>
    <Text style={styles.newsTitle}>{announcement.title}</Text>
    <Text style={styles.newsDate}>{utcToLocal(announcement.created_at)}</Text>
    <Text style={styles.newsDesc}>{announcement.description}</Text>
    {announcement.link && (
      <TouchableOpacity onPress={() => Linking.openURL(announcement.link)}>
        <Text style={styles.newsLink}>Batafsil ?</Text>
      </TouchableOpacity>
    )}
  </View>
);

const PromoCard: React.FC<{ promo: PromoCode; onActivate: (code: string) => void }> = ({ promo, onActivate }) => (
  <View style={styles.promoCard}>
    <View>
      <Text style={styles.promoCode}>{promo.code}</Text>
      <Text style={styles.promoBonus}>Bonus: +{promo.bonus_percent}%</Text>
      {promo.expires_at && <Text style={styles.promoDate}>Gacha: {promo.expires_at}</Text>}
    </View>
    <TouchableOpacity style={styles.promoBtn} onPress={() => onActivate(promo.code)}>
      <Text style={styles.promoBtnLabel}>Faollashtirish</Text>
    </TouchableOpacity>
  </View>
);

export default NewsScreen;

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#050912',
    padding: 20,
  },
  header: {
    fontSize: 22,
    fontWeight: '700',
    color: '#f8fafc',
    marginBottom: 12,
  },
  linkBtn: {
    backgroundColor: '#101727',
    borderRadius: 14,
    padding: 14,
    marginBottom: 12,
  },
  linkLabel: {
    color: '#93c5fd',
    fontWeight: '600',
  },
  linkUrl: {
    color: '#64748b',
  },
  newsCard: {
    backgroundColor: '#0f172a',
    borderRadius: 14,
    padding: 16,
    marginBottom: 12,
  },
  newsTitle: {
    color: '#f8fafc',
    fontWeight: '600',
    fontSize: 16,
  },
  newsDate: {
    color: '#64748b',
    fontSize: 12,
    marginVertical: 4,
  },
  newsDesc: {
    color: '#cbd5f5',
  },
  newsLink: {
    color: '#60a5fa',
    marginTop: 8,
  },
  empty: {
    color: '#64748b',
    marginBottom: 12,
  },
  promoCard: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: '#1d2342',
    borderRadius: 14,
    padding: 16,
    marginBottom: 12,
  },
  promoCode: {
    color: '#fbbf24',
    fontWeight: '700',
    fontSize: 18,
  },
  promoBonus: {
    color: '#f8fafc',
  },
  promoDate: {
    color: '#94a3b8',
    fontSize: 12,
  },
  promoBtn: {
    backgroundColor: '#22c55e',
    borderRadius: 12,
    paddingVertical: 8,
    paddingHorizontal: 12,
  },
  promoBtnLabel: {
    color: '#052e16',
    fontWeight: '700',
  },
});

