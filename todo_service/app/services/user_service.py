from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from todo_service.app.models import User
from todo_service.app.schemas import UserCreate
from todo_service.app.security import get_password_hash, verify_password
from todo_service.app.services.cache_service import cache_service


class UserService:
    """Сервіс для роботи з користувачами"""

    @staticmethod
    def _serialize_user(user: User) -> dict:
        """Перетворюємо User в dict для кешу"""
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "updated_at": user.updated_at.isoformat() if user.updated_at else None,
        }

    @staticmethod
    def _deserialize_user(data: dict) -> User:
        """Перетворюємо dict з кешу назад в User object"""
        return User(
            id=data["id"],
            username=data["username"],
            email=data["email"],
            is_active=data["is_active"],
        )

    @staticmethod
    async def create_user(db: AsyncSession, user: UserCreate) -> User:
        """Створюємо нового користувача"""

        username_result = await db.execute(
            select(User).where(User.username == user.username)
        )
        existing_username = username_result.scalar_one_or_none()

        if existing_username:
            raise ValueError("Username already exists")

        email_result = await db.execute(select(User).where(User.email == user.email))
        existing_email = email_result.scalar_one_or_none()

        if existing_email:
            raise ValueError("Email already exists")

        hashed_password = get_password_hash(user.password)

        db_user = User(
            username=user.username, email=user.email, hashed_password=hashed_password
        )

        db.add(db_user)

        await db.commit()
        await db.refresh(db_user)

        return db_user

    @staticmethod
    async def authenticate_user(
        db: AsyncSession,
        username: str,
        password: str,
    ) -> User | None:
        """Перевіряємо credentials"""

        result = await db.execute(select(User).where(User.username == username))
        user = result.scalar_one_or_none()

        if not user:
            return None

        if not verify_password(password, user.hashed_password):
            return None

        return user

    @staticmethod
    async def get_user_by_username(
        db: AsyncSession,
        username: str,
    ) -> User | None:
        """Отримуємо користувача за username з кешем"""
        cache_key = f"user:username:{username}"

        cached_user = await cache_service.get(cache_key)
        if cached_user:
            return UserService._deserialize_user(cached_user)

        result = await db.execute(select(User).where(User.username == username))
        user = result.scalar_one_or_none()

        if user:
            await cache_service.set(cache_key, UserService._serialize_user(user))

        return user

    @staticmethod
    async def get_user_by_id(
        db: AsyncSession,
        user_id: int,
    ) -> User | None:
        """Отримуємо користувача за ID з кешем"""
        cache_key = f"user:id:{user_id}"

        cached_user = await cache_service.get(cache_key)
        if cached_user:
            return UserService._deserialize_user(cached_user)

        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if user:
            await cache_service.set(cache_key, UserService._serialize_user(user))

        return user

    @staticmethod
    async def get_user_by_username_db(
        db: AsyncSession,
        username: str,
    ) -> User | None:
        """Отримуємо користувача за username напряму з БД без кешу"""

        result = await db.execute(select(User).where(User.username == username))

        return result.scalar_one_or_none()
