import psycopg2, os, random, time

print("Waiting for DB to be fully ready...")
time.sleep(5)

conn = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT", "5432"),
    dbname=os.getenv("POSTGRES_DB"),
    user=os.getenv("POSTGRES_USER"),
    password=os.getenv("POSTGRES_PASSWORD"),
)
cur = conn.cursor()
cur.execute(
    "CREATE TABLE IF NOT EXISTS diabetes_risk (id SERIAL PRIMARY KEY, age INT, bmi FLOAT, glucose FLOAT, blood_pressure FLOAT, insulin FLOAT, risk_score FLOAT, risk_level TEXT);"
)


# Определяем специальные функции для сохранения бизнес-логики
def calculate_risk(age, bmi, glucose, bp):
    score = 0
    if age > 45:
        score += 0.2
    if bmi > 30:
        score += 0.3
    if glucose > 140:
        score += 0.4
    if bp > 140:
        score += 0.1

    return min(score, 1.0)


def risk_label(score):
    if score < 0.3:
        return "low"
    elif score < 0.6:
        return "medium"
    return "high"

# Генерируем данные с учетом особенностей медицинских показателей
for _ in range(1000):
    age = random.randint(18, 80)
    # BMI (с возрастом увеличивается)
    bmi = round(random.gauss(27 + (age > 50) * 2, 4), 2)
    # Глюкоза зависит от BMI и возраста
    glucose_base = 90 + (bmi - 25) * 2 + (age - 40) * 0.5
    glucose = round(random.gauss(glucose_base, 15), 2)
    # Давление зависит от возраста
    blood_pressure = round(random.gauss(110 + (age - 40) * 0.5, 10), 2)
    # Инсулин (связан с глюкозой)
    insulin = round(random.gauss(80 + (glucose - 100) * 0.7, 30), 2)

    risk = calculate_risk(age, bmi, glucose, blood_pressure)
    label = risk_label(risk)

    cur.execute(
        """
        INSERT INTO diabetes_risk 
        (age, bmi, glucose, blood_pressure, insulin, risk_score, risk_level)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """,
        (age, bmi, glucose, blood_pressure, insulin, risk, label),
    )

conn.commit()
print("Diabetes risk data loaded successfully!")
cur.close()
conn.close()
