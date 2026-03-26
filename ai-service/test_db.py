import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

try:
    conn = psycopg2.connect(DATABASE_URL)
    print("Connected to the database")
    conn.close()
except Exception as e:
    print(f"Error connecting to the database: {e}")