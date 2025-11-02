#!/usr/bin/env python3
"""
Initialize database with default data
"""
import asyncio
from datetime import date, datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal, engine, Base
from app.models.pricing import DailyPrice
from app.models.settings import AppSettings


async def init_database():
    """Initialize database with tables and default data"""
    
    print("Creating database tables...")
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    print("Tables created successfully!")
    
    # Add default data
    async with AsyncSessionLocal() as db:
        # Check if default price exists
        from sqlalchemy import select
        
        result = await db.execute(
            select(DailyPrice).where(DailyPrice.date == date.today())
        )
        existing_price = result.scalar_one_or_none()
        
        if not existing_price:
            # Create default price
            default_price = DailyPrice(
                date=date.today(),
                price_per_gb=1.50,
                price_per_mb=0.0015,
                message="Default pricing initialized",
            )
            db.add(default_price)
            print("Created default price: $1.50/GB")
        
        # Check if app settings exist
        result = await db.execute(
            select(AppSettings).where(AppSettings.key == "app_version")
        )
        existing_setting = result.scalar_one_or_none()
        
        if not existing_setting:
            # Create default settings
            settings = [
                AppSettings(key="app_version", value="1.0.0", description="Application version"),
                AppSettings(key="maintenance_mode", value="false", description="Maintenance mode flag"),
                AppSettings(key="min_withdraw_usd", value="1.39", description="Minimum withdrawal amount"),
                AppSettings(key="max_withdraw_usd", value="100.00", description="Maximum withdrawal amount"),
            ]
            
            for setting in settings:
                db.add(setting)
            
            print("Created default app settings")
        
        await db.commit()
        print("Default data initialized!")
    
    print("\n? Database initialization completed!")


if __name__ == "__main__":
    asyncio.run(init_database())
