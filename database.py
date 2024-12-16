import os
import psycopg2
from psycopg2 import sql
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

# Получение значений из .env
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")


def create_connection():
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )


def create_tables(conn):
    with conn.cursor() as cursor:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS emails (
                id SERIAL PRIMARY KEY,
                email TEXT UNIQUE NOT NULL
            );
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS phone_numbers (
                id SERIAL PRIMARY KEY,
                phone TEXT UNIQUE NOT NULL
            );
        ''')
        conn.commit()


def add_email(conn, email):
    with conn.cursor() as cursor:
        cursor.execute('INSERT INTO emails (email) VALUES (%s) ON CONFLICT DO NOTHING;', (email,))
        conn.commit()


def add_phone_number(conn, phone):
    with conn.cursor() as cursor:
        cursor.execute('INSERT INTO phone_numbers (phone) VALUES (%s) ON CONFLICT DO NOTHING;', (phone,))
        conn.commit()


def get_all_emails(conn):
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute('SELECT email FROM emails;')
        return [row["email"] for row in cursor.fetchall()]


def get_all_phone_numbers(conn):
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute('SELECT phone FROM phone_numbers;')
        return [row["phone"] for row in cursor.fetchall()]
