# Вариант 25. Савкина Мария

# 1. Базовый образ с фиксированной версией
FROM python:3.10-slim

# 2. Метаданные образа
LABEL maintainer="student" \
      description="Diabetes risk analytics: anonymization ETL loader + Streamlit dashboard"

# 3. Установка системных зависимостей + очистка кэша
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

# 4. Создание непривилегированного пользователя (UID 1000)
RUN groupadd -r appuser && useradd -r -g appuser -u 1000 -m appuser

# 5. Рабочая директория
WORKDIR /app

# 6. Установка зависимостей (используем кэш Docker)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 7. Копирование исходного кода приложения
COPY loader.py dashboard.py ./

# 8. Переключение на непривилегированного пользователя
USER appuser

# 9. Порт приложения Streamlit
EXPOSE 8501

# 10. Точка входа по умолчанию — аналитический дашборд
CMD ["streamlit", "run", "dashboard.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \
     "--server.headless=true"]