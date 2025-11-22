from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from src.shopcart_service.core.config import get_settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()

logger.info("🔧 DATABASE CONFIGURATION:")
logger.info(f"DB_HOST: {settings.DB_HOST}")
logger.info(f"DB_USER: {settings.DB_USER}")
logger.info(f"DB_NAME: {settings.DB_NAME}")
logger.info(f"DATABASE_URL: {settings.DATABASE_URL}")

# Entrypoint artıq database hazır olduğunu yoxlayıb
try:
    engine = create_engine(settings.DATABASE_URL, future=True)
    logger.info("✅ Database engine created successfully!")
except Exception as e:
    logger.error(f"❌ Failed to create database engine: {e}")
    raise

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()