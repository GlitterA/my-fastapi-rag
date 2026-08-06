from pydantic import BaseModel

class ChatBody(BaseModel):
    session_id: str
    message: str