# Plant Moisture Monitor - Docker Deployment Guide

Deploy the Plant Moisture Monitor to your Portainer/Docker stack on your full-time server.

---

## Architecture Overview

```
┌─────────────────────────────────────┐
│    Internet / Home Network          │
└────────────────┬────────────────────┘
                 │
        ┌────────▼────────┐
        │  Nginx Reverse  │
        │     Proxy       │
        │  (Port 80/443)  │
        └────────┬────────┘
         ┌───────┴──────┬────────────────┐
         │              │                │
   ┌─────▼──────┐  ┌──▼──────┐    ┌────▼────────┐
   │   Static   │  │ API     │    │ Health      │
   │  Dashboard │  │ Proxy   │    │ Checks      │
   └────────────┘  └──┬──────┘    └─────────────┘
                      │
              ┌───────▼──────────┐
              │  FastAPI Backend │
              │  (Port 8000)     │
              │  Container       │
              └───────┬──────────┘
                      │
           ┌──────────▼──────────┐
           │  SQLite Database    │
           │  (Persistent Volume)│
           └─────────────────────┘
```

---

## Files Included

- `docker-compose.yml` - Service definitions
- `Dockerfile.api` - FastAPI container build
- `nginx.conf` - Nginx reverse proxy configuration
- `requirements.txt` - Python dependencies
- `backend.py` - FastAPI application
- `dashboard.html` - Web UI (served by Nginx)

---

## Prerequisites

- Portainer running on your server
- Docker and Docker Compose installed
- Access to your home server IP address
- (Optional) SSL certificates for HTTPS

---

## Deployment Methods

### Method 1: Portainer UI (Easiest)

1. **Clone or upload files** to your server:
   ```bash
   git clone <your-repo-url> /opt/plants-monitor
   # OR upload files manually to that directory
   ```

2. **Open Portainer Dashboard**
   - Navigate to your Portainer instance (usually `http://server-ip:9000`)

3. **Create Stack**
   - Click **Stacks** → **Add stack**
   - Name: `plants-monitor`
   - Paste contents of `docker-compose.yml`
   - Click **Deploy the stack**

4. **Verify Services Started**
   - Check **Containers** to see `plants-api` and `plants-nginx` running
   - Both should show **healthy** status

5. **Access Dashboard**
   - Open browser: `http://your-server-ip`
   - Should see Plant Moisture Monitor dashboard

---

### Method 2: Docker Compose CLI (Advanced)

1. **SSH into server**:
   ```bash
   ssh user@your-server-ip
   ```

2. **Clone repository**:
   ```bash
   cd /opt
   git clone <your-repo-url> plants-monitor
   cd plants-monitor
   ```

3. **Start stack**:
   ```bash
   docker-compose up -d
   ```

4. **Monitor logs**:
   ```bash
   docker-compose logs -f plants-api
   docker-compose logs -f plants-nginx
   ```

5. **Stop stack**:
   ```bash
   docker-compose down
   ```

---

### Method 3: Portainer Git Integration (CI/CD)

1. **Push to Git repository**:
   ```bash
   git init
   git add .
   git commit -m "Add Docker deployment files"
   git push origin main
   ```

2. **In Portainer UI**:
   - **Stacks** → **Add stack**
   - Select **Repository** tab
   - Enter Git URL, branch, and path to `docker-compose.yml`
   - Portainer auto-deploys on Git updates

---

## Configuration

### For Local Network Access

The stack is configured for local network access by default:

```bash
# Access dashboard
http://192.168.1.100  # Replace with your server IP
```

No additional configuration needed.

### For HTTPS/SSL

