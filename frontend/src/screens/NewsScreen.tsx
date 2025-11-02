import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  TouchableOpacity,
  RefreshControl,
  ActivityIndicator,
  Linking,
  Image,
} from 'react-native';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';
import { API } from '../api/client';

export default function NewsScreen() {
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [announcements, setAnnouncements] = useState<any[]>([]);
  const [promoCodes, setPromoCodes] = useState<any[]>([]);
  const [telegramLinks, setTelegramLinks] = useState<any>(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [announcementsRes, promoRes, linksRes] = await Promise.all([
        API.getAnnouncements(),
        API.getPromoCodes(),
        API.getTelegramLinks(),
      ]);

      setAnnouncements(announcementsRes.data.announcements);
      setPromoCodes(promoRes.data.promo_codes);
      setTelegramLinks(linksRes.data.telegram_links);
    } catch (error) {
      console.error('Load data error:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const onRefresh = () => {
    setRefreshing(true);
    loadData();
  };

  const openTelegramLink = (url: string) => {
    Linking.openURL(url).catch((err) =>
      console.error('Failed to open URL:', err)
    );
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#007bff" />
      </View>
    );
  }

  return (
    <ScrollView
      style={styles.container}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
      }
    >
      <View style={styles.header}>
        <Icon name="newspaper-variant" size={48} color="#007bff" />
        <Text style={styles.title}>Yangiliklar & Promo</Text>
        <Text style={styles.subtitle}>
          Loyihamizdagi e'lonlar va bonuslarni kuzating
        </Text>
      </View>

      {/* Telegram Links */}
      {telegramLinks && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>?? Telegram</Text>

          <TouchableOpacity
            style={styles.telegramCard}
            onPress={() => openTelegramLink(telegramLinks.channel)}
          >
            <Icon name="bullhorn" size={32} color="#0088cc" />
            <View style={styles.telegramCardContent}>
              <Text style={styles.telegramCardTitle}>Telegram Kanal</Text>
              <Text style={styles.telegramCardSubtitle}>
                Yangiliklar va e'lonlar
              </Text>
            </View>
            <Icon name="chevron-right" size={24} color="#999" />
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.telegramCard}
            onPress={() => openTelegramLink(telegramLinks.chat)}
          >
            <Icon name="chat" size={32} color="#0088cc" />
            <View style={styles.telegramCardContent}>
              <Text style={styles.telegramCardTitle}>Muhokamalar Chat</Text>
              <Text style={styles.telegramCardSubtitle}>
                Foydalanuvchilar bilan muloqot
              </Text>
            </View>
            <Icon name="chevron-right" size={24} color="#999" />
          </TouchableOpacity>
        </View>
      )}

      {/* Announcements */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>?? E'lonlar</Text>

        {announcements.length === 0 ? (
          <View style={styles.emptyState}>
            <Text style={styles.emptyText}>Hozircha e'lonlar yo'q</Text>
          </View>
        ) : (
          announcements.map((announcement) => (
            <View key={announcement.id} style={styles.announcementCard}>
              {announcement.image_url && (
                <Image
                  source={{ uri: announcement.image_url }}
                  style={styles.announcementImage}
                />
              )}
              
              <View style={styles.announcementContent}>
                <Text style={styles.announcementTitle}>
                  {announcement.title}
                </Text>
                <Text style={styles.announcementDescription}>
                  {announcement.description}
                </Text>
                <Text style={styles.announcementDate}>
                  {new Date(announcement.created_at).toLocaleDateString('uz-UZ')}
                </Text>
              </View>

              {announcement.link && (
                <TouchableOpacity
                  style={styles.readMoreButton}
                  onPress={() => openTelegramLink(announcement.link)}
                >
                  <Text style={styles.readMoreText}>Batafsil</Text>
                  <Icon name="arrow-right" size={16} color="#007bff" />
                </TouchableOpacity>
              )}
            </View>
          ))
        )}
      </View>

      {/* Promo Codes */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>?? Promo Kodlar</Text>

        {promoCodes.length === 0 ? (
          <View style={styles.emptyState}>
            <Text style={styles.emptyText}>Faol promo kodlar yo'q</Text>
          </View>
        ) : (
          promoCodes.map((promo) => (
            <View key={promo.id} style={styles.promoCard}>
              <View style={styles.promoHeader}>
                <View>
                  <Text style={styles.promoCode}>{promo.code}</Text>
                  {promo.description && (
                    <Text style={styles.promoDescription}>
                      {promo.description}
                    </Text>
                  )}
                </View>
                <View style={styles.promoBadge}>
                  <Text style={styles.promoBadgeText}>
                    +{promo.bonus_percent}%
                  </Text>
                </View>
              </View>

              {promo.expires_at && (
                <Text style={styles.promoExpiry}>
                  ? {new Date(promo.expires_at).toLocaleDateString('uz-UZ')} gacha
                </Text>
              )}

              <TouchableOpacity style={styles.activateButton}>
                <Text style={styles.activateButtonText}>Faollashtirish</Text>
              </TouchableOpacity>
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
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
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
    fontSize: 13,
    color: '#666',
    marginTop: 5,
    textAlign: 'center',
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
  telegramCard: {
    backgroundColor: '#fff',
    flexDirection: 'row',
    alignItems: 'center',
    padding: 15,
    borderRadius: 10,
    marginBottom: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  telegramCardContent: {
    flex: 1,
    marginLeft: 15,
  },
  telegramCardTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
  },
  telegramCardSubtitle: {
    fontSize: 12,
    color: '#666',
    marginTop: 2,
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
  announcementCard: {
    backgroundColor: '#fff',
    borderRadius: 10,
    marginBottom: 15,
    overflow: 'hidden',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  announcementImage: {
    width: '100%',
    height: 180,
    resizeMode: 'cover',
  },
  announcementContent: {
    padding: 15,
  },
  announcementTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#333',
    marginBottom: 8,
  },
  announcementDescription: {
    fontSize: 14,
    color: '#666',
    lineHeight: 20,
    marginBottom: 8,
  },
  announcementDate: {
    fontSize: 11,
    color: '#999',
  },
  readMoreButton: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 5,
    paddingHorizontal: 15,
    paddingBottom: 15,
  },
  readMoreText: {
    fontSize: 14,
    color: '#007bff',
    fontWeight: '600',
  },
  promoCard: {
    backgroundColor: 'linear-gradient(135deg, #FFD700 0%, #FFA500 100%)',
    padding: 20,
    borderRadius: 10,
    marginBottom: 15,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  promoHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 10,
  },
  promoCode: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
  },
  promoDescription: {
    fontSize: 12,
    color: '#666',
    marginTop: 3,
  },
  promoBadge: {
    backgroundColor: '#28a745',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 20,
  },
  promoBadgeText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: 'bold',
  },
  promoExpiry: {
    fontSize: 12,
    color: '#666',
    marginBottom: 12,
  },
  activateButton: {
    backgroundColor: '#fff',
    paddingVertical: 12,
    borderRadius: 8,
    alignItems: 'center',
  },
  activateButtonText: {
    color: '#FFA500',
    fontSize: 14,
    fontWeight: '600',
  },
});
