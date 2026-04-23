from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from analytics_service.app.views import router

app = FastAPI(
    title="Analytics Service",
    description="Мікросервіс аналітики для Todo API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.get("/", tags=["Health"])
def read_root():
    return {"message": "Analytics Service is running!"}

@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "healthy", "service": "analytics"}