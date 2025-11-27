# Plant Moisture Monitor - Integration Guide

## System Overview

You now have a complete plant monitoring system with:

1. **Hardware**: ESP-32 microcontroller running ESPHome firmware (boots successfully ✅)
2. **Backend API**: FastAPI server receiving and storing sensor data (running ✅)
3. **Web Dashboard**: Beautiful HTML dashboard showing real-time plant status (connected ✅)

---

## Running the System

### 1. Start the Backend API

```bash
cd D:\nextcloud\projects\plants
python backend.py
```

The API will start on **http://localhost:8000**

You can also view interactive API documentation at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 2. Serve the Dashboard

Option A: Use Python's built-in server
```bash
cd D:\nextcloud\projects\plants
python -m http.server 8080
```

Then open: **http://localhost:8080/dashboard.html**

Option B: Open directly from file system
```
file:///D:/nextcloud/projects/plants/dashboard.html
```

Note: API calls will work from anywhere since CORS is enabled on the backend.

### 3. Check ESP-32 Connection

The ESP-32 should already be running and connected to WiFi (Tigernet3).

To verify:
1. Connect ESP-32 via USB to COM4
2. View serial logs to confirm WiFi connection
3. You'll see: `[I][wifi:1079]: Connected`

---

## How Data Flows

```
ESP-32 (WiFi connected)
    ↓
    └→ POST /reading (every X minutes)
       ↓
    FastAPI Backend
       ├→ SQLite Database (stores readings)
       └→ HTTP Response (OK)
           ↓
    Web Dashboard
       ├→ GET /devices (poll every 30 seconds)
       ├→ GET /device/{id} (on demand)
       └→ Display real-time moisture levels
```

---

## Device-to-User Mapping

The dashboard uses this mapping (in `dashboard.html`):

```javascript
const deviceUserMap = {
    'plant-monitor-1': 'sarah',
    'plant-monitor-2': 'tom',
    'plant-monitor-3': 'alex',
    'plant-monitor-4': 'jordan'
};
```

Update this based on your actual device names and user assignments.

---

## Testing the System

### Test 1: Verify API is Running

```bash
curl http://localhost:8000/
```

Expected response:
```json
{"status":"running","api":"Plant Moisture Monitor","version":"1.0"}
```

### Test 2: Send Sample Data

```bash
curl -X POST http://localhost:8000/reading \
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

### Test 3: Retrieve Device Data

```bash
curl http://localhost:8000/device/plant-monitor-1
```

Should return current readings for plant-monitor-1.

### Test 4: Check Dashboard

Open http://localhost:8080/dashboard.html in a browser and verify:
- Welcome modal appears (or loads saved user)
- User/plant selectors work
- Moisture percentage displays
- Status (happy/warning/critical) is correct

---

## Features Currently Enabled

✅ **ESP-32 Firmware**
- Boots successfully on power-up
- Connects to WiFi (Tigernet3)
- Ready to read dual ADC sensors (GPIO34 & GPIO35)
- OTA updates configured

✅ **FastAPI Backend**
- Receives sensor readings via POST /reading
- Stores in SQLite database
- Serves current data via GET /devices and GET /device/{id}
- Includes historical data via GET /device/{id}/plant/{number}/history
- CORS enabled for web dashboard

✅ **Web Dashboard**
- Beautiful responsive UI
- User/plant selectors
- Real-time moisture display (0-100%)
- Status indicators (happy/warning/critical)
- Cheeky plant messages
- Cookie-based user persistence
- Auto-refreshes every 30 seconds when API is available
- Fallback to mock data if API unavailable

---

## Configuring the ESP-32 to Send Data

Once your sensors arrive, you'll need to configure the ESP-32 to send readings to the backend.

### Option 1: ESPHome HTTP Component (Recommended)

Add this to `esphome-config/plant-monitor.yaml`:

```yaml
http_request:

automation:
  - trigger:
      platform: interval
      interval: 10min  # Send data every 10 minutes
    action:
      - http_request.post:
          url: http://YOUR_SERVER_IP:8000/reading
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

Replace:
- `YOUR_SERVER_IP` with your server's IP (e.g., `192.168.1.100`)
- Plant names/locations with your actual setup
- `interval: 10min` with desired frequency

### Option 2: Custom Arduino Sketch

If you prefer Arduino directly, add HTTP request code to send data periodically.

### Option 3: Mock Data for Testing

For now, use the test data from **Test 2** above to populate the database and test the dashboard.

---

## Status Thresholds

Moisture level meanings (configurable in `backend.py`):

| Level | Range | Status | Plant Message |
|-------|-------|--------|---|
| Happy | 60-100% | ✅ | "Living my best life!" |
| Warning | 30-60% | ⚠️ | "Could use a sip, ngl" |
| Critical | 0-30% | 🚨 | "WATER ME YOU MONSTER" |

