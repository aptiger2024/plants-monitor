# Device Registration & Data Flow Explained

How your plant monitors register themselves and send data to the dashboard.

---

## The Flow (In Plain English)

```
You (Builder)                   Device (ESP-32)              Your Server          Browser
     │                               │                           │                  │
     │ Flash firmware with           │                           │                  │
     │ device_id: "plant-monitor-1"  │                           │                  │
     ├──────────────────────────────>│                           │                  │
     │                               │                           │                  │
     │                               │ Boots up                  │                  │
     │                               │ Connects to WiFi          │                  │
     │                               │ Reads sensors every 1 min │                  │
     │                               │                           │                  │
     │                               │ Every 10 minutes:         │                  │
     │                               │ POST /api/reading         │                  │
     │                               ├──────────────────────────>│                  │
     │                               │  {device_id, moisture...} │                  │
     │                               │                           │                  │
     │                               │ API stores in database    │                  │
     │                               │ API creates DeviceInfo    │                  │
     │                               │ if doesn't exist yet      │                  │
     │                               │<──────────────────────────┤                  │
     │                               │ ✓ 200 OK                  │                  │
     │                               │                           │                  │
     │                               │                           │ GET /api/devices │
     │                               │                           │<──────────────────┤
     │                               │                           │                  │
     │                               │                           │ Returns device   │
     │                               │                           │ and latest       │
     │                               │                           │ readings         │
     │                               │                           ├──────────────────>│
     │                               │                           │                  │
     │                               │                           │                  │ Dashboard
     │                               │                           │                  │ displays
     │                               │                           │                  │ plant #1
     │                               │                           │                  │ and #2
     │                               │                           │                  │
```

---

## Step-by-Step: What Happens When Device Powers On

### 1. Device Startup (Immediate)

ESP-32 boots up:
```
[I] ESPHome 2024.12.1 (esp-idf framework)
[I] ESP32 starting up...
[I] Version 1.0.0
[I] Compiling components...
[I] Heap size: 268240 bytes
```

### 2. WiFi Connection (30 seconds)

Device connects to your home WiFi:
```
[I] [WiFi] Setting up WiFi...
[I] [WiFi] Connecting to 'Tigernet3'...
[I] [WiFi] Connected! IP: 192.168.1.120
[I] [WiFi] Hostname: plant-monitor-1
```

This is when the OLED shows the WiFi icon ✓

### 3. Sensor Reading Loop (Every 60 seconds)

Every minute, device reads both sensors:
```
[D] [ADC] GPIO34 raw value: 2345
[D] [ADC] GPIO35 raw value: 3456
[I] [Sensor] Plant 1 Moisture: 65%
[I] [Sensor] Plant 2 Moisture: 42%
```

The device takes 7 readings and averages them (takes ~7 minutes for stabilization).

### 4. Data Transmission (Every 10 minutes)

Every 10 minutes, device POSTs to your API:

```
[I] [HTTP] Sending POST to https://plants.suplexcentral.com/api/reading
[I] [HTTP] Request body:
{
  "device_id": "plant-monitor-1",
  "plant_1_moisture": 65.3,
  "plant_2_moisture": 42.7,
  "plant_1_name": "Monstera",
  "plant_2_name": "Pothos",
  "user_name": "Sarah",
  "location": "Living Room"
}

[I] [HTTP] Response: 200 OK
[I] [HTTP] Data stored successfully
```

---

## What the API Does (Backend Logic)

### On First Device POST

When the API receives the reading from "plant-monitor-1" for the first time:

```python
# 1. Check if device exists in database
device = db.query(DeviceInfo).filter(
    DeviceInfo.device_id == "plant-monitor-1"
).first()

# 2. If not found, create it (REGISTRATION)
if not device:
    device = DeviceInfo(
        device_id="plant-monitor-1",
        friendly_name="plant-monitor-1",
        owner_name="Sarah",
        is_active=1,
        last_seen=datetime.utcnow()
    )
    db.add(device)

# 3. Store the two moisture readings
reading_1 = MoistureSensor(
    device_id="plant-monitor-1",
    plant_number=1,
    plant_name="Monstera",
    user_name="Sarah",
    location="Living Room",
    moisture_percent=65.3,
    timestamp=datetime.utcnow()
)
reading_2 = MoistureSensor(
    device_id="plant-monitor-1",
    plant_number=2,
    plant_name="Pothos",
    user_name="Sarah",
    location="Living Room",
    moisture_percent=42.7,
    timestamp=datetime.utcnow()
)

db.add(reading_1)
db.add(reading_2)
db.commit()  # Save to database
```

