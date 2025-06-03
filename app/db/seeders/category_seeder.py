from sqlalchemy.orm import Session
from app.models.common.category import Category
from app.models.auth.user import User
import csv
import os

async def seed_categories(db: Session):
    print("Seeding categories...")
    
    admin_user = db.query(User).filter(User.username == "admin").first()
    if not admin_user:
        raise Exception("Admin user not found! Please run user seeder first.")

    # Read categories from CSV file
    csv_file = os.path.join(os.path.dirname(__file__), 'csv', 'categories.csv')
    
    with open(csv_file, 'r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            # Check if category already exists
            existing_category = db.query(Category).filter(Category.name == row["name"]).first()
            
            if not existing_category:
                category = Category(
                    name=row["name"],
                    description=row["description"],
                    status=row["status"].lower() == "true",
                    created_by=admin_user.id,
                    image_url=row["image_url"]
                )
                db.add(category)
    
    db.commit()
    print("Categories seeded successfully!")
