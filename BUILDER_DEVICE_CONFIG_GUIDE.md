# Plant Monitor - Builder's Device Configuration Guide

**For the Maker (You)** 🔧

This guide explains how to configure, test, and "register" each ESP-32 device before gifting it to a friend.

---

## Overview

Each device needs:

1. **Hardware Assembly** - Sensors soldered, battery installed
2. **Firmware Flashing** - ESPHome uploaded to ESP-32
3. **Configuration** - Device name, plant names, user info set
4. **Local Testing** - Verify sensors work with dummy data
5. **Registration** - Device appears in API and dashboard
6. **Documentation** - Setup card given to recipient

---

## 🔩 STEP 1: Hardware Assembly

### Bill of Materials (per device)

```
1x ESP-32 Dev Board (NodeMCU style)
1x TP4056 USB-C Li-ion Charger Module
1x 18650 Li-ion Battery (3000-3500 mAh)
1x 18650 Battery Holder with wires
2x Capacitive Soil Moisture Sensors
1x 0.96" I2C OLED Display (optional, currently disabled in firmware)
1x Small plastic project box
Wire, solder, hot glue
```

### Pin Assignments

| Component | ESP-32 Pin | Notes |
|-----------|-----------|-------|
| Sensor 1 | GPIO34 | ADC input, measure voltage |
| Sensor 2 | GPIO35 | ADC input, measure voltage |
| OLED SDA | GPIO21 | I2C data (optional) |
| OLED SCL | GPIO22 | I2C clock (optional) |
| TP4056 +5V | 5V | From USB charger |
| TP4056 GND | GND | Ground |
| Battery | TP4056 B+ / B- | Via charger module |

### Assembly Steps

1. **Solder battery holder wires to TP4056**
   - B+ (red) to positive wire
   - B- (black) to negative wire

2. **Connect TP4056 to ESP-32**
   - OUT+ (5V) → ESP-32 5V
   - OUT- (GND) → ESP-32 GND

3. **Connect sensors to ADC pins**
   - Sensor 1 VCC → 3.3V, GND → GND, AO → GPIO34
   - Sensor 2 VCC → 3.3V, GND → GND, AO → GPIO35

4. **Mount in enclosure**
   - Keep USB-C port accessible on back
   - Route sensor wires out bottom

5. **Insert battery**
   - Battery goes into holder, polarity marked
   - Connected to TP4056

---

## 📝 STEP 2: Update Firmware Configuration

Before flashing, customize the firmware for THIS device.

### A. Create Device-Specific Config

Copy `esphome-config/plant-monitor.yaml` and create a new version:

```bash
cd D:\nextcloud\projects\plants\esphome-config
copy plant-monitor.yaml plant-monitor-1.yaml  # For device 1
copy plant-monitor.yaml plant-monitor-2.yaml  # For device 2
# etc.
```

### B. Edit Configuration File

Open `plant-monitor-1.yaml`:

```yaml
esphome:
  name: plant-monitor-1              # Device ID - must be unique
  friendly_name: "Sarah's Plants"    # Display name

# ... rest of config stays the same ...

http_request:

# Automation to send readings every 10 minutes
automation:
  - trigger:
      platform: interval
      interval: 10min
    action:
      - http_request.post:
          url: https://plants.suplexcentral.com/api/reading  # Your domain
          headers:
            Content-Type: application/json
          json:
            device_id: "plant-monitor-1"              # Must match esphome.name
            plant_1_moisture: !lambda 'return id(moisture_1).state;'
            plant_2_moisture: !lambda 'return id(moisture_2).state;'
            plant_1_name: "Monstera"                  # Customize per device
            plant_2_name: "Pothos"                    # Customize per device
            user_name: "Sarah"                        # Recipient's name
            location: "Living Room"                   # Where it's placed
```

### Key Changes Per Device

| Device | device_id | friendly_name | user_name | plant_1_name | plant_2_name | location |
|--------|-----------|---------------|-----------|--------------|--------------|----------|
| #1 | plant-monitor-1 | Sarah's Plants | Sarah | Monstera | Pothos | Living Room |
| #2 | plant-monitor-2 | Tom's Plants | Tom | Snake Plant | Fiddle Leaf | Kitchen |
| #3 | plant-monitor-3 | Alex's Plants | Alex | Succulent | Peace Lily | Bedroom |
| #4 | plant-monitor-4 | Jordan's Plants | Jordan | Rubber Plant | Aloe Vera | Office |

**IMPORTANT:** Each device must have a **unique device_id**. This is how the API identifies which device sent data.

---

## 🔌 STEP 3: Flash Firmware to ESP-32

### Option A: ESPHome Web Flasher (Easiest)

```bash
# Compile the firmware
cd D:\nextcloud\projects\plants\esphome-config
python -m esphome compile plant-monitor-1.yaml
```

1. Navigate to: https://web.esphome.io/
2. Click **"Connect"** → select your board's COM port
3. Click **"Install"** → select compiled `.bin` file
4. Wait for flash to complete
5. Logs should show WiFi connection