To change thresholds, modify the `get_moisture_status()` function in `backend.py`.

---

## Database

SQLite database at: `D:\nextcloud\projects\plants\plants.db`

View data with:
```bash
sqlite3 plants.db
```

Useful queries:
```sql
-- All readings
SELECT * FROM moisture_sensors ORDER BY timestamp DESC LIMIT 10;

-- Latest reading per plant
SELECT DISTINCT ON (device_id, plant_number) *
FROM moisture_sensors
ORDER BY device_id, plant_number, timestamp DESC;

-- All devices
SELECT * FROM devices;
```

---

## Next Steps

1. **Add sensors** - Once capacitive moisture sensors arrive:
   - Connect to GPIO34 and GPIO35
   - Configure ESP-32 to send data to backend
   - Verify readings in dashboard

2. **Telegram alerts** - Set up N8N workflow:
   - Monitor critical moisture levels
   - Send notifications to users

3. **Additional devices** - Repeat for 2-4 more ESP-32 boards:
   - Flash firmware to each board
   - Map to users in `dashboard.html`
   - Update backend device list

4. **OLED display** - Re-add to firmware once stable:
   - Show local plant status on device
   - Less dependent on WiFi

5. **Production deployment**:
   - Deploy API to home server (Proxmox/Docker)
   - Use your actual network IP
   - Set up dynamic DNS if IP changes

---

## Troubleshooting

### API not responding
```bash
# Check if running
curl http://localhost:8000/

# Check logs in backend.log
cat backend.log | tail -50

# Restart
# Kill existing process and re-run: python backend.py
```

### Dashboard shows mock data
- Check browser console for errors (F12)
- Verify API_BASE_URL in dashboard.html matches your server
- Ensure backend is running before opening dashboard

### ESP-32 won't connect
- Verify WiFi SSID/password in secrets.yaml
- Check that Tigernet3 is online
- View serial logs (COM4) for connection errors

### No data in database
- Ensure POST /reading requests are being sent
- Check database file exists: `plants.db`
- Run test from **Test 2** to verify API accepts data

---

## Architecture Decisions

**Why esp-idf instead of Arduino?**
- More stable bootloader handling
- Better memory management
- Fewer corruption issues during flashing

**Why SQLite instead of Cloud DB?**
- Runs locally on home server
- No external dependencies
- Fast and reliable
- Easy backups

**Why FastAPI?**
- Modern Python web framework
- Async support for scalability
- Automatic API documentation
- Type checking with Pydantic

**Why direct polling instead of WebSockets?**
- Simpler to implement
- Dashboard doesn't require persistent connection
- 30-second refresh is sufficient for plants
- Easy to extend later if needed

---

## API Response Examples

### GET /device/plant-monitor-1

```json
{
  "device_id": "plant-monitor-1",
  "friendly_name": "plant-monitor-1",
  "is_active": true,
  "last_seen": "2025-11-26T23:49:25.622457",
  "plant_1": {
    "plant_number": 1,
    "name": "Monstera",
    "location": "Living Room",
    "user_name": "Sarah",
    "current_moisture": 65.5,
    "status": "happy",
    "last_reading": "2025-11-26T23:49:25.625455"
  },
  "plant_2": {
    "plant_number": 2,
    "name": "Pothos",
    "location": "Living Room",
    "user_name": "Sarah",
    "current_moisture": 42.3,
    "status": "warning",
    "last_reading": "2025-11-26T23:49:25.625455"
  }
}
```

### GET /devices

```json
{
  "devices": [
    {
      "device_id": "plant-monitor-1",
      "friendly_name": "plant-monitor-1",
      "owner_name": "Sarah",
      "is_active": true,
      "last_seen": "2025-11-26T23:49:25.622457",
      "plant_1": {
        "moisture": 65.5,
        "status": "happy",
        "name": "Monstera"
      },
      "plant_2": {
        "moisture": 42.3,
        "status": "warning",
        "name": "Pothos"
      }
    }
  ]
}
```

---

## Files Summary

| File | Purpose | Status |
|------|---------|--------|
| `backend.py` | FastAPI server | ✅ Running |
| `dashboard.html` | Web UI | ✅ Connected |
| `API_DOCS.md` | API documentation | ✅ Complete |
| `plants.db` | SQLite database | ✅ Auto-created |
| `esphome-config/plant-monitor.yaml` | ESP-32 firmware | ✅ Tested |
| `esphome-config/secrets.yaml` | WiFi credentials | ✅ Configured |
| `INTEGRATION_GUIDE.md` | This file | ✅ Complete |

---

**Status**: System is ready for sensor integration. All core components working.

Last updated: 2025-11-26
