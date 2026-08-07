from fastapi import APIRouter
from app.api.routes import login, qa, documents

api_router = APIRouter()

api_router.include_router(login.route, tags=["login"])
api_router.include_router(qa.route, prefix="/qa", tags=["qa"])
api_router.include_router(documents.route, prefix="/documents", tags=["documents"])
