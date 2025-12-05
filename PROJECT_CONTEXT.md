# Plant Moisture Monitor Project - Context & Status

## Project Overview
Building custom **plant moisture monitors** as gifts for friends. Each device monitors **2 plants independently** with WiFi connectivity and cute dashboard.

**Tech Stack:**
- Hardware: ESP-32 + dual capacitive soil moisture sensors + 0.96" I2C OLED display
- Firmware: ESPHome (YAML-based)
- Backend: FastAPI (Python) on home server (Proxmox/Docker/Portainer)
- Dashboard: Single-page HTML with user selector (no passwords, trusted friends only)
- Notifications: Telegram bot via N8N

---

## Current Status

### ✅ Completed
1. **Parts List** - All hardware sourced and ready to order
2. **Web Dashboard** (`dashboard.html`) - Enhanced with:
   - User selector (Sarah, Tom, Alex, Jordan)
   - Plant selector (dynamically updates per user)
   - Moisture display with animated plant icon
   - Cheeky messages (happy/warning/critical)
   - Settings modal for customizing thresholds
   - **NEW:** Welcome screen with cute plant animation
   - **NEW:** Plant droops/wilts animation when dry
   - **NEW:** Alarm sound when plant critical
   - **NEW:** Water sprinkles animation
   - **NEW:** Cookie-based user persistence (remembers name)
   - No authentication (trusted friends)

