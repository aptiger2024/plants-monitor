# Plant Moisture Monitor Project - Context & Status

## Project Overview
Building custom **plant moisture monitors** as gifts for friends. Each device monitors **2 plants independently** with WiFi connectivity and cute dashboard.

**Tech Stack:**
- Hardware: ESP-32 + dual capacitive soil moisture sensors + 0.96" I2C OLED display
- Firmware: ESPHome (YAML-based, esp-idf framework)
- Backend: FastAPI (Python) on home server (Proxmox/Docker/Portainer)
- Dashboard: Single-page HTML served from API (dynamic, real device data)
- CI/CD: GitHub Actions builds Docker images to ghcr.io
- Notifications: Telegram bot via N8N (planned)

**Recipients:**
- Laurie (`plant-monitor-laurie`)
- Rhea (`plant-monitor-rhea`)
- Ronak (`plant-monitor-ronak`)

---

## Current Status (Session 6 - 2025-12-09)

### ✅ FULLY WORKING END-TO-END
1. **Laurie's device flashed and tested** - Successfully:
   - Boots and creates "Plant-Monitor Laurie" hotspot
   - User connects, configures WiFi via captive portal at http://192.168.4.1
   - WiFi credentials persist to flash (survives power cycles!)
   - Device connects to home WiFi and POSTs sensor data every 5 minutes
   - Data appears on dashboard at https://plants.suplexcentral.com

2. **Dashboard (plants.suplexcentral.com)** - Fully functional:
   - Fetches real device data from `/devices` API
   - Device selector dropdown (auto-populated from registered devices)
   - Plant selector shows actual plant names (persisted)
   - Settings modal saves plant names/locations to database
   - Plant names persist (stored in separate `PlantConfig` table)
   - Welcome intro animation works (replay via Intro button)
   - Auto-refreshes every 30 seconds
   - Cheeky messages based on moisture level

3. **Backend API** - Running on srv-media-2:7000:
   - `POST /reading` - Receive sensor data from devices
   - `GET /devices` - List all devices with latest readings
   - `PUT /device/{id}/plant/{num}` - Update plant name/location (persists!)
   - `GET /device/{id}` - Get specific device status
   - `GET /device/{id}/plant/{num}/history` - Historical data
   - Database tables: `moisture_sensors`, `devices`, `plant_configs`

4. **CI/CD Pipeline** - GitHub Actions:
   - Pushes to main trigger automatic Docker builds
   - Images pushed to `ghcr.io/aptiger2024/plants-monitor:latest`
   - Portainer just needs "Pull and redeploy" (no more cache issues!)

### ✅ Hardware Ready
- All components acquired for building devices
- ESP-32 boards, sensors, charger modules, batteries, enclosures ready

