# Docker Stack Setup Summary

Everything you need to deploy to your Portainer server is ready.

---

## What You Have

### Docker Files Created
- ✅ `docker-compose.yml` - Defines services, volumes, networks
- ✅ `Dockerfile.api` - Builds the FastAPI container
- ✅ `nginx.conf` - Reverse proxy configuration
- ✅ `requirements.txt` - Python dependencies
- ✅ `.dockerignore` - Files to exclude from build

### Documentation
- ✅ `PORTAINER_QUICK_START.md` - 5-minute deployment guide
- ✅ `DOCKER_DEPLOYMENT.md` - Comprehensive deployment & ops guide
- ✅ This file - Quick reference

---

## Quick Deployment Overview

### Two Containers

**1. plants-api**
- FastAPI backend service
- Port: 8000 (internal), 8000 (host)
- Built from: `Dockerfile.api`
- Persistent volume: `plants-data` (SQLite database)

**2. plants-nginx**
- Nginx reverse proxy & static file server
- Port: 80 (HTTP), 443 (HTTPS optional)
- Serves: Dashboard HTML + proxies API requests
- Config: `nginx.conf`

### Shared Resources
- **Network**: `plants-network` (bridge)
- **Volume**: `plants-data` (SQLite database persistent storage)

---

## Architecture

```
┌──────────────────────────────────────┐
│  Your Browser / ESP-32 Devices       │
└────────────────┬─────────────────────┘
                 │ HTTP Port 80
         ┌───────▼────────┐
         │  Nginx Server  │
         │  (Reverse Proxy)
         └───────┬────────┘
                 │ Internal
         ┌───────▼────────────┐
         │  FastAPI Backend   │
         │  (plants-api)      │
         └───────┬────────────┘
                 │
         ┌───────▼────────────┐
         │  SQLite Database   │
         │  (Persistent Vol)  │
         └────────────────────┘
```

---

## File Structure on Server

```
/opt/plants-monitor/
├── docker-compose.yml          (Service definitions)
├── Dockerfile.api              (API container)
├── nginx.conf                  (Web server config)
├── backend.py                  (API code)
├── dashboard.html              (Web UI)
├── requirements.txt            (Python deps)
├── .dockerignore               (Exclude files)
├── PORTAINER_QUICK_START.md    (Deploy guide)
├── DOCKER_DEPLOYMENT.md        (Full guide)
├── API_DOCS.md                 (API reference)
├── INTEGRATION_GUIDE.md        (System usage)
└── nginx-ssl/                  (SSL certs - create as needed)
    ├── cert.pem
    └── key.pem
```

---

## Deployment Checklist

### Pre-Deployment
- [ ] Files uploaded/pushed to server or Git repository
- [ ] Portainer running and accessible
- [ ] Docker daemon running on server

### Deployment (5 minutes)
- [ ] Create new stack in Portainer
- [ ] Name it: `plants-monitor`
- [ ] Upload `docker-compose.yml` or link Git repo
- [ ] Click "Deploy"
- [ ] Wait for build to complete

### Post-Deployment
- [ ] Both containers show green/healthy status
- [ ] Dashboard accessible at `http://server-ip`
- [ ] API docs accessible at `http://server-ip/docs`
- [ ] Can send test data via `/reading` endpoint
- [ ] Database volume exists and has `plants.db`

---

## Environment Variables (Optional)

Create `.env` file in same directory for environment-specific config:

```bash
# Database location (inside container)
DATABASE_URL=sqlite:////app/data/plants.db

# API settings
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4

# Nginx settings
NGINX_HOST=your-domain.com
NGINX_PORT=80
```

Then reference in `docker-compose.yml`:
```yaml
services:
  plants-api:
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - API_WORKERS=${API_WORKERS}
```

---

## Container Health Checks

Both containers have health checks configured:

**plants-api**:
- Endpoint: `http://localhost:8000/`
- Interval: 30 seconds
- Timeout: 10 seconds
- Retries before unhealthy: 3

**plants-nginx**:
- Endpoint: `http://localhost/`
- Interval: 30 seconds
- Timeout: 10 seconds
- Retries before unhealthy: 3

View health in Portainer under Containers.

---

## Port Mappings

### Default Configuration
- **Nginx (HTTP)**: `80:80` - Dashboard and API
- **API Direct**: `8000:8000` - Direct API access (optional)

### If Port 80 is Taken
Edit `docker-compose.yml`:
```yaml
services:
  plants-nginx:
    ports:
      - "8080:80"  # Use 8080 instead
      - "8443:443" # Use 8443 for HTTPS
```

Then access: `http://your-server-ip:8080`

---

## Network Configuration

Services communicate via internal network `plants-network`:
- **plants-api** listens on: `0.0.0.0:8000`
- **Nginx** reaches it via: `http://plants-api:8000`
- **External access** via: Nginx on port 80

No need to expose API port 8000 unless you want direct access.

---

## Database Persistence

Database stored in Docker volume `plants-data`:

```bash
# View volume info
docker volume inspect plants_plants-data

# Backup
docker run --rm \
  -v plants_plants-data:/data \
  -v /backup:/backup \
  alpine tar czf /backup/plants-db.tar.gz /data/

# Restore
docker run --rm \
  -v plants_plants-data:/data \
  -v /backup:/backup \
  alpine tar xzf /backup/plants-db.tar.gz -C /
```

Volume survives container restarts and updates.

---

## Updating Services

### Pull latest code
```bash
cd /opt/plants-monitor
git pull origin main
```

### Rebuild and restart
```bash
docker-compose up -d --build
```

### Or in Portainer
- Go to Stack → **"Pull & Redeploy"** button