### Option B: Command Line

```bash
python -m esphome run plant-monitor-1.yaml
```

Monitor the logs - you should see:
```
[I] [WiFi] Connecting to 'Tigernet3'...
[I] [WiFi] IP Address: 192.168.1.120
[I] [HTTP] Starting HTTP request to https://plants.suplexcentral.com/api/reading
[I] Sending POST request with sensor data
```

---

## 🧪 STEP 4: Local Testing (Without Sensors)

Before giving the device to the recipient, verify it works.

### A. Simulate Sensor Data (Temporary)

Edit `plant-monitor-1.yaml` to use fixed test values:

```yaml
sensor:
  # TESTING: Replace ADC with fixed values
  - platform: template
    name: "Plant 1 Moisture"
    id: moisture_1
    lambda: return 65.0;  # Always return 65% for testing
    unit_of_measurement: "%"

  - platform: template
    name: "Plant 2 Moisture"
    id: moisture_2
    lambda: return 42.0;  # Always return 42% for testing
    unit_of_measurement: "%"
```

### B. Check Dashboard

1. Access dashboard: `https://plants.suplexcentral.com`
2. Select user from dropdown (e.g., "Sarah")
3. Should show:
   - Plant 1: 65% ✓
   - Plant 2: 42% ✓
   - Moisture bars updating

4. Check database:
```bash
# SSH to srv-media-2
docker exec -it plants-api sqlite3 /app/data/plants.db

# Run this query
SELECT device_id, plant_number, moisture_percent, timestamp
FROM moisture_sensors
ORDER BY timestamp DESC LIMIT 10;
```

Expected output:
```
plant-monitor-1|1|65.0|2025-11-28 10:30:00
plant-monitor-1|2|42.0|2025-11-28 10:30:00
plant-monitor-1|1|65.0|2025-11-28 10:20:00
plant-monitor-1|2|42.0|2025-11-28 10:20:00
```

### C. Verify All Endpoints

```bash
# Health check
curl https://plants.suplexcentral.com/api/

# Get device status
curl https://plants.suplexcentral.com/api/device/plant-monitor-1

# Get device list
curl https://plants.suplexcentral.com/api/devices

# Get plant history
curl https://plants.suplexcentral.com/api/device/plant-monitor-1/plant/1/history?limit=5
```

All should return valid JSON with your test data.

---

## 🔄 STEP 5: Switch Back to Real Sensors

Once testing is complete:

### A. Restore Real Sensor Config

In `plant-monitor-1.yaml`, replace the template sensors with real ADC sensors:

```yaml
sensor:
  # Real Moisture Sensor 1 (GPIO34)
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

  # Real Moisture Sensor 2 (GPIO35)
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
```

### B. Re-Flash Device

```bash
python -m esphome run plant-monitor-1.yaml
```

### C. Physical Test

1. Power on device
2. Insert sensors into soil (or water for max reading)
3. Wait 60 seconds for first ADC reading
4. Check OLED display - should show moisture percentages
5. Wait 10 minutes for first API POST
6. Verify data appears on dashboard

---

## 📊 STEP 6: Device Registration in API

The API **auto-registers** devices on first data submission. When the device sends its first reading:

```json
{
  "device_id": "plant-monitor-1",
  "plant_1_moisture": 65.5,
  "plant_2_moisture": 42.3,
  "plant_1_name": "Monstera",
  "plant_2_name": "Pothos",
  "user_name": "Sarah",
  "location": "Living Room"
}
```

The API creates:

1. **DeviceInfo record** (devices table)
   - device_id = "plant-monitor-1"
   - friendly_name = "plant-monitor-1"
   - owner_name = "Sarah"
   - last_seen = current timestamp

2. **MoistureSensor records** (moisture_sensors table)
   - One record per plant per reading
   - Includes device_id, plant_name, user_name, moisture_percent, timestamp

### Verify Registration

