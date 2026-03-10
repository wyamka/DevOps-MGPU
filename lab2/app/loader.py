#!/usr/bin/env python3
"""
Вариант 25. Савкина Мария
ETL loader:
1. Читает diabetes_new.csv
2. Анонимизирует FirstName и LastName
3. Загружает данные в PostgreSQL
Использует Docker Secret для ключа анонимизации (для индивидуального задания).
"""

import csv
import hashlib
import os
import sys
import time

import psycopg2


# Настройки конфигурации
DB_HOST = os.getenv("DB_HOST", "db")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB", "diabetes")
DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "postgres")

CSV_PATH = os.getenv("CSV_PATH", "/data/diabetes_new.csv")

# путь к секрету Docker
SECRET_PATH = "/run/secrets/encryption_key"


DDL = """
CREATE TABLE IF NOT EXISTS diabetes_data (
    id SERIAL PRIMARY KEY,
    pregnancies INT,
    glucose INT,
    blood_pressure INT,
    skin_thickness INT,
    insulin INT,
    bmi REAL,
    diabetes_pedigree_function REAL,
    age INT,
    outcome INT,
    first_name_hash TEXT,
    last_name_hash TEXT
);
"""


def wait_for_db(max_retries=30, delay=2):
    """Ожидание готовности PostgreSQL."""
    for attempt in range(1, max_retries + 1):
        try:
            conn = psycopg2.connect(
                host=DB_HOST,
                port=DB_PORT,
                dbname=DB_NAME,
                user=DB_USER,
                password=DB_PASS,
            )
            print(f"[loader] PostgreSQL доступен (попытка {attempt})")
            return conn
        except psycopg2.OperationalError:
            print(f"[loader] Ожидание PostgreSQL... {attempt}/{max_retries}")
            time.sleep(delay)

    print("[loader] Не удалось подключиться к БД")
    sys.exit(1)


def load_secret():
    """Чтение ключа анонимизации из Docker Secret."""
    try:
        with open(SECRET_PATH, encoding="utf-8") as f:
            key = f.read().strip()
            print("[loader] Ключ анонимизации загружен")
            return key
    except FileNotFoundError:
        print("[loader] Secret encryption_key не найден")
        sys.exit(1)


def anonymize(value, key):
    """Хеширование персональных данных."""
    data = f"{value}:{key}".encode()
    return hashlib.sha256(data).hexdigest()


def load_csv(conn, key):
    """Загрузка CSV с анонимизацией."""
    cur = conn.cursor()

    cur.execute(DDL)
    conn.commit()

    cur.execute("SELECT COUNT(*) FROM diabetes_data;")
    if cur.fetchone()[0] > 0:
        print("[loader] Таблица уже содержит данные — пропуск загрузки.")
        return

    count = 0

    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            first_hash = anonymize(row["FirstName"], key)
            last_hash = anonymize(row["LastName"], key)

            cur.execute(
                """
                INSERT INTO diabetes_data(
                    pregnancies,
                    glucose,
                    blood_pressure,
                    skin_thickness,
                    insulin,
                    bmi,
                    diabetes_pedigree_function,
                    age,
                    outcome,
                    first_name_hash,
                    last_name_hash
                )
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """,
                (
                    int(row["Pregnancies"]),
                    int(row["Glucose"]),
                    int(row["BloodPressure"]),
                    int(row["SkinThickness"]),
                    int(row["Insulin"]),
                    float(row["BMI"]),
                    float(row["DiabetesPedigreeFunction"]),
                    int(row["Age"]),
                    int(row["Outcome"]),
                    first_hash,
                    last_hash,
                ),
            )

            count += 1

    conn.commit()
    cur.close()

    print(f"[loader] Загружено {count} строк")


def main() -> None:
    conn = wait_for_db()
    key = load_secret()

    try:
        load_csv(conn, key)
    finally:
        conn.close()

    print("[loader] Готово")


if __name__ == "__main__":
    main()
