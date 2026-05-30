#!/usr/bin/env python3
"""
Database initialization script for Render deployment.
Run this after the first deployment to create database tables.
"""

from app.core.config import get_settings
from app.db.database import Base, engine

def init_database():
    settings = get_settings()
    print(f"Initializing database: {settings.database_url}")
    print(f"App name: {settings.app_name}")

    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

if __name__ == "__main__":
    init_database()