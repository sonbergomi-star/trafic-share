# Traffic Sharing Platform

Trafik ulashish platformasi - foydalanuvchilar o'z internet trafigini ulashib daromad topish uchun Android ilova va backend tizim.

## ?? Loyiha tuzilmasi

```
traffic-platform/
??? backend/                 # FastAPI Backend
?   ??? app/
?   ?   ??? api/            # API endpoints
?   ?   ??? models/         # Database models
?   ?   ??? services/       # Business logic
?   ?   ??? core/           # Core configurations
?   ?   ??? utils/          # Utility functions
?   ??? requirements.txt
?   ??? Dockerfile
?   ??? .env.example
??? frontend/               # React Native Android App
?   ??? src/
?   ?   ??? screens/       # App screens
?   ?   ??? components/    # Reusable components
?   ?   ??? api/           # API client
?   ?   ??? utils/         # Utilities
?   ??? package.json
?   ??? App.tsx
??? deployment/             # VPS deployment scripts
?   ??? deploy.sh          # Deployment script
?   ??? start.sh           # Start services
?   ??? stop.sh            # Stop services
?   ??? setup-ssl.sh       # SSL setup
?   ??? nginx.conf         # Nginx configuration
??? docker-compose.yml     # Docker orchestration

```

## ?? VPS da ishga tushirish (Ubuntu 24.04)

### 1. VPS sozlamasi

**VPS Ma'lumotlar:**
- IP: `113.30.191.89`
- User: `adminuser`
- OS: Ubuntu 24.04

### 2. Lokal kompyuterdan deployment

```bash
# Deployment scriptni ishga tushirish
chmod +x deployment/deploy.sh
./deployment/deploy.sh
```

### 3. VPS ga SSH orqali kirish

```bash
ssh adminuser@113.30.191.89
cd /home/adminuser/traffic-platform
```

### 4. Environment o'zgaruvchilarini sozlash

```bash
# .env faylini yaratish
cd backend
cp .env.example .env
nano .env
```

**Majburiy o'zgaruvchilar:**

```env
# Database
DATABASE_URL=postgresql://traffic_user:traffic_password@db:5432/traffic_db

# JWT
JWT_SECRET=your-very-long-and-secure-jwt-secret-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=10080

# Telegram Bot
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_BOT_USERNAME=your_bot_username

# Admin IDs (Telegram IDs, vergul bilan ajratilgan)
ADMIN_IDS=599382114,605472971

# Payment Provider
PAYMENT_PROVIDER_API_KEY=your_payment_api_key
PAYMENT_PROVIDER_API_SECRET=your_payment_secret

# Firebase (Push notifications)
FCM_SERVER_KEY=your_fcm_server_key
FCM_PROJECT_ID=your_firebase_project_id
```

### 5. Servislarni ishga tushirish

```bash
# Servislarni start qilish
cd /home/adminuser/traffic-platform
chmod +x deployment/start.sh
./deployment/start.sh
```

### 6. Servislar holatini tekshirish

```bash
# Docker containerlarni ko'rish
docker-compose ps

# Loglarni ko'rish
docker-compose logs -f

# Backend loglarni ko'rish
docker-compose logs -f backend

# Database loglarni ko'rish
docker-compose logs -f db
```

## ?? API Endpoints

Backend API quyidagi manzilda ishlaydi:
- **Base URL**: `http://113.30.191.89/api`
- **API Docs**: `http://113.30.191.89/docs`
- **Health Check**: `http://113.30.191.89/health`

### Asosiy Endpoints:

#### Authentication
- `POST /api/auth/telegram` - Telegram orqali login
- `POST /api/auth/logout` - Logout

#### Dashboard
- `GET /api/dashboard/{telegram_id}` - Dashboard ma'lumotlari

#### Balance
- `GET /api/balance/{telegram_id}` - Balans va tranzaksiyalar
- `POST /api/balance/refresh` - Balansni yangilash

#### Withdraw
- `POST /api/withdraw` - Pul yechish so'rovi
- `GET /api/withdraw/history/{telegram_id}` - Yechish tarixi

#### Sessions
- `POST /api/sessions/start` - Sessiya boshlash
- `POST /api/sessions/stop` - Sessiya to'xtatish
- `GET /api/sessions/{telegram_id}` - Sessiyalar tarixi

