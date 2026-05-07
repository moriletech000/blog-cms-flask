# Production Deployment Guide

Complete guide for deploying Blog CMS to production.

## Pre-Deployment Checklist

### 1. Server Requirements

**Minimum Specifications:**
- 2 CPU cores
- 4GB RAM
- 20GB disk space
- Ubuntu 20.04+ or similar Linux distribution

**Software Requirements:**
- Docker 20.10+
- Docker Compose 2.0+
- Git

### 2. Domain and DNS

- Register a domain name
- Point A record to your server IP
- Configure DNS (may take 24-48 hours to propagate)

### 3. SSL Certificate

**Option A: Let's Encrypt (Recommended)**
```bash
# Install certbot
sudo apt-get update
sudo apt-get install certbot

# Generate certificate
sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com

# Certificates will be in /etc/letsencrypt/live/yourdomain.com/
```

**Option B: Commercial Certificate**
- Purchase from a CA
- Follow CA's installation instructions

## Deployment Steps

### Step 1: Server Setup

```bash
# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Install Git
sudo apt-get install git -y
```

### Step 2: Clone Repository

```bash
# Clone to /opt or your preferred location
cd /opt
sudo git clone <repository-url> blog-cms
cd blog-cms
sudo chown -R $USER:$USER .
```

### Step 3: Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit environment variables
nano .env
```

**Critical Production Settings:**

```bash
# Flask
FLASK_ENV=production
FLASK_SECRET_KEY=<generate-with: openssl rand -hex 32>
FLASK_DEBUG=0

# Database
DATABASE_URL=postgresql://bloguser:<strong-password>@postgres:5432/blogdb

# Redis
REDIS_URL=redis://redis:6379/0

# Celery
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/1

# Email (use your SMTP provider)
MAIL_SERVER=smtp.sendgrid.net
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=apikey
MAIL_PASSWORD=<your-sendgrid-api-key>
MAIL_DEFAULT_SENDER=noreply@yourdomain.com

# JWT
JWT_SECRET_KEY=<generate-with: openssl rand -hex 32>
JWT_ACCESS_TOKEN_EXPIRES=3600
JWT_REFRESH_TOKEN_EXPIRES=604800

# Rate Limiting
RATELIMIT_STORAGE_URI=redis://redis:6379/2

# Sentry (optional but recommended)
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id

# PostgreSQL
POSTGRES_DB=blogdb
POSTGRES_USER=bloguser
POSTGRES_PASSWORD=<strong-password>
```

### Step 4: Configure SSL

```bash
# Create SSL directory
mkdir -p nginx/ssl

