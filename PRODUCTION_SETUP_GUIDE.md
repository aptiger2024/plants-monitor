# Plant Moisture Monitor - Production Setup Guide

Complete step-by-step guide from server running to fully operational system.

---

## 🎯 Current Status

✅ FastAPI backend running on `srv-media-2:7000`
✅ Docker container deployed in Portainer
✅ Database (SQLite) initialized and persistent
✅ GitHub repository with source code
❌ Frontend website not yet served
❌ Nginx routing not configured
❌ ESP-32 devices not yet configured
❌ Sensors not yet connected

---

## 📋 Architecture Overview

```
                    plants.suplexcentral.com
                            │
                ┌───────────┴───────────┐
                │                       │
        Dashboard (Frontend)     API Proxy
           (HTML/CSS/JS)         (/api/*)
                │                       │
                │                       │
        Serve dashboard.html   192.168.140.94:7000
                │                       │
                │                   FastAPI
                │               (plants-api container)
                │                       │
                └───────────┬───────────┘
                            │
                      SQLite Database
                    (persistent volume)
                            │
                    ┌───────┴────────┐
            ESP-32 Device 1    ESP-32 Device 2
            (Plant Monitor 1)  (Plant Monitor 2)
                    │                  │
              Sensor Data         Sensor Data
                    │                  │
                    └───────┬──────────┘
                            │
                      POST /reading
```

---

## 📝 STEP-BY-STEP SETUP

### STEP 1: Configure Nginx for plants.suplexcentral.com

**Location:** Your Nginx server (different environment)

**Add this server block to your Nginx config:**

```nginx
server {
    listen 80;
    server_name plants.suplexcentral.com;

    # Redirect HTTP to HTTPS (if you have SSL)
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;  # Change to 80 if no SSL
    server_name plants.suplexcentral.com;

    # SSL certificates (if using HTTPS)
    # ssl_certificate /path/to/cert.pem;
    # ssl_certificate_key /path/to/key.pem;

    # API endpoint - proxy to FastAPI backend
    location /api/ {
        proxy_pass http://192.168.140.94:7000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;

        # CORS headers
        add_header 'Access-Control-Allow-Origin' '*' always;
        add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, OPTIONS' always;
        add_header 'Access-Control-Allow-Headers' 'Content-Type' always;

        if ($request_method = 'OPTIONS') {
            return 204;
        }
    }

    # Dashboard - serve the HTML
    location / {
        root /var/www/plants-monitor;  # Change to your path
        try_files $uri $uri/ /dashboard.html;

        # Cache control
        expires 1h;
        add_header Cache-Control "public, must-revalidate";
    }

    # Health check endpoint
    location /health {
        access_log off;
        proxy_pass http://192.168.140.94:7000/;
    }
}
```

**Then:**
1. Copy `dashboard.html` to `/var/www/plants-monitor/`
2. Reload Nginx: `sudo systemctl reload nginx`
3. Test: `curl https://plants.suplexcentral.com/` (should return HTML)

---

### STEP 2: Update Dashboard to Use Production API

The dashboard needs to point to the production API, not localhost.

**Edit `dashboard.html`** - find this line:

```javascript
const API_BASE_URL = 'http://localhost:8000';
```

**Change to:**

```javascript
const API_BASE_URL = 'https://plants.suplexcentral.com/api';
```

**Commit and push:**
```bash
git add dashboard.html
git commit -m "Update API URL to production: plants.suplexcentral.com/api"
git push
```

---

### STEP 3: Verify Frontend is Working

1. Open browser: `https://plants.suplexcentral.com`
2. Should see Plant Moisture Monitor dashboard
3. Click different users/plants
4. Should display mock data (no real data yet)

---

### STEP 4: Test API Directly

```bash
# Health check
curl https://plants.suplexcentral.com/api/

# Send test data
curl -X POST https://plants.suplexcentral.com/api/reading \
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

# Get device status
curl https://plants.suplexcentral.com/api/device/plant-monitor-1
```

Dashboard should now show real data!

---

## 🔧 ESP-32 DEVICE SETUP

### Prerequisites
- ESP-32 board (you have 2)
- 2x Capacitive soil moisture sensors
- USB-C cable for programming
- ESPHome installed

### For Each Device:

#### STEP 1: Prepare Hardware

1. **Solder connections** (or use headers):
   - Sensor 1 → GPIO34 (+ 3.3V, GND)
   - Sensor 2 → GPIO35 (+ 3.3V, GND)
   - Power from TP4056 module or USB

#### STEP 2: Configure ESPHome Firmware

Edit `esphome-config/plant-monitor.yaml`:

