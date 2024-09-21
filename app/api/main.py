from fastapi import APIRouter

from app.api.routes import login, users, stories, places

api_router = APIRouter()
api_router.include_router(login.router, tags=["login"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(stories.router, prefix="/stories", tags=["stories"])
api_router.include_router(places.router, prefix="/places", tags=["places"])
