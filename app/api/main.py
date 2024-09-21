from fastapi import APIRouter, Depends

from app.api.routes import login, users, cities

api_router = APIRouter()
api_router.include_router(login.router, tags=["login"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(cities.router, prefix="/cities", tags=["Cities"])