from sqlmodel import Session, select
from app.models import City, UserQuest, Quest, QuestStatusEnum
from app.api.deps import CurrentUser


def get_city_by_id(session: Session, city_id: int) -> City:
    return session.exec(select(City).where(City.id == city_id)).first()


def get_all_cities(session: Session):
    return session.exec(select(City)).all()


def get_quests_by_city(session: Session, city_id: int):
    return session.exec(select(Quest).where(Quest.city_id == city_id)).count()


def get_completed_quests_by_city_and_user(session: Session, city_id: int, current_user: CurrentUser):
    return session.exec(
        select(Quest)
        .join(UserQuest, Quest.id == UserQuest.quest_id)
        .where(Quest.city_id == city_id)
        .where(UserQuest.user_id == current_user.id)
        .where(UserQuest.status == QuestStatusEnum.completed)
    ).count()
