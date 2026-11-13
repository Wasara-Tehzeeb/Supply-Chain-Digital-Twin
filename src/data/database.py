import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

# Locate and load the project's .env file
BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env")

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL not found in .env file")

# Create the PostgreSQL connection
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# Test the connection
if __name__ == "__main__":
    try:
        with engine.connect() as connection:
            result = connection.execute(
                text("SELECT current_database(), current_user;")
            )
            database, user = result.fetchone()

            print("PostgreSQL connection successful!")
            print(f"Database: {database}")
            print(f"User: {user}")

    except Exception as error:
        print(f"Database connection failed: {error}")