# Copy Let's Encrypt certificates
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem nginx/ssl/cert.pem
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem nginx/ssl/key.pem
sudo chown $USER:$USER nginx/ssl/*
```

**Edit nginx/nginx.conf:**

Uncomment the HTTPS server block and update:

```nginx
server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers off;

    # ... rest of configuration
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}
```

### Step 5: Build and Start

```bash
# Build images
docker compose build

# Start services
docker compose up -d

# Check status
docker compose ps

# View logs
docker compose logs -f
```

### Step 6: Initialize Database

```bash
# Run migrations
docker compose exec flask flask db upgrade

# Seed database
docker compose exec flask flask seed-db

# Create admin user
docker compose exec flask flask create-admin \
  --email admin@yourdomain.com \
  --password <secure-password>
```

### Step 7: Verify Deployment

1. **Check services:**
```bash
docker compose ps
# All services should show "Up"
```

2. **Test website:**
```bash
curl -I https://yourdomain.com
# Should return 200 OK
```

3. **Test API:**
```bash
curl https://yourdomain.com/api/v1/posts
# Should return JSON response
```

4. **Check logs:**
```bash
docker compose logs flask
docker compose logs celery
docker compose logs nginx
```

## Post-Deployment Configuration

### 1. Set Up Automated Backups

**Database Backup Script:**

```bash
# Create backup script
sudo nano /usr/local/bin/backup-blog-db.sh
```

```bash
#!/bin/bash
BACKUP_DIR="/backups/blog-cms"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

# Backup database
docker compose -f /opt/blog-cms/docker-compose.yml exec -T postgres \
  pg_dump -U bloguser blogdb | gzip > $BACKUP_DIR/db_$DATE.sql.gz

# Keep only last 30 days
find $BACKUP_DIR -name "db_*.sql.gz" -mtime +30 -delete

echo "Backup completed: db_$DATE.sql.gz"
```

```bash
# Make executable
sudo chmod +x /usr/local/bin/backup-blog-db.sh

# Add to crontab (daily at 2 AM)
sudo crontab -e
# Add: 0 2 * * * /usr/local/bin/backup-blog-db.sh
```

**Image Backup:**

```bash
# Backup uploads directory
rsync -av /opt/blog-cms/app/static/uploads/ /backups/blog-cms/uploads/
```

### 2. Set Up Log Rotation

```bash
# Create logrotate config
sudo nano /etc/logrotate.d/blog-cms
```

```
/opt/blog-cms/logs/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
    sharedscripts
    postrotate
        docker compose -f /opt/blog-cms/docker-compose.yml restart nginx
    endscript
}
```

### 3. Set Up Monitoring

**Install monitoring tools:**

```bash
# Install htop for resource monitoring
sudo apt-get install htop

# Monitor Docker containers
docker stats

# Set up Sentry for error tracking (already configured in .env)
```

### 4. Configure Firewall

```bash
# Install UFW
sudo apt-get install ufw

# Allow SSH
sudo ufw allow 22/tcp

# Allow HTTP and HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Enable firewall
sudo ufw enable

# Check status
sudo ufw status
```

### 5. Set Up Auto-Renewal for SSL

```bash
# Test renewal
sudo certbot renew --dry-run

# Add to crontab (runs twice daily)
sudo crontab -e
# Add: 0 0,12 * * * certbot renew --quiet --post-hook "docker compose -f /opt/blog-cms/docker-compose.yml restart nginx"
```

## Maintenance

### Regular Tasks

**Daily:**
- Check logs for errors
- Monitor disk space
- Verify backups completed

**Weekly:**
- Review Sentry errors
- Check performance metrics
- Update content

**Monthly:**
- Update Docker images
- Review and optimize database
- Test backup restoration

### Update Procedure

```bash
# Pull latest code
cd /opt/blog-cms
git pull

# Rebuild and restart
docker compose build
docker compose up -d

# Run migrations
docker compose exec flask flask db upgrade

# Clear cache
docker compose exec flask flask clear-cache
```

### Scaling

**Horizontal Scaling:**

```yaml
# In docker-compose.yml, scale Flask workers
flask:
  deploy:
    replicas: 3
    
celery:
  deploy:
    replicas: 2
```

**Vertical Scaling:**

```yaml
# Increase resources
flask:
  deploy:
    resources:
      limits:
        cpus: '2'
        memory: 2G
```

## Troubleshooting

### Services Won't Start

```bash
# Check logs
docker compose logs

# Restart specific service
docker compose restart flask

# Rebuild if needed
docker compose build --no-cache flask
docker compose up -d
```

### Database Connection Issues

```bash
# Check PostgreSQL
docker compose logs postgres

# Restart database
docker compose restart postgres

# Check connection
docker compose exec postgres psql -U bloguser -d blogdb -c "SELECT 1;"
```

### High Memory Usage

```bash
# Check resource usage
docker stats

# Restart services
docker compose restart

# Reduce worker count if needed
# Edit docker-compose.yml and reduce Celery concurrency
```

### SSL Certificate Issues

```bash
# Check certificate expiry
sudo certbot certificates

# Renew manually
sudo certbot renew

# Restart nginx
docker compose restart nginx
```

## Security Hardening

### 1. Disable Root Login

```bash
sudo nano /etc/ssh/sshd_config
# Set: PermitRootLogin no
sudo systemctl restart sshd
```

### 2. Set Up Fail2Ban

```bash
sudo apt-get install fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

### 3. Regular Updates

```bash
# Set up automatic security updates
sudo apt-get install unattended-upgrades
sudo dpkg-reconfigure --priority=low unattended-upgrades
```

### 4. Database Security

```bash
# Change default passwords
# Restrict PostgreSQL access to localhost only
# Use strong passwords (20+ characters)
```

## Performance Optimization

### 1. Enable Gzip Compression

Already configured in nginx.conf

### 2. Optimize PostgreSQL

```bash
# Edit PostgreSQL config
docker compose exec postgres bash
nano /var/lib/postgresql/data/postgresql.conf

# Increase shared_buffers (25% of RAM)
shared_buffers = 1GB

# Increase work_mem
work_mem = 16MB

# Restart PostgreSQL
docker compose restart postgres
```

### 3. Redis Optimization

```bash
# Set maxmemory policy
docker compose exec redis redis-cli CONFIG SET maxmemory 512mb
docker compose exec redis redis-cli CONFIG SET maxmemory-policy allkeys-lru
```

## Monitoring and Alerts

### Set Up Email Alerts

```bash
# Install mailutils
sudo apt-get install mailutils

# Create monitoring script
sudo nano /usr/local/bin/monitor-blog.sh
```

```bash
#!/bin/bash
# Check if services are running
if ! docker compose -f /opt/blog-cms/docker-compose.yml ps | grep -q "Up"; then
    echo "Blog CMS services are down!" | mail -s "ALERT: Blog CMS Down" admin@yourdomain.com
fi
```

```bash
# Make executable and add to crontab
sudo chmod +x /usr/local/bin/monitor-blog.sh
sudo crontab -e
# Add: */5 * * * * /usr/local/bin/monitor-blog.sh
```

## Disaster Recovery

### Backup Restoration

```bash
# Stop services
docker compose down

# Restore database
gunzip < /backups/blog-cms/db_20240101_020000.sql.gz | \
  docker compose exec -T postgres psql -U bloguser blogdb

# Restore uploads
rsync -av /backups/blog-cms/uploads/ /opt/blog-cms/app/static/uploads/

# Start services
docker compose up -d
```

### Complete System Recovery

1. Set up new server
2. Install Docker and dependencies
3. Clone repository
4. Restore .env file
5. Restore database backup
6. Restore uploads
7. Start services

---

**Your Blog CMS is now production-ready! 🚀**

For support, check the main README.md or open an issue on GitHub.