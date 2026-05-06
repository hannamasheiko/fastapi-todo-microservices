import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from todo_service.app.models import TodoItem, User
from todo_service.app.schemas import TodoItemCreate, TodoItemUpdate
from todo_service.app.services.cache_service import cache_service
from todo_service.app.services.rabbitmq_producer import producer


logger = logging.getLogger(__name__)


class TodoService:
    """Сервіс для роботи з завданнями"""

    @staticmethod
    async def create_todo(
        db: AsyncSession,
        todo: TodoItemCreate,
        user: User,
    ) -> TodoItem:
        """Створюємо завдання"""
        db_todo = TodoItem(
            title=todo.title,
            description=todo.description,
            completed=todo.completed,
            priority=todo.priority,
            owner_id=user.id
        )

        db.add(db_todo)
        await db.commit()
        await db.refresh(db_todo)

        # Інвалідуємо кеш списку задач користувача
        await cache_service.delete(f"user:{user.id}:todos")

        # Відправляємо повідомлення в RabbitMQ
        try:
            producer.publish_message(
                queue_name="task:created",
                message={
                    "event": "task_created",
                    "user_id": user.id,
                    "username": user.username,
                    "task_id": db_todo.id,
                    "title": db_todo.title,
                    "timestamp": db_todo.created_at.isoformat()
                }
            )
        except Exception as e:
            logger.error(f"RabbitMQ publish failed: {e}")
        return db_todo

    @staticmethod
    def _serialize_todo(todo: TodoItem) -> dict:
        return {
            "id": todo.id,
            "title": todo.title,
            "description": todo.description,
            "completed": todo.completed,
            "priority": todo.priority,
            "owner_id": todo.owner_id,
            "created_at": todo.created_at.isoformat() if todo.created_at else None,
            "updated_at": todo.updated_at.isoformat() if todo.updated_at else None,
        }

    @staticmethod
    async def get_user_todos(
        db: AsyncSession,
        user: User,
    ) -> list[dict]:
        """Отримуємо завдання користувача з кешем"""
        cache_key = f"user:{user.id}:todos"
        cached_todos = await cache_service.get(cache_key)
        if cached_todos:
            return cached_todos

        result = await db.execute(
            select(TodoItem)
            .where(TodoItem.owner_id == user.id)
            .order_by(TodoItem.created_at.desc())
        )

        todos = result.scalars().all()

        serialized_todos = [TodoService._serialize_todo(t) for t in todos]
        await cache_service.set(cache_key, serialized_todos, ttl=300)

        return serialized_todos

    @staticmethod
    async def get_todo_by_id(
        db: AsyncSession,
        todo_id: int,
        user: User,
    ) -> dict | None:
        """Отримуємо завдання з кешем для read-only сценарію"""
        cache_key = f"todo:{todo_id}:user:{user.id}"
        cached_todo = await cache_service.get(cache_key)
        if cached_todo:
            return cached_todo

        result = await db.execute(
            select(TodoItem).where(
                TodoItem.id == todo_id,
                TodoItem.owner_id == user.id,
            )
        )

        todo = result.scalar_one_or_none()

        if todo:
            serialized = TodoService._serialize_todo(todo)
            await cache_service.set(cache_key, serialized, ttl=300)
            return serialized

        return None

    @staticmethod
    async def get_todo_orm_by_id(
        db: AsyncSession,
        todo_id: int,
        user: User,
    ) -> TodoItem | None:
        """Отримуємо ORM-об'єкт із БД для update/delete"""
        result = await db.execute(
            select(TodoItem).where(
                TodoItem.id == todo_id,
                TodoItem.owner_id == user.id,
            )
        )

        return result.scalar_one_or_none()

    @staticmethod
    async def update_todo(
        db: AsyncSession,
        todo: TodoItem,
        update_data: TodoItemUpdate,
    ) -> TodoItem:
        """Оновлюємо завдання і інвалідуємо кеш"""

        was_completed = todo.completed

        if update_data.title is not None:
            todo.title = update_data.title
        if update_data.description is not None:
            todo.description = update_data.description
        if update_data.completed is not None:
            todo.completed = update_data.completed
        if update_data.priority is not None:
            todo.priority = update_data.priority

        await db.commit()
        await db.refresh(todo)

        await cache_service.delete(f"todo:{todo.id}:user:{todo.owner_id}")
        await cache_service.delete(f"user:{todo.owner_id}:todos")

        if not was_completed and todo.completed:
            try:
                producer.publish_message(
                    queue_name="task:completed",
                    message={
                        "event": "task_completed",
                        "user_id": todo.owner_id,
                        "task_id": todo.id,
                        "title": todo.title,
                        "timestamp": todo.updated_at.isoformat()
                    }
                )
            except Exception as e:
                logger.error(f"RabbitMQ publish failed: {e}")

        return todo

    @staticmethod
    async def delete_todo(
        db: AsyncSession,
        todo: TodoItem,
    ) -> None:
        """Видаляємо завдання та інвалідуємо кеш"""
        user_id = todo.owner_id
        todo_id = todo.id

        await db.delete(todo)
        await db.commit()

        # Видаляємо з кеша
        await cache_service.delete(f"todo:{todo_id}:user:{user_id}")
        await cache_service.delete(f"user:{user_id}:todos")