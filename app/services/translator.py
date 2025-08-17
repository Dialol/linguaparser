from deep_translator import GoogleTranslator
from typing import Dict
from app.models.word import Word
from sqlalchemy.orm import Session


class TranslationService:
    """Сервис для перевода слов"""
    
    def __init__(self):
        self.translator = GoogleTranslator(source='en', target='ru')
    
    def translate_word(self, word: str, db: Session) -> str:
        """Переводит слово или берет из базы"""
        
        existing_word = db.query(Word).filter(Word.word == word.lower()).first()
        
        if existing_word is not None and existing_word.translation is not None:
            return str(existing_word.translation)  
        
        try:
            translation = self.translator.translate(word)
            
            new_word = Word(word=word.lower(), translation=translation)
            db.add(new_word)
            db.commit()
            
            return translation
            
        except Exception as e:
            print(f"Ошибка перевода слова '{word}': {e}")
            return word  
    
    def translate_words(self, words: list[str], db: Session) -> Dict[str, str]:
        """Переводит список слов"""
        translations = {}
        for word in words:
            translation = self.translate_word(word, db)
            translations[word] = translation
        return translations
