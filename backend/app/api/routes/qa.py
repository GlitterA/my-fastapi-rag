from fastapi import APIRouter

route = APIRouter()


@route.get("/chat")
async def chat_action():
    return "welcome to qa chat"
