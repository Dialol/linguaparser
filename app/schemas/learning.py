from pydantic import BaseModel
from typing import List


class ProgressUpdate(BaseModel):
    action: str


class StudyCard(BaseModel):
    id: int
    word: str
    translation: str
    score: float


class StudySession(BaseModel):
    cards: List[StudyCard]
    count: int


class ProgressResponse(BaseModel):
    word_id: int
    new_score: float
    message: str


class LearningStats(BaseModel):
    total_words: int
    learned_words: int
    in_progress: int
    completion_percentage: float
