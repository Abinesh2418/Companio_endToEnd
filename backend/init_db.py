"""
Database initialization script
Run this to create all tables in the PostgreSQL database
"""

from dotenv import load_dotenv
load_dotenv()

import psycopg2
from database import engine, DATABASE_URL, POSTGRES_HOST, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB, POSTGRES_PORT, Base
from features.auth.models import UserDB
from features.goals.models import GoalDB
from features.tasks.models import TaskDB
from features.productivity.models import UserProductivityProfileDB, ActivityLogDB, ReminderDB

def mask_db_url(url: str) -> str:
    return url.replace(url.split(":")[2].split("@")[0], "***")

def main():
    print("🚀 Initializing database...")
    print(f"📊 Database URL from .env: {mask_db_url(DATABASE_URL)}")
    print(f"📊 Engine URL: {engine.url}")

    # 1️⃣ Test raw PostgreSQL connection
    print("\n🔍 Testing direct PostgreSQL connection...")
    try:
        conn = psycopg2.connect(
            host=POSTGRES_HOST,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            dbname=POSTGRES_DB,
            port=int(POSTGRES_PORT)
        )
        conn.close()
        print("✅ Direct PostgreSQL connection successful")
    except Exception as e:
        print(f"❌ PostgreSQL connection failed: {e}")
        return

    # 2️⃣ Create tables
    try:
        Base.metadata.create_all(bind=engine)
        print("\n✅ Database initialized successfully!")
        print("📋 Tables created:")
        print("   - users (authentication)")
        print("   - goals")
        print("   - tasks")
        print("   - user_productivity_profiles")
        print("   - activity_logs")
        print("   - reminders")
        print("\n🎉 You can now start the FastAPI server!")
    except Exception as e:
        print(f"❌ Error creating tables: {e}")

if __name__ == "__main__":
    main()
