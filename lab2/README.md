# Лабораторная работа 2. Упаковка многокомпонентного аналитического приложения с помощью Docker и Docker Compose.

## Выполнила Савкина Мария, группа БД-251м

## Вариант 25

*Бизнес-задача:* Диабет (Риски)	

*Проектная задача:* loader: Скрипт анонимизации данных перед загрузкой.	

*Техническое задание:* Использовать секреты (Docker Secrets или эмуляцию через файлы), чтобы передать ключи шифрования, а не через ENV.

## Архитектура решения.
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
