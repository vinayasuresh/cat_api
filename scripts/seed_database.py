import sys
import os
import asyncio

# Add project root to PYTHONPATH
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from app.db.session import SessionLocal
from app.db.seeders import run_all_seeders

async def main():
    db = SessionLocal()
    try:
        await run_all_seeders(db)
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(main())
