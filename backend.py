"""
Plant Moisture Monitor - FastAPI Backend
Receives sensor data from ESP-32 devices and stores in SQLite database
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from datetime import datetime
import os
from pathlib import Path
from typing import Optional, List, Dict, Any

# Database setup
DATABASE_URL = "sqlite:///./plants.db"
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# FastAPI app setup
app = FastAPI(title="Plant Moisture Monitor API")

# CORS middleware to allow dashboard to make requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# DATABASE MODELS
# ============================================================================

class MoistureSensor(Base):
    """Database model for individual sensor readings"""
    __tablename__ = "moisture_sensors"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String, index=True)  # e.g., "plant-monitor-1"
    plant_number = Column(Integer)  # 1 or 2 per device
    plant_name = Column(String, nullable=True)  # e.g., "Monstera"
    user_name = Column(String, nullable=True)  # e.g., "Sarah"
    location = Column(String, nullable=True)  # e.g., "Living Room"
    moisture_percent = Column(Float)  # 0-100%
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)


class DeviceInfo(Base):
    """Database model for device metadata"""
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String, unique=True, index=True)
    friendly_name = Column(String)
    owner_name = Column(String)
    last_seen = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Integer, default=1)  # 1 = active, 0 = inactive


# Create all tables
Base.metadata.create_all(bind=engine)

# ============================================================================
# PYDANTIC MODELS (for request/response validation)
# ============================================================================

class SensorReadingRequest(BaseModel):
    """Request body when ESP-32 sends moisture data"""
    device_id: str
    plant_1_moisture: float
    plant_2_moisture: float
    plant_1_name: Optional[str] = None
    plant_2_name: Optional[str] = None
    user_name: Optional[str] = None
    location: Optional[str] = None


class PlantData(BaseModel):
    """Plant data response"""
    plant_number: int
    name: Optional[str]
    location: Optional[str]
    user_name: Optional[str]
    current_moisture: float
    status: str  # "happy", "warning", "critical"
    last_reading: datetime


class DeviceStatusResponse(BaseModel):
    """Device status and latest readings"""
    device_id: str
    friendly_name: Optional[str]
    is_active: bool
    last_seen: datetime
    plant_1: PlantData
    plant_2: PlantData


class HistoricalDataResponse(BaseModel):
    """Historical data for a plant"""
    device_id: str
    plant_number: int
    readings: list


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_db():
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_moisture_status(moisture_percent: float) -> str:
    """Determine status based on moisture level"""
    if moisture_percent >= 60:
        return "happy"
    elif moisture_percent >= 30:
        return "warning"
    else:
        return "critical"


# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """Serve the dashboard HTML"""
    dashboard_path = Path(__file__).parent / "dashboard.html"
    if dashboard_path.exists():
        return FileResponse(dashboard_path, media_type="text/html")
    else:
        # Fallback if dashboard.html not found
        return {
            "status": "running",
            "api": "Plant Moisture Monitor",
            "version": "1.0"
        }

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "running",
        "api": "Plant Moisture Monitor",
        "version": "1.0"
    }


@app.post("/reading", response_model=Dict[str, Any])
async def receive_reading(request: SensorReadingRequest, db: Session = Depends(get_db)):
    """
    Receive moisture sensor readings from ESP-32 device

    Expected JSON from ESP-32:
    {
        "device_id": "plant-monitor-1",
        "plant_1_moisture": 65.5,
        "plant_2_moisture": 42.3,
        "plant_1_name": "Monstera",
        "plant_2_name": "Pothos",
        "user_name": "Sarah",
        "location": "Living Room"
    }
    """
    try:
        # Store plant 1 reading
        reading_1 = MoistureSensor(
            device_id=request.device_id,
            plant_number=1,
            plant_name=request.plant_1_name,
            user_name=request.user_name,
            location=request.location,
            moisture_percent=request.plant_1_moisture,
        )
        db.add(reading_1)

        # Store plant 2 reading
        reading_2 = MoistureSensor(
            device_id=request.device_id,
            plant_number=2,
            plant_name=request.plant_2_name,
            user_name=request.user_name,
            location=request.location,
            moisture_percent=request.plant_2_moisture,
        )
        db.add(reading_2)

        # Update device info
        device = db.query(DeviceInfo).filter(
            DeviceInfo.device_id == request.device_id
        ).first()

        if not device:
            device = DeviceInfo(
                device_id=request.device_id,
                friendly_name=request.device_id,
                owner_name=request.user_name or "Unknown",
            )
            db.add(device)

        device.last_seen = datetime.utcnow()

        db.commit()

        return {
            "status": "received",
            "device_id": request.device_id,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/device/{device_id}", response_model=Dict[str, Any])
async def get_device_status(device_id: str, db: Session = Depends(get_db)):
    """
    Get latest sensor readings for a device

    Returns both plants' current moisture levels and status
    """
    # Get latest readings for both plants
    plant_1 = db.query(MoistureSensor).filter(
        MoistureSensor.device_id == device_id,
        MoistureSensor.plant_number == 1
    ).order_by(MoistureSensor.timestamp.desc()).first()

    plant_2 = db.query(MoistureSensor).filter(
        MoistureSensor.device_id == device_id,
        MoistureSensor.plant_number == 2
    ).order_by(MoistureSensor.timestamp.desc()).first()

    device = db.query(DeviceInfo).filter(
        DeviceInfo.device_id == device_id
    ).first()

    if not plant_1 or not plant_2:
        raise HTTPException(status_code=404, detail="No readings found for device")

    return {
        "device_id": device_id,
        "friendly_name": device.friendly_name if device else device_id,
        "is_active": device.is_active == 1 if device else True,
        "last_seen": device.last_seen.isoformat() if device else None,
        "plant_1": {
            "plant_number": 1,
            "name": plant_1.plant_name,
            "location": plant_1.location,
            "user_name": plant_1.user_name,
            "current_moisture": plant_1.moisture_percent,
            "status": get_moisture_status(plant_1.moisture_percent),
            "last_reading": plant_1.timestamp.isoformat()
        },
        "plant_2": {
            "plant_number": 2,
            "name": plant_2.plant_name,
            "location": plant_2.location,
            "user_name": plant_2.user_name,
            "current_moisture": plant_2.moisture_percent,
            "status": get_moisture_status(plant_2.moisture_percent),
            "last_reading": plant_2.timestamp.isoformat()
        }
    }


@app.get("/device/{device_id}/plant/{plant_number}/history", response_model=Dict[str, Any])
async def get_plant_history(device_id: str, plant_number: int, limit: int = 100, db: Session = Depends(get_db)):
    """
    Get historical moisture readings for a specific plant

    Parameters:
        device_id: Device identifier
        plant_number: 1 or 2
        limit: Maximum number of readings to return (default 100)
    """
    if plant_number not in [1, 2]:
        raise HTTPException(status_code=400, detail="plant_number must be 1 or 2")

    readings = db.query(MoistureSensor).filter(
        MoistureSensor.device_id == device_id,
        MoistureSensor.plant_number == plant_number
    ).order_by(MoistureSensor.timestamp.desc()).limit(limit).all()

    if not readings:
        raise HTTPException(status_code=404, detail="No readings found")

    return {
        "device_id": device_id,
        "plant_number": plant_number,
        "plant_name": readings[0].plant_name,
        "readings": [
            {
                "moisture_percent": r.moisture_percent,
                "status": get_moisture_status(r.moisture_percent),
                "timestamp": r.timestamp.isoformat()
            }
            for r in reversed(readings)  # Reverse to oldest first
        ]
    }


@app.get("/devices", response_model=Dict[str, Any])
async def list_devices(db: Session = Depends(get_db)):
    """Get all registered devices and their latest status"""
    devices = db.query(DeviceInfo).all()

    result = []
    for device in devices:
        plant_1 = db.query(MoistureSensor).filter(
            MoistureSensor.device_id == device.device_id,
            MoistureSensor.plant_number == 1
        ).order_by(MoistureSensor.timestamp.desc()).first()

        plant_2 = db.query(MoistureSensor).filter(
            MoistureSensor.device_id == device.device_id,
            MoistureSensor.plant_number == 2
        ).order_by(MoistureSensor.timestamp.desc()).first()

        result.append({
            "device_id": device.device_id,
            "friendly_name": device.friendly_name,
            "owner_name": device.owner_name,
            "is_active": device.is_active == 1,
            "last_seen": device.last_seen.isoformat(),
            "plant_1": {
                "moisture": plant_1.moisture_percent if plant_1 else None,
                "status": get_moisture_status(plant_1.moisture_percent) if plant_1 else None,
                "name": plant_1.plant_name if plant_1 else None
            } if plant_1 else None,
            "plant_2": {
                "moisture": plant_2.moisture_percent if plant_2 else None,
                "status": get_moisture_status(plant_2.moisture_percent) if plant_2 else None,
                "name": plant_2.plant_name if plant_2 else None
            } if plant_2 else None,
        })

    return {"devices": result}


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    print("Starting Plant Moisture Monitor API...")
    print("API running at http://localhost:8000")
    print("API docs at http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)
