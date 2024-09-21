from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import select

from app.models import Story, StoriesPublic
from app.api.deps import (
    get_current_user,
    SessionDep,
)

router = APIRouter()


@router.get("/", dependencies=[Depends(get_current_user)], response_model=StoriesPublic)
def get_stories(session: SessionDep):
    statement = select(Story).order_by(Story.created_at.desc())
    stories = session.exec(statement).all()

    return StoriesPublic(data=stories, count=len(stories))


@router.get("/{story_id}", dependencies=[Depends(get_current_user)], response_model=Story)
def get_story_content(story_id: int, session: SessionDep):
    story = session.get(Story, story_id)
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    return story
