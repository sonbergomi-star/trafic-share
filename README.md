## Traffic Sharing Platform

Full-stack project that delivers a Telegram-authenticated dashboard for bandwidth sharing, real-time analytics, balance management, withdraw flows, notifications and support tooling. The stack consists of a FastAPI backend, PostgreSQL, Redis, and an Expo/React Native Android app.

### Project layout

```
/backend      ? FastAPI application
/frontend     ? React Native (Expo) Android app
docker-compose.yml
README.md
```

### Backend quick start (development)

```bash
cd backend
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python -m app.db.init_db  # create tables
uvicorn app.main:app --reload
```

The API will be available on `http://127.0.0.1:8000` with docs at `/docs`.

### React Native app (Expo)

```bash
cd frontend
npm install
npm run android        # requires Android Studio emulator or device
```

Update `app.json` ? `extra.apiUrl` to point at your backend domain/IP before building the Android app.

### Docker / docker-compose

```bash
docker compose up -d --build
```

This spins up:

- `backend` (FastAPI + Uvicorn)
- `db` (PostgreSQL 15)
- `redis` (Redis 7)

Exposed ports: backend `8000`, Postgres `5432`, Redis `6379`.

### VPS deployment (Ubuntu 24.04 on 113.30.191.89)

SSH into the server:

```bash
ssh adminuser@113.30.191.89
```

Install Docker & Compose:

```bash
sudo apt update && sudo apt install -y ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list
sudo apt update && sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo usermod -aG docker adminuser && newgrp docker
```

Deploy the stack:

```bash
git clone <repo-url> traffic-platform
cd traffic-platform
cp backend/.env.example backend/.env   # adjust secrets (JWT, Telegram bot, FCM, etc.)
docker compose up -d --build
```

Create a systemd unit for automatic start:

```
sudo tee /etc/systemd/system/traffic.service > /dev/null <<'EOF'
[Unit]
Description=Traffic Sharing Backend
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
WorkingDirectory=/home/adminuser/traffic-platform
RemainAfterExit=yes
ExecStart=/usr/bin/docker compose up -d
ExecStop=/usr/bin/docker compose down

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl enable --now traffic.service
```

Reverse proxy (optional) with Nginx for TLS:

```bash
sudo apt install -y nginx certbot python3-certbot-nginx
sudo certbot --nginx -d api.yourdomain.com
```

Proxy block:

```
location / {
    proxy_pass http://127.0.0.1:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

### Environment variables

`backend/.env.example` lists required variables:

- `DATABASE_URL`
- `REDIS_URL`
- `TELEGRAM_BOT_USERNAME`, `TELEGRAM_BOT_TOKEN`
- `JWT_SECRET`
- `FCM_SERVER_KEY` (optional)
- `ADMIN_IDS`

### API highlights

- `POST /api/auth/telegram` ? Telegram Login widget authentication.
- `GET /api/dashboard/{telegram_id}` ? consolidated dashboard.
- `POST /api/traffic/start|stop` ? start/stop traffic sessions with filter logic.
- `POST /api/user/refresh_balance`, `POST /api/withdraw` ? balance operations.
- `GET /api/stats/{daily|weekly|monthly}/{telegram_id}` ? analytics.
- `POST /api/support/send` ? support ticket, plus history endpoints.
- Admin endpoints under `/api/admin/*` for dashboards and metrics.

### Mobile app highlights

- Telegram widget auth (WebView).
- Dashboard with balance, traffic metrics, real-time price banner and start/stop controls.
- Analytics charts (daily/weekly/monthly).
- Balance view with withdraw workflow and transaction list.
- Session history, settings (toggles, logout), support form, news/promo cards.

### Testing

- Backend unit tests can be added using `pytest`. Current code ships with DB init script only.
- Expo app uses TypeScript; run `npx tsc --noEmit` for type checking.

### Next steps

- Harden security (OAuth state, HTTPS everywhere).
- Add Celery worker for notifications / withdraw payouts.
- Implement automated CI/CD pipelines.
- Extend Android app with offline caching and push notification listeners.

