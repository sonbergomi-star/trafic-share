## VPS Deployment Guide (Ubuntu 24.04)

Target host: `adminuser@113.30.191.89`

### 1. Prerequisites

- Ensure SSH access with `ssh adminuser@113.30.191.89`
- Update the OS and install Docker + Compose plugin:

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo $VERSION_CODENAME) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo usermod -aG docker $USER
```

Log out/in to apply docker group membership.

### 2. Clone Repository

```bash
git clone https://your.repo.url.git traffic-platform
cd traffic-platform
```

### 3. Configure Environment

Copy the backend environment template and adjust secrets:

```bash
cp backend/.env.example backend/.env
``` 

Edit `backend/.env` with production secrets (JWT, Telegram, FCM, etc.).

### 4. Build & Run Containers

```bash
docker compose pull
docker compose build
docker compose up -d
```

### 5. Database Migration

```bash
docker compose exec backend alembic upgrade head
```

### 6. Systemd Service (Optional)

Create `/etc/systemd/system/traffic-platform.service`:

```
[Unit]
Description=Traffic Platform Stack
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
WorkingDirectory=/home/adminuser/traffic-platform
ExecStart=/usr/bin/docker compose up -d
ExecStop=/usr/bin/docker compose down
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
```

Enable service:

```bash
sudo systemctl enable --now traffic-platform.service
```

### 7. Firewall

Expose backend on port 8000 or behind reverse proxy:

```bash
sudo ufw allow 22/tcp
sudo ufw allow 8000/tcp
sudo ufw enable
```

### 8. Logs & Monitoring

```bash
docker compose logs -f backend
docker compose logs -f worker
```

### 9. Android App Configuration

- Update `BuildConfig.BASE_URL` (release build already points to `https://113.30.191.89`).
- Ensure HTTPS certificate in front of backend for production use.

### 10. Backup & Updates

- Use `docker compose down` before updating.
- Take PostgreSQL dumps regularly (`docker compose exec db pg_dump`).
