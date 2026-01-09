from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app import schemas, crud, services, models

router = APIRouter(prefix="/devices", tags=["Device Management"])

@router.get("/", response_model=List[schemas.Device])
async def get_devices(
    user_id: Optional[int] = Query(None),
    type: Optional[models.DeviceType] = Query(None),
    location: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    if user_id is not None:
        devices = crud.DeviceCRUD.get_by_user_id(db, user_id)
    elif type is not None:
        devices = crud.DeviceCRUD.get_by_type(db, type)
    elif location is not None:
        devices = crud.DeviceCRUD.get_by_location(db, location)
    else:
        devices = crud.DeviceCRUD.get_all(db)
    return devices

@router.get("/{device_id}", response_model=schemas.Device)
async def get_device(device_id: int, db: Session = Depends(get_db)):
    device = crud.DeviceCRUD.get_by_id(db, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    return device

@router.post("/", response_model=schemas.Device, status_code=201)
async def create_device(device: schemas.DeviceCreate, db: Session = Depends(get_db)):
    return await services.DeviceService(None, "").create_device(db, device)  # Producer injected via dependency

@router.put("/{device_id}", response_model=schemas.Device)
async def update_device(
    device_id: int, 
    device: schemas.DeviceUpdate, 
    db: Session = Depends(get_db)
):
    updated_device = crud.DeviceCRUD.update(db, device_id, device)
    if not updated_device:
        raise HTTPException(status_code=404, detail="Device not found")
    return updated_device

@router.delete("/{device_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_device(device_id: int, db: Session = Depends(get_db)):
    if not crud.DeviceCRUD.delete(db, device_id):
        raise HTTPException(status_code=404, detail="Device not found")

@router.patch("/{device_id}/status", response_model=schemas.Device)
async def update_status(
    device_id: int, 
    status_update: schemas.DeviceStatusUpdate, 
    db: Session = Depends(get_db)
):
    device = crud.DeviceCRUD.update_status(db, device_id, status_update.status)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    return device

@router.post("/{device_id}/heartbeat")
async def heartbeat(
    device_id: int,
    heartbeat_data: schemas.HeartbeatRequest = None,
    db: Session = Depends(get_db)
):
    success = await services.DeviceService(None, "").heartbeat(db, device_id, heartbeat_data.ip_address)
    if not success:
        raise HTTPException(status_code=404, detail="Device not found")
    return {"message": "Heartbeat registered successfully"}

@router.get("/stats", response_model=schemas.DeviceStats)
async def get_stats(db: Session = Depends(get_db)):
    return crud.DeviceCRUD.get_stats(db)

@router.get("/types", response_model=List[models.DeviceType])
async def get_types():
    return list(models.DeviceType)

@router.get("/statuses", response_model=List[models.DeviceStatus])
async def get_statuses():
    return list(models.DeviceStatus)