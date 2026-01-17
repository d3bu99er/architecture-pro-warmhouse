from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from datetime import datetime  # ✅ ДОБАВЛЕН НЕОБХОДИМЫЙ ИМПОРТ
from app import models, schemas  # ✅ АБСОЛЮТНЫЕ ИМПОРТЫ вместо относительных

class DeviceCRUD:
    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[models.Device]:
        return db.query(models.Device).offset(skip).limit(limit).all()

    @staticmethod
    def get_by_id(db: Session, device_id: int) -> Optional[models.Device]:
        return db.query(models.Device).filter(models.Device.id == device_id).first()

    @staticmethod
    def get_by_user_id(db: Session, user_id: int) -> List[models.Device]:
        return db.query(models.Device).filter(models.Device.user_id == user_id).all()

    @staticmethod
    def get_by_type(db: Session, device_type: models.DeviceType) -> List[models.Device]:
        return db.query(models.Device).filter(models.Device.type == device_type).all()

    @staticmethod
    def get_by_location(db: Session, location: str) -> List[models.Device]:
        return db.query(models.Device).filter(
            models.Device.location.ilike(f"%{location}%")
        ).all()

    @staticmethod
    def get_by_mac_address(db: Session, mac_address: str) -> Optional[models.Device]:
        return db.query(models.Device).filter(models.Device.mac_address == mac_address).first()

    @staticmethod
    def create(db: Session, device: schemas.DeviceCreate) -> models.Device:
        db_device = models.Device(**device.dict())
        db.add(db_device)
        db.commit()
        db.refresh(db_device)
        return db_device

    @staticmethod
    def update(db: Session, device_id: int, device_update: schemas.DeviceUpdate) -> Optional[models.Device]:
        db_device = db.query(models.Device).filter(models.Device.id == device_id).first()
        if db_device:
            update_data = device_update.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_device, field, value)
            db.commit()
            db.refresh(db_device)
        return db_device

    @staticmethod
    def update_status(db: Session, device_id: int, status: models.DeviceStatus, last_seen: Optional[datetime] = None) -> Optional[models.Device]:
        # ✅ Теперь datetime определен!
        db_device = db.query(models.Device).filter(models.Device.id == device_id).first()
        if db_device:
            db_device.status = status
            if last_seen:
                db_device.last_seen = last_seen
            db_device.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(db_device)
        return db_device

    @staticmethod
    def delete(db: Session, device_id: int) -> bool:
        db_device = db.query(models.Device).filter(models.Device.id == device_id).first()
        if db_device:
            db.delete(db_device)
            db.commit()
            return True
        return False

    @staticmethod
    def get_stats(db: Session) -> schemas.DeviceStats:
        total = db.query(models.Device).count()
        online = db.query(models.Device).filter(models.Device.status == models.DeviceStatus.ONLINE).count()
        offline = db.query(models.Device).filter(models.Device.status == models.DeviceStatus.OFFLINE).count()
        error = db.query(models.Device).filter(models.Device.status == models.DeviceStatus.ERROR).count()
        return schemas.DeviceStats(
            total_devices=total,
            online_devices=online,
            offline_devices=offline,
            error_devices=error
        )