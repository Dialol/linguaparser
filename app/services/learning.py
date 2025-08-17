from typing import Optional, Dict, List
from sqlalchemy.orm import Session
from app.models.word import Word
from app.models.user_word import UserWord
import random
from datetime import datetime


class LearningService:
    """Сервис для системы изучения слов"""

    def __init__(self):
        self.min_score = 0
        self.max_score = 10
        self.know_bonus = 1
        self.dont_know_penalty = 1.5
        self.cards_per_session = 10
        self.release_threshold = 7

    def get_study_session(self, db: Session) -> List[Dict]:
        """Получает 10 слов для изучения"""
        
        active_words = db.query(UserWord).filter(
                UserWord.score < self.release_threshold
                ).all()

        if len(active_words) < self.cards_per_session:
            needed = self.cards_per_session - len(active_words)
            new_words = self._get_new_words(db, needed)
            active_words.extend(new_words)

        random.shuffle(active_words)

        session_words = active_words[:self.cards_per_session]

        cards = []
        for user_word in session_words:
            word = db.query(Word).filter(Word.id == user_word.word_id).first()
            if word:
                cards.append({
                    "id": word.id,
                    "word": word.word,
                    "translation": word.translation,
                    "score": user_word.score
                    })

        return cards

    def _get_new_words(self, db: Session, count: int) -> List[UserWord]:
        """Добавляет новые слова в изучение"""

        new_words = db.query(Word).outerjoin(UserWord).filter(
                UserWord.id.is_(None)
                ).limit(count).all()
        
        user_words = []
        for word in new_words:
            user_word = UserWord(word_id=word.id, score=0)
            db.add(user_word)
            user_words.append(user_word)

        db.commit()
        return user_words
    
    def update_progress(self, db: Session, word_id: int, action: str) -> Dict:
        """Обновляет прогресс изучения слова"""
        user_word = db.query(UserWord).filter(
                UserWord.word_id == word_id
                ).first()

        if not user_word:
            user_word = UserWord(word_id=word_id, score=0)
            db.add(user_word)

        if action == "know":
            user_word.score += self.know_bonus
            message = "Отлично! Слово изучено лучше"
        elif action == "dont_know":
            user_word.score -= self.dont_know_penalty
            message = "Плохо, пробуйте еще раз"
        elif action == "remove":
            user_word.score = self.max_score
            message = "Слово убрано из изучения"
        else:
            raise ValueError("Неизвестное действие")

        user_word.score = max(0, user_word.score)
        user_word.last_reviewed = datetime.now()
        db.commit()

        return {
                "word_id": word_id,
                "new_score": user_word.score,
                "message": message
                }

    def get_learning_stats(self, db: Session) -> Dict:
        """Получает статистику изучения"""

        total_words = db.query(Word).count()
        learned_words = db.query(UserWord).filter(
                UserWord.score >= 10
                ).count()
        in_progress = db.query(UserWord).filter(
                UserWord.score < 7
                ).count()

        completion_percentage = 0
        if total_words > 0:
            completion_percentage = round((learned_words / total_words * 100), 2)

        return {
                "total_words": total_words,
                "learned_words": learned_words,
                "in_progress": in_progress,
                "completion_percentage": completion_percentage
                }
