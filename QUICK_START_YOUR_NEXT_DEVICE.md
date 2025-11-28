# Your Next Device Setup - Quick Checklist

Checklist for building and registering your next plant monitor (device #2, #3, etc.)

---

## Before You Start

- [ ] You have the BUILDER_DEVICE_CONFIG_GUIDE.md open
- [ ] You have hardware: ESP-32, sensors, TP4056, battery
- [ ] You know who you're gifting this to (their name)
- [ ] Your API is running at: `https://plants.suplexcentral.com/api`

---

## 🔩 HARDWARE BUILD (30 minutes)

1. [ ] Solder TP4056 to battery holder (B+ and B- wires)
2. [ ] Connect TP4056 to ESP-32 (5V and GND)
3. [ ] Solder sensors to GPIO34 and GPIO35 (with 3.3V/GND)
4. [ ] Test power - ESP-32 boots without errors
5. [ ] Mount in enclosure - USB-C port accessible

---

## 📝 FIRMWARE CONFIG (10 minutes)

### Step 1: Create New Config File

```bash
cd D:\nextcloud\projects\plants\esphome-config
copy plant-monitor.yaml plant-monitor-2.yaml  # Change number
```

### Step 2: Edit File

Open `plant-monitor-2.yaml` and change these values:

| Section | Field | Old Value | New Value |
|---------|-------|-----------|-----------|
| esphome | name | plant-monitor | **plant-monitor-2** |
| esphome | friendly_name | plant-monitor | **Tom's Plants** |
| automation | device_id | plant-monitor-1 | **plant-monitor-2** |
| automation | user_name | (empty) | **Tom** |
| automation | plant_1_name | (empty) | **Snake Plant** |
| automation | plant_2_name | (empty) | **Fiddle Leaf Fig** |
| automation | location | (empty) | **Kitchen** |

**Key Rule:** device_id must match esphome.name!

---

## ⚡ FLASH TO ESP-32 (5 minutes)

### Option A: ESPHome Web Flasher (Easiest)

```bash
# Terminal
cd D:\nextcloud\projects\plants\esphome-config
python -m esphome compile plant-monitor-2.yaml

# Then:
# 1. Go to https://web.esphome.io/
# 2. Click "Connect" → select COM port
# 3. Click "Install" → select .bin file
# 4. Wait for success message
```

### Option B: Direct Command

```bash
python -m esphome run plant-monitor-2.yaml
```

---

## 🧪 LOCAL TESTING (15 minutes)

### Test 1: Check OLED Display

- [ ] Device boots without errors
- [ ] OLED shows: "Plant Monitor Starting..."
- [ ] After 30 seconds: WiFi icon ✓ + IP address
- [ ] OLED shows both moisture levels (0% initially without sensors)

### Test 2: Check WiFi Connection

1. Look for OLED showing: `IP: 192.168.1.???`
2. From your computer, ping the device:
   ```bash
   ping 192.168.1.???
   # Should show "Reply from..."
   ```

### Test 3: Simulate Data (Without Real Sensors)

Edit `plant-monitor-2.yaml` temporarily:

```yaml
sensor:
  - platform: template
    name: "Plant 1 Moisture"
    id: moisture_1
    lambda: return 65.0;  # Always return 65%
    unit_of_measurement: "%"

  - platform: template
    name: "Plant 2 Moisture"
    id: moisture_2
    lambda: return 42.0;  # Always return 42%
    unit_of_measurement: "%"
```

Re-flash, then wait 10-15 minutes.

### Test 4: Check Dashboard

1. Open: `https://plants.suplexcentral.com`
2. Select user: "Tom" from dropdown
3. Should show:
   - Plant 1 (Snake Plant): 65% ✓
   - Plant 2 (Fiddle Leaf Fig): 42% ✓

### Test 5: Verify Database

```bash
docker exec -it plants-api sqlite3 /app/data/plants.db

.mode column
.headers on
SELECT device_id, plant_number, moisture_percent, timestamp
FROM moisture_sensors
WHERE device_id = 'plant-monitor-2'
ORDER BY timestamp DESC LIMIT 5;
```

Should show your test data!

---

## 🔄 RESTORE REAL SENSORS (5 minutes)

Once testing passes:

1. [ ] Restore ADC sensors in config:
   ```yaml
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
   ```

2. [ ] Re-flash device
3. [ ] Insert sensors into test soil/water
4. [ ] Verify readings on OLED after 60 seconds
5. [ ] Wait 10+ minutes for dashboard update

---

## ✅ FINAL CHECKS

Before giving to recipient:

- [ ] Device powers on (USB plugged in)
- [ ] OLED displays boot messages
- [ ] WiFi connects (icon shows on OLED)
- [ ] At least 2 POSTs sent (20+ minutes runtime)
- [ ] Dashboard shows device + both plants
- [ ] Moisture readings are reasonable (not 0% or 100%)
- [ ] User name correct ("Tom" in this example)
- [ ] Plant names correct
- [ ] Device ID in database matches firmware (`plant-monitor-2`)

---

## 📦 PREPARE FOR RECIPIENT

### Print Setup Card

```
╔═══════════════════════════════════════╗
║  Plant Monitor Setup Card             ║
├───────────────────────────────────────┤
║                                       ║
║ Device Name: plant-monitor-2          ║
║ Owner: Tom                            ║
║                                       ║
║ Plants:                               ║
║  1. Snake Plant (left sensor)         ║
║  2. Fiddle Leaf Fig (right sensor)    ║
║                                       ║
║ Dashboard: https://plants.suplexcentral.com
║                                       ║
║ First Time Setup:                     ║
║  1. Plug in USB-C cable               ║
║  2. Insert sensors in pots            ║
║  3. Open dashboard URL                ║
║  4. Enter your name: Tom              ║
║  5. See your plants!                  ║
║                                       ║
║ Questions? See DEVICE_SETUP_GUIDE.md  ║
║                                       ║
╚═══════════════════════════════════════╝
```

### Package Contents

- [x] Device (powered off)
- [x] USB-C cable
- [x] Setup card (printed)
- [x] Link to full guide: `DEVICE_SETUP_GUIDE.md`

---

## 🚀 DEVICE #3, #4, #5...

Repeat the same checklist, just change:
- device_id: `plant-monitor-3`, `plant-monitor-4`, etc.
- user_name: new recipient's name
- plant names
- location

---

## Troubleshooting Quick Fixes

| Problem | Quick Fix |
|---------|-----------|
| Device won't boot | Check battery power, try USB-only first |
| WiFi won't connect | Check SSID is "Tigernet3", try fallback hotspot |
| No OLED display | OLED support is disabled, that's normal |
| 0% moisture reading | Sensor not in soil, or disconnected |
| Dashboard shows no data | Wait 10 minutes, refresh browser, hard refresh (Ctrl+Shift+R) |
| Multiple same devices | device_id mismatch - check firmware matches esphome.name |

---

## When Recipients Ask Questions

### "How do I know if it's working?"

A: 1) Device power LED on, 2) OLED shows "WiFi ✓", 3) Dashboard shows plants after 10 minutes

### "Why does it update every 10 minutes?"

A: To save battery and server load. Devices are on batteries, so we batch updates.

### "Can I water my plant and see it immediately?"

A: No, up to 15 minute delay. That's normal. Check in a few minutes, not instantly.

### "Why is the reading jumping around?"

A: Sensors vary slightly. Device averages the last 7 readings (~7 minutes), so expect ±2% variation.

---

## You're Ready!

Next device: **[Device Name] for [Recipient]**

Expected timeline:
- Hardware build: 30 min
- Firmware config: 10 min
- Testing: 30 min
- **Total: ~1.5 hours per device**

Once you've built 1-2 devices, you'll have the workflow down and subsequent devices will be faster.

---

**Last Updated:** 2025-11-28
**Current Devices Built:** 1 (waiting on sensors for more)
**Next Device:** #2 (ready to build)

