# ?? Traffic Sharing Platform - To'liq O'rnatish Qo'llanmasi

## VPS: 113.30.191.89 | Ubuntu 24.04 | User: adminuser

---

## ?? Boshlash uchun kerakli narsalar

1. **Telegram Bot**
   - BotFather orqali bot yarating: https://t.me/BotFather
   - Bot token oling
   - Bot username oling

2. **Firebase Account** (Push notifications uchun)
   - Firebase console: https://console.firebase.google.com
   - Yangi loyiha yarating
   - Firebase Cloud Messaging (FCM) yoqing
   - Server Key oling

3. **Payment Provider** (NowPayments, CryptoCloud, va h.k.)
   - Hisob oching
   - API Key va Secret oling

4. **SSH Access**
   - VPS ga SSH key orqali kirish sozlang

---

## ?? 1-QADAM: Lokal kompyuterdan deployment

### 1.1. Loyihani clone qiling (agar git da bo'lsa)

```bash
git clone <repository_url>
cd traffic-platform
```

### 1.2. Environment o'zgaruvchilarini tayyorlang

```bash
# Backend .env faylini tahrirlang
nano backend/.env
```

**Majburiy parametrlar:**
- `TELEGRAM_BOT_TOKEN` - Telegram bot token
- `TELEGRAM_BOT_USERNAME` - Bot username
- `ADMIN_IDS` - Admin Telegram ID'lar (vergul bilan)
- `JWT_SECRET` - Uzun va murakkab secret key
- `FCM_SERVER_KEY` - Firebase server key
- `PAYMENT_PROVIDER_API_KEY` - Payment API key

### 1.3. Deployment scriptni ishga tushiring

```bash
chmod +x deployment/deploy.sh
./deployment/deploy.sh
```

Bu script:
- ? Loyiha fayllarini tar.gz ga to'playdi
- ? VPS ga yuklaydi
- ? Docker va Docker Compose o'rnatadi
- ? Firewall sozlaydi
- ? Kataloglar yaratadi

---

## ?? 2-QADAM: VPS da sozlash

### 2.1. VPS ga kirish

```bash
ssh adminuser@113.30.191.89
cd /home/adminuser/traffic-platform
```

### 2.2. Environment sozlash

```bash
cd backend
nano .env
```

Barcha parametrlarni to'ldiring (yuqoridagi ro'yxatga qarang).

### 2.3. Servislarni ishga tushirish

```bash
cd /home/adminuser/traffic-platform
./deployment/start.sh
```

Bu script:
- ? Docker imagelarni pull qiladi
- ? Backend build qiladi
- ? PostgreSQL database yaratadi
- ? Redis cache serverini ishga tushiradi
- ? Backend API serverni ishga tushiradi
- ? Nginx reverse proxy ishga tushiradi

### 2.4. Tekshirish

```bash
# Health check
curl http://113.30.191.89/health

# API docs
curl http://113.30.191.89/docs

# Docker containerlar
docker-compose ps

# Logs
docker-compose logs -f
```

**Kutilgan natija:**
```json
{
  "status": "ok",
  "version": "1.0.0"
}
```

---

## ?? 3-QADAM: SSL o'rnatish (ixtiyoriy, domain bo'lsa)

### 3.1. Domain sozlash

Agar sizda domain bo'lsa (masalan: `traffic.example.com`):

```bash
# DNS sozlash
# Domain DNS sozlamalarida A record qo'shing:
# Type: A
# Name: @
# Value: 113.30.191.89
```

### 3.2. SSL certificate olish

```bash
cd /home/adminuser/traffic-platform
sudo ./deployment/setup-ssl.sh
```

### 3.3. Nginx konfiguratsiyani yangilash

```bash
nano deployment/nginx.conf
```

HTTPS qismini uncomment qiling va `server_name` ni domain nomiga o'zgartiring.

```bash
docker-compose restart nginx
```

---

## ?? 4-QADAM: Android App Setup

### 4.1. Frontend sozlash

Lokal kompyuteringizda:

```bash
cd frontend
npm install
```

### 4.2. API URL tekshirish

`frontend/src/api/client.ts` faylida:

```typescript
const API_BASE_URL = 'http://113.30.191.89/api';
```

### 4.3. Development test

```bash
# Android emulator yoki real device ulang
npm run android
```

### 4.4. Production build

```bash
cd android
./gradlew assembleRelease

# APK joylashuvi:
# android/app/build/outputs/apk/release/app-release.apk
```

APK ni qurilmaga o'rnating va test qiling.

---

## ?? 5-QADAM: Admin Panel sozlash

