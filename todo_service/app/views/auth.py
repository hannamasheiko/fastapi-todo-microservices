from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from todo_service.app.config import settings
from todo_service.app.database import get_db
from todo_service.app.dependencies import get_current_user
from todo_service.app.schemas import Token, UserCreate, UserInDB
from todo_service.app.security import create_access_token
from todo_service.app.services import UserService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserInDB, status_code=201)
async def register(
    user: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    """Реєстрація нового користувача."""
    try:
        created_user = await UserService.create_user(db, user)
        return created_user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """Вхід користувача та отримання токена."""
    user = await UserService.authenticate_user(
        db,
        form_data.username,
        form_data.password,
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserInDB)
async def get_me(current_user=Depends(get_current_user)):
    """Отримати інформацію про поточного користувача."""
    return current_user
