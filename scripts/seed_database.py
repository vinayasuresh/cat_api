
import asyncio
import sys
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add the project root directory to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from app.db.session import SessionLocal
from app.db.seeders import run_all_seeders

async def main():
    db = SessionLocal()
    try:
        await run_all_seeders(db)
        logger.info("Seeding completed successfully.")
    finally:
        db.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logger.error(f"Seeding failed: {e}")
        sys.exit(1)
