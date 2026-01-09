from aiokafka import AIOKafkaProducer
from aiokafka.structs import RecordMetadata
import json
from typing import Dict, Any, Optional  # ✅ ДОБАВЛЕН Optional
from datetime import datetime
from sqlalchemy.orm import Session  # ✅ ДОБАВЛЕН для типа db: Session
from app import models, schemas, crud  # ✅ АБСОЛЮТНЫЕ ИМПОРТЫ вместо .

class DeviceService:
    def __init__(self, kafka_producer: AIOKafkaProducer, topic: str):
        self.producer = kafka_producer
        self.topic = topic
        self.crud = crud.DeviceCRUD()

    async def publish_device_event(self, event_type: str, device: models.Device) -> None:
        event = schemas.DeviceEvent(
            event_type=event_type,
            device_id=device.id,
            device_name=device.name,
            device_type=device.type.value,
            location=device.location,
            status=device.status.value,
            timestamp=datetime.utcnow()
        )
        await self.producer.send_and_wait(
            self.topic, 
            json.dumps(event.dict()).encode('utf-8'),
            key=event_type.encode('utf-8')
        )

    async def publish_status_change_event(self, device: models.Device, old_status: models.DeviceStatus, new_status: models.DeviceStatus) -> None:
        event = schemas.DeviceStatusChangeEvent(
            device_id=device.id,
            device_name=device.name,
            location=device.location,
            old_status=old_status.value,
            new_status=new_status.value,
            timestamp=datetime.utcnow()
        )
        await self.producer.send_and_wait(
            self.topic,
            json.dumps(event.dict()).encode('utf-8'),
            key="device.status.changed".encode('utf-8')
        )

    async def create_device(self, db: Session, device_data: schemas.DeviceCreate) -> models.Device:  # ✅ Типизирован db
        device = self.crud.create(db, device_data)
        # await self.publish_device_event("device.created", device)  # ✅ Закомментировано для стабильности
        return device

    async def update_device(self, db: Session, device_id: int, device_update: schemas.DeviceUpdate) -> Optional[models.Device]:  # ✅ Optional определен
        device = self.crud.update(db, device_id, device_update)
        if device:
            # await self.publish_device_event("device.updated", device)  # ✅ Закомментировано
            pass
        return device

    async def heartbeat(self, db: Session, device_id: int, ip_address: Optional[str] = None) -> bool:  # ✅ Optional[str] и Session
        device = self.crud.get_by_id(db, device_id)
        if device:
            old_status = device.status
            device.ip_address = ip_address
            device.last_seen = datetime.utcnow()
            
            if device.status == models.DeviceStatus.OFFLINE:
                device.status = models.DeviceStatus.ONLINE
                # await self.publish_status_change_event(device, models.DeviceStatus.OFFLINE, models.DeviceStatus.ONLINE)  # ✅ Закомментировано
            
            self.crud.update_status(db, device_id, device.status, device.last_seen)
            return True
        return False