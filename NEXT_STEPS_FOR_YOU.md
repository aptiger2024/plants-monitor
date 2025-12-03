# What To Do Next - Your Action Items

Based on where we are in the project right now (2025-11-28)

---

## Current Status

✅ **Done:**
- Backend API running on srv-media-2:7000 (Portainer)
- API type annotation bugs fixed ✓
- Web dashboard configured for production (plants.suplexcentral.com/api)
- Complete documentation created for recipients and builders
- Device registration system ready
- Database (SQLite) persistent and storing data

🟡 **In Progress:**
- Waiting on sensors to arrive (ordered)
- You have 1-2 ESP-32 boards ready

❌ **Not Started:**
- Sensors not yet connected to first device
- No real device has sent data yet
- Telegram alerts not configured
- Additional devices (2-5) not yet built

---

## Immediate Next Steps (This Week)

### Step 1: Prepare for Sensors (Today)

When you mentioned "I'm still waiting on sensors" - here's what to do:

1. **Create firmware config files for each device NOW**
   ```bash
   cd esphome-config
   # Create one config per person you're gifting to:
   cp plant-monitor.yaml plant-monitor-1.yaml  # For Sarah (example)
   cp plant-monitor.yaml plant-monitor-2.yaml  # For Tom
   # Edit each with their names (see QUICK_START_YOUR_NEXT_DEVICE.md)
   ```

2. **Test device WITHOUT sensors (use dummy data)**
   - Edit config to use `platform: template` with fixed values (65% and 42%)
   - Flash to ESP-32
   - Verify dashboard shows data
   - This tests WiFi, API connection, and dashboard without waiting for sensors

3. **Verify API is working**
   ```bash
   # This should return your health check
   curl https://plants.suplexcentral.com/api/

   # List any registered devices
   curl https://plants.suplexcentral.com/api/devices
   ```

### Step 2: When Sensors Arrive (Next 1-2 weeks)

1. **Solder sensors to first ESP-32**
   - GPIO34: Sensor 1 (with 3.3V, GND)
   - GPIO35: Sensor 2 (with 3.3V, GND)
   - Follow BUILDER_DEVICE_CONFIG_GUIDE.md steps 1-2

2. **Switch firmware from dummy data to real sensors**
   - Edit `plant-monitor-1.yaml`
   - Restore ADC sensor config (not template)
   - Re-flash device

3. **Test real sensor data**
   - Insert sensors into soil/water
   - Wait 1 minute for first ADC reading
   - Check OLED display shows percentages
   - Wait 10 minutes for first API POST
   - Verify data on dashboard

4. **Document what you learned**
   - Write down the dry/wet ADC values you observed
   - Update calibration constants if needed
   - Note any issues for other devices

---

## Testing Checklist (Before Sensors Arrive)

You can do all this RIGHT NOW without sensors:

- [ ] Create per-device firmware config files
- [ ] Test device #1 with dummy data (65%, 42%)
- [ ] Verify device boots without errors
- [ ] Verify WiFi connects (OLED shows IP)
- [ ] Verify device POSTs to API (wait 10 minutes)
- [ ] Verify data appears on dashboard
- [ ] Verify device appears in `/api/devices` endpoint
- [ ] Verify data stored in database
- [ ] Verify user "Sarah" shows up in dashboard dropdown

**Time to complete:** ~1 hour
**When to do:** Right now, don't wait for sensors

---

## Building Device #2, #3, etc.

Once you've gotten device #1 working with real sensors:

1. **Reference:** `QUICK_START_YOUR_NEXT_DEVICE.md` (checklist)
2. **Time per device:** ~1.5 hours
3. **Steps:**
   - Assemble hardware
   - Create device-specific firmware config
   - Flash to ESP-32
   - Test with dummy data
   - Verify dashboard
   - Switch to real sensors
   - Handoff to recipient

Repeat for each person you're gifting to.

---

## Things You DON'T Need To Do Yet

❌ **Don't modify Nginx** - You said you already have Nginx running elsewhere. The configuration is in PRODUCTION_SETUP_GUIDE.md if you need it later.

❌ **Don't set up Telegram alerts** - That's in INTEGRATION_GUIDE.md, but only needed after you have working devices.

❌ **Don't rebuild Docker** - Backend is already running on your server. Just updated code fixes, no rebuild needed unless you change something.

❌ **Don't create additional users** - Dashboard automatically creates users based on `user_name` in device firmware.

---

## Who Gets What Documentation

### Your Recipients (When you gift them)

Include with device:
- Print: Setup card (in DEVICE_SETUP_GUIDE.md)
- PDF/Link: DEVICE_SETUP_GUIDE.md (full guide)
- Fallback: Contact info for you if they need help

They follow these steps:
1. Plug in device
2. Connect sensors
3. Wait for WiFi
4. Open dashboard URL
5. Enter their name
6. See their plants!

### You (as the builder)

Keep these handy:
- QUICK_START_YOUR_NEXT_DEVICE.md (checklist for building)
- BUILDER_DEVICE_CONFIG_GUIDE.md (detailed reference)
- DEVICE_REGISTRATION_EXPLAINED.md (understanding the system)

### Your Server (srv-media-2)

Already has:
- Backend API running at 192.168.140.94:7000
- Database with persistent volume
- Health checks enabled

---

## Decision Points Coming Up

### "Should I configure WiFi credentials differently per device?"

