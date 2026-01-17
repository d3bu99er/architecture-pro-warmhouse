import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database
    database_host: str = os.getenv("DATABASE_HOST", "localhost")
    database_port: int = int(os.getenv("DATABASE_PORT", "5432"))
    database_name: str = os.getenv("DATABASE_NAME", "smarthome_devices")
    database_user: str = os.getenv("DATABASE_USER", "postgres")
    database_password: str = os.getenv("DATABASE_PASSWORD", "postgres")
    
    # Kafka
    kafka_bootstrap_servers: str = os.getenv("KAFKA_BROKERS", "kafka:9092")
    kafka_topic: str = "device.events"
    
    # Server
    server_port: int = 8082

    model_config = {  # ✅ ПРЯМЫЙ ДИКТ, НЕ Field()
        "env_file": ".env",
        "env_ignore_empty": True
    }

settings = Settings()