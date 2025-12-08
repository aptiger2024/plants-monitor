# Plant Monitor - Device Setup Guide

## Overview

Your Plant Monitor device has been pre-configured and is ready to go! This guide walks you through the simple setup process to get your device connected to your home WiFi and monitoring your plants.

## What You'll Need

- Your Plant Monitor device (in package)
- USB-C power adapter
- Your home WiFi SSID (network name)
- Your home WiFi password
- A smartphone or computer with WiFi capability

## Setup Steps

### Step 1: Power On Your Device

1. Connect the USB-C power adapter to the device
2. The device will boot up (takes about 30 seconds)
3. You should see a WiFi hotspot appear called **"Plant-Monitor Fallback"**

### Step 2: Connect to Device Hotspot

1. On your phone or computer, open WiFi settings
2. Look for the network: **"Plant-Monitor [Name]"** (e.g., "Plant-Monitor Laurie")
3. Connect to it using password: **flowers123**

*Note: This network has NO internet. It's only for setup. Don't worry - once setup is complete, the device will automatically connect to your home WiFi.*

### Step 3: Open Setup Form

1. Once connected to "Plant-Monitor Fallback", open a web browser
2. Visit: **http://192.168.4.1/**
3. You should see the Plant Monitor setup page

*On some devices, you may get a popup to complete setup automatically. If so, follow the prompts.*

### Step 4: Complete the Setup Form

Fill in the following information:

- **Your Name** *(required)* - Your first name (e.g., "Laurie")
- **Device Name** - Optional friendly name for your monitor (e.g., "Living Room Monitor")
- **Plant 1 Name** - Name of the first plant (e.g., "Monstera")
- **Plant 2 Name** - Name of the second plant (e.g., "Pothos")
- **Location** - Where the device is (e.g., "Living Room")

### Step 5: Click "Complete Setup"

1. Click the **"Complete Setup"** button
2. You should see a success message: "✅ Setup Complete!"

### Step 6: Connect to Your Home WiFi

1. **Important**: You should now see a new WiFi network appear with your device's name
2. This network will have WiFi connection info (you may see it briefly in setup logs)
3. The device will automatically attempt to connect to your configured WiFi
4. Give it 30-60 seconds to connect

### Step 7: Verify Connection

1. Return to your normal home WiFi network on your phone
2. Visit: **http://plants.suplexcentral.com** or **http://192.168.140.94:7000**
3. You should see your Plant Monitor dashboard
4. Your device should appear in the dashboard after sending its first sensor reading (within 1-2 minutes)

## Dashboard Access

Once your device is set up and connected, you can monitor your plants at:

**http://plants.suplexcentral.com**

The dashboard shows:
- Current moisture levels for each plant
- Plant health status (Happy / Warning / Critical)
- Historical moisture trends
- WiFi signal strength

## Troubleshooting

### Device Doesn't Appear in Dashboard

1. **Check WiFi connection**: Make sure your device connected to your home WiFi
2. **Wait for first reading**: Devices send data every 10 minutes. Wait at least 2 minutes after setup.
3. **Check sensor connection**: Make sure the moisture sensors are properly soldered to GPIO34 and GPIO35

### Can't Connect to Setup Hotspot

1. Make sure device is powered on
2. Look for "Plant-Monitor Fallback" in WiFi networks
3. Try reconnecting to the hotspot
4. If still not visible, unplug device and wait 10 seconds, then plug back in

### Can't Access Setup Page (http://192.168.4.1)

1. Make sure you're connected to "Plant-Monitor Fallback" WiFi
2. Try opening in a different browser
3. Clear browser cache and try again
4. Try visiting http://192.168.4.1 directly (no https)

### Device Won't Connect to Home WiFi

1. Make sure your WiFi SSID and password are correct
2. Check that your WiFi network isn't using special characters in the name
3. Try rebooting the device by unplugging and replugging USB power

## Technical Details

### Hardware Specifications

- **Microcontroller**: ESP-32 Development Board
- **Moisture Sensors**: Capacitive soil moisture sensors on GPIO34 and GPIO35
- **Power**: 5V USB-C (TP4056 charging module with 18650 battery support)
- **WiFi**: 802.11 b/g/n

### Software

- **Firmware**: ESPHome 2025.11.0 with ESP-IDF framework
- **API**: FastAPI backend running Python
- **Database**: SQLite for sensor readings and device info
- **Data Updates**: Every 60 seconds (sensor reading), every 10 minutes (API upload)

### Default Credentials

During setup, the device's local web interface uses:
- **Username**: admin
- **Password**: admin

This is only for the local network setup page.

## Support & Advanced Configuration

For technical support or to reconfigure your device:

1. Contact the person who gave you this device
2. If needed, the device can be reset by:
   - Unplugging for 30 seconds
   - Plugging back in
   - Reconnecting to "Plant-Monitor [Name]" hotspot
   - Completing setup again with new information

## Enjoying Your Plant Monitor

Once set up:

1. **Monitor regularly**: Check your dashboard daily to track plant health
2. **Respond to alerts**: When moisture gets critical (too low), water your plants
3. **Track trends**: Watch how moisture levels change over time
4. **Share results**: You can share your plants' progress with friends!

Your Plant Monitor will help you keep your plants healthy by providing real-time moisture data. Happy gardening! 🌱

---

**Device ID**: Each device has a unique ID (e.g., `plant-monitor-laurie`) that appears in the dashboard. This identifies your specific device.

**Questions?** Refer back to the person who gave you this device or consult the troubleshooting section above.
