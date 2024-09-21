from datetime import datetime, timedelta
from typing import Annotated
import jwt

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import ValidationError
from loguru import logger

from app import crud
from app.api.deps import CurrentUser, SessionDep, TokenBlacklistRedisDep, blacklist_token, TokenDep
from app.core import security
from app.core.config import settings
from app.models import Token, Message

router = APIRouter()


def decode_jwt_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[security.ALGORITHM])
    except (jwt.InvalidTokenError, ValidationError) as e:
        logger.error(f"Failed to decode token: {e}")
        raise HTTPException(status_code=403, detail="Invalid token")


@router.post("/login/access-token")
def login_access_token(session: SessionDep, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = crud.authenticate(
        session=session, email=form_data.username, password=form_data.password
    )
    if not user:
        logger.warning(f"Login failed for user: {form_data.username}")
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        user.id, expires_delta=access_token_expires
    )
    logger.info(f"User {user.email} logged in successfully")

    return Token(access_token=access_token)


@router.post("/logout")
async def logout_user(current_user: CurrentUser, token: TokenDep, redis_client: TokenBlacklistRedisDep) -> Message:
    """
    User logout. Token is blacklisted.
    """
    payload = decode_jwt_token(token)
    expiration = datetime.fromtimestamp(payload["exp"]) - datetime.utcnow()
    await blacklist_token(redis_client, token, expiration)
    logger.info(f"User {current_user.email} logged out, token blacklisted")

    return Message(message="Successfully logged out")
