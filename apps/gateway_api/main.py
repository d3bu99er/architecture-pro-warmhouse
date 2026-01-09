"""
Smart Home API Gateway
АПИ шлюз для микросервисной архитектуры Smart Home Pro
Backend for Frontend (BFF) паттерн
"""

import os
import logging
import time
import signal
import sys
from typing import Dict, Any
from urllib.parse import urlparse, urlunparse
import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from contextlib import asynccontextmanager
from pydantic import BaseModel
import httpx

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='API Gateway - %(asctime)s | %(levelname)s | %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
class GatewayConfig:
    def __init__(self):
        self.smart_home_url = os.getenv("SMART_HOME_URL", "http://smarthome-app:8080")
        self.device_service_url = os.getenv("DEVICE_SERVICE_URL", "http://device-service:8082")
        self.telemetry_service_url = os.getenv("TELEMETRY_SERVICE_URL", "http://telemetry-service:8083")

config = GatewayConfig()

# HTTP Client
http_client = httpx.AsyncClient(timeout=30.0, limits=httpx.Limits(max_keepalive_connections=10))

# Pydantic models for responses
class GatewayStatus(BaseModel):
    status: str = "running"
    version: str = "1.0.0"
    services: Dict[str, str]
    timestamp: int

class ServiceInfo(BaseModel):
    name: str
    url: str
    description: str

# FastAPI app with graceful shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("API Gateway starting...")
    yield
    await http_client.aclose()
    logger.info("API Gateway stopped")

app = FastAPI(
    title="Smart Home API Gateway",
    version="1.0",
    description="АПИ шлюз для микросервисной архитектуры Smart Home Pro",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    logger.info(
        f"{request.client.host} - {request.method} {request.url.path} "
        f"{response.status_code} {process_time:.3f}s"
    )
    return response

# Health check
@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "service": "api-gateway",
        "timestamp": int(time.time())
    }

# Gateway status endpoints
@app.get("/gateway/status")
async def get_gateway_status():
    return GatewayStatus(
        services={
            "smart-home": config.smart_home_url,
            "device": config.device_service_url,
            "telemetry": config.telemetry_service_url,
        },
        timestamp=int(time.time())
    )

@app.get("/gateway/services")
async def get_services():
    services = [
        ServiceInfo(name="smart-home-app", url=config.smart_home_url, description="Монолитное приложение Smart Home"),
        ServiceInfo(name="device-service", url=config.device_service_url, description="Микросервис управления устройствами"),
        ServiceInfo(name="telemetry-service", url=config.telemetry_service_url, description="Микросервис сбора телеметрии"),
    ]
    return services

# ✅ ИСПРАВЛЕННАЯ Proxy function
async def proxy_request(request: Request, target_base_url: str):
    """Проверенный рабочий прокси"""
    try:
        # Формируем URL
        path = request.scope["path"]
        query = request.url.query or ""
        url = f"{target_base_url.rstrip('/')}{path}"
        if query:
            url += f"?{query}"
            
        logger.info(f"Proxying {request.method} {path} -> {url}")
        
        # КОПИРУЕМ headers БЕЗ host
        headers = {k: v for k, v in dict(request.headers).items() if k.lower() != 'host'}
        
        # GET без body, остальные с body
        if request.method == 'GET':
            resp = await http_client.get(url, headers=headers)
        else:
            # Правильно получаем body ОДИН РАЗ
            body = await request.body()
            resp = await http_client.request(
                method=request.method, 
                url=url, 
                headers=headers, 
                content=body
            )
        
        logger.info(f"Backend response: {resp.status_code}")
        
        return Response(
            content=resp.content,
            status_code=resp.status_code,
            headers=dict(resp.headers)
        )
    except httpx.ConnectError as e:
        logger.error(f"Connection failed: {e}")
        raise HTTPException(502, "Backend connection failed")
    except Exception as e:
        logger.error(f"Proxy error: {type(e).__name__}: {e}")
        raise HTTPException(502, "Backend unavailable")

# Роуты прокси
@app.api_route("/api/v1/sensors/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def proxy_sensors(request: Request, path: str):
    return await proxy_request(request, config.smart_home_url)

@app.api_route("/api/v1/devices/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def proxy_devices(request: Request, path: str):
    return await proxy_request(request, config.smart_home_url)

@app.api_route("/api/v1/telemetry/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def proxy_telemetry(request: Request, path: str):
    return await proxy_request(request, config.telemetry_service_url)

# Catch-all -> Smart Home App
@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def catch_all(request: Request, path: str):
    return await proxy_request(request, config.smart_home_url)

# Graceful shutdown
def signal_handler(sig, frame):
    logger.info("Shutdown signal received")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    logger.info(f"API Gateway starting on port {port}")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=False
    )