from sqlalchemy.orm import Session
from typing import List
from todo_service.app.models import TodoItem, User
from todo_service.app.schemas import TodoItemCreate, TodoItemUpdate
from todo_service.app.services.rabbitmq_producer import producer  # Додаємо import
from todo_service.app.services.cache_service import cache_service
import logging

logger = logging.getLogger(__name__)

class TodoService:
    """Сервіс для роботи з завданнями"""

    @staticmethod
    def create_todo(db: Session, todo: TodoItemCreate, user: User) -> TodoItem:
        """Створюємо завдання"""
        db_todo = TodoItem(
            title=todo.title,
            description=todo.description,
            completed=todo.completed,
            priority=todo.priority,
            owner_id=user.id
        )

        db.add(db_todo)
        db.commit()
        db.refresh(db_todo)

        # 🆕 Відправляємо повідомлення в RabbitMQ
        try:
            producer.declare_queue("task:created")
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
    def get_user_todos(db: Session, user: User) -> List[TodoItem]:
        """Отримуємо завдання користувача з кешем"""
        cache_key = f"user:{user.id}:todos"

        # Спробуємо отримати з кеша
        cached_todos = cache_service.get(cache_key)
        if cached_todos:
            return cached_todos

        # Якщо немає в кеші, беремо з БД
        todos = db.query(TodoItem).filter(
            TodoItem.owner_id == user.id
        ).order_by(TodoItem.created_at.desc()).all()

        # Зберігаємо в кеш на 5 хвилин
        # cache_service.set(cache_key, [t.__dict__ for t in todos], ttl=300)
        cache_service.set(
            cache_key,
            [
                {
                    "id": t.id,
                    "title": t.title,
                    "description": t.description,
                    "completed": t.completed,
                    "priority": t.priority,
                    "owner_id": t.owner_id,
                    "created_at": t.created_at.isoformat() if t.created_at else None,
                    "updated_at": t.updated_at.isoformat() if t.updated_at else None,
                }
                for t in todos
            ],
            ttl=300
        )

        return todos

    @staticmethod
    def get_todo_by_id(db: Session, todo_id: int, user: User) -> TodoItem | None:
        """Отримуємо завдання з кешем"""
        cache_key = f"todo:{todo_id}:user:{user.id}"

        # Спробуємо кеш
        cached_todo = cache_service.get(cache_key)
        if cached_todo:
            return cached_todo

        # З БД
        todo = db.query(TodoItem).filter(
            (TodoItem.id == todo_id) &
            (TodoItem.owner_id == user.id)
        ).first()

        if todo:
            # cache_service.set(cache_key, todo.__dict__)
            cache_service.set(cache_key, {
                "id": todo.id,
                "title": todo.title,
                "description": todo.description,
                "completed": todo.completed,
                "priority": todo.priority,
                "owner_id": todo.owner_id,
                "created_at": todo.created_at.isoformat() if todo.created_at else None,
                "updated_at": todo.updated_at.isoformat() if todo.updated_at else None,
            })
        return todo

    @staticmethod
    def update_todo(db: Session, todo: TodoItem, update_data: TodoItemUpdate) -> TodoItem:
        """Оновлюємо завдання і інвалідуємо кеш"""
        if update_data.title is not None:
            todo.title = update_data.title
        if update_data.description is not None:
            todo.description = update_data.description
        if update_data.completed is not None:
            todo.completed = update_data.completed
        if update_data.priority is not None:
            todo.priority = update_data.priority

        db.commit()
        db.refresh(todo)

        # 🆕 Інвалідуємо кеш при оновленні
        cache_service.delete(f"todo:{todo.id}:user:{todo.owner_id}")
        cache_service.delete(f"user:{todo.owner_id}:todos")

        return todo

    @staticmethod
    def delete_todo(db: Session, todo: TodoItem) -> None:
        """Видаляємо завдання та інвалідуємо кеш"""
        user_id = todo.owner_id
        todo_id = todo.id

        db.delete(todo)
        db.commit()

        # 🆕 Видаляємо з кеша
        cache_service.delete(f"todo:{todo_id}:user:{user_id}")
        cache_service.delete(f"user:{user_id}:todos")

