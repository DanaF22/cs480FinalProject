import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    return psycopg2.connect(
        host="localhost",
        database="cs480",
        user="postgres",
        password=os.getenv("DB_PASSWORD")
    )