```bash
# List all registered devices
curl https://plants.suplexcentral.com/api/devices

# Expected response:
{
  "devices": [
    {
      "device_id": "plant-monitor-1",
      "friendly_name": "plant-monitor-1",
      "owner_name": "Sarah",
      "is_active": true,
      "last_seen": "2025-11-28T10:30:00",
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

If your device isn't showing:
- Check device WiFi connection (OLED display)
- Check API logs: `docker logs -f plants-api`
- Verify device can reach `plants.suplexcentral.com` (DNS resolution)

---

## 📋 STEP 7: Create Setup Card for Recipient

Print or write down this card to include in the device box:

```
╔════════════════════════════════════════════════════╗
║        🌱 PLANT MONITOR SETUP CARD 🌱            ║
├────────────────────────────────────────────────────┤
║                                                    ║
║ Your Device Name: plant-monitor-1                 ║
║ (Leave this as-is)                                ║
║                                                    ║
║ Your Dashboard: https://plants.suplexcentral.com  ║
║ (Bookmark this!)                                  ║
║                                                    ║
║ Your Plants:                                       ║
║  · Monstera (Sensor in left pot)                  ║
║  · Pothos (Sensor in right pot)                   ║
║                                                    ║
║ Setup Steps:                                       ║
║  1. Plug in USB-C cable                           ║
║  2. Insert sensors 2-3 inches into soil           ║
║  3. Wait 30 seconds for boot                      ║
║  4. Open dashboard URL                            ║
║  5. Enter your name: Sarah                        ║
║  6. See your plants!                              ║
║                                                    ║
║ Troubleshooting:                                   ║
║  · No WiFi? See fallback instructions (separate)  ║
║  · No data? Wait 10 minutes for first update      ║
║  · Questions? Contact your gift-giver             ║
║                                                    ║
║ Device ID: plant-monitor-1                        ║
║ User: Sarah                                        ║
║ Location: Living Room                             ║
║                                                    ║
╚════════════════════════════════════════════════════╝
```

---

## 🚀 STEP 8: Handoff Checklist

Before giving the device to the recipient:

- [ ] Device powers on (USB plugged in)
- [ ] OLED displays boot messages
- [ ] OLED shows WiFi connected + IP address
- [ ] Device successfully flashed with correct device_id
- [ ] Sensors physically connected to GPIO34/GPIO35
- [ ] Tested with dummy data - appears on dashboard
- [ ] Switched back to real sensor config
- [ ] Device appears in `/api/devices` endpoint
- [ ] At least 2 data readings sent (20 minutes runtime)
- [ ] Dashboard shows correct user name
- [ ] Plant names correct in dashboard
- [ ] Setup card printed and included in box
- [ ] Recipient knows how to access fallback WiFi if needed
- [ ] You have contact info for troubleshooting

---

## 🔧 Troubleshooting During Build

### Device Won't Boot

**Symptoms:** Red LEDs, no OLED display

**Causes & Fixes:**
1. Battery not charged - try USB power without battery
2. Loose wires - check solder joints
3. Short circuit - carefully inspect soldering
4. Bootloader corrupted - reflash via web.esphome.io

### Sensors Reading 0% or 100%

**Symptoms:** Moisture stuck at extreme values

**Causes & Fixes:**
1. Sensor not connected - verify GPIO34/GPIO35 wires
2. Dry sensor (being tested in air) - insert into soil
3. Bad sensor - swap GPIO34 and GPIO35 to test
4. ADC calibration - raw values may need adjustment (see CALIBRATION section below)

### Device Won't POST to API

**Symptoms:** Device boots, shows WiFi, but no data on dashboard

**Causes & Fixes:**
1. Wrong URL in firmware - verify `https://plants.suplexcentral.com/api/reading`
2. DNS not resolving - check if WiFi has internet access
3. HTTP client disabled - ensure `http_request:` section uncommented
4. device_id mismatch - must match `esphome.name:`
5. Firewall blocking - contact server admin

### Dashboard Shows No Data After 10 Minutes

**Symptoms:** Device is online (logs show POST), but dashboard blank

**Causes & Fixes:**
1. Wrong user_name in API POST - check spelling matches dropdown
2. Browser cache - hard refresh (Ctrl+Shift+R)
3. API not responding - check `curl https://plants.suplexcentral.com/api/`
4. Database error - check API logs: `docker logs -f plants-api`

---

## 📐 CALIBRATION (Advanced)

### Raw ADC Values

The firmware converts ADC readings (0-4095) to percentages (0-100) using:

```
percentage = (1.0 - (raw_value - 1400) / (4095 - 1400)) * 100
```

This assumes:
- **Dry sensor in air:** 4095 (ADC max)
- **Wet sensor in water:** 1400 (ADC min)

### Calibrate for Your Sensors

1. **Get raw ADC values:**
   - Edit config to log raw ADC: `adc_id: adc`
   - Check logs: `python -m esphome logs plant-monitor-1.yaml`

2. **Find dry baseline:**
   - Hold sensor in air
   - Note ADC value (should be ~4000+)

3. **Find wet baseline:**
   - Submerge sensor in water
   - Note ADC value (should be ~1200-1500)

4. **Update formula:**
   ```yaml
   filters:
     - lambda: return (1.0 - (x - 1200) / (4000 - 1200)) * 100.0;
   ```

Replace 1400 and 4095 with your actual values.

---

## 📚 Complete Example Config

Here's a complete `plant-monitor-1.yaml` for reference:

```yaml
esphome:
  name: plant-monitor-1
  friendly_name: "Sarah's Plant Monitor"

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
    ssid: "Plant-Monitor Fallback"
    password: "ND9kIKauNGyJ"

captive_portal:

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

http_request:

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

---

## Next Steps

1. **Build device #1** using steps 1-7
2. **Give to recipient** with setup card
3. **Repeat for devices #2-5** as needed
4. **Monitor initial data** - check dashboard first week for any issues

---

**Created:** 2025-11-28
**Firmware Version:** 1.0
**API Endpoint:** https://plants.suplexcentral.com/api

