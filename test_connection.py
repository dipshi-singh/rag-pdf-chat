# test_connection.py

import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()  # loads DATABASE_URL from .env

DATABASE_URL = os.getenv("DATABASE_URL")
print("Using DATABASE_URL:", DATABASE_URL)

# Create engine
engine = create_engine(DATABASE_URL)

try:
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 'Connection successful!'"))
        print(result.fetchone()[0])
        result = conn.execute(text("SELECT version();"))
        print("Postgres version:", result.fetchone()[0])
except Exception as e:
    print("❌ Connection failed!")
    print(e)
