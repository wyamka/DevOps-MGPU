# Лабораторная работа 2. Упаковка многокомпонентного аналитического приложения с помощью Docker и Docker Compose.

## Выполнила Савкина Мария, группа БД-251м

## Вариант 25

*Бизнес-задача:* Диабет (Риски)	

*Проектная задача:* loader: Скрипт анонимизации данных перед загрузкой.	

*Техническое задание:* Использовать секреты (Docker Secrets или эмуляцию через файлы), чтобы передать ключи шифрования, а не через ENV.

## 1. Архитектура решения.
```mermaid
---
config:
  layout: elk
---
flowchart LR

    subgraph HOST["Хост-машина (Ubuntu 22.04)"]
        RAW["data/patient_diabetes.csv"]
        SECRETFILE["secrets/encryption_key.txt"]
    end

    subgraph COMPOSE["docker compose"]
        
        subgraph NET["Docker network"]
            LOADER["loader (ETL-скрипт)"]
            DB[(PostgreSQL 16)]
            DASH["dashboard (Streamlit)"]
        end

        SECRET["Docker Secret"]
 
    end

    RAW -- "bind mount (read-only)" --> LOADER
    SECRETFILE --> SECRET
    SECRET -- "encryption key" --> LOADER

    LOADER -- "INSERT INTO diabetes" --> DB
    DASH -- "SELECT * FROM diabetes" --> DB



    style DB fill:#336791,color:#fff
    style LOADER fill:#3a7d44,color:#fff
    style DASH fill:#ff4b4b,color:#fff
    style SECRET fill:#808080,color:#fff
```



## 4. Описание компонентов

### 4.1. Датасет diabetes_new.csv

Дата-сет получен из открытого набора данных с Kaggle: https://www.kaggle.com/datasets/mathchi/diabetes-data-set путём добавления полей FirstName и SecondName для дальнейшей анонимизации данных в рамках проектной задачи Варианта 25.

Поля набора данных:
| Поле                        | Тип       | Описание                                                                                   |
|------------------------------|----------|-------------------------------------------------------------------------------------------|
| Pregnancies                  | INT      | Количество беременностей                                                                   |
| Glucose                      | INT      | Концентрация глюкозы в плазме через 2 часа после перорального теста на толерантность       |
| BloodPressure                | INT      | Диастолическое артериальное давление (мм рт. ст.)                                         |
| SkinThickness                | INT      | Толщина кожной складки на трицепсе (мм)                                                  |
| Insulin                      | INT      | Уровень инсулина в сыворотке крови через 2 часа (мМЕ/мл)                                  |
| BMI                          | FLOAT    | Индекс массы тела (вес в кг / (рост в м)²)                                                 |
| DiabetesPedigreeFunction     | FLOAT    | Функция родословной для выявления риска диабета                                           |
| Age                          | INT      | Возраст пациента (лет)                                                                    |
| Outcome                      | INT      | Переменная класса (0 — нет диабета, 1 — диабет)                                          |
| FirstName                    | STRING   | Имя пациента                                                                             |
| LastName                     | STRING   | Фамилия пациента                                                                         |
