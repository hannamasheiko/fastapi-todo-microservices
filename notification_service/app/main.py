from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.views import router
from app.consumers.task_consumer import start_consumers

app = FastAPI(
    title="Notification Service",
    description="Мікросервіс нотифікацій з RabbitMQ",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

#Запускаємо консюмерів при старті
@app.on_event("startup")
async def startup_event():
    """Запускаємо RabbitMQ консюмерів"""
    start_consumers()


@app.get("/", tags=["Health"])
def read_root():
    return {"message": "Notification Service is running!"}

@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "healthy", "service": "notifications"}