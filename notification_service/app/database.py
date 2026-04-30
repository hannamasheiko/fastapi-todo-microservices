from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from notification_service.app.config import settings


engine = create_engine(
    settings.notification_database_url,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()