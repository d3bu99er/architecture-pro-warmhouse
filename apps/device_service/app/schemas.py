from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from .models import DeviceStatus, DeviceType

class DeviceBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    type: DeviceType
    location: str = Field(..., min_length=1, max_length=100)

class DeviceCreate(DeviceBase):
    user_id: Optional[int] = None
    mac_address: Optional[str] = Field(None, max_length=17)
    ip_address: Optional[str] = Field(None, max_length=15)
    firmware_version: Optional[str] = Field(None, max_length=50)

class DeviceUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    type: Optional[DeviceType] = None
    location: Optional[str] = Field(None, max_length=100)
    mac_address: Optional[str] = Field(None, max_length=17)
    ip_address: Optional[str] = Field(None, max_length=15)
    firmware_version: Optional[str] = Field(None, max_length=50)
    user_id: Optional[int] = None

class DeviceStatusUpdate(BaseModel):
    status: DeviceStatus

class Device(DeviceBase):
    id: int
    status: DeviceStatus
    mac_address: Optional[str] = None
    ip_address: Optional[str] = None
    firmware_version: Optional[str] = None
    user_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_seen: Optional[datetime] = None

    class Config:
        from_attributes = True

class DeviceStats(BaseModel):
    total_devices: int
    online_devices: int
    offline_devices: int
    error_devices: int

class HeartbeatRequest(BaseModel):
    ip_address: Optional[str] = None

class DeviceEvent(BaseModel):
    event_type: str
    device_id: int
    device_name: str
    device_type: str
    location: str
    status: str
    timestamp: datetime

class DeviceStatusChangeEvent(BaseModel):
    device_id: int
    device_name: str
    location: str
    old_status: str
    new_status: str
    timestamp: datetime