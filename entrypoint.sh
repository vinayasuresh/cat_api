#!/bin/sh

# Run Alembic migrations
echo "🚀 Running Alembic migrations..."
alembic upgrade head

# Seed the database
echo "🌱 Seeding the database..."
python scripts/seed_database.py

# Start the app (adjust if your app has a different start command)
echo "▶️ Starting app..."
uvicorn app.main:app --host 0.0.0.0 --port 4389
