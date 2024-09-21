from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from loguru import logger

from app import crud

from app.models import City

from app.api.deps import (
    SessionDep
)

router = APIRouter()

@router.get("/", response_model = list[City])
def get_cities(session: SessionDep):
    cities = crud.list_cities(session=session)  # Use your CRUD function to get cities
    if not cities:
        raise HTTPException(status_code=404, detail="No cities found")
    return cities