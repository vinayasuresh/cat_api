import asyncio
import sys
import os
from sqlalchemy.exc import IntegrityError

# Add the project root directory to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from app.db.session import SessionLocal
from app.db.models import User  # Adjust this import to your User model location
from app.core.security import get_password_hash  # Adjust to your password hashing function

async def seed_users(db):
    print("Seeding users...")
    try:
        # Check if admin user exists
        admin = db.query(User).filter(User.email == "admin@example.com").first()
        if admin:
            print("Admin user already exists, skipping.")
        else:
            admin_user = User(
                email="admin@example.com",
                username="admin",
                hashed_password=get_password_hash("your_password_here"),
                is_active=True,
                is_superuser=True
            )
            db.add(admin_user)
            db.commit()
            print("Admin user seeded successfully.")
    except IntegrityError as e:
        print(f"IntegrityError during user seeding: {e}")
        db.rollback()
    except Exception as e:
        print(f"Unexpected error during user seeding: {e}")
        db.rollback()

async def main():
    db = SessionLocal()
    try:
        await seed_users(db)
        # Add more seed functions here, e.g. seed_states(db), etc.
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(main())