#### Statistics
- `GET /api/stats/daily/{telegram_id}` - Kunlik statistika
- `GET /api/stats/weekly/{telegram_id}` - Haftalik statistika
- `GET /api/stats/monthly/{telegram_id}` - Oylik statistika

#### Admin
- `GET /api/admin/dashboard?admin_id={telegram_id}` - Admin dashboard
- `POST /api/admin/price/set` - Kunlik narx belgilash
- `GET /api/admin/users` - Foydalanuvchilar ro'yxati
- `GET /api/admin/withdraws/pending` - Kutilayotgan to'lovlar

## ?? Android App Setup

### 1. Development uchun setup

```bash
cd frontend

# Dependencies o'rnatish
npm install

# Android build
npm run android
```

### 2. Production build

```bash
# Release APK yaratish
cd android
./gradlew assembleRelease

# APK joylashuvi
# android/app/build/outputs/apk/release/app-release.apk
```

### 3. API URL sozlash

Frontend uchun API URL `frontend/src/api/client.ts` faylida:

```typescript
const API_BASE_URL = 'http://113.30.191.89/api';
```

## ?? SSL Certificate o'rnatish

```bash
cd /home/adminuser/traffic-platform

# SSL sozlash (domain bo'lsa)
sudo chmod +x deployment/setup-ssl.sh
sudo ./deployment/setup-ssl.sh

# Nginx.conf da HTTPS qismini yoqish
nano deployment/nginx.conf
# HTTPS section uncomment qiling

# Nginx restart
docker-compose restart nginx
```

## ?? Foydali Komandalar

### Docker

```bash
# Barcha servislarni to'xtatish
docker-compose stop

# Barcha servislarni qayta ishga tushirish
docker-compose restart

# Containerlarni o'chirish
docker-compose down

# Containerlarni o'chirish va volumelarni ham o'chirish
docker-compose down -v

# Backend rebuild qilish
docker-compose build backend
docker-compose up -d backend
```

### Database

```bash
# Database ga kirish
docker-compose exec db psql -U traffic_user -d traffic_db

# Database backup
docker-compose exec db pg_dump -U traffic_user traffic_db > backup.sql

# Database restore
cat backup.sql | docker-compose exec -T db psql -U traffic_user traffic_db
```

### Logs

```bash
# Barcha loglar
docker-compose logs -f

# Faqat backend loglar
docker-compose logs -f backend

# Oxirgi 100 qator
docker-compose logs --tail=100

# Real-time monitoring
docker stats
```

## ?? Troubleshooting

### Port allaqachon ishlatilmoqda

```bash
# 8000 portni ishlatayotgan jarayonni topish
sudo lsof -i :8000

# Jarayonni to'xtatish
sudo kill -9 <PID>
```

### Database connection xatosi

```bash
# Database container holatini tekshirish
docker-compose ps db

# Database loglarni ko'rish
docker-compose logs db

# Database container qayta ishga tushirish
docker-compose restart db
```

### Nginx xatolari

```bash
# Nginx konfiguratsiyani test qilish
docker-compose exec nginx nginx -t

# Nginx restart
docker-compose restart nginx
```

## ?? Monitoring

### System Resources

```bash
# CPU va RAM ishlatilishi
docker stats

# Disk space
df -h

# Logs hajmi
du -sh /var/lib/docker/
```

### Application Health

```bash
# Health check
curl http://113.30.191.89/health

# API response time
time curl http://113.30.191.89/api/health

# Database connections
docker-compose exec db psql -U traffic_user -d traffic_db -c "SELECT count(*) FROM pg_stat_activity;"
```

## ?? Keyingi qadamlar

1. ? Telegram Bot yarating va tokenni oling
2. ? Firebase loyihasi yarating va FCM sozlang
3. ? Payment provider hisob ochib, API keys oling
4. ? .env faylni to'liq to'ldiring
5. ? Android ilovani build qiling va test qiling
6. ? SSL certificate o'rnating (domain bo'lsa)
7. ? Admin panel orqali kunlik narx belgilang
8. ? Test foydalanuvchilar bilan sinov o'tkazing

## ?? Yordam

Savol yoki muammo bo'lsa:
- Backend logs: `docker-compose logs -f backend`
- Database logs: `docker-compose logs -f db`
- Nginx logs: `docker-compose logs -f nginx`

## ?? License

Private project - barcha huquqlar himoyalangan.
