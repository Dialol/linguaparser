from fastapi import APIRouter, HTTPException, Depends, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import Optional
from app.services.parser import TextParser
from app.services.translator import TranslationService
from app.services.learning import LearningService
from app.models.word import Word
from app.core.database import get_db
from sqlalchemy.orm import Session


router = APIRouter()
templates = Jinja2Templates(directory="app/static/html")

parser = TextParser()
translator = TranslationService()
learning_service = LearningService()


@router.get("/")
async def index_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@router.post("/parse")
async def parse_content(
    request: Request,
    url: Optional[str] = Form(None), 
    text: Optional[str] = Form(None), 
    db: Session = Depends(get_db)
):
    """Парсит текст/URL, добавляет новые слова в базу, показывает результат"""
    if not url and not text:
        raise HTTPException(status_code=400, detail="Нужно указать URL или текст")

    try:
        if url:
            if not url.startswith(('http://', 'https://')):
                url = 'http://' + url
            words = parser.parser_url(url)
            source_message = f"URL: {url}"
        else:
            words = parser.extract_words(text)
            source_message = "введенного текста"

        translations = translator.translate_words(words, db)
        
        existing_words_query = db.query(Word.word).filter(Word.word.in_(words)).all()
        existing_words = [w[0] for w in existing_words_query]
        
        new_words = [w for w in words if w not in existing_words]
        
        added_words = []
        for word in new_words:
            translation = translations.get(word, "Перевод не найден")
            new_word = Word(word=word, translation=translation)
            db.add(new_word)
            added_words.append(word)
        
        db.commit()
        
        return templates.TemplateResponse("results.html", {
            "request": request,
            "source_message": source_message,
            "added_words": added_words,
            "existing_words": existing_words,
            "translations": translations,
            "total_count": len(words),
            "added_count": len(added_words),
            "existing_count": len(existing_words)
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка парсинга: {str(e)}")


@router.get("/study")
async def study_page(request: Request, db: Session = Depends(get_db)):
    """Страница обучения с карточками"""
    cards = learning_service.get_study_session(db)
    
    if not cards:
        return templates.TemplateResponse("study.html", {
            "request": request,
            "cards": [],
            "total_cards": 0,
            "message": "Нет слов для изучения. Сначала добавьте слова через парсинг."
        })
    
    return templates.TemplateResponse("study.html", {
        "request": request,
        "cards": cards,
        "total_cards": len(cards)
    })


@router.post("/study/progress/{word_id}")
async def update_word_progress(
    word_id: int,
    action: str = Form(...),
    db: Session = Depends(get_db)
):
    """Обновляет прогресс изучения слова"""
    if action not in ["know", "dont_know", "remove"]:
        raise HTTPException(status_code=400, detail="Неизвестное действие")
    
    try:
        learning_service.update_progress(db, word_id, action)
        return RedirectResponse(url="/study", status_code=303)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка обновления: {str(e)}")


@router.get("/words")
async def words_page(request: Request, db: Session = Depends(get_db)):
    """Страница управления всеми словами"""
    words = db.query(Word).order_by(Word.word).all()
    
    return templates.TemplateResponse("words.html", {
        "request": request,
        "words": words,
        "total_words": len(words)
    })


@router.post("/words/{word_id}/delete")
async def delete_word(word_id: int, db: Session = Depends(get_db)):
    """Удаляет слово из базы"""
    try:
        word = db.query(Word).filter(Word.id == word_id).first()
        if word:
            db.delete(word)
            db.commit()
        return RedirectResponse(url="/words", status_code=303)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка удаления: {str(e)}")


@router.post("/words/{word_id}/edit")
async def edit_word(
    word_id: int,
    translation: str = Form(...),
    db: Session = Depends(get_db)
):
    """Редактирует перевод слова"""
    try:
        word = db.query(Word).filter(Word.id == word_id).first()
        if word:
            word.translation = translation.strip()
            db.commit()
        return RedirectResponse(url="/words", status_code=303)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка редактирования: {str(e)}")
