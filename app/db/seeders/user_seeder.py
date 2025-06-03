from sqlalchemy.orm import Session
from app.models.auth.user import User
from app.core.auth.security import get_password_hash

async def seed_users(db: Session):
    print("Seeding users...")
    
    default_users = [
        {
            "email": "admin@example.com",
            "username": "admin",
            "password": "admin123",  # In production, use secure passwords
            "is_superuser": True
        },
        {
            "email": "user@example.com",
            "username": "user",
            "password": "user123",
            "is_superuser": False
        }
    ]
    
    for user_data in default_users:
        # Check if user already exists
        existing_user = db.query(User).filter(
            (User.email == user_data["email"]) | 
            (User.username == user_data["username"])
        ).first()
        
        if not existing_user:
            user = User(
                email=user_data["email"],
                username=user_data["username"],
                hashed_password=get_password_hash(user_data["password"]),
                is_superuser=user_data["is_superuser"]
            )
            db.add(user)
    
    db.commit()
    print("Users seeded successfully!")
