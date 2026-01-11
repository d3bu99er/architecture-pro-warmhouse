from fastapi import FastAPI, HTTPException, Query, Path
from pydantic import BaseModel
from typing import Optional
import random
import uvicorn
from datetime import datetime, timezone
from fastapi.middleware.cors import CORSMiddleware
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Temperature API",
    description="Микросервис для получения данных o температуре c датчиков умного дома",
    version="1.0"
)

# Добавляем CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TemperatureData(BaseModel):
    value: float
    unit: str
    timestamp: datetime
    location: str
    status: str
    sensor_id: str
    sensor_type: str
    description: str

@app.get("/health", summary="Проверка состояния сервиса", tags=["Health"])
async def health_check() -> dict:
    """
    Endpoint для проверки работоспособности сервиса
    """
    return {"status": "ok"}

@app.get("/temperature", response_model=TemperatureData, summary="Получить температуру по названию комнаты", tags=["Temperature"])
async def get_temperature_by_location(location: str = Query(..., description="Название комнаты", regex="^(Kitchen|Bedroom|Living Room)$")):
    """
    Возвращает случайное значение температуры для указанной комнаты.
    Используйте: /temperature?location={room}
    """
    if not location:
        raise HTTPException(status_code=400, detail="Location is required")
    
    data = generate_temperature_data(location, "")
    return data

@app.get("/temperature/{id}", response_model=TemperatureData, summary="Получить температуру по ID датчика", tags=["Temperature"])
async def get_temperature_by_sensor_id(id: str = Path(..., description="ID датчика", regex="^(1|2|3)$")):
    """
    Возвращает случайное значение температуры для указанного датчика
    """
    if not id:
        raise HTTPException(status_code=400, detail="Sensor ID is required")
    
    data = generate_temperature_data("", id)
    return data

def generate_temperature_data(location: str, sensor_id: str) -> TemperatureData:
    """
    Генерирует случайные данные о температуре на основе локации или ID датчика
    """
    # Генерируем случайную температуру между 10 и 30 градусами Цельсия
    value = 10.0 + random.uniform(0, 20)
    
    # Если локация не указана, определяем по ID датчика
    if not location:
        location_map = {
            "1": "Living Room",
            "2": "Bedroom", 
            "3": "Kitchen"
        }
        location = location_map.get(sensor_id, "Unknown")
    
    # Если ID датчика не указан, определяем по локации
    if not sensor_id:
        sensor_map = {
            "Living Room": "1",
            "Bedroom": "2",
            "Kitchen": "3"
        }
        sensor_id = sensor_map.get(location, "0")
    
    return TemperatureData(
        value=value,
        unit="°C",
        timestamp=datetime.now(timezone.utc).isoformat(),
        location=location,
        status="active",
        sensor_id=sensor_id,
        sensor_type="temperature",
        description=f"Temperature sensor in {location}"
    )

if __name__ == "__main__":
    logger.info("Temperature API starting on :8081")
    uvicorn.run(app, host="0.0.0.0", port=8081)