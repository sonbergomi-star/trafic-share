# Loyiha Xulosa - Traffic Sharing Platform

## Yaratilgan Struktura

### ? Backend (FastAPI)
1. **API Endpointlar** (`backend/app/api/v1/`):
   - `/api/auth/telegram` - Telegram autentifikatsiya
   - `/api/dashboard/{telegram_id}` - Dashboard ma'lumotlari
   - `/api/traffic/start` - Trafik sessiyasini boshlash
   - `/api/traffic/stop` - Trafik sessiyasini to'xtatish
   - `/api/traffic/report` - Trafik hisobotlari
   - `/api/user/balance/{telegram_id}` - Balans ma'lumotlari
   - `/api/withdraw` - Pul yechish
   - `/api/stats/*` - Statistika API
   - `/api/sessions/*` - Sessiyalar API
   - `/api/support/*` - Qo'llab-quvvatlash
   - `/api/news/*` - Yangiliklar va promo-kodlar
   - `/api/profile/*` - Profil boshqaruvi
   - `/api/admin/*` - Admin panel API
   - `/api/daily_price` - Kunlik narx

2. **Database Modellar** (`backend/app/models/`):
   - `User` - Foydalanuvchilar
   - `TrafficSession` - Trafik sessiyalari
   - `SessionReport` - Sessiya hisobotlari
   - `Transaction` - Tranzaksiyalar
   - `WithdrawRequest` - Pul yechish so'rovlari
   - `DailyPrice` - Kunlik narxlar
   - `Announcement` - E'lonlar
   - `PromoCode` - Promo-kodlar
   - `SupportRequest` - Support so'rovlari
   - `FilterAudit` - Filter audit loglari

3. **Services** (`backend/app/services/`):
   - `auth_service.py` - Autentifikatsiya
   - `user_service.py` - Foydalanuvchi boshqaruvi
   - `dashboard_service.py` - Dashboard logikasi
   - `daily_price_service.py` - Narx boshqaruvi
   - `notification_service.py` - FCM bildirishnomalar

4. **Core Utilities** (`backend/app/core/`):
   - `config.py` - Konfiguratsiya
   - `database.py` - Database ulanishi
   - `jwt_manager.py` - JWT token boshqaruvi
   - `telegram_auth.py` - Telegram autentifikatsiya tekshiruvi

### ? Android App Strukturasi
1. **API Integration**:
   - `ApiClient.kt` - Retrofit client
   - `ApiService.kt` - API interfeyslar
   - `Models.kt` - Data modellar

2. **Data Management**:
   - `PreferencesManager.kt` - Local storage

3. **Configuration**:
   - `build.gradle` - Dependencies
   - `AndroidManifest.xml` - Permissions va services

### ? Deployment
1. **Docker**:
   - `Dockerfile` - Container image
   - `docker-compose.yml` - Multi-container setup

2. **Systemd Service**:
   - `deploy.sh` - Avtomatik deployment script
   - `DEPLOYMENT_GUIDE.md` - Batafsil qo'llanma

## VPS Serverga O'rnatish

### Tezkor Start:

1. **Loyihani yuklab olish**:
```bash
cd /home/adminuser
# Repository yoki fayllarni yuklash
```

2. **Deployment scriptni ishga tushirish**:
```bash
chmod +x deploy.sh
./deploy.sh
```

3. **Environment sozlash**:
```bash
cd backend
cp .env.example .env
nano .env  # Ma'lumotlarni to'ldiring
```

4. **Database migration**:
```bash
# Alembic migration yaratish va ishga tushirish
alembic upgrade head
```

5. **Service ishga tushirish**:
```bash
sudo systemctl start traffic-backend
sudo systemctl status traffic-backend
```

## API Endpointlar (Asosiy)

### Auth
- `POST /api/auth/telegram` - Telegram orqali kirish

### Dashboard
- `GET /api/dashboard/{telegram_id}` - Dashboard ma'lumotlari
- `GET /api/daily_price` - Kunlik narx

### Traffic
- `POST /api/traffic/start` - Sessiyani boshlash
- `POST /api/traffic/stop?session_id={id}` - Sessiyani to'xtatish
- `POST /api/traffic/report` - Trafik hisoboti

### Balance
- `GET /api/user/balance/{telegram_id}` - Balans ma'lumotlari
- `POST /api/user/refresh_balance?telegram_id={id}` - Balansni yangilash

### Withdraw
- `POST /api/withdraw` - Pul yechish so'rovi
- `GET /api/withdraw` - Yechish tarixi

### Admin
- `GET /api/admin/dashboard/summary` - Admin statistika
- `GET /api/admin/users` - Foydalanuvchilar ro'yxati
- `POST /api/admin/daily_price` - Narx belgilash

## API Dokumentatsiyasi

Ishga tushgandan keyin:
- Swagger UI: `http://113.30.191.89/docs`
- ReDoc: `http://113.30.191.89/redoc`

## Keyingi Qadamlar

### Backend:
1. ? Asosiy struktura yaratildi
2. ? Alembic migration fayllarini yaratish
3. ? Worker (Celery) qo'shish (payout processing uchun)
4. ? IP filtering logikasini to'liq implement qilish
5. ? WebSocket real-time updates

### Android:
1. ? API client va modellar yaratildi
2. ? UI sahifalarni yaratish
3. ? Telegram Login Widget integratsiyasi
4. ? FCM notification service
5. ? Traffic monitoring service

### Deployment:
1. ? Docker va systemd service konfiguratsiyasi
2. ? SSL sertifikat (Let's Encrypt)
3. ? Monitoring va logging setup
4. ? Backup automation

## Muhim Eslatmalar

1. **Environment Variables**: `.env` faylida barcha kerakli ma'lumotlarni to'ldiring
2. **Database**: PostgreSQL database va foydalanuvchi yaratilgan bo'lishi kerak
3. **Redis**: Redis server ishga tushgan bo'lishi kerak (cache va queue uchun)
4. **Firewall**: 80 va 443 portlar ochiq bo'lishi kerak
5. **Telegram Bot**: Bot token va username sozlang
6. **FCM**: Firebase Cloud Messaging server key sozlang

## Qo'llab-quvvatlash

Savollar uchun:
- Backend API: `http://113.30.191.89/docs`
- Support sahifasi: Ilova ichida

---

**Yaratilgan sana**: 2025-01-XX
**Versiya**: 1.0.0
**Status**: ? Asosiy struktura tayyor, deployment kerak
