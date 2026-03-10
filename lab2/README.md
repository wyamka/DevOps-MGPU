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
        RAW["data/diabetes_new.csv"]
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

## 2. Технологический стек
```mermaid
  graph TD
    A[Python 3.10-slim] --> B[psycopg2 — драйвер PostgreSQL]
    A --> C[Streamlit — веб-интерфейс аналитики]
    A --> D[Plotly — интерактивные графики]
    A --> E[Pandas — обработка данных]
    A --> F[hashlib — анонимизация персональных данных]

    G[PostgreSQL 16 Alpine] --> H[Хранение diabetes_data]

    I[Docker Compose V2] --> J[Оркестрация сервисов: db, loader, dashboard]
    I --> K[depends_on + healthcheck]
    I --> L[named volume для PostgreSQL]

    M[Docker Secrets] --> N[Передача encryption_key для анонимизации]

    O[CSV Dataset] --> P[diabetes_new.csv]
```

## 3. Структура проекта
```
LW_02/
├── app/
│   ├── dashboard.py
│   ├── Dockerfile
│   ├── loader.py
│   └── requirements.txt
├── data/
│   └── diabetes_new.csv
├── secrets/
│   └── encryption_key.txt
├── .env
├── .dockerignore
└── docker-compose.yml
```

## 4. Описание компонентов

### 4.1. Датасет diabetes_new.csv

Датасет получен из открытого набора данных с Kaggle: https://www.kaggle.com/datasets/mathchi/diabetes-data-set путём добавления полей FirstName и SecondName для дальнейшей анонимизации данных в рамках проектной задачи Варианта 25.

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

### 4.2 Dockerfile (`app/Dockerfile`)

Соблюдены все требуемые «хорошие практики»:

| Рекомендация                          | Реализация в лабораторной работе                                                                 |
| ------------------------------------- | ------------------------------------------------------------------------------------------------ |
| Фиксированная версия базового образа  | Использован `python:3.10-slim`, а не тег `latest`                                                |
| Непривилегированный пользователь      | Создан пользователь `appuser` с UID 1000, далее используется команда `USER appuser`              |
| Эффективное использование кэша Docker | Сначала копируется `requirements.txt` и устанавливаются зависимости, затем основной код (`*.py`) |
| Очистка временных файлов и кэша       | Очистка `apt` кэша (`rm -rf /var/lib/apt/lists/*`) и установка Python-пакетов с `--no-cache-dir` |
| Исключение лишних файлов из сборки    | В `.dockerignore` добавлены `__pycache__`, `.git`, `venv`, `.env`                               |

### 4.3 app/loader.py
Логика работы:

- Ожидание доступности PostgreSQL (retry-цикл для предотвращения race condition между контейнерами).
- Чтение ключа анонимизации из Docker Secret (/run/secrets/encryption_key), чтобы не передавать его через переменные окружения.
- Создание таблицы diabetes_data в базе данных (CREATE TABLE IF NOT EXISTS).
- Проверка наличия данных: если таблица уже содержит записи — загрузка пропускается (обеспечение идемпотентности ETL-процесса).
- Чтение файла /data/diabetes_new.csv (подключён через bind mount из каталога data/).
- Анонимизация персональных данных (FirstName, LastName) с помощью SHA-256 хеширования и секретного ключа.
- Преобразование строк CSV в числовые значения и вставка данных в таблицу PostgreSQL (INSERT INTO diabetes_data).
- Завершение работы ETL-контейнера (loader выполняется как init-контейнер и останавливается после загрузки данных).

### 4.4 Dashboard (app/dashboard.py)

Streamlit-приложение с несколькими визуализациями факторов риска диабета:

- Гистограмма — распределение уровня глюкозы среди пациентов (с разделением по наличию диабета).
- Диаграмма boxplot — связь индекса массы тела (BMI) и наличия диабета.
- Точечная диаграмма — зависимость возраста и уровня глюкозы у пациентов.
- Тепловая карта корреляции — показывает взаимосвязь между медицинскими показателями (глюкоза, давление, ИМТ, возраст и др.).

Фильтр в боковой панели позволяет выбрать диапазон возраста пациентов для анализа.

### 4.5 Docker Compose (`docker-compose.yml`)

```mermaid
sequenceDiagram
    participant DC as docker compose up
    participant DB as db (PostgreSQL)
    participant L as loader (ETL)
    participant D as dashboard (Streamlit)
    participant S as Secret (encryption_key)

    DC->>DB: Запуск контейнера
    loop healthcheck (каждые 5s)
        DB->>DB: pg_isready
    end
    DB-->>DC: status: healthy
    DC->>L: Запуск loader
    L->>S: Чтение ключа анонимизации
    L->>DB: CREATE TABLE + анонимизация
    L-->>DC: exit 0 (completed_successfully)
    DC->>D: Запуск dashboard
    D->>DB: SELECT * FROM diabetes_data
    D-->>DC: Слушает 0.0.0.0:8501
    Note over DC,D: Streamlit дашборд доступен на хосте localhost:8501
```
### Ключевые настройки проекта

