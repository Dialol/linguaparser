from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from app.services.parser import TextParser
from app.services.translator import TranslationService
from app.services.learning import LearningService
from app.models.word import Word
from app.core.database import get_db
from sqlalchemy.orm import Session
from app.schemas.learning import ProgressUpdate, StudySession, ProgressResponse, LearningStats


router = APIRouter()
parser = TextParser()
translator = TranslationService()
learning_service = LearningService()


class ParserRequest(BaseModel):
    url: Optional[str] = None
    text: Optional[str] = None


class ParserResponse(BaseModel):
    words: list[str]
    count: int
    message: str
    translations: dict[str, str]


@router.post("/parse", response_model=ParserResponse)
async def parser_content(request: ParserRequest, db: Session = Depends(get_db)):
    """Парсит текст или урл и извлекает слова"""
    if not request.url and not request.text:
        raise HTTPException(status_code=400, detail="Нужно указать URL или текст")

    try:
        if request.url:
            words = parser.parser_url(request.url)
            message = f"Успешно спарсили {len(words)} слов с URL"
        else:
            words = parser.extract_words(request.text)
            message = f"Успешно извлекли {len(words)} слов из текста"

        translations = translator.translate_words(words, db)

        return ParserResponse(
                words=words,
                count=len(words),
                message=message,
                translations=translations
                )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка парсинга: {str(e)}")


@router.get("/words")
async def get_words(db: Session = Depends(get_db)):
    """Получает все слова из базы"""
    words = db.query(Word).all()
    return {"words": [{"id": w.id, "word": w.word, "translation": w.translation}
            for w in words]}


@router.get("/cards", response_model=StudySession, tags=["learning"])
async def get_study_cards(db: Session = Depends(get_db)):
    """Получает набор слов для изучения"""
    cards = learning_service.get_study_session(db)
    return {"cards": cards, "count": len(cards)}


@router.post("/cards/{word_id}/progress", response_model=ProgressResponse, tags=["learning"])
async def update_word_progress(
        word_id: int, 
        progress: ProgressUpdate,
        db: Session = Depends(get_db)
        ):
    """Обновляет прогресс изучения слова"""
    if progress.action not in ["know", "dont_know", "remove"]:
        raise HTTPException(status_code=400, detail="Неизвестное действие")
    result = learning_service.update_progress(db, word_id, progress.action)
    return result


@router.get("/stats", response_model=LearningStats, tags=["learning"])
async def get_learning_stats(db: Session = Depends(get_db)):
    """ Получает статистику изучения"""
    return learning_service.get_learning_stats(db)
