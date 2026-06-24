from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from ai_service.app.routes.tasks import router as tasks_router

app = FastAPI(
    title="AI Service",
    description="AI assistant service for task parsing and productivity features.",
    version="1.0.0",
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

app.include_router(tasks_router)

@app.get("/", tags=["Health"])
def read_root():
    return {"message": "AI Service is running!"}


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "healthy", "service": "ai"}