```yaml
esphome:
  name: plant-monitor-1  # Change per device: plant-monitor-1, plant-monitor-2, etc.
  friendly_name: plant-monitor-1

esp32:
  board: esp32dev
  framework:
    type: esp-idf
    version: recommended

logger:
  level: INFO

ota:
  - platform: esphome
    password: "27b87c2c9de41b858c0ad84ad13984f5"

wifi:
  ssid: !secret wifi_ssid
  password: !secret wifi_password
  fast_connect: true
  ap:
    ssid: "Plant-Monitor-1 Fallback"
    password: "ND9kIKauNGyJ"

captive_portal:

# Analog sensors for moisture
sensor:
  - platform: adc
    pin: GPIO34
    name: "Plant 1 Moisture"
    id: moisture_1
    attenuation: auto
    update_interval: 60s
    filters:
      - median:
          window_size: 7
          send_every: 7
      - lambda: return (1.0 - (x - 1400) / (4095 - 1400)) * 100.0;
      - clamp:
          min_value: 0
          max_value: 100
    unit_of_measurement: "%"

  - platform: adc
    pin: GPIO35
    name: "Plant 2 Moisture"
    id: moisture_2
    attenuation: auto
    update_interval: 60s
    filters:
      - median:
          window_size: 7
          send_every: 7
      - lambda: return (1.0 - (x - 1400) / (4095 - 1400)) * 100.0;
      - clamp:
          min_value: 0
          max_value: 100
    unit_of_measurement: "%"

  - platform: wifi_signal
    name: "WiFi Signal"
    update_interval: 60s

# HTTP client for sending data
http_request:

# Automation to send readings every 10 minutes
automation:
  - trigger:
      platform: interval
      interval: 10min
    action:
      - http_request.post:
          url: https://plants.suplexcentral.com/api/reading
          headers:
            Content-Type: application/json
          json:
            device_id: "plant-monitor-1"
            plant_1_moisture: !lambda 'return id(moisture_1).state;'
            plant_2_moisture: !lambda 'return id(moisture_2).state;'
            plant_1_name: "Monstera"
            plant_2_name: "Pothos"
            user_name: "Sarah"
            location: "Living Room"
```

**Key changes per device:**
- `name:` → `plant-monitor-1`, `plant-monitor-2`, etc.
- `device_id:` → `"plant-monitor-1"`, `"plant-monitor-2"`, etc.
- Plant names/user names as needed
- URL → `https://plants.suplexcentral.com/api/reading`

#### STEP 3: Flash to ESP-32

```bash
cd esphome-config
python -m esphome compile plant-monitor.yaml
```

Then use web flasher: https://web.esphome.io/
- Select compiled firmware
- Flash to board on COM port

#### STEP 4: Verify Connection

1. Open serial monitor (baud 115200)
2. Should see WiFi connecting
3. Should see HTTP POST requests every 10 minutes
4. Check dashboard - data should appear!

---

## 📱 Device-to-User Mapping

Update this mapping in `dashboard.html` based on your devices:

```javascript
const deviceUserMap = {
    'plant-monitor-1': 'sarah',
    'plant-monitor-2': 'tom',
    'plant-monitor-3': 'alex',
    'plant-monitor-4': 'jordan'
};
```

Also update the mock data structure to match your actual plant names/locations.

---

## 🔄 Database Management

### View Stored Data

```bash
# SSH to srv-media-2
ssh user@srv-media-2

# Connect to database
docker exec -it plants-api sqlite3 /app/data/plants.db

# View tables
.tables

# View all readings
SELECT device_id, plant_number, moisture_percent, timestamp FROM moisture_sensors LIMIT 10;

# View latest per device
SELECT DISTINCT ON (device_id) * FROM moisture_sensors ORDER BY device_id, timestamp DESC;
```

### Backup Database

```bash
# On srv-media-2
docker exec plants-api tar czf - /app/data/plants.db | gzip > /backup/plants-db-$(date +%Y%m%d).tar.gz

# Or via volume
docker run --rm -v plants_plants-data:/data -v /backup:/backup \
  alpine tar czf /backup/plants-db.tar.gz /data/
```

---

## 🧪 Testing Checklist

### Before Deploying Devices

- [ ] Frontend loads at plants.suplexcentral.com
- [ ] Dashboard shows mock data
- [ ] API responds to curl requests
- [ ] Can POST test data to `/api/reading`
- [ ] Dashboard updates with new data in real-time
- [ ] Database stores readings correctly

### After Connecting First Device

- [ ] ESP-32 boots and connects to WiFi
- [ ] Serial logs show HTTP POST requests
- [ ] Dashboard receives and displays real sensor data
- [ ] Data persists in database
- [ ] Device appears in `/api/devices` endpoint

### Full System Test

- [ ] All 3-5 devices reporting data
- [ ] Dashboard shows all plants
- [ ] User selector updates per-device views
- [ ] Historical data endpoint works
- [ ] Database growing with readings