**Result:** Device is now "registered" - it exists in the database!

### On Subsequent POSTs

Every 10 minutes, the same flow repeats:
1. Store new moisture readings
2. Update `device.last_seen` timestamp
3. Keep device as active

---

## Database Structure

### `devices` Table (Device Registration)

Created automatically on first data POST:

| Column | Example Value | Notes |
|--------|---------------|-------|
| id | 1 | Auto-increment |
| device_id | plant-monitor-1 | Unique identifier |
| friendly_name | plant-monitor-1 | Display name |
| owner_name | Sarah | For grouping on dashboard |
| last_seen | 2025-11-28 10:30:00 | When device last sent data |
| is_active | 1 | 1=active, 0=inactive |

### `moisture_sensors` Table (Historical Data)

One row per plant per reading:

| Column | Example Value | Notes |
|--------|---------------|-------|
| id | 42 | Auto-increment |
| device_id | plant-monitor-1 | Links to devices table |
| plant_number | 1 | Which plant (1 or 2) |
| plant_name | Monstera | Name of plant |
| user_name | Sarah | Name of recipient |
| location | Living Room | Where monitor is |
| moisture_percent | 65.3 | 0-100% |
| timestamp | 2025-11-28 10:30:00 | When reading was taken |

**Note:** You get 2 rows per POST (one per plant).

---

## Dashboard Query Flow

### When User Opens Dashboard

1. **User enters URL:** `https://plants.suplexcentral.com`
2. **Browser loads HTML** with JavaScript
3. **JavaScript calls API:** `GET /api/devices`

### API Response

```json
{
  "devices": [
    {
      "device_id": "plant-monitor-1",
      "friendly_name": "plant-monitor-1",
      "owner_name": "Sarah",
      "is_active": true,
      "last_seen": "2025-11-28T10:35:00",
      "plant_1": {
        "moisture": 65.3,
        "status": "happy",
        "name": "Monstera"
      },
      "plant_2": {
        "moisture": 42.7,
        "status": "warning",
        "name": "Pothos"
      }
    },
    {
      "device_id": "plant-monitor-2",
      "friendly_name": "plant-monitor-2",
      "owner_name": "Tom",
      "is_active": true,
      "last_seen": "2025-11-28T10:32:00",
      "plant_1": {
        "moisture": 71.2,
        "status": "happy",
        "name": "Snake Plant"
      },
      "plant_2": {
        "moisture": 35.6,
        "status": "warning",
        "name": "Fiddle Leaf"
      }
    }
  ]
}
```

### Dashboard Displays

1. **User selector:** Dropdown shows "Sarah", "Tom", etc.
2. **Plant selector:** Shows plants for selected user
3. **Moisture display:** Shows latest reading + status

**Update frequency:** Dashboard refreshes every 30 seconds (calls `/api/devices` again)

---

## Data Delay Timeline

From when a plant dries to when you see it on dashboard:

```
t=0s      Device reads sensors (every 60s)
t=60s     Device reads sensors again
t=120s    Device still reading...
t=600s    Device sends POST (10 minutes after last POST)
t=605s    API receives and stores data
t=610s    Dashboard queries API
t=615s    Dashboard shows updated moisture
          ─────────────────────────────
          Total delay: ~10-15 minutes
```

**In practice:**
- Minimum delay: 0 seconds (if device just sent data)
- Maximum delay: ~20 minutes (if change happens right after device sends)
- **Average:** ~10 minutes

This is why you won't see instant updates - that's by design to save bandwidth/battery.

---

## Multiple Devices Example

Let's say you have 3 devices:

