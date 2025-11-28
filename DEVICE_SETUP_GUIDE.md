# Plant Moisture Monitor - Device Setup Guide

**For the Gift Recipient** 🌱

This guide walks you through setting up your plant moisture monitor from scratch. No technical knowledge required!

---

## What You're Getting

A WiFi-enabled plant monitor that:
- Checks soil moisture for **2 plants** automatically
- Sends data to a beautiful web dashboard every 10 minutes
- Alerts you when your plants need water
- Works on any WiFi network in your home

---

## 📋 What's Included

Your device comes pre-assembled with:
- ESP-32 microcontroller (brain of the device)
- 2 soil moisture sensors (for Plant 1 & Plant 2)
- 0.96" OLED display (shows moisture levels locally)
- USB-C charging port
- Rechargeable battery
- Sensor cables with connectors

---

## 🔧 STEP 1: Physical Setup (5 minutes)

### A. Unpack and Inspect
1. Remove device from box
2. Check for any loose wires or damage
3. The two sensor cables should be wrapped separately

### B. Power On
1. Plug USB-C cable into a USB power adapter
2. Plug into wall outlet
3. Device should boot (you may see the OLED display light up)
4. Wait 30 seconds for it to fully start

### C. Connect Your Plants
The device comes with **2 sensor cables**:

```
          [Device Box]
         /            \
    [Sensor 1]    [Sensor 2]
        |              |
    Plant A         Plant B
```

1. Insert **Sensor 1** cable into the soil of your first plant (about 2-3 inches deep)
2. Insert **Sensor 2** cable into the soil of your second plant
3. Make sure sensors are fully inserted and not touching pot walls

**IMPORTANT:** The sensors have a polarity - look for directional marks. Insert the **marked end down** into the soil.

---

## 📡 STEP 2: Connect to WiFi (3 minutes)

### Option A: Automatic Connection (If WiFi is 2.4GHz)

The device is pre-configured to connect to **Tigernet3** WiFi automatically.

1. Check that your WiFi name (SSID) is "Tigernet3"
2. Power on the device
3. Wait 30 seconds
4. Check the OLED display - you should see:
   - WiFi icon ✓
   - IP address (e.g., `192.168.1.50`)

**Device is now connected!** ✓

### Option B: Manual WiFi Setup (If your WiFi is different)

If you need to connect to a different WiFi:

1. The device creates a fallback hotspot called **"Plant-Monitor Fallback"**
2. On your phone/computer, look for this WiFi network
3. Connect to it (password: `ND9kIKauNGyJ`)
4. Open browser and go to `http://192.168.4.1`
5. Follow the setup wizard to enter your WiFi credentials
6. Device will restart and connect to your network

---

## 🌐 STEP 3: Access Your Dashboard (2 minutes)

### From Your Phone/Computer

1. **Ask your gift-giver** for the dashboard URL
   - It will look like: `https://plants.suplexcentral.com` or similar
   - **Bookmark this in your browser!**

2. **First time setup:**
   - Enter your name (e.g., "Sarah", "Tom")
   - Click "Save"
   - Your browser will remember you next time

3. **View your plants:**
   - Select your name from the dropdown
   - You should see 2 plants listed
   - **Moisture percentage** appears for each

### What You'll See

```
┌─────────────────────────────────┐
│    Plant Moisture Monitor       │
├─────────────────────────────────┤
│   [Your Name] | [Plant Selector]│
├─────────────────────────────────┤
│                                 │
│            🌿  (or 💀 if dry)   │
│                                 │
│        Moisture: 65%            │
│        [========>---]           │
│                                 │
│   "Living my best life! 🌿"     │
│                                 │
└─────────────────────────────────┘
```

- **Green/blue bar** = Good moisture (60-100%) ✓
- **Yellow bar** = Getting dry (30-60%) ⚠️
- **Red bar** = Needs water now! (<30%) 🚨

---

## ⏱️ How Data Flows

```
Device                  Internet              Dashboard
  ↓                        ↓                      ↓
[ESP-32]  ──WiFi──→  [Cloud Server]  ──→  [Your Browser]
(reads sensors          (stores data)    (shows moisture)
every 1 minute)     (sends every 10 min)  (updates every 30 sec)
```

The device:
1. Reads soil moisture **every 1 minute**
2. Sends data to server **every 10 minutes**
3. Dashboard updates on your browser **every 30 seconds**

So expect a **10-40 second delay** between watering and seeing it on the dashboard.

---

## 🌱 STEP 4: Customize Your Plants (Optional)

Each device has two plants. You can customize:

### On the Device (via Serial Console)
If you're technical, you can edit the configuration file to change:
- Plant names (e.g., "Monstera", "Pothos")
- User name (displayed on dashboard)
- Location (e.g., "Living Room", "Bedroom")

Ask your gift-giver for access to this file if you want to change names.

### On the Dashboard
The dashboard shows whatever names are programmed in the device. If you want different plant names, ask your gift-giver to update the device configuration.

---

## 💧 STEP 5: Understanding Moisture Levels

### Sensor Calibration

Your sensors are pre-calibrated, but moisture readings depend on:
- **Soil type** (clay vs sandy)
- **Plant pot size** (larger = different readings)
- **Sensor depth** (deeper = different readings)

