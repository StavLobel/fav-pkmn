# Deployment Guide

## VPS Details

- **Host**: Hostinger VPS `69.62.119.109`
- **User**: `favpkmn` (non-root, docker group)
- **Stack**: Caddy (reverse proxy) + nginx (app) + Autoheal

---

## One-Time VPS Setup

### 1. Generate SSH key pair (on your local machine)

```bash
ssh-keygen -t ed25519 -C "favpkmn-deploy" -f ~/.ssh/favpkmn-deploy -N ""
cat ~/.ssh/favpkmn-deploy.pub
# Copy the output for step 3
```

### 2. SSH into VPS as root

```bash
ssh root@69.62.119.109
```

### 3. Create the favpkmn user (as root on VPS)

```bash
useradd -m -s /bin/bash favpkmn
usermod -aG docker favpkmn

mkdir -p /home/favpkmn/.ssh
echo "PASTE_YOUR_PUBLIC_KEY_HERE" > /home/favpkmn/.ssh/authorized_keys
chmod 700 /home/favpkmn/.ssh
chmod 600 /home/favpkmn/.ssh/authorized_keys
chown -R favpkmn:favpkmn /home/favpkmn/.ssh
```

### 4. Test SSH access (open a SECOND terminal, keep root open)

```bash
ssh -i ~/.ssh/favpkmn-deploy favpkmn@69.62.119.109
```

Only proceed if this works.

### 5. Harden SSH (back in root session)

```bash
sed -i 's/^#*PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config
sed -i 's/^#*PasswordAuthentication.*/PasswordAuthentication no/' /etc/ssh/sshd_config
echo "AllowUsers favpkmn" >> /etc/ssh/sshd_config
systemctl restart ssh
```

### 6. Configure firewall (as root)

```bash
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable
exit
```

### 7. Deploy the app (as favpkmn)

```bash
ssh -i ~/.ssh/favpkmn-deploy favpkmn@69.62.119.109

# Log into GitHub Container Registry
docker login ghcr.io -u StavLobel -p <YOUR_GHCR_PAT>

# Clone the repo
git clone https://github.com/StavLobel/fav-pkmn.git ~/fav-pkmn
cd ~/fav-pkmn

# Start the stack
docker compose -f docker-compose.prod.yml up -d

# Verify
curl http://localhost
```

---

## GitHub Secrets

Set these in the repo at Settings > Secrets > Actions:

| Secret | Value |
|--------|-------|
| `VPS_HOST` | `69.62.119.109` |
| `VPS_USER` | `favpkmn` |
| `VPS_SSH_KEY` | Contents of `~/.ssh/favpkmn-deploy` (private key) |

The workflow uses `GITHUB_TOKEN` for GHCR, so no separate token secret is needed.

---

## SSH Shortcut (optional)

Add to `~/.ssh/config` on your local machine:

```
Host favpkmn
    HostName 69.62.119.109
    User favpkmn
    IdentityFile ~/.ssh/favpkmn-deploy
```

Then connect with: `ssh favpkmn`

---

## Operations

### View logs

```bash
ssh favpkmn "cd ~/fav-pkmn && docker compose -f docker-compose.prod.yml logs -f"
```

### Restart the app

```bash
ssh favpkmn "cd ~/fav-pkmn && docker compose -f docker-compose.prod.yml restart web"
```

### Restart everything

```bash
ssh favpkmn "cd ~/fav-pkmn && docker compose -f docker-compose.prod.yml down && docker compose -f docker-compose.prod.yml up -d"
```

### Manual deploy (pull latest image)

```bash
ssh favpkmn "cd ~/fav-pkmn && docker compose -f docker-compose.prod.yml pull web && docker compose -f docker-compose.prod.yml up -d web"
```

### Update Caddyfile or compose config

```bash
ssh favpkmn "cd ~/fav-pkmn && git pull && docker compose -f docker-compose.prod.yml up -d"
```

---

## Adding a Domain

1. Point an A record to `69.62.119.109`
2. Edit `deploy/Caddyfile` -- replace `:80` with your domain name
3. Push to main -- CI deploys the change
4. Caddy auto-provisions a Let's Encrypt TLS certificate

---

## Adding Another Project to This VPS

Create a new Linux user per project for isolation:

```bash
# As root (or via a user with sudo)
useradd -m -s /bin/bash newproject
usermod -aG docker newproject
# Add to AllowUsers in /etc/ssh/sshd_config
```

Each user manages its own Docker Compose stack from its home directory.
