import psycopg
import os

def get_connection():
    conn = psycopg.connect(os.getenv("DATABASE_URL"))
    conn.execute("SET client_encoding TO 'UTF8'")
    return conn