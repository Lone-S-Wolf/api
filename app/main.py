from fastapi import FastAPI
from app.routers import items, auth
from app.models import models
from app.database.database import engine
import sqlalchemy.exc
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(
    title="FastAPI CRUD with Auth",
    description="A simple FastAPI CRUD application with PostgreSQL and authentication",
    version="0.2.0",
    debug=os.getenv("DEBUG", "False").lower() == "true"
)

# Try to create tables, but handle potential database connection errors
try:
    models.Base.metadata.create_all(bind=engine)
    print("Database tables created successfully")
except sqlalchemy.exc.OperationalError:
    print("Could not connect to the database. Please check your connection settings.")
    print("The application will continue to run, but database operations may fail.")

# Include routers
app.include_router(auth.router)
app.include_router(items.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to FastAPI CRUD API with Authentication"} 