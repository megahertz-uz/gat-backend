from loguru import logger
from sqlmodel import Session, select
from typing import List

from app.models import City


def list_cities(*, session: Session) -> List[City] | None:
    statement = select(City)
    cities = session.exec(statement).all()
    return cities