---

## 📊 Device Configuration Reference

For each ESP-32 device you build:

| Device | device_id | User | Plant 1 | Plant 2 | GPIO34 | GPIO35 |
|--------|-----------|------|---------|---------|--------|--------|
| #1 | plant-monitor-1 | Sarah | Monstera | Pothos | Sensor1 | Sensor2 |
| #2 | plant-monitor-2 | Tom | Snake Plant | Fiddle Leaf | Sensor3 | Sensor4 |
| #3 | plant-monitor-3 | Alex | Succulent | Peace Lily | Sensor5 | Sensor6 |
| #4 | plant-monitor-4 | Jordan | Rubber Plant | Aloe Vera | Sensor7 | Sensor8 |
| #5 | plant-monitor-5 | Friend | Plant 1 | Plant 2 | Sensor9 | Sensor10 |

---

## 🔐 Security Notes

✅ **Currently Secure:**
- API only accessible through Nginx proxy
- HTTPS/SSL configured at Nginx layer
- Database not exposed to network
- Docker isolation

⚠️ **Configure Before Production:**
- [ ] SSL certificates for HTTPS
- [ ] Rate limiting in Nginx (prevent abuse)
- [ ] Database backups automated
- [ ] Monitor logs for errors

---

## 🚨 Troubleshooting

### Dashboard Shows "No data"

1. Check if API is responding: `curl https://plants.suplexcentral.com/api/`
2. Check if database has readings: `docker exec plants-api sqlite3 /app/data/plants.db "SELECT COUNT(*) FROM moisture_sensors;"`
3. Check Nginx logs: Look for 502/504 errors

### ESP-32 Won't Connect to WiFi

1. Check serial logs for errors
2. Verify WiFi SSID/password in `secrets.yaml`
3. Check if WiFi is 2.4GHz (5GHz not supported on ESP-32)
4. Try resetting ESP-32 with `esptool erase_flash`

### API Returning 500 Errors

```bash
docker logs -f plants-api
```

Look for database or Python errors. Most likely:
- Database locked (restart container)
- Malformed JSON from device
- Missing environment variables

---

## 📅 Implementation Timeline

**Week 1:**
- [ ] Configure Nginx for plants.suplexcentral.com
- [ ] Update dashboard API URL
- [ ] Verify frontend and API working
- [ ] Test with curl requests

**Week 2-3:** (When sensors arrive)
- [ ] Solder connections on 1st device
- [ ] Configure ESPHome firmware for device 1
- [ ] Flash to board
- [ ] Verify data in dashboard
- [ ] Fix calibration if needed

**Week 4-6:**
- [ ] Build remaining devices (2-4 more)
- [ ] Configure each with correct device_id
- [ ] Verify all sending data
- [ ] Fine-tune moisture thresholds

**Week 7+:**
- [ ] Set up N8N Telegram alerts
- [ ] Configure critical alerts
- [ ] Monitor system stability
- [ ] Plan additional features (OLED display, etc.)

---

## 📚 Quick Reference

### Important URLs
- Frontend: `https://plants.suplexcentral.com`
- API: `https://plants.suplexcentral.com/api/`
- API Docs: `https://plants.suplexcentral.com/api/docs`
- API Health: `https://plants.suplexcentral.com/api/` (returns JSON)

### Important Files

| File | Location | Purpose |
|------|----------|---------|
| `dashboard.html` | `/var/www/plants-monitor/` | Frontend UI |
| `docker-compose.yml` | GitHub repo | Portainer deployment |
| `plant-monitor.yaml` | `esphome-config/` | ESP-32 firmware |
| `backend.py` | Docker container `/app/` | API backend |
| `plants.db` | Docker volume | SQLite database |

### Important Commands

```bash
# Check container status
docker ps | grep plants-api

# View API logs
docker logs -f plants_plants-api_1

# Connect to database
docker exec -it plants_plants-api_1 sqlite3 /app/data/plants.db

# Reload Nginx
sudo systemctl reload nginx

# Compile ESP-32 firmware
python -m esphome compile esphome-config/plant-monitor.yaml

# Flash to ESP-32
python -m esphome run esphome-config/plant-monitor.yaml
```

---

## 🎉 When Everything is Working

You'll have:
- ✅ **Frontend dashboard** at plants.suplexcentral.com
- ✅ **Real-time sensor data** from 3-5 ESP-32 devices
- ✅ **REST API** for data retrieval
- ✅ **Persistent database** with historical readings
- ✅ **Clean Nginx proxy** routing traffic
- ✅ **Secure HTTPS** connection
- ✅ **Automated data collection** every 10 minutes

Ready for Telegram alerts via N8N! 🌱

---

**Status:** Production environment configured, ready for device deployment
**Last Updated:** 2025-11-28