### Device 1: Sarah's (plant-monitor-1)
- Firmware: device_id = "plant-monitor-1", user_name = "Sarah"
- When POSTs: API registers with owner_name = "Sarah"
- Dashboard shows: User "Sarah" with her 2 plants

### Device 2: Tom's (plant-monitor-2)
- Firmware: device_id = "plant-monitor-2", user_name = "Tom"
- When POSTs: API registers with owner_name = "Tom"
- Dashboard shows: User "Tom" with his 2 plants

### Device 3: Alex's (plant-monitor-3)
- Firmware: device_id = "plant-monitor-3", user_name = "Alex"
- When POSTs: API registers with owner_name = "Alex"
- Dashboard shows: User "Alex" with their 2 plants

Dashboard user dropdown automatically populates from `owner_name` in database!

---

## What "Registration" Really Means

**"Registration" = First successful data POST**

There's no signup form, no password, no manual registration.

Instead:
1. You flash device with correct `device_id` and `user_name`
2. Device boots and connects to WiFi
3. Device waits 10 minutes (or you can manually trigger if you add a button)
4. Device POSTs its first reading
5. API sees new `device_id`, creates entry in `devices` table
6. Device is now "registered"
7. Dashboard automatically shows it

**That's it!**

---

## Troubleshooting Registration

### "Device Not Showing in Dashboard"

**Checklist:**

1. **Is device online?**
   - Check OLED display shows WiFi ✓ icon
   - If not, fix WiFi connection first

2. **Has 10 minutes passed?**
   - Device only POSTs every 10 minutes
   - Wait up to 10 minutes from power-on

3. **Is API receiving the POST?**
   ```bash
   # Check API logs
   docker logs -f plants-api | grep "POST\|reading"
   ```
   Should show:
   ```
   INFO: POST /reading from 192.168.1.120
   ```

4. **Is device_id unique?**
   - Check no other device uses same device_id
   - Each device must have different name in firmware

5. **Did user_name change?**
   - If you change user_name in firmware without changing device_id
   - Old device still exists with old user_name
   - You may see duplicates

6. **Check database directly:**
   ```bash
   docker exec -it plants-api sqlite3 /app/data/plants.db
   sqlite> SELECT device_id, owner_name, last_seen FROM devices;
   ```

### "Data Stopped Showing After First Day"

**Likely cause:** Device lost WiFi connection or crashed

**Fixes:**
1. Check device power - might be drained battery
2. Check WiFi connection
3. Look at device logs if you can access it
4. Check API logs for errors

---

## Manual Testing Without Device

Want to test the dashboard before devices are ready?

### Method 1: cURL POST Test Data

```bash
curl -X POST https://plants.suplexcentral.com/api/reading \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "plant-monitor-test",
    "plant_1_moisture": 65.5,
    "plant_2_moisture": 42.3,
    "plant_1_name": "Test Plant 1",
    "plant_2_name": "Test Plant 2",
    "user_name": "TestUser",
    "location": "Test Location"
  }'
```

Dashboard should update immediately!

### Method 2: Update Dashboard to Use Test Data

Edit dashboard HTML to use mock data (already has this):

```javascript
const mockData = {
    'sarah': [
        { plant: 1, name: 'Monstera', moisture: 65, status: 'happy' },
        { plant: 2, name: 'Pothos', moisture: 42, status: 'warning' }
    ]
};
```

This lets recipients test dashboard without device!

---

## Security Note

**No authentication on API endpoints**

The API accepts readings from anyone. In production, you might want:

1. **API key validation** - Check secret key in POST header
2. **IP whitelisting** - Only your devices' IPs
3. **Rate limiting** - Max X POSTs per minute per device_id

For now (trusted friends only), the open API is fine.

---

## Summary

- **Device registers itself** automatically on first POST
- **No manual signup needed** - firmware has all info
- **API stores data** in two tables: `devices` (metadata) and `moisture_sensors` (readings)
- **Dashboard queries API** every 30 seconds and displays latest data
- **Multiple devices** each appear as separate user on dashboard

---

**Created:** 2025-11-28
**API Version:** 1.0
**Database:** SQLite with persistent Docker volume

