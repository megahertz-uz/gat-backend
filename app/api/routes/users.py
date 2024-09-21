from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from loguru import logger

from app import crud
from app.api.deps import (
    CurrentUser,
    SessionDep,
    get_current_user,
)
from app.models import (
    UserCreate,
    UserPublic,
    UserUpdate,
    UserRegister,
)

router = APIRouter()


@router.patch("/me", dependencies=[Depends(get_current_user)], response_model=UserPublic)
def update_user_me(*, session: SessionDep, user_in: UserUpdate, current_user: CurrentUser) -> Any:
    if user_in.email:
        existing_user = crud.get_user_by_email(session=session, email=user_in.email)
        if existing_user and existing_user.id != current_user.id:
            raise HTTPException(
                status_code=409, detail="User with this email already exists"
            )
    user_data = user_in.model_dump(exclude_unset=True)
    current_user.sqlmodel_update(user_data)
    session.add(current_user)
    session.commit()
    session.refresh(current_user)
    return current_user


@router.get("/me", response_model=UserPublic)
def read_user_me(current_user: CurrentUser) -> Any:
    return current_user


@router.post("/signup", response_model=UserPublic)
def register_user(session: SessionDep, user_in: UserRegister) -> Any:
    check_email_unique(session=session, email=user_in.email)

    user_create = UserCreate.model_validate(user_in)
    user = crud.create_user(session=session, user_create=user_create)

    logger.info(f"User registered with email: {user_in.email}")

    return user


def check_email_unique(session: SessionDep, email: str, exclude_user_id: int = None):
    user = crud.get_user_by_email(session=session, email=email)
    if user and user.id != exclude_user_id:
        logger.warning(f"Email already in use: {email}")
        raise HTTPException(
            status_code=409,
            detail="User with this email already exists"
        )
