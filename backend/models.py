from datetime import datetime
from typing import List
from pydantic import BaseModel

class Message(BaseModel):
    username: str
    text: str
    timestamp: datetime
    read_by: List[str]

class Emoticon(BaseModel):
    name: str
    url: str
    size: str  # small, medium, large
    animated: bool

class File(BaseModel):
    filename: str
    url: str
    version: int
    uploaded_at: datetime
    edited_by: List[str]
