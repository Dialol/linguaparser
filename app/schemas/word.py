from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class WordBase(BaseModel):
    word: str
    translation: str


class WordCreate():
    pass 


class WordUpdate(BaseModel):
    word: Optional[str] = None
    translation: Optional[str] = None


class Word(WordBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class WordWithProgress(Word):
    score: Optional[float] = None
    last_reviewed: Optional[datetime] = None

