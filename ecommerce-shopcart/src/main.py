from fastapi import FastAPI
from src.shopcart_service.core.db import Base, engine
from src.shopcart_service.api.v1 import routes as routes_v1
from src.shopcart_service.core.config import get_settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()

try:
    Base.metadata.create_all(bind=engine)
    logger.info("✅ Database tables created successfully!")
except Exception as e:
    logger.error(f"❌ Failed to create database tables: {e}")
    raise

app = FastAPI(
    title="Shopcart Service",
    debug=settings.DEBUG
)

app.include_router(routes_v1.router, prefix="", tags=["Cart v1"])

@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "service": "shopcart", 
        "port": settings.PORT,
        "environment": settings.ENV
    }

@app.get("/")
async def root():
    return {"message": "ShopCart Service is running", "port": settings.PORT}