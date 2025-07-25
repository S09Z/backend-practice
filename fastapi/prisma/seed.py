import asyncio
from prisma import Prisma
from app.core.security import get_password_hash

async def main():
    db = Prisma()
    await db.connect()
    
    # Create admin user
    admin_user = await db.user.create(
        data={
            "email": "admin@example.com",
            "name": "Admin User",
            "password": get_password_hash("admin123"),
            "is_active": True
        }
    )
    
    # Create sample items
    await db.item.create(
        data={
            "title": "Sample Item 1",
            "description": "This is a sample item",
            "price": 29.99,
            "owner_id": admin_user.id
        }
    )
    
    await db.item.create(
        data={
            "title": "Sample Item 2", 
            "description": "Another sample item",
            "price": 49.99,
            "owner_id": admin_user.id
        }
    )
    
    print("✅ Database seeded successfully!")
    await db.disconnect()

if __name__ == "__main__":
    asyncio.run(main())