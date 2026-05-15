from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from todo_service.app.database import get_db
from todo_service.app.dependencies import get_current_user
from todo_service.app.models import User
from todo_service.app.schemas import TodoItemCreate, TodoItemInDB, TodoItemUpdate
from todo_service.app.services import TodoService
from todo_service.app.services.analytics_client import sync_user_analytics

router = APIRouter(prefix="/todos", tags=["Todos"])


@router.get("", response_model=List[TodoItemInDB])
async def get_todos(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Отримати завдання поточного користувача."""
    todos = await TodoService.get_user_todos(db, current_user)
    return todos


@router.get("/{todo_id}", response_model=TodoItemInDB)
async def get_todo(
    todo_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Отримати конкретне завдання."""
    todo = await TodoService.get_todo_by_id(db, todo_id, current_user)

    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found",
        )

    return todo


@router.post("", response_model=TodoItemInDB, status_code=201)
async def create_todo(
    todo: TodoItemCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Створити нове завдання."""
    created_todo = await TodoService.create_todo(db, todo, current_user)

    await sync_user_analytics(db, current_user)

    return created_todo


@router.put("/{todo_id}", response_model=TodoItemInDB)
async def update_todo(
    todo_id: int,
    todo_update: TodoItemUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Оновити завдання."""
    todo = await TodoService.get_todo_orm_by_id(db, todo_id, current_user)

    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found",
        )

    updated_todo = await TodoService.update_todo(db, todo, todo_update)

    await sync_user_analytics(db, current_user)

    return updated_todo


@router.delete("/{todo_id}", status_code=204)
async def delete_todo(
    todo_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Видалити завдання."""
    todo = await TodoService.get_todo_orm_by_id(db, todo_id, current_user)

    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found",
        )

    await TodoService.delete_todo(db, todo)

    await sync_user_analytics(db, current_user)
