from fastapi import APIRouter
from app.api.routes import login, qa

api_router = APIRouter()

api_router.include_router(login.route, tags=["login"])
api_router.include_router(qa.route, prefix="/qa", tags=["qa"])
