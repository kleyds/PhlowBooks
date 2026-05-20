# PhlowBooks Ubuntu Docker Deploy

This guide assumes a fresh Ubuntu server and a repo clone from GitHub.

## 1. Prepare the server

```bash
sudo apt update
sudo apt upgrade -y
sudo apt install -y ca-certificates curl git ufw
```

Allow SSH and web traffic:

```bash
sudo ufw allow OpenSSH
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
sudo ufw status
```

## 2. Install Docker Engine and Compose plugin

Follow Docker's official Ubuntu repository install flow:

```bash
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

Optional, so you can run Docker without `sudo`:

```bash
sudo usermod -aG docker $USER
newgrp docker
```

Verify:

```bash
docker --version
docker compose version
```

## 3. Clone and configure PhlowBooks

```bash
git clone https://github.com/kleyds/PhlowBooks.git
cd PhlowBooks
cp .env.server.example .env
nano .env
```

At minimum, change:

- `POSTGRES_PASSWORD`
- `SECRET_KEY`
- `API_KEY`
- `OPENAI_API_KEY`
- `FRONTEND_BASE_URL`
- `CORS_ORIGINS`
- SMTP settings, if email verification should send real email

Generate a good `SECRET_KEY`:

```bash
openssl rand -hex 32
```

For first testing by server IP, use:

```text
FRONTEND_BASE_URL=http://YOUR_SERVER_IP
CORS_ORIGINS=http://YOUR_SERVER_IP
```

When you add a real domain and HTTPS, update both to `https://yourdomain.com`.

## 4. Start the app

```bash
docker compose up -d --build
docker compose ps
```

Check logs:

```bash
docker compose logs -f api
docker compose logs -f frontend
```

Open:

```text
http://YOUR_SERVER_IP
```

## 5. Update after pushing new code

```bash
cd PhlowBooks
git pull
docker compose up -d --build
```

## 6. Useful maintenance

Stop the app:

```bash
docker compose down
```

Restart:

```bash
docker compose restart
```

View database volume and upload volume:

```bash
docker volume ls
```

Back up Postgres:

```bash
docker compose exec db pg_dump -U phlowbooks phlowbooks > phlowbooks-backup.sql
```

Do not run `docker compose down -v` unless you intentionally want to delete the database and uploaded files.
