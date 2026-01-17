from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from .database import Base
import enum

class DeviceStatus(str, enum.Enum):  # ✅ Стандартный enum.Enum
    ONLINE = "online"
    OFFLINE = "offline"
    ERROR = "error"
    MAINTENANCE = "maintenance"
    CONFIGURING = "configuring"
    LOW_BATTERY = "low_battery"

class DeviceType(str, enum.Enum):  # ✅ Стандартный enum.Enum
    TEMPERATURE_SENSOR = "temperature_sensor"
    HUMIDITY_SENSOR = "humidity_sensor"
    MOTION_SENSOR = "motion_sensor"
    UNKNOWN = "unknown"

class Device(Base):
    __tablename__ = "devices"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    type = Column(String(50), nullable=False)  # ✅ String вместо Enum
    location = Column(String(100), nullable=False)
    status = Column(String(20), nullable=False, default="offline")  # ✅ String
    mac_address = Column(String(17), unique=True)
    ip_address = Column(String(15))
    firmware_version = Column(String(50))
    user_id = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True))
    last_seen = Column(DateTime(timezone=True))
    
    # ✅ Check constraints (опционально)
    __table_args__ = (
        {'schema': None}
    )