| Требование                   | Реализация в `docker-compose.yml` |
|-------------------------------|----------------------------------|
| **healthcheck БД**            | `pg_isready` каждые 5 сек, 10 попыток |
| **depends_on + condition**    | loader ждёт `service_healthy`; dashboard ждёт `service_completed_successfully` |
| **Именованный том**           | `pg_data:/var/lib/postgresql/data` — данные БД сохраняются после `docker compose down` |
| **Bind mount (read-only)**    | `./data:/data:ro` — CSV доступен loader-у только для чтения |
| **Изолированная сеть**        | `backend-network` (bridge) — все 3 сервиса подключены |
| **Docker Secret**             | `encryption_key` — ключ анонимизации передаётся loader-у через secrets |

### .env

```dotenv
POSTGRES_DB=diabetes
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
CSV_PATH=/data/diabetes_new.csv
```
### secrets/encryption_key.txt

```
d1aB9xQ7pLkR4zT2mS8yV6wN
```

### .dockerignore

```dotedockerignore
__pycache__/
*.pyc
*.pyo
*.pyd

.env
secrets/
*.key
*.txt

venv/
env/

.git/
.gitignore
.DS_Store
.idea/
.vscode/

*.log
```

# Ход работы

1. **Проверка текущих контейнеров Docker**  
Перед запуском проекта проверяем, какие контейнеры уже запущены:  
![docker ps до работы](https://raw.githubusercontent.com/wyamka/DevOps-MGPU/blob/main/lab2/screenshots/docker%20ps%20до%20работы.png)

2. **Сборка и запуск контейнеров проекта**  
Запускаем Docker Compose с опцией сборки образов:  
![docker compose up -d -build 1](https://raw.githubusercontent.com/wyamka/DevOps-MGPU/blob/main/lab2/screenshots/docker%20compose%20up%20-d%20-build%201.png)  
![docker compose up -d -build 2](https://raw.githubusercontent.com/wyamka/DevOps-MGPU/blob/main/lab2/screenshots/docker%20compose%20up%20-d%20-build%202.png)

3. **Проверка статуса контейнеров после запуска**  
Убедимся, что все сервисы запущены корректно:  
![docker compose ps после запуска](https://raw.githubusercontent.com/wyamka/DevOps-MGPU/blob/main/lab2/screenshots/docker%20compose%20ps%20после%20запуска.png)

4. **Просмотр логов загрузчика**  
Проверяем процесс загрузки и анонимизации данных:  
![logs](https://raw.githubusercontent.com/wyamka/DevOps-MGPU/blob/main/lab2/screenshots/logs.png)

5. **Визуализация данных**  
После успешной загрузки данных открываем Streamlit на локальном хосте:  

- **Распределение уровня глюкозы у пациентов с диабетом и без него**  
![Распределение уровня глюкозы у пациентов с диабетом и без него](https://raw.githubusercontent.com/wyamka/DevOps-MGPU/blob/main/lab2/screenshots/Распределение%20уровня%20глюкозы%20у%20пациентов%20с%20диабетом%20и%20без%20него.png)  

- **Связь ИМТ и наличия диабета**  
![Связь ИМТ и диабета](https://raw.githubusercontent.com/wyamka/DevOps-MGPU/blob/main/lab2/screenshots/Связь%20ИМТ%20и%20диабета.png)  

- **Возраст и уровень глюкозы**  
![Корреляция возраста и уровня глюкозы](https://raw.githubusercontent.com/wyamka/DevOps-MGPU/blob/main/lab2/screenshots/Корреляция%20возраста%20и%20уровня%20глюкозы.png)  

- **Корреляционная тепловая карта медицинских показателей**  
![Тепловая карта медицинских показателей](https://raw.githubusercontent.com/wyamka/DevOps-MGPU/blob/main/lab2/screenshots/Тепловая%20карта%20медицинских%20показателей.png)

6. **Остановка и удаление контейнеров после работы**  
Завершаем работу с проектом, останавливаем и удаляем контейнеры:  
![docker compose down](https://raw.githubusercontent.com/wyamka/DevOps-MGPU/blob/main/lab2/screenshots/docker%20compose%20down.png)

## Вывод

В ходе лабораторной работы реализована многокомпонентная аналитическая система для анализа факторов риска диабета. С помощью Docker Compose удалось организовать взаимодействие ETL-загрузчика, базы данных PostgreSQL и Streamlit-дэшборда с применением Docker Secrets для безопасной анонимизации персональных данных. Полученные визуализации позволяют наглядно исследовать распределение медицинских показателей и выявлять корреляции, обеспечивая удобный интерфейс для анализа данных.
