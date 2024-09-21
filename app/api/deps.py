from collections.abc import Generator
from typing import Annotated
import jwt
from datetime import timedelta
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError
from pydantic import ValidationError
from sqlmodel import Session
from loguru import logger

from app.core import security
from app.core.config import settings
from app.core.db import engine
from app.core.redis import redis_manager, RedisClient
from app.models import TokenPayload, User

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)


def get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_db)]
TokenDep = Annotated[str, Depends(reusable_oauth2)]


async def get_redis(db: int = 0) -> RedisClient:
    return redis_manager.get_client(db=db)


async def get_token_blacklist_redis() -> RedisClient:
    return await get_redis(db=settings.RedisDB.TOKEN_BLACK_LIST.value)


async def get_lesson_content_redis() -> RedisClient:
    return await get_redis(db=settings.RedisDB.LESSON_CONTENT.value)


TokenBlacklistRedisDep = Annotated[RedisClient, Depends(get_token_blacklist_redis)]
LessonContentRedisDep = Annotated[RedisClient, Depends(get_lesson_content_redis)]


async def get_current_user(session: SessionDep, token: TokenDep, redis: TokenBlacklistRedisDep) -> User:
    try:
        if await is_token_blacklisted(redis, token):
            raise HTTPException(
                status_code=401,
                detail="Token has been revoked"
            )

        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except ExpiredSignatureError as e:
        raise HTTPException(
            status_code=401,
            detail=f"Token has expired: {e}"
        )

    except (InvalidTokenError, ValidationError) as e:
        logger.error(f"Token validation error: {e}")
        raise HTTPException(
            status_code=403,
            detail="Could not validate credentials",
        )

    user = session.get(User, token_data.sub)

    if not user:
        logger.warning(f"User not found: {token_data.sub}")
        raise HTTPException(status_code=404, detail="User not found")

    logger.info(f"User authenticated: {user.email}")

    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


async def is_token_blacklisted(redis: TokenBlacklistRedisDep, token: str) -> bool:
    """
    Checking for a blacklisted token (in Redis).
    """
    return await redis.get(token)


async def blacklist_token(redis: TokenBlacklistRedisDep, token: str, expiration: timedelta):
    """
    Adds a token to the blacklist indicating its expiration time.
    """
    try:
        await redis.setex(token, expiration, "blacklisted")
    except Exception as e:
        logger.error(f"Error blacklisting token: {e}")
        raise
