from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlmodel import select
from app.models import QuestPublic, CityPublic, Quest, Mission, Dialogue
from app import crud
from app.api.deps import (
    get_current_user,
    SessionDep,
    CurrentUser,
)

router = APIRouter()


@router.get("/", dependencies=[Depends(get_current_user)], response_model=List[QuestPublic])
def get_quests(session: SessionDep):
    results = crud.get_quests_with_cities(session)

    quests_with_cities = [
        QuestPublic(
            id=quest.id,
            title=quest.name,
            description=quest.description,
            picture_small_url=quest.picture_small_url,
            city=CityPublic(
                id=city.id,
                title=city.title,
                latitude=city.latitude,
                longitude=city.longitude
            )
        )
        for quest, city in results
    ]

    return quests_with_cities


@router.get("/{quest_id}", dependencies=[Depends(get_current_user)])
def get_quest(quest_id: int, session: SessionDep, current_user: CurrentUser):
    quest = session.exec(select(Quest).where(Quest.id == quest_id)).first()
    if not quest:
        raise HTTPException(status_code=404, detail="Quest not found")

    missions = session.exec(select(Mission).where(Mission.quest_id == quest_id).order_by(Mission.mission_order)).all()

    detailed_missions = []
    for mission in missions:
        dialogues = session.exec(
            select(Dialogue).where(Dialogue.mission_id == mission.id).order_by(Dialogue.order)).all()

        detailed_missions.append({
            "mission_id": mission.id,
            "name": mission.name,
            "description": mission.description,
            "dialogues": [{"character_name": d.character_name, "text": d.text, "background_url": d.background_url,
                           "character_image_url": d.character_image_url} for d in dialogues]
        })

    return {
        "quest_id": quest.id,
        "title": quest.title,
        "description": quest.description,
        "missions": detailed_missions
    }
