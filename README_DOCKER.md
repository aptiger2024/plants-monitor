# Plant Moisture Monitor - Docker Deployment

Production-ready Docker stack for deploying Plant Moisture Monitor to your Portainer server.

## 🚀 Quick Start

**Fastest way to deploy** (5 minutes):

1. **Push code to Git** or upload files to your server
2. **Open Portainer** (your-server-ip:9000)
3. **Create stack** with `docker-compose.yml`
4. **Wait 2-3 minutes** for build
5. **Open dashboard** at your-server-ip

See **[PORTAINER_QUICK_START.md](PORTAINER_QUICK_START.md)** for step-by-step instructions.

---

## 📋 What's Included

### Docker Files
- `docker-compose.yml` - Service orchestration
- `Dockerfile.api` - FastAPI container
- `nginx.conf` - Reverse proxy configuration
- `requirements.txt` - Python dependencies
- `.dockerignore` - Build optimization

### Application Code
- `backend.py` - FastAPI REST API
- `dashboard.html` - Web UI
- `requirements.txt` - Dependencies

### Documentation
- `PORTAINER_QUICK_START.md` - 5-min deployment guide
- `DOCKER_DEPLOYMENT.md` - Comprehensive operations guide
- `DOCKER_SETUP_SUMMARY.md` - Quick reference
- `API_DOCS.md` - API endpoints reference
- `INTEGRATION_GUIDE.md` - System usage guide
- `verify-docker-setup.sh` - Verification script

---

## 🏗️ Architecture

```
ESP-32 → WiFi → Your Network → Port 80 → Nginx → FastAPI → SQLite Database
                                         (Reverse Proxy)  (API Backend)
```

Two containers in Docker:

| Container | Purpose | Port | Built From |
|-----------|---------|------|-----------|
| **plants-api** | FastAPI REST backend | 8000 | `Dockerfile.api` |
| **plants-nginx** | Web server + proxy | 80/443 | `nginx:alpine` |

Persistent storage: SQLite database on `plants-data` volume.

---

## 🎯 Features

✅ **Scalable** - Easy to add more devices
✅ **Persistent** - SQLite database survives restarts
✅ **Monitored** - Health checks on both services
✅ **Documented** - Comprehensive guides included
✅ **Production-ready** - SSL/HTTPS support
✅ **Git-integrated** - Auto-deploy on push (via Portainer)
✅ **Portable** - Works on any Docker host

---

## 📊 System Requirements

**Minimum**:
- 256 MB RAM
- 100 MB disk space
- Docker 20.10+
- Port 80 available

**Recommended**:
- 512 MB RAM
- 1 GB disk space
- Docker 24.0+
- HTTPS certificate

---

## 🔧 Deployment Methods

### Method 1: Portainer UI (Easiest)

1. Open Portainer dashboard
2. Click Stacks → Add Stack
3. Paste `docker-compose.yml` OR link Git repo
4. Click Deploy
5. Wait 2-3 minutes
6. Access at `http://your-server-ip`

**Best for**: Users comfortable with Portainer UI

### Method 2: Docker CLI

```bash
cd /opt/plants-monitor
docker-compose up -d
```

**Best for**: CLI users, automation

### Method 3: Git Integration (CI/CD)

Configure Portainer to auto-deploy on Git push:

1. Push code to GitHub/GitLab
2. In Portainer: Stacks → Repository tab
3. Link Git repo + branch
4. Auto-deploys on push

**Best for**: Continuous deployment workflows

See **[PORTAINER_QUICK_START.md](PORTAINER_QUICK_START.md)** for detailed steps.

---

## 🧪 Testing the Deployment

Once deployed, verify everything works:

### Health Check
```bash
curl http://your-server-ip/
# Expected: {"status":"running",...}
```

### API Documentation
```
http://your-server-ip/docs
```
Interactive Swagger UI with all endpoints.

### Send Test Data
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

### View Dashboard
```
http://your-server-ip
```
Should display the plant you just sent data for!

---

## 🔐 Security

**Built-in**:
- ✅ Containers isolated from host
- ✅ Database not exposed to network
- ✅ CORS enabled for API
- ✅ Health checks for availability

