# ESPHome Quick Start Guide

## Starting the ESPHome Dashboard

### Step 1: Open PowerShell or Command Prompt
- Press `Win + R`
- Type `powershell` (or `cmd`) and press Enter

### Step 2: Navigate to your project folder
```powershell
cd D:\nextcloud\projects\plants\esphome-config
```

### Step 3: Start the dashboard
```powershell
python -m esphome dashboard .
```

You'll see output like:
```
INFO Starting dashboard web server on http://0.0.0.0:6052 and configuration dir .
```

### Step 4: Open your browser
Go to: **http://localhost:6052**

---

## That's it! 🎉

The web dashboard will show all your devices and let you:
- Create new devices
- Edit configurations (YAML)
- Compile and flash firmware
- View logs in real-time
- Update wirelessly (OTA)

---

## Stopping the Dashboard

Press `Ctrl + C` in the PowerShell/Command Prompt window

---

## Troubleshooting

**Dashboard won't start?**
- Make sure you're in the correct folder: `D:\nextcloud\projects\plants\esphome-config`
- Try closing PowerShell completely and reopening it
- Try using Command Prompt instead of PowerShell

**Can't access http://localhost:6052?**
- Give it a few seconds to start
- Check that the PowerShell window shows the "Starting dashboard" message
- Try a different port: `python -m esphome dashboard --port 6053 .`

**Port already in use?**
- Another instance is running, or something else is using port 6052
- Either stop the other process or use a different port as shown above

---

## One-Liner (Copy & Paste)

If you want to skip the steps, just copy and paste this entire command:
```powershell
cd D:\nextcloud\projects\plants\esphome-config && python -m esphome dashboard .
```

Then open: **http://localhost:6052**
