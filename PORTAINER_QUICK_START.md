# Plant Moisture Monitor - Portainer Quick Start

Deploy to Portainer in under 5 minutes.

---

## Prerequisites

✅ Portainer running on your server
✅ Docker daemon accessible from Portainer
✅ Git repository with Docker files (OR upload manually)

---

## Step-by-Step Deployment

### Step 1: Prepare Files

**Option A: Using Git (Recommended)**

Push all files to your Git repository:
```bash
cd D:\nextcloud\projects\plants
git add .
git commit -m "Add Docker deployment"
git push origin main
```

Copy the Git URL: `https://github.com/username/plants-monitor.git`

**Option B: Manual Upload**

If not using Git, you'll paste the `docker-compose.yml` content directly in Portainer.

---

### Step 2: Open Portainer

1. Open browser: `http://your-server-ip:9000`
2. Login with your Portainer credentials
3. Select your Docker endpoint (usually "local")

---

### Step 3: Create New Stack

1. **Click "Stacks"** on left menu
2. **Click "+ Add stack"** button
3. **Enter name**: `plants-monitor`
4. **Choose upload method**:

#### If using Git:
- Select **Repository** tab
- Enter repository URL: `https://github.com/username/plants-monitor.git`
- Enter compose path: `docker-compose.yml`
- Branch: `main` (or your branch)
- Click **"Deploy the stack"**

#### If uploading manually:
- Select **Editor** tab
- Paste entire contents of `docker-compose.yml`
- Click **"Deploy the stack"**

---

### Step 4: Wait for Deployment

Portainer will:
1. Build the `plants-api` Docker image
2. Start `plants-nginx` container
3. Create persistent volume for database
4. Configure networking

**Time to complete**: 1-3 minutes

---

### Step 5: Verify Services Are Running

1. **Go to Containers** tab
2. **Look for**:
   - `plants_plants-api_1` → Status should be **green/healthy**
   - `plants_plants-nginx_1` → Status should be **green/healthy**

If either shows red/unhealthy, click it to view logs.

---

### Step 6: Access the Dashboard

Open browser: **`http://your-server-ip`**

You should see the Plant Moisture Monitor dashboard!

---

## Verification Checklist

- [ ] Both containers show green status in Portainer
- [ ] Dashboard loads at `http://your-server-ip`
- [ ] API responds at `http://your-server-ip/docs` (Swagger docs)
- [ ] Can select different users/plants without errors

---

## View Logs

If something doesn't work:

1. **In Portainer**:
   - Click container name
   - Click **"Logs"** tab
   - Look for error messages

2. **Helpful commands**:
   ```bash
   # SSH to server
   ssh user@your-server-ip

   # View API logs
   docker logs plants_plants-api_1

   # View Nginx logs
   docker logs plants_plants-nginx_1
   ```

---

## Common Issues

### "Failed to connect to database"
- **Cause**: Database file wasn't created
- **Fix**:
  ```bash
  docker exec plants_plants-api_1 mkdir -p /app/data
  docker restart plants_plants-api_1
  ```

### "Nginx can't reach API"
- **Cause**: Services not on same network
- **Fix**: Delete stack, redeploy

### "Port 80 already in use"
- **Cause**: Something else using port 80
- **Fix**: Edit `docker-compose.yml`, change to different port:
  ```yaml
  plants-nginx:
    ports:
      - "8080:80"  # Use 8080 instead
  ```

### Dashboard shows mock data, not real data
- **Cause**: API not available
- **Fix**: Check that `plants-api` container is healthy

---

## Configuration

### Change API Port

Edit `docker-compose.yml`:
```yaml
services:
  plants-api:
    ports:
      - "8001:8000"  # Changed from 8000 to 8001
```

### Add SSL/HTTPS

1. Copy your SSL certificates to server
2. Edit `nginx.conf` (uncomment HTTPS section)
3. Restart: `docker-compose restart plants-nginx`

See **DOCKER_DEPLOYMENT.md** for detailed SSL setup.

---

## Stopping/Restarting

### Via Portainer UI
1. Go to **Stacks**
2. Click **plants-monitor** stack
3. Click **"Stop"** or **"Restart"**

### Via Command Line
```bash
# Stop
docker-compose stop

# Start
docker-compose start

# Restart
docker-compose restart
```

---

## Testing the API

Once deployed, test endpoints:

### Health Check
```bash
curl http://your-server-ip/
```
Expected: `{"status":"running",...}`

### API Documentation
Open: `http://your-server-ip/docs`

You'll see interactive Swagger UI with all endpoints.

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

### Get Device Data
```bash
curl http://your-server-ip/device/plant-monitor-1
```

---

## Auto-Updates with Git

If you set up Git repository integration in Portainer:

1. **Push updates to Git**:
   ```bash
   git add .
   git commit -m "Update backend"
   git push origin main
   ```

2. **Portainer automatically** pulls and redeplooys

3. **To manually trigger**, go to Stack → **Pull & Redeploy**

---

## Backup Database

```bash
# SSH to server
ssh user@your-server-ip

# Create backup
docker run --rm -v plants_plants-data:/data -v $(pwd):/backup \
  alpine tar czf /backup/plants-db-backup.tar.gz /data/

# Download backup to your computer
scp user@your-server-ip:~/plants-db-backup.tar.gz .
```

---

## Monitor Resource Usage

In **Portainer**:
1. Go to **Containers**
2. Select each container
3. View **Stats** tab for CPU/Memory/Network usage

Typical usage:
- API: 50-100 MB RAM
- Nginx: 10-20 MB RAM
- Database: Grows with readings

---

## Next Steps

1. ✅ Deploy Docker stack
2. ✅ Verify containers are running
3. ✅ Access dashboard
4. ⏳ Wait for sensors to arrive
5. ⏳ Configure ESP-32 to send data to API
6. ⏳ Set up Telegram alerts (N8N)
7. ⏳ Build additional devices

---

## Need Help?

See detailed troubleshooting in **DOCKER_DEPLOYMENT.md**

Key files:
- `docker-compose.yml` - Service definitions
- `Dockerfile.api` - API container build
- `nginx.conf` - Web server configuration
- `backend.py` - API application code
- `dashboard.html` - Web UI

---

**Ready to deploy!** 🚀

Once sensors arrive, update the dashboard user/device mapping and ESP-32 will start sending real data automatically.
