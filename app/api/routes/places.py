from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from app.models import Place, PlacePublic, PlaceDetailPublic
from typing import List
from app.api.deps import (
    get_current_user,
    SessionDep,
)

router = APIRouter()


@router.get("/places", dependencies=[Depends(get_current_user)], response_model=List[PlacePublic])
def get_places(session: SessionDep):
    statement = select(Place).order_by(Place.created_at.desc())
    places = session.exec(statement).all()

    return [
        PlacePublic(
            id=place.id,
            title=place.title,
            picture_small_url=place.picture_small_url,
            latitude=place.latitude,
            longitude=place.longitude
        )
        for place in places
    ]


@router.get("/{place_id}", dependencies=[Depends(get_current_user)], response_model=PlaceDetailPublic)
def get_place_detail(place_id: int, session: SessionDep):
    place = session.get(Place, place_id)
    if not place:
        raise HTTPException(status_code=404, detail="Place not found")

    return PlaceDetailPublic(
        id=place.id,
        title=place.title,
        picture_big_url=place.picture_big_url,
        description=place.description,
        latitude=place.latitude,
        longitude=place.longitude
    )
