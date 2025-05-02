from pydantic import BaseModel
from typing import List

class Message(BaseModel):
    role: str
    content: str

class QueryRequest(BaseModel):
    question: str
    history: List[Message] = []

class QueryResponse(BaseModel):
    answer: str
    sources: list[str]
