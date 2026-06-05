import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Expects DATABASE_URL from environment or fallback to local sqlite
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./travel_planner.db")

# For sqlite, we need connect_args={"check_same_thread": False}
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
