# app/main.py
from fastapi import FastAPI
from app.database import create_db_and_tables
from app.api.v1.endpoints.wishlist import router


app = FastAPI(title="Wishlist Service", version="0.1.0")

# ✅ DATABASE YARAT
@app.on_event("startup")
def on_startup():
    create_db_and_tables()

# ✅ WISHLIST ROUTER İMPORT ET
try:
    from app.api.v1.endpoints.wishlist import router as wishlist_router
    print("✅ Wishlist router uğurla import olundu")
    app.include_router(wishlist_router, prefix="/api/wishlist")
except ImportError as e:
    print(f"❌ Router import xətası: {e}")
    
    # Fallback endpointlər
    @app.get("/api/wishlist/")
    def get_wishlist_fallback():
        return {"message": "Fallback GET endpoint işləyir"}
    
    @app.post("/api/wishlist/")
    def post_wishlist_fallback():
        return {"message": "Fallback POST endpoint işləyir"}

# Health & Root
@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "wishlist"}

@app.get("/")
def root():
    return {"message": "Wishlist Service is running"}