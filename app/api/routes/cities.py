from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.models import CityWithProgress
from app import crud
from app.api.deps import (
    get_current_user,
    SessionDep,
    CurrentUser,
)

router = APIRouter()


@router.get("/", dependencies=[Depends(get_current_user)], response_model=List[CityWithProgress])
def get_cities_with_progress(session: SessionDep, current_user: CurrentUser):
    cities = crud.get_all_cities(session)

    cities_with_progress = []
    for city in cities:
        total_quests = crud.get_quests_by_city(session=session, city_id=city.id)
        completed_quests = crud.get_completed_quests_by_city_and_user(session=session, city_id=city.id,
                                                                      current_user=current_user)

        progress = (completed_quests / total_quests) * 100 if total_quests > 0 else 0

        cities_with_progress.append(
            CityWithProgress(
                id=city.id,
                name=city.name,
                description=city.description,
                picture_small_url=city.picture_small_url,
                latitude=city.latitude,
                longitude=city.longitude,
                progress=progress
            )
        )

    return cities_with_progress


@router.get("/{city_id}", dependencies=[Depends(get_current_user)])
def get_city(session: SessionDep, city_id: int):
    city = crud.get_city_by_id(session=session, city_id=city_id)
    if not city:
        raise HTTPException(status_code=404, detail="City not found")

    quests = crud.get_quests_by_city(session=session, city_id=city_id)

    return {
        "city": {
            "id": city.id,
            "name": city.name,
            "description": city.description,
            "picture_small_url": city.picture_small_url,
            "latitude": city.latitude,
            "longitude": city.longitude,
        },
        "quests": [
            {
                "id": quest.id,
                "title": quest.title,
                "description": quest.description,
                "picture_small_url": quest.picture_small_url
            }
            for quest in quests
        ]
    }