### 5.1. Admin sifatida kirish

Android ilovada Telegram orqali login qiling (admin Telegram ID bilan).

### 5.2. Kunlik narx belgilash

Backend API orqali:

```bash
curl -X POST http://113.30.191.89/api/admin/price/set \
  -H "Content-Type: application/json" \
  -d '{
    "admin_id": 599382114,
    "price_per_gb": 1.50,
    "message": "Bugungi narx: $1.50/GB"
  }'
```

Yoki Postman/Insomnia orqali test qiling.

---

## ?? 6-QADAM: Testing

### 6.1. Backend API test

```bash
# Health check
curl http://113.30.191.89/health

# Dashboard test (telegram_id ni o'zgartiring)
curl http://113.30.191.89/api/dashboard/599382114

# API documentation
# Browser da: http://113.30.191.89/docs
```

### 6.2. Database test

```bash
# Database ga kirish
docker-compose exec db psql -U traffic_user -d traffic_db

# Jadvalar ro'yxati
\dt

# Users jadvalini ko'rish
SELECT * FROM users LIMIT 5;

# Chiqish
\q
```

### 6.3. Android app test

1. ? Login with Telegram
2. ? Dashboard ko'rinishi
3. ? Balance tekshirish
4. ? Session start/stop
5. ? Withdraw test (minimal amount)

---

## ?? 7-QADAM: Monitoring va Maintenance

### 7.1. Logs monitoring

```bash
# Real-time logs
docker-compose logs -f

# Faqat backend
docker-compose logs -f backend

# Faqat database
docker-compose logs -f db

# Oxirgi 100 qator
docker-compose logs --tail=100
```

### 7.2. Resource monitoring

```bash
# Docker stats
docker stats

# Disk space
df -h

# Memory va CPU
htop  # yoki: top
```

### 7.3. Database backup

```bash
# Backup yaratish
docker-compose exec db pg_dump -U traffic_user traffic_db > backup_$(date +%Y%m%d).sql

# Restore
cat backup_20231102.sql | docker-compose exec -T db psql -U traffic_user traffic_db
```

### 7.4. Auto restart sozlash

Docker Compose allaqachon `restart: unless-stopped` ga sozlangan.

Server qayta ishga tushganda avtomatik ishga tushadi.

---

## ?? 8-QADAM: Troubleshooting

### Problem 1: Backend ishlamayapti

```bash
# Loglarni tekshiring
docker-compose logs backend

# Container holatini tekshiring
docker-compose ps

# Restart
docker-compose restart backend
```

### Problem 2: Database connection error

```bash
# Database container holatini tekshiring
docker-compose ps db
docker-compose logs db

# Restart
docker-compose restart db
```

### Problem 3: Nginx 502 Bad Gateway

```bash
# Backend ishlayotganini tekshiring
docker-compose ps backend

# Nginx konfiguratsiyani test qiling
docker-compose exec nginx nginx -t

# Restart
docker-compose restart nginx
```

### Problem 4: Disk to'lgan

```bash
# Disk space tekshiring
df -h

# Docker tozalash
docker system prune -a --volumes

# Eski loglarni tozalash
docker-compose logs > /dev/null
```

---

## ? 9-QADAM: Production checklist

Ishga tushirishdan oldin:

- [ ] `.env` fayldagi barcha parametrlar to'ldirilgan
- [ ] `JWT_SECRET` uzun va murakkab
- [ ] `ADMIN_IDS` to'g'ri
- [ ] Telegram bot ishlayapti
- [ ] Firebase FCM sozlangan
- [ ] Payment provider API keys to'g'ri
- [ ] Health check muvaffaqiyatli
- [ ] Database backup avtomatik sozlangan
- [ ] Firewall sozlangan (80, 443, 22)
- [ ] SSL certificate o'rnatilgan (domain bo'lsa)
- [ ] Monitoring sozlangan
- [ ] Android app production build tayyor

---

## ?? Yordam

Muammo yuzaga kelsa:

1. Loglarni tekshiring: `docker-compose logs -f`
2. Container holatini tekshiring: `docker-compose ps`
3. Health check: `curl http://113.30.191.89/health`
4. API docs: `http://113.30.191.89/docs`

---

## ?? Tayyor!

Loyiha muvaffaqiyatli ishga tushdi. Foydalanuvchilar Android app orqali login qilishlari va trafik ulashishni boshlashlari mumkin.

**VPS URLs:**
- API: `http://113.30.191.89/api`
- Docs: `http://113.30.191.89/docs`
- Health: `http://113.30.191.89/health`
