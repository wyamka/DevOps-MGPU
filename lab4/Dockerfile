FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
# По умолчанию запускаем тесты при старте контейнера
CMD ["uvicorn", "diabetes_etl:app", "--host", "0.0.0.0", "--port", "8000"]