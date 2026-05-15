from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt, ExpiredSignatureError
from passlib.context import CryptContext
from todo_service.app.config import settings
from todo_service.app.schemas import TokenData
import logging

logger = logging.getLogger(__name__)

# ==================== PASSWORD HASHING ====================

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Перевіряємо пароль"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Хешуємо пароль"""
    return pwd_context.hash(password)


# ==================== JWT TOKENS ====================


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Створюємо JWT токен"""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.access_token_expire_minutes
        )

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode, settings.secret_key, algorithm=settings.algorithm
    )

    return encoded_jwt


def decode_token(token: str) -> Optional[TokenData]:
    """Декодуємо JWT токен"""
    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        username: str | None = payload.get("sub")
        if username is None:
            logger.warning("JWT token is missing 'sub' claim")

            return None

        return TokenData(username=username)

    except ExpiredSignatureError:
        logger.warning("JWT token has expired")

        return None

    except JWTError as e:
        logger.warning(f"Invalid JWT token: {e}")

        return None
