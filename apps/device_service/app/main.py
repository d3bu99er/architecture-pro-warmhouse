from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# ✅ Импорт database автоматически создает БД/таблицы!
from app.database import get_db
from app.api.health import router as health_router
from app.api.v1.devices import router as devices_router

app = FastAPI(
    title="Device Management Service API",
    description="Микросервис для управления устройствами умного дома",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router, prefix="/health")
app.include_router(devices_router, prefix="/api/v1")

@app.on_event("startup")
async def startup_event():
    print("🚀 Device Service started!")
    print("✅ Database auto-created by database.py import")

@app.get("/")
async def root():
    return {"message": "Device Service running ✅"}

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8082,
        reload=False
    )