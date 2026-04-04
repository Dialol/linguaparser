from fastapi import APIRouter, HTTPException, Depends, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import Optional
from app.core.auth import get_current_user
from app.services.parser import TextParser
from app.services.translator import TranslationService
from app.services.learning import LearningService
from app.services.users import get_or_create_user
from app.models.word import Word
from app.models.user_word import UserWord
from app.core.database import get_db
from sqlalchemy.orm import Session


router = APIRouter()
templates = Jinja2Templates(directory="app/static/html")

parser = TextParser()
translator = TranslationService()
learning_service = LearningService()


@router.get("/")
async def index_page(request: Request):
    return templates.TemplateResponse(
            request=request,
            name="index.html"
            )

@router.post("/parse")
async def parse_content(
    request: Request,
    url: Optional[str] = Form(None), 
    text: Optional[str] = Form(None), 
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
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
        
        db_user = get_or_create_user(db, current_user)

        added_word_ids = (
                db.query(Word.id)
                .filter(Word.word.in_(words))
                .all()
                )

        for (word_id,) in added_word_ids:
            existing = db.query(UserWord).filter(
                    UserWord.user_id == db_user.id,
                    UserWord.word_id == word_id
                    ).first()
            if not existing:
                db.add(UserWord(user_id=db_user.id, word_id=word_id, score=0.0))

        db.commit()

        return templates.TemplateResponse("results.html", {
            "request": request,
            "source_message": source_message,
            "translations": translations,
            "total_count": len(words),
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка парсинга: {str(e)}")


@router.get("/study")
async def study_page(
        request: Request, 
        db: Session = Depends(get_db),
        current_user: dict = Depends(get_current_user),):
    """Страница обучения с карточками"""

    db_user = get_or_create_user(db, current_user)

    cards = learning_service.get_study_session(db, db_user.id)
    
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
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Обновляет прогресс изучения слова"""
    if action not in ["know", "dont_know", "remove"]:
        raise HTTPException(status_code=400, detail="Неизвестное действие")
    
    try:
        db_user = get_or_create_user(db, current_user)
        learning_service.update_progress(db, db_user.id, word_id, action)
        return RedirectResponse(url="/study", status_code=303)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка обновления: {str(e)}")


@router.get("/words")
async def words_page(
        request: Request,
        db: Session = Depends(get_db),
        current_user: dict = Depends(get_current_user),):
    """Страница управления всеми словами"""
    db_user = get_or_create_user(db, current_user)
    words_with_scores = (
            db.query(Word, UserWord.score)
            .outerjoin(
                UserWord,
                (UserWord.word_id == Word.id) & (UserWord.user_id == db_user.id),
                )
            .order_by(Word.word)
            .all()
            )
    
    words_data = []
    for word, score in words_with_scores:
        words_data.append({
            'id': word.id,
            'word': word.word,
            'translation': word.translation,
            'score': score if score is not None else 0.0
        })
    
    return templates.TemplateResponse("words.html", {
        "request": request,
        "words": words_data,
        "total_words": len(words_data)
    })


@router.post("/words/{word_id}/delete")
async def delete_word(
        word_id: int,
        db: Session = Depends(get_db),
        current_user: dict = Depends(get_current_user),):
    """Удаляет слово из базы"""
    try:
        db_user = get_or_create_user(db, current_user)
        user_word = (
        db.query(UserWord)
        .filter(UserWord.user_id == db_user.id, UserWord.word_id == word_id)
        .first()
        )
        if user_word:
            db.delete(user_word)
            db.commit()

        return RedirectResponse(url="/words", status_code=303)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка удаления: {str(e)}")


@router.post("/words/{word_id}/edit")
async def edit_word(
    word_id: int,
    translation: str = Form(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Редактирует перевод слова"""
    try:
        db_user = get_or_create_user(db, current_user)
        word = (
                db.query(Word)
                .join(UserWord, UserWord.word_id == Word.id)
                .filter(UserWord.user_id == db_user.id,
                        Word.id == word_id)
                .first()
                )
        if word:
            word.translation = translation.strip()
            db.commit()
        return RedirectResponse(url="/words", status_code=303)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка редактирования: {str(e)}")


@router.post("/words/{word_id}/score")
async def update_word_score(
    word_id: int,
    score: float = Form(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Обновляет рейтинг слова"""
    try:
        db_user = get_or_create_user(db, current_user)
        user_word = (
                db.query(UserWord)
                .filter(UserWord.user_id == db_user.id, 
                        UserWord.word_id == word_id)
                .first()
                )
        
        if not user_word:
            user_word = UserWord(user_id=db_user.id, word_id=word_id, score=0.0)
            db.add(user_word)
         
        user_word.score = float(score)
        db.commit()
        
        return RedirectResponse(url="/words", status_code=303)
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка обновления рейтинга: {str(e)}")

