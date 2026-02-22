# app/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database URL
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    DATABASE_URL = "postgresql://postgres:1234@localhost:5432/fastapi_db"
    print("⚠️ Using hardcoded database URL")

# Create engine
engine = create_engine(DATABASE_URL)

# Create session factory(basically session generator h baad m just session local)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)#blue print keh skte ho 

# Create Base class - THIS IS WHAT MODELS.PY NEEDS
Base = declarative_base()# Later, any class that uses this Base becomes a database table.

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()