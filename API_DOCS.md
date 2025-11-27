# Plant Moisture Monitor - API Documentation

## Overview

FastAPI backend that receives sensor data from ESP-32 devices and provides endpoints for the web dashboard to fetch real-time and historical plant moisture data.

## Running the Backend

```bash
cd D:\nextcloud\projects\plants
python backend.py
```

The API will start on **http://localhost:8000**

### Interactive API Docs
- Swagger UI: **http://localhost:8000/docs**
- ReDoc: **http://localhost:8000/redoc**

---

## Database

SQLite database at `D:\nextcloud\projects\plants\plants.db`

Two tables:
- **moisture_sensors** - Individual sensor readings (one row per reading)
- **devices** - Device metadata and last seen timestamps

---

## Endpoints

### 1. Health Check
```
GET /
```

**Response:**
```json
{
  "status": "running",
  "api": "Plant Moisture Monitor",
  "version": "1.0"
}
```

---

### 2. Submit Sensor Reading
```
POST /reading
```

**Request Body:**
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

**Response:**
```json
{
  "status": "received",
  "device_id": "plant-monitor-1",
  "timestamp": "2025-11-26T23:49:25.961788"
}
```

**Notes:**
- `device_id` - Required, unique identifier for device
- `plant_1_moisture`, `plant_2_moisture` - Required, percentage (0-100)
- Other fields are optional for flexibility

---

### 3. Get Device Status (Latest Readings)
```
GET /device/{device_id}
```

**Example:**
```
GET /device/plant-monitor-1
```

**Response:**
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

**Status Values:**
- `"happy"` - Moisture >= 60%
- `"warning"` - Moisture 30-60%
- `"critical"` - Moisture < 30%

---

### 4. Get Plant History
```
GET /device/{device_id}/plant/{plant_number}/history?limit=100
```

**Example:**
```
GET /device/plant-monitor-1/plant/1/history?limit=50
```

**Parameters:**
- `device_id` - Device identifier
- `plant_number` - 1 or 2
- `limit` - Maximum readings to return (default: 100)

**Response:**
```json
{
  "device_id": "plant-monitor-1",
  "plant_number": 1,
  "plant_name": "Monstera",
  "readings": [
    {
      "moisture_percent": 65.5,
      "status": "happy",
      "timestamp": "2025-11-26T23:49:25.625455"
    },
    {
      "moisture_percent": 63.2,
      "status": "happy",
      "timestamp": "2025-11-26T23:35:12.123456"
    }
  ]
}
```

---

### 5. List All Devices
```
GET /devices
```

**Response:**
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

## Integration with ESP-32

The ESP-32 firmware needs to send periodic POST requests to `/reading` endpoint.

### ESPHome Integration (Future)

Once ESPHome has HTTP client support enabled, add this to `plant-monitor.yaml`:

```yaml
# HTTP Client (send readings to backend)
http_request:

# Automation to send readings every 10 minutes
automation:
  - trigger:
      platform: interval
      interval: 10min
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

---

## Error Responses

### Device Not Found
```json
{
  "detail": "No readings found for device"
}
```

### Invalid Plant Number
```json
{
  "detail": "plant_number must be 1 or 2"
}
```

### Server Error
```json
{
  "detail": "Internal server error message"
}
```

---

## CORS Headers

The API allows cross-origin requests from any source (for the web dashboard):

```
Access-Control-Allow-Origin: *
Access-Control-Allow-Credentials: true
Access-Control-Allow-Methods: *
Access-Control-Allow-Headers: *
```

---

## Database Queries (SQLite)

View all readings:
```sql
SELECT device_id, plant_number, moisture_percent, timestamp
FROM moisture_sensors
ORDER BY timestamp DESC;
```

Get latest reading for each device:
```sql
SELECT device_id, plant_number, moisture_percent, timestamp
FROM moisture_sensors
WHERE (device_id, timestamp) IN (
  SELECT device_id, MAX(timestamp)
  FROM moisture_sensors
  GROUP BY device_id, plant_number
);
```

---

## Status Thresholds

Configurable in code at `get_moisture_status()` function:

Currently:
- Happy: >= 60%
- Warning: 30-60%
- Critical: < 30%

Modify the function to change thresholds based on your needs.