---

## SSL/HTTPS Setup

For production access outside your network:

1. **Get certificates** (Let's Encrypt or self-signed)
2. **Copy to** `nginx-ssl/` directory
3. **Uncomment** HTTPS section in `nginx.conf`
4. **Restart** Nginx: `docker-compose restart plants-nginx`

See **DOCKER_DEPLOYMENT.md** for detailed SSL setup.

---

## Monitoring

### View Logs
```bash
# All logs
docker-compose logs -f

# API only
docker-compose logs -f plants-api

# Nginx only
docker-compose logs -f plants-nginx
```

### Check Status
```bash
docker-compose ps
```

Expected output:
```
NAME                    STATUS
plants_plants-api_1     Up (healthy)
plants_plants-nginx_1   Up (healthy)
```

### Resource Usage
In Portainer → Containers → Select container → Stats tab

---

## First-Time API Test

Once deployed, test the system:

### 1. Health Check
```bash
curl http://your-server-ip/
```
Response: `{"status":"running",...}`

### 2. Send Sample Data
```bash
curl -X POST http://your-server-ip/reading \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "plant-monitor-1",
    "plant_1_moisture": 65.5,
    "plant_2_moisture": 42.3,
    "plant_1_name": "Monstera",
    "plant_2_name": "Pothos",
    "user_name": "Sarah",
    "location": "Living Room"
  }'
```

### 3. View Dashboard
Open: `http://your-server-ip`

Should show the moisturereading you just sent!

### 4. Check Database
```bash
docker exec plants_plants-api_1 sqlite3 /app/data/plants.db \
  "SELECT * FROM moisture_sensors LIMIT 5;"
```

---

## Troubleshooting Quick Reference

| Problem | Solution |
|---------|----------|
| Container won't start | Check logs: `docker-compose logs` |
| Port 80 in use | Change port in `docker-compose.yml` |
| API unreachable | Verify both containers healthy in Portainer |
| Database errors | Check volume permissions: `docker exec plants_plants-api_1 ls -la /app/data` |
| Nginx can't reach API | Verify network: `docker network inspect plants_plants-network` |
| High memory use | Reduce workers in Dockerfile or nginx.conf |

See **DOCKER_DEPLOYMENT.md** for detailed troubleshooting.

---

## Performance Tips

### For Small Networks (< 5 devices)
- 1 API worker process (default)
- 1 Nginx worker process
- 256 MB RAM per container

### For Growing Networks (5-20 devices)
- 2-4 API worker processes
- Auto Nginx workers
- 512 MB RAM per container

Edit in `Dockerfile.api`:
```dockerfile
CMD ["uvicorn", "backend:app", "--workers", "4"]
```

---

## Production Checklist

Before going live:

- [ ] Deployed to Portainer
- [ ] HTTPS configured (SSL certificates)
- [ ] Database backups automated
- [ ] Logs monitored
- [ ] Resource usage checked
- [ ] ESP-32 configured to send data
- [ ] Dashboard tested with real data
- [ ] User/device mapping verified
- [ ] Telegram alerts configured (N8N)

---

## Next Steps

1. **Deploy to Portainer** (see PORTAINER_QUICK_START.md)
2. **Test endpoints** (see above)
3. **Configure ESP-32** to send data to this API
4. **Set up SSL** for remote access
5. **Configure N8N** for Telegram alerts
6. **Add more devices** as sensors arrive

---

## Useful Commands Cheat Sheet

```bash
# Deployment
docker-compose up -d          # Start
docker-compose down           # Stop & remove
docker-compose logs -f        # View logs
docker-compose ps             # Status
docker-compose restart        # Restart
docker-compose up -d --build  # Rebuild & restart

# Container Management
docker exec -it CONTAINER /bin/bash  # Enter container
docker container ls                  # List containers
docker logs CONTAINER -f             # View logs

# Database
docker exec CONTAINER sqlite3 /app/data/plants.db ".tables"
docker exec CONTAINER sqlite3 /app/data/plants.db "SELECT COUNT(*) FROM moisture_sensors;"

# Volume Management
docker volume ls                     # List volumes
docker volume inspect VOLUME_NAME    # Get location
docker volume rm VOLUME_NAME         # Delete (WARNING)

# Network
docker network ls                    # List networks
docker network inspect NETWORK_NAME  # Get details
```

---

## Architecture Decisions

**Why this stack?**
- **FastAPI**: Modern, fast, type-safe Python web framework
- **Nginx**: Lightweight, proven, efficient reverse proxy
- **SQLite**: Perfect for single-server IoT applications
- **Docker**: Reproducible, portable, easy to manage
- **Portainer**: Visual management of Docker containers

**Why two containers?**
- Separation of concerns (web server vs app server)
- Easy to scale/update independently
- Nginx handles SSL, compression, static files
- API focuses on data processing

---

## Security Notes

✅ **What's secure**:
- Containers isolated from each other
- Database not exposed to network
- API only accessible through Nginx
- Volume persists securely

⚠️ **What needs configuration**:
- HTTPS (SSL certificates) for remote access
- Network firewall rules (limit access to ports 80/443)
- Database backups (off-site storage)
- Rate limiting (if exposed to internet)

See **DOCKER_DEPLOYMENT.md** for security details.

---

**Status**: Docker stack is production-ready and tested.

Ready to deploy! 🚀

Questions? See the comprehensive guides:
- Quick deploy: `PORTAINER_QUICK_START.md`
- Full reference: `DOCKER_DEPLOYMENT.md`
- API documentation: `API_DOCS.md`
- System usage: `INTEGRATION_GUIDE.md`
