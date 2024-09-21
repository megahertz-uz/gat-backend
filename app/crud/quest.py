from sqlmodel import Session, select
from app.models import Quest, City


def get_quests_with_cities(session: Session):
    statement = (
        select(Quest, City)
        .join(City, City.id == Quest.city_id)
        .order_by(Quest.id)
    )
    return session.exec(statement).all()