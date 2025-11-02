# Traffic Sharing Platform

Bu loyiha Android ilova va backend tizimini o'z ichiga oladi. Foydalanuvchilar o'z internet trafiklarini boshqalar bilan ulashish va daromad olish imkoniyatiga ega bo'ladilar.

## Loyiha Strukturasi

```
traffic-platform/
??? backend/          # FastAPI backend
?   ??? app/
?   ?   ??? api/      # API endpointlar
?   ?   ??? models/   # Database modellar
?   ?   ??? services/ # Business logic
?   ?   ??? core/     # Core utilities
??? android/          # Android ilova (keyingi qadam)
??? deploy.sh         # VPS deployment skripti
```

## VPS Deployment

### Server Ma'lumotlari
- IP: 113.30.191.89
- OS: Ubuntu 24.04
- Username: adminuser

### Deployment Qadamlari

1. **Serverga ulanish:**
```bash
ssh adminuser@113.30.191.89
```

2. **Loyihani yuklab olish:**
```bash
git clone <repository-url>
cd traffic-platform
```

3. **Deployment skriptini ishga tushirish:**
```bash
chmod +x deploy.sh
./deploy.sh
```

4. **Environment o'zgaruvchilarini sozlash:**
```bash
cd backend
cp .env.example .env
nano .env  # Ma'lumotlarni to'ldiring
```

5. **Database migration:**
```bash
alembic upgrade head
```

6. **Servisni qayta ishga tushirish:**
```bash
sudo systemctl restart traffic-backend
```

## Backend API

API asosiy manzil: `http://113.30.191.89:8000` yoki `http://113.30.191.89`

### Asosiy Endpointlar

- `POST /api/auth/telegram` - Telegram orqali autentifikatsiya
- `GET /api/dashboard/{telegram_id}` - Dashboard ma'lumotlari
- `POST /api/traffic/start` - Trafik sessiyasini boshlash
- `POST /api/traffic/stop` - Trafik sessiyasini to'xtatish
- `GET /api/user/balance/{telegram_id}` - Balans ma'lumotlari
- `POST /api/withdraw` - Pul yechish so'rovi

To'liq API dokumentatsiyasi: `http://113.30.191.89/docs`

## Environment Variables

Kerakli environment o'zgaruvchilar `.env.example` faylida ko'rsatilgan:

- `DATABASE_URL` - PostgreSQL connection string
- `JWT_SECRET` - JWT token secret key
- `TELEGRAM_BOT_TOKEN` - Telegram bot token
- `FCM_SERVER_KEY` - Firebase Cloud Messaging server key
- `ADMIN_IDS` - Admin foydalanuvchilar IDlari (vergul bilan ajratilgan)

## Development

### Lokal ishga tushirish

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# .env faylini sozlash
cp .env.example .env

# Database yaratish
# PostgreSQL ishga tushirilgan bo'lishi kerak

# Migration
alembic upgrade head

# Serverni ishga tushirish
uvicorn app.main:app --reload
```

## Android Ilova

Android ilova qismi keyingi qadamda qo'shiladi.

## Qo'llab-quvvatlash

Savollar yoki muammolar bo'lsa, support sahifasi orqali murojaat qiling.