1. **Obtain SSL certificates** (Let's Encrypt or self-signed):
   ```bash
   # Let's Encrypt with certbot
   sudo certbot certonly --standalone -d your-domain.com
   ```

2. **Copy certificates to server**:
   ```bash
   mkdir -p nginx-ssl
   cp /etc/letsencrypt/live/your-domain.com/fullchain.pem nginx-ssl/cert.pem
   cp /etc/letsencrypt/live/your-domain.com/privkey.pem nginx-ssl/key.pem
   chmod 644 nginx-ssl/*.pem
   ```

3. **Uncomment HTTPS section** in `nginx.conf`:
   ```nginx
   # Redirect HTTP to HTTPS
   return 301 https://$host$request_uri;

   # HTTPS server block (uncomment and configure)
   server {
       listen 443 ssl http2;
       server_name your-domain.com;
       # ... rest of SSL config
   }
   ```

4. **Restart containers**:
   ```bash
   docker-compose restart plants-nginx
   ```

### Environment Variables

Create `.env` file for environment-specific settings:

```bash
# .env (in same directory as docker-compose.yml)
DB_PATH=/data/plants.db
API_HOST=0.0.0.0
API_PORT=8000
NGINX_HOST=your-domain.com
```

Update `docker-compose.yml` to use:
```yaml
services:
  plants-api:
    environment:
      - DATABASE_URL=sqlite:///${DB_PATH}
```

---

## Database Persistence

The database is stored in a Docker volume `plants-data`:

```bash
# View volume location
docker volume inspect plants_plants-data

# Backup database
docker volume create plants-backup
docker run --rm -v plants_plants-data:/source -v plants-backup:/backup \
  alpine cp /source/plants.db /backup/

# Restore from backup
docker run --rm -v plants_plants-data:/dest -v plants-backup:/source \
  alpine cp /source/plants.db /dest/
```

---

## Health Checks

Both containers include health checks:

```bash
# Check container health
docker ps

# View health status in logs
docker-compose logs plants-api
docker-compose logs plants-nginx
```

Expected output:
```
plants-api      up (healthy)
plants-nginx    up (healthy)
```

---

## Monitoring & Logs

### Real-time Logs

```bash
# API logs
docker-compose logs -f plants-api

# Nginx logs
docker-compose logs -f plants-nginx

# Both services
docker-compose logs -f
```

### View via Portainer

1. Go to **Containers**
2. Click `plants-api` → **Logs** tab
3. Watch real-time output

### Historical Logs

```bash
# Last 100 lines
docker-compose logs --tail 100 plants-api

# Specific time range
docker-compose logs --since 2025-11-26T10:00:00 plants-api
```

---

## Troubleshooting

### Services won't start

```bash
# Check errors
docker-compose logs plants-api
docker-compose logs plants-nginx

# Restart with verbose output
docker-compose up plants-api
```

### Database permission errors

```bash
# Fix volume permissions
docker exec plants-api mkdir -p /app/data
docker exec plants-api chmod 777 /app/data
```

### Nginx can't reach API

```bash
# Verify API is responding
docker exec plants-nginx curl http://plants-api:8000/

# Check network connectivity
docker network inspect plants_plants-network
```

### High memory usage

```bash
# Reduce number of workers in Dockerfile
CMD ["uvicorn", "backend:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]

# Rebuild and restart
docker-compose up -d --build
```

---

## Updating the Stack

### Update code

```bash
# Pull latest from Git
cd /opt/plants-monitor
git pull origin main

# Rebuild and restart
docker-compose up -d --build
```

### Update dependencies

1. Edit `requirements.txt` with new versions
2. Rebuild containers:
   ```bash
   docker-compose up -d --build
   ```

### Update configuration

1. Edit `nginx.conf` or environment variables
2. Restart service:
   ```bash
   docker-compose restart plants-nginx
   # or
   docker-compose restart plants-api
   ```

---

## Performance Tuning

### Nginx Worker Processes

In `nginx.conf`:
```nginx
worker_processes auto;  # Uses all CPU cores
```

### API Worker Processes

In `Dockerfile.api`:
```dockerfile
# Single-core server
CMD ["uvicorn", "backend:app", "--workers", "1"]

# Multi-core server
CMD ["uvicorn", "backend:app", "--workers", "4"]
```

### Database Connection Pool

In `backend.py`:
```python
# Adjust connection pool size
engine = create_engine(
    DATABASE_URL,
    connect_args={"timeout": 10, "check_same_thread": False},
    pool_size=5,
    max_overflow=10
)
```

---

## Backup & Restore

### Backup Database

```bash
# Stop containers (optional, for consistency)
docker-compose pause plants-api

# Export database
docker run --rm -v plants_plants-data:/data -v $(pwd):/backup \
  alpine tar czf /backup/plants-db-$(date +%Y%m%d-%H%M%S).tar.gz /data/

# Resume containers
docker-compose unpause plants-api
```

### Restore Database

```bash
# Stop API to release database lock
docker-compose stop plants-api

# Restore from backup
docker run --rm -v plants_plants-data:/data -v $(pwd):/backup \
  alpine tar xzf /backup/plants-db-YYYYMMDD-HHMMSS.tar.gz -C /

# Restart API
docker-compose start plants-api
```

---

## Security Considerations

### Network Security

- [ ] API is only accessible through Nginx proxy
- [ ] Database is not exposed to network
- [ ] Use HTTPS in production (see SSL setup above)
- [ ] Configure firewall rules on host

### API Security

```bash
# Add rate limiting in nginx.conf
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;

location /api/ {
    limit_req zone=api_limit burst=20 nodelay;
    ...
}
```

### Database Backups

- [ ] Automated daily backups to separate drive
- [ ] Test restore procedures regularly
- [ ] Store backups off-site

---

## Scaling

### Multiple API Instances

For higher load, use Docker Swarm or Kubernetes:

```yaml
services:
  plants-api:
    deploy:
      replicas: 3  # Run 3 instances
      resources:
        limits:
          cpus: '0.5'
          memory: 256M
```

### Load Testing

```bash
# Install Apache Bench
apt-get install apache2-utils

# Test API
ab -n 1000 -c 10 http://localhost:8000/devices

# Test dashboard
ab -n 1000 -c 10 http://localhost/dashboard.html
```

---

## Maintenance Schedule

**Daily**:
- [ ] Monitor logs for errors
- [ ] Check container health status

**Weekly**:
- [ ] Backup database
- [ ] Review logs for patterns

**Monthly**:
- [ ] Update Docker images
- [ ] Review and optimize resource usage
- [ ] Test backup/restore procedures

**Quarterly**:
- [ ] Update dependencies to latest stable versions
- [ ] Security audit
- [ ] Capacity planning

---

## Docker Compose Reference Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View status
docker-compose ps

# View logs
docker-compose logs -f

# Rebuild images
docker-compose build

# Rebuild and restart
docker-compose up -d --build

# Remove data volumes (WARNING: deletes database!)
docker-compose down -v

# Execute command in container
docker-compose exec plants-api bash

# Restart service
docker-compose restart plants-api

# Scale service to 3 replicas
docker-compose up -d --scale plants-api=3
```

---

## Exposing to Internet (Advanced)

If you want to access from outside your home network:

### Option 1: Reverse Proxy (Recommended)

Set up Nginx/Caddy on a VPS:
```nginx
server {
    listen 80;
    server_name plants.yourdomain.com;

    location / {
        proxy_pass http://YOUR_HOME_IP:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Option 2: Port Forwarding

1. Forward port 80/443 in router to server (risky!)
2. Use dynamic DNS for changing home IP
3. Strongly recommend HTTPS

### Option 3: VPN

1. Set up WireGuard/OpenVPN on home server
2. Connect remotely via VPN
3. Access at local IP (`192.168.x.x`)
4. Most secure option

---

## Troubleshooting Checklist

- [ ] Containers are running: `docker-compose ps`
- [ ] API is responding: `curl http://localhost:8000/`
- [ ] Nginx can reach API: `docker-compose logs plants-nginx`
- [ ] Database file exists: `docker volume inspect plants_plants-data`
- [ ] Ports are not in use: `netstat -tulpn | grep 80`
- [ ] Network exists: `docker network ls | grep plants`

---

## Next Steps

1. **Deploy to Portainer** using Method 1 or 2 above
2. **Verify connectivity** from browser
3. **Test API endpoints** with curl
4. **Set up SSL** when domain is ready
5. **Configure automated backups** for reliability
6. **Monitor logs** for first 24 hours
7. **Add to monitoring** (Grafana, Prometheus, etc.) if desired

---

## Support

For issues:
1. Check logs: `docker-compose logs -f`
2. Verify containers: `docker-compose ps`
3. Test connectivity: `curl http://localhost:8000/`
4. Check Portainer UI for container health status

---

**Status**: Docker stack ready for deployment
**Last Updated**: 2025-11-26
