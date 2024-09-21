from loguru import logger
from sqlmodel import Session, select
from typing import Any

from app.core.security import get_password_hash, verify_password
from app.models import User, UserCreate, UserUpdate


def get_user_by_email(*, session: Session, email: str) -> User | None:
    statement = select(User).where(User.email == email)
    session_user = session.exec(statement).first()
    return session_user


def hash_user_password(password: str) -> str:
    return get_password_hash(password)


def create_user(*, session: Session, user_create: UserCreate) -> User:
    existing_user = get_user_by_email(session=session, email=user_create.email)
    if existing_user:
        logger.warning(f"Attempt to create a user with an existing email: {user_create.email}")
        raise ValueError("The user with this email already exists in the system.")

    hashed_password = hash_user_password(user_create.password)
    db_obj = User(
        email=user_create.email,
        first_name=user_create.first_name,
        last_name=user_create.last_name,
        hashed_password=hashed_password,
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)

    logger.info(f"User created with email: {user_create.email}")

    return db_obj


def update_user(*, session: Session, db_user: User, user_in: UserUpdate) -> Any:
    user_data = user_in.model_dump(exclude_unset=True)
    extra_data = {}

    if "password" in user_data:
        password = user_data.pop("password")
        hashed_password = hash_user_password(password)
        extra_data["hashed_password"] = hashed_password

    db_user.sqlmodel_update(user_data, update=extra_data)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    logger.info(f"User updated: {db_user.email}")

    return db_user


def authenticate(*, session: Session, email: str, password: str) -> User | None:
    db_user = get_user_by_email(session=session, email=email)
    if not db_user:
        logger.warning(f"Authentication failed for non-existent user: {email}")
        return None
    if not verify_password(password, db_user.hashed_password):
        logger.warning(f"Authentication failed for user: {email} - Incorrect password")
        return None
    return db_user
