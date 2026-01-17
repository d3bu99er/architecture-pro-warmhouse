from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from app.config import settings
import logging
import os
Base = declarative_base()
log = logging.getLogger(__name__)

MASTER_URL = f"postgresql://{settings.database_user}:{settings.database_password}@{settings.database_host}:{settings.database_port}/postgres"
SQLALCHEMY_DATABASE_URL = f"postgresql://{settings.database_user}:{settings.database_password}@{settings.database_host}:{settings.database_port}/{settings.database_name}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

def ensure_database_exists():
    """Создать БД"""
    master_engine = create_engine(MASTER_URL, isolation_level="AUTOCOMMIT")
    with master_engine.connect() as conn:
        result = conn.execute(text(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{settings.database_name}'"))
        if not result.fetchone():
            conn.execute(text(f'CREATE DATABASE "{settings.database_name}"'))
            log.info(f"✅ Database CREATED")
        else:
            log.info(f"✅ Database exists")
    master_engine.dispose()

def ensure_tables_exist():
    """✅ 1. СОЗДАТЬ СТРУКТУРУ ТАБЛИЦ"""
    from .models import Device
    Base.metadata.create_all(bind=engine)
    log.info("✅ Tables structure created")

def load_init_data():
    """✅ 2. ЗАГРУЗИТЬ ДАННЫЕ (ПОСЛЕ таблиц!)"""
    init_sql_path = "/app/init.sql"
    
    if not os.path.exists(init_sql_path):
        log.warning("⚠️ init.sql not found")
        return
    
    # ✅ Проверяем devices после создания таблицы
    try:
        with engine.connect() as conn:
            device_count = conn.execute(text("SELECT COUNT(*) FROM devices")).scalar() or 0
            
            if device_count == 0:
                # Выполняем init.sql
                with open(init_sql_path, 'r') as f:
                    sql_content = f.read()
                conn.execute(text(sql_content))
                conn.commit()
                log.info("✅ Loaded init.sql data")
            else:
                log.info(f"✅ {device_count} devices exist - skipped init.sql")
    except Exception as e:
        log.error(f"❌ init.sql error: {e}")

# ✅ АВТОЗАПУСК (строгий порядок!)
ensure_database_exists()      # 1. БД
ensure_tables_exist()         # 2. Таблицы
load_init_data()              # 3. Данные

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()