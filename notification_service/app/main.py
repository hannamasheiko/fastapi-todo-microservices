from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from notification_service.app.views import router
from notification_service.app.consumers.task_consumer import start_consumers
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Запускаємо RabbitMQ консюмерів при старті застосунку"""
    start_consumers()
    yield



app = FastAPI(
    title="Notification Service",
    description="Мікросервіс нотифікацій з RabbitMQ",
    lifespan=lifespan,
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/", tags=["Health"])
def read_root():
    return {"message": "Notification Service is running!"}

@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "healthy", "service": "notifications"}