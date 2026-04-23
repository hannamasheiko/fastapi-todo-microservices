from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from todo_service.app.database import get_db
from todo_service.app.dependencies import get_current_user
from todo_service.app.schemas import TodoItemCreate, TodoItemUpdate, TodoItemInDB
from todo_service.app.services import TodoService
from todo_service.app.models import User

router = APIRouter(prefix="/todos", tags=["Todos"])


@router.get("", response_model=List[TodoItemInDB])
def get_todos(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """Отримати завдання поточного користувача"""
    todos = TodoService.get_user_todos(db, current_user)
    return todos


@router.get("/{todo_id}", response_model=TodoItemInDB)
def get_todo(
        todo_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """Отримати конкретне завдання"""
    todo = TodoService.get_todo_by_id(db, todo_id, current_user)

    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found"
        )

    return todo


@router.post("", response_model=TodoItemInDB, status_code=201)
def create_todo(
        todo: TodoItemCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """Створити нове завдання"""
    return TodoService.create_todo(db, todo, current_user)


@router.put("/{todo_id}", response_model=TodoItemInDB)
def update_todo(
        todo_id: int,
        todo_update: TodoItemUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """Оновити завдання"""
    todo = TodoService.get_todo_by_id(db, todo_id, current_user)

    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found"
        )

    return TodoService.update_todo(db, todo, todo_update)


@router.delete("/{todo_id}", status_code=204)
def delete_todo(
        todo_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """Видалити завдання"""
    todo = TodoService.get_todo_by_id(db, todo_id, current_user)

    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found"
        )

    TodoService.delete_todo(db, todo)