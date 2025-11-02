# ? Quick Start Guide

## ?? 5 daqiqada ishga tushiring!

### 1?? Lokal kompyuterdan deployment

```bash
cd /path/to/traffic-platform

# .env faylni sozlang
nano backend/.env

# Deploy qiling
chmod +x deployment/deploy.sh
./deployment/deploy.sh
```

### 2?? VPS ga SSH qiling

```bash
ssh adminuser@113.30.191.89
cd /home/adminuser/traffic-platform
```

### 3?? Servislarni ishga tushiring

```bash
./deployment/start.sh
```

### 4?? Tekshiring

```bash
# Health check
curl http://113.30.191.89/health

# Result:
# {"status":"ok","version":"1.0.0"}
```

### 5?? Android app

```bash
# Lokal kompyuterda
cd frontend
npm install
npm run android
```

## ? Tayyor!

- **API**: http://113.30.191.89/api
- **Docs**: http://113.30.191.89/docs
- **Health**: http://113.30.191.89/health

---

## ?? Muhim .env parametrlar

```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_BOT_USERNAME=your_bot_username
ADMIN_IDS=599382114,605472971
JWT_SECRET=very-long-secret-key-here
FCM_SERVER_KEY=your_fcm_key
PAYMENT_PROVIDER_API_KEY=your_payment_key
```

---

## ?? Asosiy funksiyalar

? Telegram OAuth login  
? Dashboard (balans, trafik, narx)  
? Traffic sharing (START/STOP)  
? Withdraw (USDT BEP20)  
? Statistics & Analytics  
? Session history  
? Push notifications  
? Admin panel  

---

## ?? Foydali komandalar

```bash
# Restart
docker-compose restart

# Logs
docker-compose logs -f

# Stop
docker-compose stop

# Status
docker-compose ps
```

---

Batafsil qo'llanma: **SETUP_GUIDE.md**
