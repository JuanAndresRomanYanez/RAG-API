from pydantic import BaseModel
from typing import List, Optional

class Message(BaseModel):
    role: str
    content: str

class QueryRequest(BaseModel):
    question: str
    history: List[Message] = []
    summary: Optional[str] = ""

class QueryResponse(BaseModel):
    answer: str
    sources: List[str]
    summary: str