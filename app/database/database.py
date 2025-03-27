# app/database/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv

# Import custom serializers
from app.utils.time_utils import json_serializer, json_deserializer

# Load environment variables
load_dotenv()

# Get database URL from environment variable
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./sql_app.db")

# Create database engine based on URL
if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, 
        connect_args={"check_same_thread": False},
        json_serializer=json_serializer,
        json_deserializer=json_deserializer
    )
else:
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        json_serializer=json_serializer,
        json_deserializer=json_deserializer
    )

# Create SessionLocal without timezone parameter
SessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=engine
)

Base = declarative_base()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()