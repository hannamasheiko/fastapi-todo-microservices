from sqlalchemy.orm import Session
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
            "hashed_password": user.hashed_password,
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
            hashed_password=data["hashed_password"],
            is_active=data["is_active"],
        )

    @staticmethod
    def create_user(db: Session, user: UserCreate) -> User:
        """Створюємо нового користувача"""
        # Перевіряємо унікальність
        if db.query(User).filter(User.username == user.username).first():
            raise ValueError("Username already exists")
        if db.query(User).filter(User.email == user.email).first():
            raise ValueError("Email already exists")

        # Хешуємо пароль
        hashed_password = get_password_hash(user.password)

        # Створюємо користувача
        db_user = User(
            username=user.username,
            email=user.email,
            hashed_password=hashed_password
        )

        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        return db_user

    @staticmethod
    def authenticate_user(db: Session, username: str, password: str) -> User | None:
        """Перевіряємо credentials"""
        user = db.query(User).filter(User.username == username).first()

        if not user:
            return None

        if not verify_password(password, user.hashed_password):
            return None

        return user

    @staticmethod
    def get_user_by_username(db: Session, username: str) -> User | None:
        """Отримуємо користувача за username з кешем"""
        cache_key = f"user:username:{username}"

        cached_user = cache_service.get(cache_key)
        if cached_user:
            return UserService._deserialize_user(cached_user)

        user = db.query(User).filter(User.username == username).first()

        if user:
            cache_service.set(cache_key, UserService._serialize_user(user))

        return user


    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> User | None:
        """Отримуємо користувача за ID з кешем"""
        cache_key = f"user:id:{user_id}"

        cached_user = cache_service.get(cache_key)
        if cached_user:
            return UserService._deserialize_user(cached_user)

        user = db.query(User).filter(User.id == user_id).first()

        if user:
            cache_service.set(cache_key, UserService._serialize_user(user))

        return user