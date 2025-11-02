#!/usr/bin/env python3
"""
Create admin user
"""
import asyncio
from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.models.user import User


async def create_admin(telegram_id: int, username: str, first_name: str):
    """Create admin user"""
    
    async with AsyncSessionLocal() as db:
        # Check if user exists
        result = await db.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            print(f"User {telegram_id} already exists!")
            return
        
        # Create admin user
        admin_user = User(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            is_active=True,
        )
        
        db.add(admin_user)
        await db.commit()
        
        print(f"? Admin user created: {first_name} (@{username}) - ID: {telegram_id}")
        print(f"\nAdd this ID to .env ADMIN_IDS: {telegram_id}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 4:
        print("Usage: python create_admin.py <telegram_id> <username> <first_name>")
        print("Example: python create_admin.py 123456789 admin_user AdminName")
        sys.exit(1)
    
    telegram_id = int(sys.argv[1])
    username = sys.argv[2]
    first_name = sys.argv[3]
    
    asyncio.run(create_admin(telegram_id, username, first_name))
