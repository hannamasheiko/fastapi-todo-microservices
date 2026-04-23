# FastAPI Microservices Todo Project

Невеликий бекенд-проєкт із мікросервісною архітектурою, побудований на FastAPI з використанням PostgreSQL, Redis та RabbitMQ.

У проєкті реалізовано:
- REST API
- авторизацію (JWT)
- кешування (Redis)
- асинхронну взаємодію між сервісами (RabbitMQ)
- базову мікросервісну архітектуру

## Архітектура

Система складається з кількох сервісів:

- Todo Service (порт 8000) — основний API (користувачі + задачі)
- Analytics Service (порт 8001) — проста аналітика по користувачу
- Notification Service (порт 8002) — зберігає і віддає повідомлення

Також використовуються додаткові сервіси:

- PostgreSQL (порт 5432) — основна база даних
- Redis (порт 6379) — використовується для кешування
- RabbitMQ (порти 5672 / 15672) — брокер повідомлень для взаємодії між сервісами


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

---

## Основний функціонал

### Auth
- Реєстрація користувача
- Логін (JWT)
- Захищені endpoint-и через Bearer Token

---

### Todo Service
- CRUD операції для задач
- Прив’язка задач до користувача
- Кешування через Redis
- Інвалідація кешу при зміні даних

---

### Analytics Service
- Отримання статистики користувача
- Взаємодія через HTTP (httpx)

---

### Notification Service
- Отримання повідомлень
- Створення повідомлень через API
- Обробка подій із RabbitMQ (consumer)

---

## Основний флоу

1. Користувач логіниться і отримує JWT
2. Створює задачі через todo_service
3. При створенні/оновленні задачі:
   - дані йдуть у БД
   - частина читається через Redis
   - подія відправляється в RabbitMQ
4. notification_service обробляє події і створює повідомлення
5. analytics_service віддає базову статистику

## Запуск

### Через Docker

Запускає всі сервіси разом:

docker compose -f docker-compose-full.yml up -d --build

### Локально

Запуск кожного сервісу окремо:

- uvicorn todo_service.app.main:app --reload --port 8000
- uvicorn analytics_service.app.main:app --reload --port 8001
- uvicorn notification_service.app.main:app --reload --port 8002

## API документація

Swagger UI доступний за адресами:

- http://127.0.0.1:8000/docs
- http://127.0.0.1:8001/docs
- http://127.0.0.1:8002/docs