**Answer:** No. All devices use same WiFi "Tigernet3". If recipient has different WiFi, they use fallback hotspot (device creates "Plant-Monitor Fallback" AP) to configure.

### "What if someone's WiFi name is different?"

**Answer:** Device has fallback mode. See DEVICE_SETUP_GUIDE.md - STEP 2B.

### "Should I use same device_id for testing?"

**Answer:** No. Each device needs unique device_id (plant-monitor-1, plant-monitor-2, etc.). For testing, use something like "plant-monitor-test", then change before gifting.

### "Can I have multiple devices in same household?"

**Answer:** Yes! Each device has unique device_id. Dashboard shows each user separately.

### "What if they want to monitor 3 plants instead of 2?"

**Answer:** Not with current device. Would need to build a second monitor or modify firmware to use more GPIOs. Future enhancement.

---

## Timeline Estimate

Based on current status:

**Week 1 (Now - Dec 5):**
- [ ] Prepare firmware configs for all recipients
- [ ] Test device #1 with dummy data
- [ ] Wait for sensors to arrive

**Week 2-3 (Dec 6-19):**
- [ ] Solder sensors to device #1
- [ ] Test real sensor readings
- [ ] Document calibration values
- [ ] Build device #2 (repeat testing)
- [ ] Build device #3 (if you have sensors)

**Week 4+ (Dec 20+):**
- [ ] Build remaining devices as needed
- [ ] Prepare recipient setup cards
- [ ] Hand off to friends
- [ ] Support during their initial setup
- [ ] Set up Telegram alerts (optional)

---

## Files You'll Modify Soon

When sensors arrive:

1. **`esphome-config/plant-monitor-1.yaml`**
   - Remove `platform: template` sensors
   - Restore `platform: adc` sensors
   - Update calibration constants if needed

2. **`esphome-config/plant-monitor-2.yaml`** (when building device #2)
   - Create from plant-monitor.yaml
   - Update device_id, user_name, plant names

3. **Dashboard** - No changes needed
   - Already updated to use production API URL
   - Already handles dynamic user/device creation

4. **Backend** - Only if you add new features
   - Already handles device registration
   - Already stores data correctly

---

## Troubleshooting Common Issues NOW

### "I'm testing with dummy data but dashboard shows nothing"

1. Wait 10 minutes - device only POSTs every 10 minutes
2. Check API: `curl https://plants.suplexcentral.com/api/`
3. Check database: `docker exec -it plants-api sqlite3 /app/data/plants.db "SELECT COUNT(*) FROM moisture_sensors;"`
4. If count is 0, device isn't reaching API (network issue?)
5. If count > 0, dashboard might need hard refresh (Ctrl+Shift+R)

### "Device won't connect to WiFi"

1. Check "Tigernet3" WiFi is available (2.4GHz)
2. Check WiFi password in secrets.yaml
3. Try fallback hotspot: look for "Plant-Monitor Fallback" network
4. If still stuck, check device logs (see ESPHOME_QUICKSTART.md)

### "Device won't boot"

1. Check battery/USB power
2. Check no shorts in soldering
3. Try flashing again via web.esphome.io
4. Check bootloader didn't corrupt (look for "invalid header" errors)

---

## Success Criteria

You'll know you're ready to gift device #1 when:

✅ Device boots without errors
✅ OLED shows WiFi connected + IP address
✅ Device sends data to API (check logs)
✅ Data appears on dashboard after 10 minutes
✅ Sensors read realistic values (not 0% or 100%)
✅ Multiple readings stored in database
✅ User name appears correctly in dropdown
✅ Plant names are correct

---

## Questions to Answer Before Building

Before building device #2, ask yourself:

1. **Names:** Who am I giving this to? What are their plants called?
2. **Location:** Where will it be placed? (Living room, bedroom, kitchen?)
3. **Plants:** What types of plants? (helps with naming)
4. **Device ID:** What unique name? (must be different from device #1)

---

## Support Resources

If you get stuck:

1. **Device won't boot:** → ESPHOME_QUICKSTART.md
2. **Firmware won't compile:** → BUILDER_DEVICE_CONFIG_GUIDE.md - Troubleshooting
3. **No data on dashboard:** → DEVICE_REGISTRATION_EXPLAINED.md - Troubleshooting
4. **Need API help:** → API_DOCS.md
5. **General setup:** → DOCUMENTATION_INDEX.md (master index of all guides)

---

## Your Next Action

**TODAY:**

Open `QUICK_START_YOUR_NEXT_DEVICE.md` and follow the testing section WITHOUT sensors.

This will:
- Verify your API is working
- Verify your dashboard is accessible
- Give you confidence when sensors arrive
- Let you know if anything is broken before you solder

**Estimated time:** 1 hour

---

## Celebrate! 🎉

You've completed:
- ✅ Backend API deployed
- ✅ Dashboard configured
- ✅ Documentation complete
- ✅ Device registration system ready

The hard part is done. Now it's just:
1. Solder sensors (20 min per device)
2. Configure firmware (10 min per device)
3. Test (30 min per device)
4. Gift! 🌱

---

**Current Date:** 2025-11-28
**API Status:** Running at 192.168.140.94:7000
**Dashboard:** Ready at plants.suplexcentral.com
**Documentation:** Complete in DOCUMENTATION_INDEX.md

**Next meeting:** When sensors arrive - we'll do first real build together!

