#database.py
from sqlmodel import SQLModel, create_engine, Session
from .config import get_settings  # ✅ get_settings istifadə edək

settings = get_settings()

# Database Engine
engine = create_engine(settings.DATABASE_URL, echo=True)

def create_db_and_tables():
    """Create all database tables"""
    SQLModel.metadata.create_all(engine)

def get_session():
    """Dependency for FastAPI"""
    with Session(engine) as session:
        yield session