# FastAPI Microservices Todo Project

Невеликий бекенд-проєкт із мікросервісною архітектурою, побудований на FastAPI з використанням PostgreSQL, Redis та RabbitMQ, Docker та Alembic.

У проєкті реалізовано:
- REST API
- авторизацію (JWT)
- кешування (Redis)
- взаємодію між сервісами (RabbitMQ)
- базову мікросервісну архітектуру 
- тестування API (pytest)
- міграції бази даних (Alembic)

## Архітектура

Система побудована у monorepo microservices-style структурі та складається з трьох FastAPI-сервісів:

| Сервіс | Порт | Відповідальність | База даних |
|---|---:|---|---|
| Todo Service | 8000 | Користувачі, JWT-авторизація, CRUD для задач, кешування, публікація подій | `todo_db` |
| Analytics Service | 8001 | Збереження агрегованої статистики по задачах користувача | `analytics_db` |
| Notification Service | 8002 | Обробка RabbitMQ-подій, збереження та отримання повідомлень користувача | `notification_db` |

Додаткова інфраструктура:

| Сервіс | Порт | Призначення |
|---|---:|---|
| PostgreSQL Todo DB | 5432 | Основна база даних для користувачів і задач |
| PostgreSQL Analytics DB | 5433 | Окрема база даних для аналітики |
| PostgreSQL Notification DB | 5434 | Окрема база даних для повідомлень |
| Redis | 6379 | Кешування списку задач і окремих задач |
| RabbitMQ | 5672 / 15672 | Брокер повідомлень та management UI |

## Технології

- **FastAPI**
- **SQLAlchemy**
- **PostgreSQL**
- **Redis**
- **RabbitMQ**
- **Docker / Docker Compose**
- **Alembic (міграції)**
- **JWT (авторизація)**
- **httpx (міжсервісні запити)**
- **pytest**

---

## Основний функціонал

### Auth
- Реєстрація користувача
- Логін із JWT-токеном
- Захищені endpoint-и через Bearer Token

---

### Todo Service
- CRUD-операції для задач
- Прив’язка задач до конкретного користувача
- Перевірка доступу: користувач бачить і змінює тільки власні задачі
- Redis-кешування списку задач і окремих задач
- Інвалідація кешу після створення, оновлення та видалення задач
- Публікація RabbitMQ-подій при створенні задачі (`task:created`)
- Публікація RabbitMQ-подій при зміні задачі на виконану (`task:completed`)
- Синхронізація агрегованої статистики з Analytics Service після змін у задачах

---

### Analytics Service
- Окрема PostgreSQL-база для аналітики
- Збереження агрегованої статистики по задачах користувача
- Створення або оновлення статистики через sync endpoint
- Отримання збереженої статистики користувача
- Розрахунок відсотка виконаних задач

---

### Notification Service
- Окрема PostgreSQL-база для повідомлень
- Обробка RabbitMQ-подій через consumer
- Створення повідомлень на основі подій `task:created` і `task:completed`


## Основний флоу

1. Користувач логіниться і отримує JWT
2. Створює задачі через todo_service
3. При створенні/оновленні задачі:
   - дані йдуть у БД
   - частина читається через Redis
   - подія відправляється в RabbitMQ
4. notification_service обробляє події з RabbitMQ і зберігає повідомлення в `notification_db`
5. analytics_service зберігає та віддає агреговану статистику користувача з `analytics_db`
6. Користувач може отримати свої задачі, статистику та повідомлення через відповідні API endpoint-и.

## Запуск

### Environment variables

Для локального запуску кожен сервіс має власний `.env` файл.

Створи локальні `.env` файли на основі прикладів:

`cp todo_service/.env.example todo_service/.env`

`cp analytics_service/.env.example analytics_service/.env`

`cp notification_service/.env.example notification_service/.env`

Після цього відредагуй значення у .env під своє локальне середовище.

> `docker-compose-full.yml` містить development-значення для локального запуску.
> Для реального середовища секрети, зокрема `SECRET_KEY`, потрібно передавати через environment variables.

### Через Docker

Запускає всі сервіси разом:

` docker compose -f docker-compose-full.yml up -d --build`

### Локально

Запуск кожного сервісу окремо:

- `uvicorn todo_service.app.main:app --reload --port 8000`
- `uvicorn analytics_service.app.main:app --reload --port 8001`
- `uvicorn notification_service.app.main:app --reload --port 8002`

### Міграції

У проєкті використовуються Alembic-міграції для баз даних сервісів.

Перед застосуванням міграцій переконайся, що PostgreSQL-контейнери запущені:

```docker compose -f docker-compose-full.yml up -d postgres analytics_postgres notification_postgres```

Застосувати міграції для todo_service:

`alembic upgrade head`

Застосувати міграції для analytics_service:

```alembic -c analytics_service/alembic.ini upgrade head```

Застосувати міграції для notification_service:

```alembic -c notification_service/alembic.ini upgrade head```

Після цього будуть створені необхідні таблиці в базах:

* todo_db
* analytics_db
* notification_db

### Тестування

У проєкті є API-тести для основних сервісів.

#### Todo Service

Перевіряється:

- health endpoint
- auth flow: реєстрація та логін
- todo CRUD
- доступ тільки до власних задач користувача
- 404 для неіснуючих задач
- unauthorized-сценарії без валідного токена

#### Analytics Service

Перевіряється:

- health endpoint
- sync endpoint для створення аналітики користувача
- оновлення вже існуючої аналітики
- отримання збереженої статистики користувача
- 404 для користувача без аналітики

#### Notification Service

Перевіряється:

- health endpoint
- отримання порожнього списку повідомлень
- отримання збережених повідомлень користувача
- фільтрація повідомлень за `user_id`


Запуск усіх тестів:

```pytest -v```

## API документація

Swagger UI доступний окремо для кожного сервісу:

- Todo Service: http://127.0.0.1:8000/docs
- Analytics Service: http://127.0.0.1:8001/docs
- Notification Service: http://127.0.0.1:8002/docs