### ⏳ Pending
- Finalize firmware template (Laurie's config is the working template)
- Compile Rhea and Ronak firmware (just change device name)
- Solder sensors and assemble physical devices
- N8N Telegram notifications
- OLED display integration (disabled for now)
- Captive portal styling (functional but plain)

---

## Firmware Template (Working)

**File:** `esphome-config/plant-monitor-laurie.yaml`

**Key Features:**
```yaml
# WiFi Provisioning (no hardcoded credentials)
wifi:
  ap:
    ssid: "Plant-Monitor Laurie"
    password: "flowers123"
  reboot_timeout: 0s  # Go straight to AP mode

captive_portal:  # Enables WiFi config page

web_server:
  port: 80  # No auth needed (only accessible on device hotspot)

# Sensors with calibration
sensor:
  - platform: adc
    pin: GPIO34/GPIO35
    filters:
      - calibrate_linear:
          - 3.0 -> 0.0   # Dry
          - 1.5 -> 100.0 # Wet
      - clamp: 0-100

# API Upload every 5 minutes
interval:
  - interval: 5min
    then:
      - http_request.post:
          url: "https://plants.suplexcentral.com/reading"
          json: device_id, moisture values, user_name
```

**To create Rhea/Ronak configs:** Copy Laurie's, change:
- `name: plant-monitor-rhea` / `plant-monitor-ronak`
- `friendly_name: "Rhea's Plant Monitor"` / `"Ronak's Plant Monitor"`
- `ap: ssid: "Plant-Monitor Rhea"` / `"Plant-Monitor Ronak"`
- `root["device_id"]` and `root["user_name"]` in the JSON

---

## User Setup Flow (for Setup Card)

### What's in the Box
- Plant Monitor device
- USB-C power cable
- 2 moisture sensor probes
- Setup card

### Setup Steps
1. **Power On** - Connect USB-C, wait ~30 seconds
2. **Connect to Device WiFi** - Find "Plant-Monitor [Name]", password: `flowers123`
3. **Configure WiFi** - Browser opens http://192.168.4.1, select home WiFi, enter password
4. **Done!** - Device connects to home WiFi, phone disconnects (normal!)
5. **Check Plants** - Visit plants.suplexcentral.com within 5 minutes

### Troubleshooting
- Can't find hotspot? Unplug/replug device
- Not on dashboard? Wait 5 min (uploads every 5 min)
- Need to change WiFi? Unplug, replug, repeat setup

---

## Files & Locations

```
D:\nextcloud\projects\plants\
├── backend.py                        # FastAPI backend
├── dashboard.html                    # Web dashboard (served by API)
├── Dockerfile.api                    # Docker build config
├── docker-compose.yml                # Uses ghcr.io image (not git build)
├── requirements.txt                  # Python dependencies
├── .github/workflows/docker-build.yml # CI/CD pipeline
├── PROJECT_CONTEXT.md                # This file
├── SETUP_GUIDE.md                    # User setup instructions
├── esphome-config/
│   ├── plant-monitor-laurie.yaml     # WORKING TEMPLATE
│   ├── plant-monitor-rhea.yaml       # Needs API upload added
│   ├── plant-monitor-ronak.yaml      # Needs API upload added
│   ├── plant-monitor.yaml            # Original test config
│   └── secrets.yaml                  # Not used (WiFi via captive portal)
```

---

## Database Schema

```sql
-- Sensor readings (time-series data)
moisture_sensors:
  id, device_id, plant_number, plant_name, user_name,
  location, moisture_percent, timestamp

-- Device registry
devices:
  id, device_id, friendly_name, owner_name, last_seen, is_active

-- Persistent plant settings (survives new readings)
plant_configs:
  id, device_id, plant_number, plant_name, location
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Serves dashboard.html |
| GET | `/health` | Health check |
| POST | `/reading` | Receive sensor data from device |
| GET | `/devices` | List all devices + latest readings |
| GET | `/device/{id}` | Get specific device status |
| PUT | `/device/{id}/plant/{num}` | Update plant name/location |
| GET | `/device/{id}/plant/{num}/history` | Historical readings |

---

## Deployment

### Docker (Portainer)
```yaml
# docker-compose.yml
services:
  plants-api:
    image: ghcr.io/aptiger2024/plants-monitor:latest
    ports:
      - "7000:8000"
    volumes:
      - plants-data:/app/data
```

### Redeploying
1. Push changes to GitHub main branch
2. GitHub Action builds new image (~2-3 min)
3. In Portainer: Pull and redeploy
4. Done! No more deleting stacks/images.

### ESPHome Compilation
```powershell
cd D:\nextcloud\projects\plants\esphome-config
python -m esphome compile plant-monitor-laurie.yaml
# Output: .esphome/build/plant-monitor-laurie/.pioenvs/.../firmware.factory.bin
```

### Flashing
Use https://web.esphome.io/ - erases and flashes in one step.

---

## Known Issues & Solutions

### Plant name reverts to "Plant 1"
- **Fixed:** Plant names now stored in `PlantConfig` table, separate from readings
- Names persist even when new sensor data arrives

### Docker cache not updating
- **Fixed:** Now using GitHub Actions + ghcr.io registry
- Just "Pull and redeploy" in Portainer

### WiFi tries "SetupMode" on boot
- **Fixed:** Removed hardcoded WiFi from secrets.yaml
- Device goes straight to AP mode if no saved credentials

### Intro button doesn't work
- **Fixed:** Button now calls `openWelcomeModal()` instead of `playWelcomeAnimation()`

---

## Next Steps

### Immediate (When Ready to Build)
1. Finalize any remaining firmware tweaks on Laurie's device
2. Copy Laurie's config → Rhea and Ronak (just change names)
3. Compile all three firmwares
4. Flash each ESP-32
5. Solder sensors to GPIO34/GPIO35
6. Assemble in enclosures
7. Test each device end-to-end

### Future Enhancements
- [ ] N8N Telegram alerts when moisture critical
- [ ] OLED display showing moisture levels
- [ ] Captive portal styling (plant-themed)
- [ ] Historical graphs on dashboard
- [ ] Battery level monitoring
- [ ] Deep sleep for battery life

---

## Session History

### Session 6 (2025-12-09) - Current
- Fixed plant name persistence (new `PlantConfig` table)
- Fixed intro button not opening modal
- Simplified intro (removed useless name input)
- Plant selector now shows actual plant names
- Settings save to API and persist
- Confirmed end-to-end flow working with Laurie's device

### Session 5 (2025-12-09)
- Set up GitHub Actions CI/CD pipeline
- Fixed docker-compose to use ghcr.io registry
- Dashboard now fetches real device data from API
- Removed hardcoded mock users
- Fixed WiFi provisioning (removed SetupMode placeholder)
- Added HTTP POST to firmware (uploads every 5 min)
- Laurie's device successfully registered and sending data

### Session 4 (2025-11-28)
- Fixed FastAPI type annotations
- Created comprehensive documentation
- Device registration system ready

### Sessions 1-3
- Initial hardware selection
- Dashboard design with animations
- ESPHome setup and first successful flash
- Backend API creation

---

**Last Updated:** 2025-12-09 (Session 6)

**Current State:**
- ✅ Laurie's device: WORKING (flashed, connected, sending data)
- ✅ Dashboard: WORKING (real data, settings persist)
- ✅ API: WORKING (all endpoints functional)
- ✅ CI/CD: WORKING (push to deploy)
- ⏳ Rhea/Ronak firmware: Template ready, just needs name changes
- ⏳ Physical assembly: Hardware ready, waiting to build
- ⏳ N8N notifications: Not started
