# Deployment Guide - VPS Server

## Server Ma'lumotlari
- **IP Address**: 113.30.191.89
- **OS**: Ubuntu 24.04
- **Username**: adminuser
- **Backend Port**: 8000
- **Nginx Port**: 80

## Qadam-baqadam Deployment

### 1. Serverga ulanish
```bash
ssh adminuser@113.30.191.89
```

### 2. System yangilanishi va kerakli paketlar
```bash
sudo apt-get update && sudo apt-get upgrade -y
sudo apt-get install -y python3 python3-pip python3-venv postgresql postgresql-contrib redis-server nginx git curl
```

### 3. PostgreSQL sozlash
```bash
sudo -u postgres psql
```

PostgreSQL ichida:
```sql
CREATE DATABASE traffic_db;
CREATE USER traffic_user WITH PASSWORD 'your_secure_password_here';
GRANT ALL PRIVILEGES ON DATABASE traffic_db TO traffic_user;
\q
```

### 4. Redis sozlash
```bash
sudo systemctl enable redis-server
sudo systemctl start redis-server
sudo systemctl status redis-server
```

### 5. Loyihani yuklab olish
```bash
cd /home/adminuser
# Git repository yoki fayllarni yuklash
# Masalan: git clone <repo-url>
# yoki: scp bilan fayllarni ko'chirish
```

### 6. Python virtual environment
```bash
cd /home/adminuser/traffic-platform/backend
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 7. Environment o'zgaruvchilarini sozlash
```bash
cp .env.example .env
nano .env
```

`.env` faylida quyidagilarni to'ldiring:
```env
DATABASE_URL=postgresql://traffic_user:your_password@localhost/traffic_db
JWT_SECRET=your_very_secure_jwt_secret_key_here
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_BOT_USERNAME=your_bot_username
ADMIN_IDS=599382114,605472971
FCM_SERVER_KEY=your_fcm_server_key
REDIS_URL=redis://localhost:6379/0
```

### 8. Database migration
```bash
# Alembic migration yaratish (agar kerak bo'lsa)
# Alembic fayllarini sozlash
alembic upgrade head
```

### 9. Systemd service yaratish
```bash
sudo nano /etc/systemd/system/traffic-backend.service
```

Quyidagi kontentni kiriting:
```ini
[Unit]
Description=Traffic Sharing Platform Backend
After=network.target postgresql.service redis.service

[Service]
User=adminuser
Group=adminuser
WorkingDirectory=/home/adminuser/traffic-platform/backend
Environment="PATH=/home/adminuser/traffic-platform/backend/venv/bin"
ExecStart=/home/adminuser/traffic-platform/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Service ni ishga tushirish:
```bash
sudo systemctl daemon-reload
sudo systemctl enable traffic-backend
sudo systemctl start traffic-backend
sudo systemctl status traffic-backend
```

### 10. Nginx reverse proxy sozlash
```bash
sudo nano /etc/nginx/sites-available/traffic-platform
```

Kontent:
```nginx
server {
    listen 80;
    server_name 113.30.191.89;

    client_max_body_size 10M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
    }

    location /static {
        alias /home/adminuser/traffic-platform/backend/static;
    }
}
```

Enable qilish:
```bash
sudo ln -s /etc/nginx/sites-available/traffic-platform /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 11. Firewall sozlash (UFW)
```bash
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### 12. Test qilish
```bash
# Backend health check
curl http://localhost:8000/health

# Nginx orqali
curl http://113.30.191.89/health

# API docs
# Browserda ochish: http://113.30.191.89/docs
```

## Service boshqarish

```bash
# Status tekshirish
sudo systemctl status traffic-backend

# Qayta ishga tushirish
sudo systemctl restart traffic-backend

# Loglarni ko'rish
sudo journalctl -u traffic-backend -f

# To'xtatish
sudo systemctl stop traffic-backend

# Ishga tushirish
sudo systemctl start traffic-backend
```

## Database backup

```bash
# Backup yaratish
pg_dump -U traffic_user traffic_db > backup_$(date +%Y%m%d).sql

# Restore qilish
psql -U traffic_user traffic_db < backup_20250101.sql
```

## Monitoring

- Loglar: `sudo journalctl -u traffic-backend -n 100`
- Nginx loglar: `/var/log/nginx/`
- PostgreSQL loglar: `/var/log/postgresql/`

## Xavfsizlik

1. SSH key-based authentication
2. Fail2ban o'rnatish
3. SSL sertifikat (Let's Encrypt) - keyingi qadam
4. Regular security updates

## Muammolar hal qilish

### Backend ishlamayapti
```bash
sudo journalctl -u traffic-backend -n 50
# Xatolarni tekshirish
```

### Database ulanish muammosi
```bash
sudo -u postgres psql -c "\l"
# Database mavjudligini tekshirish
```

### Port band
```bash
sudo netstat -tulpn | grep 8000
# Port holatini ko'rish
```