3. **ESPHome Installation** - Set up on Windows
   - ESPHome dashboard runs: `python -m esphome dashboard .`
   - Quick start guide created: `ESPHOME_QUICKSTART.md`
   - Use web flasher (https://web.esphome.io/) for flashing - most reliable!

4. **Firmware Config** (`plant-monitor.yaml`) - Compiled successfully ✅
   - Dual moisture sensors (GPIO34 & GPIO35)
   - I2C OLED display (GPIO21 & GPIO22)
   - WiFi connectivity
   - API ready for integration
   - Critical alerts (<20% moisture)

### ✅ Recent Fixes (Session 3-4)
- **Firmware Flash Issue RESOLVED** ✅
  - Root cause: Web flasher was missing bootloader + partition table
  - Solution: Used esptool to flash bootloader, partition table, and firmware together
  - ESP-32 now boots successfully and connects to WiFi
  - Switched framework from Arduino to esp-idf for stability

- **FastAPI Backend Created & Deployed** ✅
  - Full REST API for receiving and retrieving sensor data
  - SQLite database for persistent storage
  - Endpoints for: readings, device status, historical data, device list
  - CORS enabled for web dashboard integration
  - API docs at http://localhost:8000/docs
  - Running on srv-media-2:7000 via Portainer
  - Database uses persistent Docker volume

- **Type Annotation Bugs Fixed** ✅ (Session 4)
  - Fixed FastAPI response model validation errors
  - All endpoints now use proper dependency injection with `Depends(get_db)`
  - Added explicit `response_model=Dict[str, Any]` to all endpoints
  - Changes pushed to GitHub, ready for Portainer rebuild

- **Comprehensive Documentation Created** ✅ (Session 4)
  - DEVICE_SETUP_GUIDE.md - For gift recipients (non-technical)
  - BUILDER_DEVICE_CONFIG_GUIDE.md - Complete device build & config guide
  - QUICK_START_YOUR_NEXT_DEVICE.md - Checklist for building devices #2-5
  - DEVICE_REGISTRATION_EXPLAINED.md - How registration and data flow works
  - DOCUMENTATION_INDEX.md - Master navigation index
  - NEXT_STEPS_FOR_YOU.md - Immediate action items

### 🔄 In Progress
- Waiting for capacitive soil moisture sensors to arrive
- Charger board arrived (micro USB) - found USB-C alternative: https://www.amazon.ca/Charging-Lithium-Battery-Protection-Discharge/dp/B0D7Z92K51/ ✅

### ⏳ Not Started
- Soldering sensors to first ESP-32 device (waiting on sensors)
- N8N Telegram bot workflow
- Making all 3-5 devices
- OLED display integration (currently disabled for stability)

---

## Hardware Setup

### Per Device
```
1x ESP-32 (NodeMCU)
1x TP4056 USB-C Charger Module
1x 18650 Li-ion Battery (3000-3500mAh)
1x 18650 Battery Holder (pre-soldered wires)
1x 0.96" I2C OLED Display
2x Capacitive Soil Moisture Sensors
1x Small plastic project box (enclosure)
```

### Pin Assignment
| Component | Pin(s) | Type |
|-----------|--------|------|
| Sensor 1 | GPIO34 | ADC Input |
| Sensor 2 | GPIO35 | ADC Input |
| OLED SDA | GPIO21 | I2C |
| OLED SCL | GPIO22 | I2C |
| OLED Power | 3.3V + GND | Power |
| Battery | 5V from TP4056 | Power |

### Physical Layout
```
┌─────────────────────────────────┐
│     OLED Display (0.96")        │
│                                 │
│  ESP-32, TP4056, 18650 inside   │
│                                 │
│  [USB-C Port] (back)           │
│                                 │
│  Two sensor wires exit bottom:  │
│  └─→ Plant 1 sensor            │
│  └─→ Plant 2 sensor            │
└─────────────────────────────────┘
```

---

## Files & Locations

```
D:\nextcloud\projects\plants\
├── dashboard.html                    # Web dashboard (complete with animations)
├── backend.py                        # FastAPI backend (running on :8000)
├── API_DOCS.md                       # API documentation
├── ESPHOME_QUICKSTART.md             # ESPHome quick start guide
├── PROJECT_CONTEXT.md                # This file
├── plants.db                         # SQLite database (auto-created)
└── esphome-config/
    ├── plant-monitor.yaml            # Firmware config (tested & working)
    └── secrets.yaml                  # WiFi credentials (Tigernet3)
```

---

## Next Steps (In Order)

### 1. Compile & Flash Firmware
```powershell
cd D:\nextcloud\projects\plants\esphome-config
python -m esphome compile plant-monitor.yaml
```

If compilation succeeds:
- Download the `.bin` file
- Use https://web.esphome.io/ to flash to ESP-32
- Watch logs to confirm WiFi connection

### 2. Test Dual Sensors
- Connect two moisture sensors (or potentiometers) to GPIO34 & GPIO35
- Power on the device
- OLED should display both plant moisture levels
- Watch Home Assistant logs or web serial output

### 3. Build Backend API
- Create FastAPI endpoint to receive sensor readings
- Two plants per device = one POST request with both moisture values
- Store in SQLite database

### 4. Connect Dashboard to API
- Replace mock data in `dashboard.html` with real API calls
- Update every 5-10 minutes

### 5. Set Up Telegram Alerts
- Create N8N workflow
- Trigger when moisture < critical threshold
- Send message to user

### 6. Assemble All 5 Devices
- Repeat hardware assembly
- Flash firmware to each board
- Test each device

---

## Useful Commands

### ESPHome
```powershell
# Start dashboard
python -m esphome dashboard .

# Compile only
python -m esphome compile plant-monitor.yaml

# Compile and upload via USB
python -m esphome run plant-monitor.yaml

# View logs
python -m esphome logs plant-monitor.yaml

# Update ESPHome
pip install --upgrade esphome
```

### Dashboard Access
- **URL:** `http://localhost:6052`
- **Users:** Sarah, Tom, Alex, Jordan (no password)
- **Plants:** 2 per user (mock data currently)

---

## Known Issues & Solutions

### ESPHome Compilation Error (FileNotFoundError)
- **Status:** Encountered on first wizard attempt
- **Solution:** Use command line compile instead: `python -m esphome compile plant-monitor.yaml`
- **Alternative:** If still failing, might need platformio fix

### USB Connection Issues
- **Make sure:** Using a data cable (not just charging)
- **Check:** Device Manager for COM port
- **Install drivers:** CP210x or CH340 (board-dependent)

---

## Cheeky Plant Messages (Already in Dashboard)

**Happy (60-100%):**
- "Living my best life! 🌿"
- "Absolutely thriving, mate!"
- "I'm so moist right now 😎"

**Warning (30-60%):**
- "Could use a sip, ngl"
- "Getting a bit parched here..."
- "Hint hint, nudge nudge 💧"

**Critical (<30%):**
- "WATER ME YOU MONSTER 😭"
- "I'm literally desiccating rn"
- "THIRSTY THIRSTY THIRSTY"

---

## Project Goals (Summary)

1. ✅ Design cute, simple web dashboard
2. ✅ Write dual-sensor firmware
3. ✅ Flash firmware to ESP-32 (boots successfully, connects to WiFi)
4. ✅ Build backend API (FastAPI with SQLite, running on srv-media-2:7000)
5. ✅ Connect dashboard to real API (updated to use https://plants.suplexcentral.com/api)
6. ⏳ Set up Telegram alerts (N8N integration - next step)
7. ⏳ Build 3-5 physical devices (waiting on sensors, then can build with full instructions)
8. ⏳ Gift to friends! (comprehensive setup guides ready)

---

## Notes for Next Session

**Hardware Status:**
- You have **2 ESP-32 boards** already ✅
- Charger board: micro USB version arrived (ordering USB-C alternative)
- **Waiting on:** capacitive soil moisture sensors (6-10 for 3-5 devices)

**Software Status:**
- Backend API: **Running on srv-media-2:7000** ✅
- Dashboard: **Ready at plants.suplexcentral.com** ✅
- Database: **Persistent SQLite volume** ✅
- Device registration: **Automatic on first POST** ✅
- Type annotations: **Fixed** ✅

**Documentation Ready:**
- DEVICE_SETUP_GUIDE.md - For gift recipients
- BUILDER_DEVICE_CONFIG_GUIDE.md - For building devices
- QUICK_START_YOUR_NEXT_DEVICE.md - Checklist template
- DEVICE_REGISTRATION_EXPLAINED.md - How it works
- NEXT_STEPS_FOR_YOU.md - Your action items
- See DOCUMENTATION_INDEX.md for full list

**When Sensors Arrive:**
1. Create per-device firmware configs (plant-monitor-1.yaml, plant-monitor-2.yaml, etc.)
2. Solder sensors to GPIO34/GPIO35
3. Test with real data
4. Prepare recipient setup cards
5. Gift devices!

---

**Last Updated:** 2025-11-28 (Session 4)
**Status:**
- ✅ Production API running and tested
- ✅ Dashboard fully configured
- ✅ Device registration system ready
- ✅ Complete documentation created
- ⏳ Waiting on sensors for first real device build
- 🎯 Next: Build device #1 when sensors arrive, then replicate for devices #2-5