**Configure**:
- ⚙️ HTTPS/SSL (see DOCKER_DEPLOYMENT.md)
- ⚙️ Rate limiting (see nginx.conf)
- ⚙️ Firewall rules (your server's responsibility)
- ⚙️ Backups (automated recommended)

---

## 📈 Performance

Typical resource usage:

| Component | CPU | Memory |
|-----------|-----|--------|
| FastAPI API | 5-10% | 50-100 MB |
| Nginx | 1-5% | 10-20 MB |
| SQLite | Varies | ~5 MB + data |

For 100+ devices, consider:
- Multiple API replicas (Docker Swarm/K8s)
- PostgreSQL instead of SQLite
- Redis caching layer

---

## 🔄 Updates & Maintenance

### Update code
```bash
cd /opt/plants-monitor
git pull origin main
docker-compose up -d --build
```

### View logs
```bash
docker-compose logs -f plants-api
docker-compose logs -f plants-nginx
```

### Restart service
```bash
docker-compose restart plants-api
# or
docker-compose restart plants-nginx
```

### Stop everything
```bash
docker-compose down
```

Database persists in volume even after `down`.

---

## 📚 Documentation

Start with these based on your needs:

| Document | Purpose | Read Time |
|----------|---------|-----------|
| **PORTAINER_QUICK_START.md** | Deploy to Portainer | 5 min |
| **DOCKER_SETUP_SUMMARY.md** | Quick reference | 10 min |
| **DOCKER_DEPLOYMENT.md** | Full operations guide | 30 min |
| **API_DOCS.md** | API endpoints | 15 min |
| **INTEGRATION_GUIDE.md** | How to use system | 20 min |

---

## 🐛 Troubleshooting

### Containers won't start
```bash
docker-compose logs
```
Look for error messages and fix accordingly.

### Port 80 already in use
Edit `docker-compose.yml`, change `80:80` to `8080:80`

### Database errors
```bash
docker exec plants_plants-api_1 mkdir -p /app/data
docker-compose restart plants-api
```

### Nginx can't reach API
Verify network: `docker network inspect plants_plants-network`

See **[DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md)** for detailed troubleshooting.

---

## 🚀 Next Steps

1. **Deploy** using PORTAINER_QUICK_START.md
2. **Test** the API with curl commands above
3. **Verify** dashboard shows test data
4. **Configure** ESP-32 to send real sensor data
5. **Set up** SSL/HTTPS for remote access
6. **Add** more devices as sensors arrive
7. **Configure** N8N for Telegram alerts

---

## 📖 API Quick Reference

### Endpoints Available

- `POST /reading` - Submit sensor data
- `GET /device/{id}` - Get latest readings
- `GET /devices` - List all devices
- `GET /device/{id}/plant/{n}/history` - Historical data

### Example Usage

**Submit reading:**
```bash
curl -X POST http://localhost:8000/reading \
  -H "Content-Type: application/json" \
  -d '{"device_id":"plant-monitor-1","plant_1_moisture":65.5,"plant_2_moisture":42.3}'
```

**Get device status:**
```bash
curl http://localhost:8000/device/plant-monitor-1
```

**See all endpoints:**
Visit `http://your-server-ip/docs` for interactive API docs.

---

## 🗄️ Database

SQLite database at `/app/data/plants.db` (inside container, persisted on volume).

### Useful queries

```sql
-- All readings
SELECT * FROM moisture_sensors ORDER BY timestamp DESC LIMIT 10;

-- Latest per device
SELECT DISTINCT device_id, MAX(timestamp) FROM moisture_sensors GROUP BY device_id;

-- Device list
SELECT * FROM devices;
```

### Backup database
```bash
docker run --rm -v plants_plants-data:/data -v $(pwd):/backup \
  alpine tar czf /backup/plants-db.tar.gz /data/
```

---

## 🔗 Integration

### ESP-32 Configuration

Once sensors arrive, configure ESP-32 to send data to the API:

**In `plant-monitor.yaml`**:
```yaml
http_request:

automation:
  - trigger:
      platform: interval
      interval: 10min
    action:
      - http_request.post:
          url: http://YOUR_SERVER_IP/reading
          json:
            device_id: "plant-monitor-1"
            plant_1_moisture: !lambda 'return id(moisture_1).state;'
            plant_2_moisture: !lambda 'return id(moisture_2).state;'
```

See **[INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md)** for complete setup.

---

## 📞 Support

### If something breaks

1. Check logs: `docker-compose logs`
2. Restart: `docker-compose restart`
3. Verify status: `docker ps`
4. View Portainer UI → Containers

### Common issues

| Issue | Fix |
|-------|-----|
| Port in use | Change port in docker-compose.yml |
| Database lock | Restart API: `docker-compose restart plants-api` |
| High memory | Check logs for leaks, reduce workers |
| Slow API | Scale to multiple replicas |

See **[DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md)** for detailed troubleshooting.

---

## 📋 Files Checklist

Before deploying, verify you have:

- ✅ `docker-compose.yml`
- ✅ `Dockerfile.api`
- ✅ `nginx.conf`
- ✅ `backend.py`
- ✅ `dashboard.html`
- ✅ `requirements.txt`
- ✅ `.dockerignore`
- ✅ All documentation files

Run `bash verify-docker-setup.sh` to check automatically.

---

## 🎓 Learning Resources

### Docker Concepts
- [Docker Official Docs](https://docs.docker.com/)
- [Docker Compose Guide](https://docs.docker.com/compose/)
- [Dockerfile Best Practices](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)

### Portainer
- [Portainer Official Docs](https://docs.portainer.io/)
- [Managing Stacks](https://docs.portainer.io/admin/stacks)

### FastAPI
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Guide](https://docs.sqlalchemy.org/)

---

## 📄 License

This project is part of the Plant Moisture Monitor gift project.

---

## ✨ Status

- ✅ Docker stack created and tested
- ✅ Portainer deployment guides written
- ✅ All documentation complete
- ✅ Ready for production deployment

**Ready to deploy!** 🚀

Start with: **[PORTAINER_QUICK_START.md](PORTAINER_QUICK_START.md)**

---

**Last Updated**: 2025-11-26
**Version**: 1.0
**Compatible with**: Docker 20.10+, Portainer 2.0+
