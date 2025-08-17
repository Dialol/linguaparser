from pydantic import BaseModel
from datetime import datetime 
from typing import Optional


class UserWordBase(BaseModel):
    word_id: int
    score: float = 0.0


class UserWordCreate(UserWordBase):
    pass


class UserWordUpdate(BaseModel):
    score: Optional[float] = None


class UserWord(UserWordBase):
    id: int
    last_reviewed: datetime

    class Config:
        from_attributes = True


class UserWordWithWord(UserWord):
    word: Optional[str] = None
    translation: Optional[str] = None
