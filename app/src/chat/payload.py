from pydantic import BaseModel

class ChatPayload(BaseModel):
    question: str