**General Guidelines:**
- **0-20%**: Bone dry - Water immediately!
- **20-40%**: Very dry - Water soon
- **40-60%**: Getting dry - Check daily
- **60-100%**: Moist - Plant is happy

### First Week

During the first week, **observe your plants**:
1. Let one plant dry out completely, note the % reading
2. Water it fully, note the % reading
3. This teaches you what readings mean for YOUR specific plants

---

## 🚨 Alert System

When a plant gets too dry, you may receive **alerts** (if configured):

### Telegram Alerts (If Enabled)
You may get messages like:
- "🌱 **Sarah's Monstera is getting dry!** (35% moisture)"
- "🌱 **ALERT: Tom's Pothos needs water NOW!** (18% moisture)"

To enable alerts, ask your gift-giver to set up Telegram notifications for your name.

---

## 🔧 Troubleshooting

### "Dashboard Shows No Data"

**Wait 10 minutes** - Device sends data every 10 minutes, so:
1. Power on device
2. Wait 10 minutes for first data transmission
3. Refresh dashboard
4. You should see moisture levels

### "WiFi Icon Not Showing (OLED)"

1. Check WiFi name is correct
2. Try power cycling: unplug for 30 seconds, plug back in
3. Check if device is using fallback hotspot (see Step 2B)

### "Moisture Reading is 0% or 100%"

1. **Check sensor connection** - Make sure cables are fully inserted
2. **Check sensor in soil** - Sensor must be 2-3 inches deep
3. **Clean sensor** - Gently wipe with damp cloth, not in water
4. **Try different sensor** - Swap cables to see if problem moves

### "Dashboard Shows Old Data"

The dashboard shows the **latest reading from the device**:
- If device sent data 5 minutes ago, that's what you see
- Device sends every 10 minutes
- So data can be 0-10 minutes old on average

If you want fresher data, ask your gift-giver to adjust the device update frequency.

### "Can't Connect to Fallback WiFi"

1. Make sure you're looking for **"Plant-Monitor Fallback"** network
2. Try forgetting the network and reconnecting
3. Try moving your phone closer to the device
4. If still stuck, ask your gift-giver to help via phone

---

## 🔌 Maintenance

### Battery Care

Your device has a rechargeable **18650 Li-ion battery**:

**DO:**
- Charge once per week (even if not dead)
- Keep between 20-80% for best lifespan
- Use any USB-C charger (5V)

**DON'T:**
- Leave plugged in 24/7
- Let it completely drain (under 5%)
- Expose to extreme heat/cold

**Expected life:** 300-500 charge cycles (1-2 years)

### Sensor Care

1. **Don't submerge** - Sensors are water-resistant, not waterproof
2. **Avoid salt** - Salt water kills sensors (don't use softened water)
3. **Clean monthly** - Gently wipe with damp (not soaking) cloth
4. **Replace if damaged** - Contact your gift-giver for spare sensors

---

## 📞 Getting Help

### Common Questions

**Q: Why does moisture jump around?**
A: Sensors are sensitive! Each reading varies slightly. The device averages the last 7 readings (takes ~7 minutes), so expect ~2% variation.

**Q: Can I use this outside?**
A: Not recommended. The battery and electronics aren't weatherproof. Keep indoors only.

**Q: What if I go on vacation?**
A: Device keeps sending data. Dashboard stores the last 7 days of readings. When you return, you can see exactly when your plants dried out!

**Q: Can I monitor more than 2 plants?**
A: Not with this device. You'd need a second monitor. Ask your gift-giver if they can build one!

### Contact Your Gift-Giver

For technical issues:
- Device won't turn on
- WiFi won't connect
- Dashboard shows nothing
- Sensor readings seem wrong

**Ask your gift-giver for help** - they have the source code and can debug!

---

## 🎉 You're All Set!

Your plant monitor is ready to keep your plants happy.

**Quick checklist:**
- ✓ Device powered on
- ✓ Sensors in soil
- ✓ WiFi connected (WiFi icon visible)
- ✓ Dashboard accessible at given URL
- ✓ You've entered your name
- ✓ Moisture readings showing on dashboard

**Enjoy your plant monitoring!** 🌿

---

## 📋 Device Information Card

Print or screenshot this for reference:

```
╔═══════════════════════════════════════╗
║   YOUR PLANT MONITOR INFO             ║
├═══════────────────────────────────────┤
║ Device Name: ___________________      ║
║ Plant 1 Name: _________________      ║
║ Plant 2 Name: _________________      ║
║ Your Name (on dashboard): __________  ║
║                                       ║
║ Dashboard URL: __________________     ║
║                                       ║
║ WiFi Network: ___________________    ║
║ WiFi Password: __________________   ║
║                                       ║
║ Fallback Hotspot: Plant-Monitor FB   ║
║ Fallback Password: ND9kIKauNGyJ      ║
║                                       ║
║ Support Contact: __________________  ║
╚═══════════════════════════════════════╝
```

---

**Created:** 2025-11-28
**Device Version:** 1.0
**Firmware:** ESPHome (esp-idf framework)

